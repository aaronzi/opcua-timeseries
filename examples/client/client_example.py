"""
Example script showing how to connect to the CNC OPC UA server
and read time series data.
"""

import asyncio
import logging
import csv
from datetime import datetime
from typing import Any, Dict
from asyncua import Client


class CNClientExample:
    """Example OPC UA client for CNC data collection."""
    
    def __init__(self, url: str = "opc.tcp://localhost:4840/freeopcua/server/"):
        self.url = url
        self.client = None
        self.nodes: Dict[str, Any] = {}
        
    async def connect(self):
        """Connect to the OPC UA server."""
        self.client = Client(url=self.url)
        await self.client.connect()
        print(f"Connected to {self.url}")
        
        # Find and cache important nodes
        await self._find_nodes()
        
    async def disconnect(self):
        """Disconnect from the OPC UA server."""
        if self.client:
            await self.client.disconnect()
            print("Disconnected from server")
    
    async def _find_nodes(self):
        """Find and cache important OPC UA nodes."""
        if not self.client:
            raise Exception("Client not connected")
            
        # Navigate to machine node
        root = self.client.get_root_node()
        objects = self.client.get_objects_node()
        children = await objects.get_children()
        
        if not children:
            raise Exception("No machine nodes found")
            
        machine_node = children[0]  # Assume first child is our machine
        
        # Cache commonly used nodes
        await self._cache_nodes_recursive(machine_node, "")
        
    async def _cache_nodes_recursive(self, node, path_prefix):
        """Recursively cache nodes for easy access."""
        try:
            browse_name = await node.read_browse_name()
            node_name = str(browse_name).split(':')[-1]  # Get name part
            current_path = f"{path_prefix}.{node_name}" if path_prefix else node_name
            
            # Check if this is a variable (leaf node)
            node_class = await node.read_node_class()
            if node_class == 2:  # Variable node
                self.nodes[current_path] = node
                
            # Recurse into children
            children = await node.get_children()
            for child in children:
                await self._cache_nodes_recursive(child, current_path)
                
        except Exception as e:
            logging.warning(f"Could not process node: {e}")
    
    async def read_all_data(self):
        """Read all cached node values."""
        data = {}
        data['timestamp'] = datetime.now().isoformat()
        
        for path, node in self.nodes.items():
            try:
                value = await node.read_value()
                data[path] = value
            except Exception as e:
                logging.warning(f"Could not read {path}: {e}")
                data[path] = None
                
        return data
    
    async def log_data_to_csv(self, filename: str = "cnc_data.csv", duration: int = 300, interval: int = 5):
        """Log data to CSV file for specified duration."""
        print(f"Logging data to {filename} for {duration} seconds (interval: {interval}s)")
        
        data_points = []
        start_time = asyncio.get_event_loop().time()
        
        # Collect data
        while (asyncio.get_event_loop().time() - start_time) < duration:
            data = await self.read_all_data()
            data_points.append(data)
            print(f"Data point collected: {len(data_points)}")
            await asyncio.sleep(interval)
        
        # Write to CSV
        if data_points:
            fieldnames = data_points[0].keys()
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data_points)
            
            print(f"Data saved to {filename} ({len(data_points)} data points)")
    
    async def monitor_real_time(self, duration: int = 60):
        """Monitor data in real-time."""
        print(f"Monitoring real-time data for {duration} seconds...")
        
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            data = await self.read_all_data()
            
            # Print key metrics
            print(f"\n--- {data.get('timestamp', 'Unknown time')} ---")
            
            # Spindle data
            if 'Spindle.Speed' in data:
                print(f"Spindle Speed: {data['Spindle.Speed']:.1f} RPM")
            if 'Spindle.Load' in data:
                print(f"Spindle Load: {data['Spindle.Load']:.1f} %")
            if 'Spindle.Temperature' in data:
                print(f"Spindle Temp: {data['Spindle.Temperature']:.1f} °C")
            
            # Machine state
            if 'State.CurrentState' in data:
                print(f"Machine State: {data['State.CurrentState']}")
            
            # Production
            if 'Production.PartsProduced' in data:
                print(f"Parts Produced: {data['Production.PartsProduced']}")
            if 'Production.Efficiency' in data:
                print(f"Efficiency: {data['Production.Efficiency']:.1f} %")
            
            await asyncio.sleep(2)


async def main():
    """Main example function."""
    logging.basicConfig(level=logging.INFO)
    
    client = CNClientExample()
    
    try:
        await client.connect()
        
        print("\n1. Monitor real-time data")
        print("2. Log data to CSV")
        print("3. Read data once")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            await client.monitor_real_time(60)  # Monitor for 1 minute
        elif choice == "2":
            filename = input("CSV filename (default: cnc_data.csv): ").strip() or "cnc_data.csv"
            duration = int(input("Duration in seconds (default: 300): ").strip() or "300")
            interval = int(input("Interval in seconds (default: 5): ").strip() or "5")
            await client.log_data_to_csv(filename, duration, interval)
        elif choice == "3":
            data = await client.read_all_data()
            print("\nCurrent machine data:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print("Invalid choice")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
