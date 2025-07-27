"""
Configuration management for the OPC UA server.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class ServerConfig:
    """Manages server configuration from YAML file."""
    
    def __init__(self, config_path: str = "config/server_config.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {self.config_path}")
            # Ensure we return a dict, fallback to default if not
            if isinstance(config, dict):
                return config
            else:
                logger.warning("Configuration file did not contain a dict, using defaults")
                return self._get_default_config()
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            return self._get_default_config()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file is not found."""
        return {
            "server": {
                "name": "CNC Machining Center OPC UA Server",
                "endpoint": "opc.tcp://0.0.0.0:4840/freeopcua/server/",
                "namespace": "http://manufacturing.example.com/cnc"
            },
            "machine": {
                "name": "DMG MORI CTX 650 CNC Lathe",
                "model": "CTX650",
                "manufacturer": "DMG MORI",
                "serial_number": "CTX650-2024-001"
            },
            "simulation": {
                "update_interval": 1.0,
                "noise_factor": 0.05
            },
            "parameters": {
                "spindle": {
                    "max_speed": 6000,
                    "min_speed": 100,
                    "acceleration": 500
                },
                "feed_rate": {
                    "max_rate": 15000,
                    "min_rate": 10
                },
                "temperature": {
                    "ambient": 22,
                    "max_operating": 85
                },
                "vibration": {
                    "normal_range": [0.1, 0.3],
                    "warning_threshold": 1.0,
                    "alarm_threshold": 2.0
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/opcua_server.log"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        keys = key.split('.')
        value: Any = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    @property
    def server(self) -> Dict[str, Any]:
        """Get server configuration."""
        result = self._config.get("server", {})
        # Ensure we always return a dict
        return result if isinstance(result, dict) else {}
    
    @property
    def machine(self) -> Dict[str, Any]:
        """Get machine configuration."""
        result = self._config.get("machine", {})
        # Ensure we always return a dict
        return result if isinstance(result, dict) else {}
    
    @property
    def simulation(self) -> Dict[str, Any]:
        """Get simulation configuration."""
        result = self._config.get("simulation", {})
        # Ensure we always return a dict
        return result if isinstance(result, dict) else {}
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """Get machine parameters configuration."""
        result = self._config.get("parameters", {})
        # Ensure we always return a dict
        return result if isinstance(result, dict) else {}