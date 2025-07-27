"""
Data models for the CNC machining center simulation.
"""

import random
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MachineState(Enum):
    """Machine operating states."""
    IDLE = "Idle"
    RUNNING = "Running"
    ALARM = "Alarm"
    MAINTENANCE = "Maintenance"
    SETUP = "Setup"


class CuttingToolState(Enum):
    """Cutting tool states."""
    NEW = "New"
    GOOD = "Good"
    WORN = "Worn"
    BROKEN = "Broken"


@dataclass
class SpindleData:
    """Spindle sensor data."""
    speed: float = 0.0          # RPM
    load: float = 0.0           # %
    torque: float = 0.0         # Nm
    power: float = 0.0          # kW
    temperature: float = 22.0   # °C


@dataclass
class FeedData:
    """Feed system data."""
    rate: float = 0.0           # mm/min
    override: float = 100.0     # %
    position_x: float = 0.0     # mm
    position_y: float = 0.0     # mm
    position_z: float = 0.0     # mm


@dataclass
class ToolData:
    """Cutting tool data."""
    number: int = 1
    offset_length: float = 150.0    # mm
    offset_radius: float = 10.0     # mm
    wear_x: float = 0.0             # mm
    wear_z: float = 0.0             # mm
    life_remaining: float = 100.0   # %
    state: CuttingToolState = CuttingToolState.NEW


@dataclass
class VibrationData:
    """Vibration sensor data."""
    x_axis: float = 0.0         # mm/s RMS
    y_axis: float = 0.0         # mm/s RMS
    z_axis: float = 0.0         # mm/s RMS
    overall: float = 0.0        # mm/s RMS


@dataclass
class ProductionData:
    """Production metrics."""
    parts_produced: int = 0
    cycle_time: float = 0.0     # seconds
    good_parts: int = 0
    rejected_parts: int = 0
    efficiency: float = 0.0     # %


@dataclass
class MachineData:
    """Complete machine data snapshot."""
    timestamp: datetime = field(default_factory=datetime.now)
    state: MachineState = MachineState.IDLE
    spindle: SpindleData = field(default_factory=SpindleData)
    feed: FeedData = field(default_factory=FeedData)
    tool: ToolData = field(default_factory=ToolData)
    vibration: VibrationData = field(default_factory=VibrationData)
    production: ProductionData = field(default_factory=ProductionData)
    coolant_level: float = 100.0    # %
    coolant_temperature: float = 25.0  # °C
    air_pressure: float = 6.0       # bar
    hydraulic_pressure: float = 40.0  # bar


