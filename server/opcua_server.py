"""
OPC UA server implementation for CNC machining center.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from typing import Dict, Any

from asyncua import Server, ua
from asyncua.common.methods import uamethod

from .config import ServerConfig
from .simulation import CNCSim, MachineState

logger = logging.getLogger(__name__)


class CNCOPCUAServer:
    """OPC UA server for CNC machining center simulation."""

    def __init__(self, config: ServerConfig):
        self.config = config
        self.server = Server()
        self.simulator = CNCSim(config.simulation)
        self.namespace_idx: int = 0  # Will be set during start()
        self.nodes: Dict[str, Any] = {}
        self.running = False

        # Setup server
        self._setup_server()

    def _setup_server(self):
        """Setup OPC UA server configuration."""
        server_config = self.config.server

        endpoint = server_config.get(
            'endpoint', 'opc.tcp://0.0.0.0:4840/freeopcua/server/')
        self.server.set_endpoint(endpoint)
        server_name = server_config.get('name', 'CNC OPC UA Server')
        self.server.set_server_name(server_name)

        # Setup security (optional)
        self.server.set_security_policy([ua.SecurityPolicyType.NoSecurity])

    async def start(self):
        """Start the OPC UA server."""
        try:
            await self.server.init()

            # Register namespace
            namespace_uri = self.config.server.get(
                'namespace', 'http://manufacturing.example.com/cnc')
            self.namespace_idx = await self.server.register_namespace(
                namespace_uri)

            # Create node structure
            await self._create_node_structure()

            # Start server
            await self.server.start()
            self.running = True

            logger.info(f"OPC UA server started at {self.server.endpoint}")

            # Start simulation update loop
            await self._update_loop()

        except Exception as e:
            logger.error(f"Failed to start OPC UA server: {e}")
            raise

    async def stop(self):
        """Stop the OPC UA server."""
        self.running = False
        await self.server.stop()
        logger.info("OPC UA server stopped")

    async def _create_node_structure(self):
        """Create the OPC UA node structure."""
        if self.namespace_idx <= 0:
            raise RuntimeError("Namespace index not properly initialized")

        # Get root objects node
        objects = self.server.get_objects_node()

        # Machine root folder
        machine_config = self.config.machine
        machine_name = machine_config.get('name', 'CNC Machine')
        machine_folder = await objects.add_folder(
            self.namespace_idx, machine_name)

        # Machine information
        info_folder = await machine_folder.add_folder(
            self.namespace_idx, "Information")
        await info_folder.add_variable(
            self.namespace_idx, "Manufacturer",
            machine_config.get('manufacturer', 'Unknown'))
        await info_folder.add_variable(
            self.namespace_idx, "Model",
            machine_config.get('model', 'Unknown'))
        await info_folder.add_variable(
            self.namespace_idx, "SerialNumber",
            machine_config.get('serial_number', 'Unknown'))

        # Machine state
        state_folder = await machine_folder.add_folder(
            self.namespace_idx, "State")
        self.nodes['machine_state'] = await state_folder.add_variable(
            self.namespace_idx, "CurrentState", MachineState.IDLE.value)
        await self.nodes['machine_state'].set_writable()

        # Spindle data - specify as Double type
        spindle_folder = await machine_folder.add_folder(
            self.namespace_idx, "Spindle")
        self.nodes['spindle_speed'] = await spindle_folder.add_variable(
            self.namespace_idx, "Speed", 0.0, ua.VariantType.Double)
        self.nodes['spindle_load'] = await spindle_folder.add_variable(
            self.namespace_idx, "Load", 0.0, ua.VariantType.Double)
        self.nodes['spindle_torque'] = await spindle_folder.add_variable(
            self.namespace_idx, "Torque", 0.0, ua.VariantType.Double)
        self.nodes['spindle_power'] = await spindle_folder.add_variable(
            self.namespace_idx, "Power", 0.0, ua.VariantType.Double)
        self.nodes['spindle_temperature'] = await spindle_folder.add_variable(
            self.namespace_idx, "Temperature", 22.0, ua.VariantType.Double)

        # Feed system data - specify as Double type
        feed_folder = await machine_folder.add_folder(
            self.namespace_idx, "FeedSystem")
        self.nodes['feed_rate'] = await feed_folder.add_variable(
            self.namespace_idx, "FeedRate", 0.0, ua.VariantType.Double)
        self.nodes['feed_override'] = await feed_folder.add_variable(
            self.namespace_idx, "Override", 100.0, ua.VariantType.Double)

        # Position data
        position_folder = await feed_folder.add_folder(
            self.namespace_idx, "Position")
        self.nodes['position_x'] = await position_folder.add_variable(
            self.namespace_idx, "X", 0.0, ua.VariantType.Double)
        self.nodes['position_y'] = await position_folder.add_variable(
            self.namespace_idx, "Y", 0.0, ua.VariantType.Double)
        self.nodes['position_z'] = await position_folder.add_variable(
            self.namespace_idx, "Z", 0.0, ua.VariantType.Double)

        # Tool data - mix of int and float types
        tool_folder = await machine_folder.add_folder(
            self.namespace_idx, "Tool")
        self.nodes['tool_number'] = await tool_folder.add_variable(
            self.namespace_idx, "Number", 1, ua.VariantType.Int32)
        self.nodes['tool_life'] = await tool_folder.add_variable(
            self.namespace_idx, "LifeRemaining", 100.0, ua.VariantType.Double)
        self.nodes['tool_wear_x'] = await tool_folder.add_variable(
            self.namespace_idx, "WearX", 0.0, ua.VariantType.Double)
        self.nodes['tool_wear_z'] = await tool_folder.add_variable(
            self.namespace_idx, "WearZ", 0.0, ua.VariantType.Double)
        self.nodes['tool_state'] = await tool_folder.add_variable(
            self.namespace_idx, "State", "New", ua.VariantType.String)

        # Vibration data - specify as Double type
        vibration_folder = await machine_folder.add_folder(
            self.namespace_idx, "Vibration")
        self.nodes['vibration_x'] = await vibration_folder.add_variable(
            self.namespace_idx, "X_Axis", 0.0, ua.VariantType.Double)
        self.nodes['vibration_y'] = await vibration_folder.add_variable(
            self.namespace_idx, "Y_Axis", 0.0, ua.VariantType.Double)
        self.nodes['vibration_z'] = await vibration_folder.add_variable(
            self.namespace_idx, "Z_Axis", 0.0, ua.VariantType.Double)
        self.nodes['vibration_overall'] = await vibration_folder.add_variable(
            self.namespace_idx, "Overall", 0.0, ua.VariantType.Double)

        # Production data - mix of int and float types
        production_folder = await machine_folder.add_folder(
            self.namespace_idx, "Production")
        self.nodes['parts_produced'] = await production_folder.add_variable(
            self.namespace_idx, "PartsProduced", 0, ua.VariantType.Int32)
        self.nodes['cycle_time'] = await production_folder.add_variable(
            self.namespace_idx, "CycleTime", 0.0, ua.VariantType.Double)
        self.nodes['good_parts'] = await production_folder.add_variable(
            self.namespace_idx, "GoodParts", 0, ua.VariantType.Int32)
        self.nodes['rejected_parts'] = await production_folder.add_variable(
            self.namespace_idx, "RejectedParts", 0, ua.VariantType.Int32)
        self.nodes['efficiency'] = await production_folder.add_variable(
            self.namespace_idx, "Efficiency", 0.0, ua.VariantType.Double)

        # Auxiliary systems - specify as Double type
        aux_folder = await machine_folder.add_folder(
            self.namespace_idx, "AuxiliarySystems")
        self.nodes['coolant_level'] = await aux_folder.add_variable(
            self.namespace_idx, "CoolantLevel", 100.0, ua.VariantType.Double)
        self.nodes['coolant_temperature'] = await aux_folder.add_variable(
            self.namespace_idx, "CoolantTemperature", 25.0,
            ua.VariantType.Double)
        self.nodes['air_pressure'] = await aux_folder.add_variable(
            self.namespace_idx, "AirPressure", 6.0, ua.VariantType.Double)
        self.nodes['hydraulic_pressure'] = await aux_folder.add_variable(
            self.namespace_idx, "HydraulicPressure", 40.0,
            ua.VariantType.Double)

        # Timestamp
        self.nodes['timestamp'] = await machine_folder.add_variable(
            self.namespace_idx, "Timestamp", datetime.now(),
            ua.VariantType.DateTime)

        # Add methods
        await self._add_methods(machine_folder)

        # Set units and descriptions
        await self._set_variable_metadata()

        logger.info("OPC UA node structure created")

    async def _add_methods(self, parent_node):
        """Add OPC UA methods."""
        methods_folder = await parent_node.add_folder(
            self.namespace_idx, "Methods")

        # Reset production counters method
        @uamethod
        def reset_production_counters(parent):
            """Reset production counters to zero."""
            self.simulator.data.production.parts_produced = 0
            self.simulator.data.production.good_parts = 0
            self.simulator.data.production.rejected_parts = 0
            self.simulator.data.production.efficiency = 0.0
            logger.info("Production counters reset")
            return True

        # Emergency stop method
        @uamethod
        def emergency_stop(parent):
            """Trigger emergency stop."""
            self.simulator.data.state = MachineState.ALARM
            self.simulator.program_running = False
            logger.warning("Emergency stop triggered")
            return True

        # Tool change method
        @uamethod
        def change_tool(parent, tool_number: int):
            """Change to specified tool number."""
            self.simulator.data.tool.number = tool_number
            self.simulator.data.tool.wear_x = 0.0
            self.simulator.data.tool.wear_z = 0.0
            self.simulator.data.tool.life_remaining = 100.0
            logger.info(f"Tool changed to T{tool_number}")
            return True

        await methods_folder.add_method(
            self.namespace_idx, "ResetProductionCounters",
            reset_production_counters)
        await methods_folder.add_method(
            self.namespace_idx, "EmergencyStop", emergency_stop)
        await methods_folder.add_method(
            self.namespace_idx, "ChangeTool", change_tool,
            [ua.VariantType.Int32], [ua.VariantType.Boolean])

    async def _set_variable_metadata(self):
        """Set units and descriptions for variables."""
        # Define units
        units = {
            'spindle_speed': 'rpm',
            'spindle_load': '%',
            'spindle_torque': 'Nm',
            'spindle_power': 'kW',
            'spindle_temperature': '°C',
            'feed_rate': 'mm/min',
            'feed_override': '%',
            'position_x': 'mm',
            'position_y': 'mm',
            'position_z': 'mm',
            'tool_life': '%',
            'tool_wear_x': 'mm',
            'tool_wear_z': 'mm',
            'vibration_x': 'mm/s RMS',
            'vibration_y': 'mm/s RMS',
            'vibration_z': 'mm/s RMS',
            'vibration_overall': 'mm/s RMS',
            'cycle_time': 's',
            'efficiency': '%',
            'coolant_level': '%',
            'coolant_temperature': '°C',
            'air_pressure': 'bar',
            'hydraulic_pressure': 'bar'
        }

        # Set engineering units (corrected approach)
        for node_name, unit in units.items():
            if node_name in self.nodes:
                try:
                    description = ua.LocalizedText(f"Unit: {unit}")
                    variant = ua.Variant(
                        description, ua.VariantType.LocalizedText)
                    await self.nodes[node_name].write_attribute(
                        ua.AttributeIds.Description,
                        ua.DataValue(variant)
                    )
                except Exception as e:
                    logger.warning(f"Could not set unit for {node_name}: {e}")

    async def _update_loop(self):
        """Main update loop for simulation data."""
        update_interval = self.config.simulation.get('update_interval', 1.0)

        while self.running:
            try:
                # Update simulation
                machine_data = self.simulator.update(update_interval)

                # Update OPC UA variables
                await self._update_opcua_variables(machine_data)

                await asyncio.sleep(update_interval)

            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(1.0)

    async def _update_opcua_variables(self, data):
        """Update OPC UA variables with simulation data."""
        try:
            # Machine state
            await self.nodes['machine_state'].write_value(data.state.value)

            # Spindle data - ensure float types
            await self.nodes['spindle_speed'].write_value(
                float(data.spindle.speed))
            await self.nodes['spindle_load'].write_value(
                float(data.spindle.load))
            await self.nodes['spindle_torque'].write_value(
                float(data.spindle.torque))
            await self.nodes['spindle_power'].write_value(
                float(data.spindle.power))
            await self.nodes['spindle_temperature'].write_value(
                float(data.spindle.temperature))

            # Feed system data
            await self.nodes['feed_rate'].write_value(float(data.feed.rate))
            await self.nodes['feed_override'].write_value(
                float(data.feed.override))
            await self.nodes['position_x'].write_value(
                float(data.feed.position_x))
            await self.nodes['position_y'].write_value(
                float(data.feed.position_y))
            await self.nodes['position_z'].write_value(
                float(data.feed.position_z))

            # Tool data - mix of int and float
            await self.nodes['tool_number'].write_value(int(data.tool.number))
            await self.nodes['tool_life'].write_value(float(data.tool.life_remaining))
            await self.nodes['tool_wear_x'].write_value(float(data.tool.wear_x))
            await self.nodes['tool_wear_z'].write_value(float(data.tool.wear_z))
            await self.nodes['tool_state'].write_value(data.tool.state.value)

            # Vibration data
            await self.nodes['vibration_x'].write_value(float(data.vibration.x_axis))
            await self.nodes['vibration_y'].write_value(float(data.vibration.y_axis))
            await self.nodes['vibration_z'].write_value(float(data.vibration.z_axis))
            await self.nodes['vibration_overall'].write_value(
                float(data.vibration.overall))

            # Production data - mix of int and float
            await self.nodes['parts_produced'].write_value(
                int(data.production.parts_produced))
            await self.nodes['cycle_time'].write_value(
                float(data.production.cycle_time))
            await self.nodes['good_parts'].write_value(int(data.production.good_parts))
            await self.nodes['rejected_parts'].write_value(
                int(data.production.rejected_parts))
            await self.nodes['efficiency'].write_value(
                float(data.production.efficiency))

            # Auxiliary systems
            await self.nodes['coolant_level'].write_value(float(data.coolant_level))
            await self.nodes['coolant_temperature'].write_value(
                float(data.coolant_temperature))
            await self.nodes['air_pressure'].write_value(float(data.air_pressure))
            await self.nodes['hydraulic_pressure'].write_value(
                float(data.hydraulic_pressure))

            # Timestamp
            await self.nodes['timestamp'].write_value(data.timestamp)

        except Exception as e:
            logger.error(f"Error updating OPC UA variables: {e}")


async def main():
    """Main function to run the OPC UA server."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Load configuration
    config = ServerConfig()

    # Create and start server
    server = CNCOPCUAServer(config)

    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
