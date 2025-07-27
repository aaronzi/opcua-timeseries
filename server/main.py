"""
Main entry point for the CNC OPC UA server.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

from .config import ServerConfig
from .opcua_server import CNCOPCUAServer


def setup_logging(config: ServerConfig):
    """Setup logging configuration."""
    log_config = config.get('logging', {}) or {}
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_config.get('level', 'INFO')),
        format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        handlers=[
            logging.FileHandler(log_config.get('file', 'logs/opcua_server.log')),
            logging.StreamHandler(sys.stdout)
        ]
    )


async def run_server():
    """Run the OPC UA server with proper signal handling."""
    # Load configuration
    config = ServerConfig()
    
    # Setup logging
    setup_logging(config)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting CNC OPC UA Server")
    
    # Create server instance
    server = CNCOPCUAServer(config)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        server.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await server.start()
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")


def main():
    """Main function."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