class CNCSim:
    """CNC machining center simulator."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.data = MachineData()
        self.simulation_time = 0.0
        self.cycle_start_time = 0.0
        self.target_spindle_speed = 0.0
        self.target_feed_rate = 0.0
        self.program_running = False
        self.program_progress = 0.0
        self.noise_factor = config.get('noise_factor', 0.05)
        
        # Machining program simulation
        self.machining_programs = [
            {"name": "PART_001", "cycle_time": 180, "spindle_speeds": [2000, 3500, 1800]},
            {"name": "PART_002", "cycle_time": 240, "spindle_speeds": [1500, 4200, 2800]},
            {"name": "PART_003", "cycle_time": 150, "spindle_speeds": [3000, 2200, 3800]},
        ]
        self.current_program = None
        
        logger.info("CNC simulator initialized")
    
    def update(self, dt: float) -> MachineData:
        """Update simulation by time delta."""
        self.simulation_time += dt
        
        # Update machine state logic
        self._update_machine_state()
        
        # Update various subsystems
        self._update_spindle(dt)
        self._update_feed_system(dt)
        self._update_tool_data(dt)
        self._update_vibration(dt)
        self._update_auxiliary_systems(dt)
        
        self.data.timestamp = datetime.now()
        return self.data
    
    def _update_machine_state(self):
        """Update machine operating state."""
        if self.data.state == MachineState.IDLE:
            # Randomly start a machining program
            if random.random() < 0.02:  # 2% chance per update
                self._start_machining_program()
        
        elif self.data.state == MachineState.RUNNING:
            # Check if program should complete
            if self.program_running and self.program_progress >= 1.0:
                self._complete_machining_program()
            
            # Small chance of alarm
            if random.random() < 0.001:  # 0.1% chance
                self.data.state = MachineState.ALARM
                self.program_running = False
        
        elif self.data.state == MachineState.ALARM:
            # Simulate alarm clearing
            if random.random() < 0.1:  # 10% chance per update
                self.data.state = MachineState.IDLE
    
    def _start_machining_program(self):
        """Start a new machining program."""
        self.current_program = random.choice(self.machining_programs)
        self.data.state = MachineState.RUNNING
        self.program_running = True
        self.program_progress = 0.0
        self.cycle_start_time = self.simulation_time
        logger.info(f"Started machining program: {self.current_program['name']}")
    
    def _complete_machining_program(self):
        """Complete current machining program."""
        self.data.state = MachineState.IDLE
        self.program_running = False
        self.program_progress = 0.0
        
        # Update production data
        self.data.production.parts_produced += 1
        cycle_time = self.simulation_time - self.cycle_start_time
        self.data.production.cycle_time = cycle_time
        
        # Simulate quality check (95% good parts)
        if random.random() < 0.95:
            self.data.production.good_parts += 1
        else:
            self.data.production.rejected_parts += 1
        
        # Calculate efficiency
        total_parts = self.data.production.good_parts + self.data.production.rejected_parts
        if total_parts > 0:
            self.data.production.efficiency = (self.data.production.good_parts / total_parts) * 100
        
        logger.info(f"Completed part production, cycle time: {cycle_time:.1f}s")
    
    def _update_spindle(self, dt: float):
        """Update spindle data."""
        if self.data.state == MachineState.RUNNING and self.current_program:
            # Simulate spindle speed profile during machining
            speeds = self.current_program['spindle_speeds']
            speed_index = int(self.program_progress * len(speeds))
            speed_index = min(speed_index, len(speeds) - 1)
            self.target_spindle_speed = speeds[speed_index]
            
            # Update program progress
            cycle_time = self.current_program['cycle_time']
            elapsed_time = self.simulation_time - self.cycle_start_time
            self.program_progress = min(elapsed_time / cycle_time, 1.0)
        else:
            self.target_spindle_speed = 0.0
        
        # Simulate spindle acceleration/deceleration
        max_accel = self.config.get('parameters', {}).get('spindle', {}).get('acceleration', 500)
        speed_diff = self.target_spindle_speed - self.data.spindle.speed
        max_change = max_accel * dt
        
        if abs(speed_diff) <= max_change:
            self.data.spindle.speed = self.target_spindle_speed
        else:
            self.data.spindle.speed += max_change if speed_diff > 0 else -max_change
        
        # Add noise
        self.data.spindle.speed += random.gauss(0, self.data.spindle.speed * self.noise_factor * 0.1)
        self.data.spindle.speed = max(0, self.data.spindle.speed)
        
        # Calculate dependent values
        if self.data.spindle.speed > 0:
            # Spindle load based on cutting conditions
            base_load = 30 + (self.data.spindle.speed / 6000) * 40  # 30-70% load
            self.data.spindle.load = base_load + random.gauss(0, 5)
            self.data.spindle.load = max(0, min(100, self.data.spindle.load))
            
            # Torque and power calculations
            self.data.spindle.torque = (self.data.spindle.load / 100) * 200  # Max 200 Nm
            self.data.spindle.power = (self.data.spindle.torque * self.data.spindle.speed * 2 * np.pi) / (60 * 1000)
            
            # Temperature rises with load and speed
            temp_rise = (self.data.spindle.load / 100) * 30 + (self.data.spindle.speed / 6000) * 20
            self.data.spindle.temperature = 22 + temp_rise + random.gauss(0, 2)
        else:
            self.data.spindle.load = 0
            self.data.spindle.torque = 0
            self.data.spindle.power = 0
            # Temperature slowly returns to ambient
            self.data.spindle.temperature += (22 - self.data.spindle.temperature) * 0.1 * dt
    
    def _update_feed_system(self, dt: float):
        """Update feed system data."""
        if self.data.state == MachineState.RUNNING:
            # Simulate feed rate based on machining conditions
            base_feed = 500 + (self.program_progress * 2000)  # Variable feed rate
            self.target_feed_rate = base_feed * (self.data.feed.override / 100)
        else:
            self.target_feed_rate = 0
        
        # Smooth feed rate changes
        feed_diff = self.target_feed_rate - self.data.feed.rate
        max_change = 1000 * dt  # mm/min per second
        
        if abs(feed_diff) <= max_change:
            self.data.feed.rate = self.target_feed_rate
        else:
            self.data.feed.rate += max_change if feed_diff > 0 else -max_change
        
        # Add noise
        self.data.feed.rate += random.gauss(0, self.data.feed.rate * self.noise_factor * 0.1)
        self.data.feed.rate = max(0, self.data.feed.rate)
        
        # Simulate axis positions (simplified circular path)
        if self.data.state == MachineState.RUNNING:
            radius = 50  # mm
            angle = self.simulation_time * 0.1  # slow rotation
            self.data.feed.position_x = radius * np.cos(angle) + random.gauss(0, 0.01)
            self.data.feed.position_y = radius * np.sin(angle) + random.gauss(0, 0.01)
            self.data.feed.position_z = -10 + self.program_progress * -5 + random.gauss(0, 0.01)
    
    def _update_tool_data(self, dt: float):
        """Update cutting tool data."""
        if self.data.state == MachineState.RUNNING:
            # Simulate tool wear
            wear_rate = 0.001 * dt  # mm per second
            self.data.tool.wear_x += wear_rate * random.uniform(0.5, 1.5)
            self.data.tool.wear_z += wear_rate * random.uniform(0.5, 1.5)
            
            # Calculate remaining tool life
            max_wear = 0.2  # mm
            wear_percentage = max(self.data.tool.wear_x, self.data.tool.wear_z) / max_wear * 100
            self.data.tool.life_remaining = max(0, 100 - wear_percentage)
            
            # Update tool state based on wear
            if self.data.tool.life_remaining > 80:
                self.data.tool.state = CuttingToolState.NEW
            elif self.data.tool.life_remaining > 20:
                self.data.tool.state = CuttingToolState.GOOD
            elif self.data.tool.life_remaining > 5:
                self.data.tool.state = CuttingToolState.WORN
            else:
                self.data.tool.state = CuttingToolState.BROKEN
    
    def _update_vibration(self, dt: float):
        """Update vibration sensor data."""
        # Base vibration levels
        base_vibration = 0.15  # mm/s RMS
        
        if self.data.state == MachineState.RUNNING:
            # Vibration increases with spindle speed and feed rate
            speed_factor = self.data.spindle.speed / 6000
            feed_factor = self.data.feed.rate / 15000
            load_factor = self.data.spindle.load / 100
            
            vibration_multiplier = 1 + speed_factor * 2 + feed_factor * 1.5 + load_factor
            
            # Tool wear increases vibration
            wear_factor = (100 - self.data.tool.life_remaining) / 100
            vibration_multiplier += wear_factor * 3
            
        else:
            vibration_multiplier = 0.5  # Low vibration when idle
        
        # Generate vibration for each axis
        self.data.vibration.x_axis = base_vibration * vibration_multiplier * random.uniform(0.8, 1.2)
        self.data.vibration.y_axis = base_vibration * vibration_multiplier * random.uniform(0.8, 1.2)
        self.data.vibration.z_axis = base_vibration * vibration_multiplier * random.uniform(0.9, 1.1)
        
        # Calculate overall vibration (RMS of all axes)
        self.data.vibration.overall = np.sqrt(
            self.data.vibration.x_axis**2 + 
            self.data.vibration.y_axis**2 + 
            self.data.vibration.z_axis**2
        )
    
    def _update_auxiliary_systems(self, dt: float):
        """Update auxiliary system data."""
        # Coolant level slowly decreases during operation
        if self.data.state == MachineState.RUNNING:
            self.data.coolant_level -= 0.01 * dt  # % per second
            self.data.coolant_level = max(0, self.data.coolant_level)
        
        # Coolant temperature
        if self.data.state == MachineState.RUNNING:
            target_temp = 30 + (self.data.spindle.load / 100) * 10
        else:
            target_temp = 25
        
        temp_diff = target_temp - self.data.coolant_temperature
        self.data.coolant_temperature += temp_diff * 0.1 * dt
        self.data.coolant_temperature += random.gauss(0, 0.5)
        
        # Air pressure (slight variations)
        self.data.air_pressure = 6.0 + random.gauss(0, 0.1)
        self.data.air_pressure = max(5.5, min(6.5, self.data.air_pressure))
        
        # Hydraulic pressure
        if self.data.state == MachineState.RUNNING:
            self.data.hydraulic_pressure = 40 + random.gauss(0, 2)
        else:
            self.data.hydraulic_pressure = 35 + random.gauss(0, 1)
        
        self.data.hydraulic_pressure = max(30, min(50, self.data.hydraulic_pressure))
