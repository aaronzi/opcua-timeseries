"""
OPC UA client test utility for connecting to the CNC server.
"""

import asyncio
import logging
import pytest
from asyncua import Client


@pytest.mark.asyncio
async def test_connection(url: str = "opc.tcp://localhost:4840/freeopcua/server/"):
    """Test connection to OPC UA server."""
    logger = logging.getLogger(__name__)
    
    try:
        async with Client(url=url) as client:
            logger.info(f"Connected to OPC UA server at {url}")
            
            # Get root node
            root = client.get_root_node()
            logger.info(f"Root node: {root}")
            
            # Browse objects
            objects = client.get_objects_node()
            children = await objects.get_children()
            
            for child in children:
                try:
                    name = await child.read_browse_name()
                    logger.info(f"Object: {name}")
                except Exception as e:
                    logger.warning(f"Could not read browse name: {e}")
            
            return True
            
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


@pytest.mark.asyncio
async def test_read_machine_data(url: str = "opc.tcp://localhost:4840/freeopcua/server/"):
    """Read and display machine data from OPC UA server."""
    logger = logging.getLogger(__name__)
    
    try:
        async with Client(url=url) as client:
            logger.info(f"Connected to OPC UA server at {url}")
            
            # Navigate to machine data
            root = client.get_root_node()
            objects = client.get_objects_node()
            
            # Find the machine folder (assuming first child is our machine)
            children = await objects.get_children()
            machine_node = children[0] if children else None
            
            if not machine_node:
                logger.error("No machine node found")
                return
            
            machine_name = await machine_node.read_browse_name()
            logger.info(f"Reading data from: {machine_name}")
            
            # Read some key variables
            try:
                # Find spindle folder
                machine_children = await machine_node.get_children()
                for child in machine_children:
                    browse_name = await child.read_browse_name()
                    if "Spindle" in str(browse_name):
                        spindle_children = await child.get_children()
                        for spindle_var in spindle_children:
                            var_name = await spindle_var.read_browse_name()
                            try:
                                value = await spindle_var.read_value()
                                logger.info(f"  {var_name}: {value}")
                            except Exception as e:
                                logger.warning(f"Could not read {var_name}: {e}")
                        break
                        
            except Exception as e:
                logger.error(f"Error reading machine data: {e}")
            
    except Exception as e:
        logger.error(f"Failed to read machine data: {e}")


async def monitor_machine_data(url: str = "opc.tcp://localhost:4840/freeopcua/server/", 
                              duration: int = 30):
    """Monitor machine data for a specified duration."""
    logger = logging.getLogger(__name__)
    
    try:
        async with Client(url=url) as client:
            logger.info(f"Monitoring machine data for {duration} seconds...")
            
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                await test_read_machine_data(url)
                await asyncio.sleep(5)  # Read every 5 seconds
                
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")


def main():
    """Main function for client testing."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("CNC OPC UA Client Test Utility")
    print("1. Test connection")
    print("2. Read machine data once")
    print("3. Monitor machine data (30 seconds)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(test_connection())
    elif choice == "2":
        asyncio.run(test_read_machine_data())
    elif choice == "3":
        asyncio.run(monitor_machine_data())
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
