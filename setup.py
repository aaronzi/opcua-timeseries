#!/usr/bin/env python3
"""
Setup script for the OPC UA CNC Server.
"""

import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")


def install_requirements():
    """Install Python requirements."""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies")
        sys.exit(1)


def create_directories():
    """Create necessary directories."""
    directories = ["logs", "data"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")


def check_config():
    """Check if configuration file exists."""
    config_file = Path("config/server_config.yaml")
    if config_file.exists():
        print("✓ Configuration file found")
    else:
        print("Warning: Configuration file not found, using defaults")


def run_basic_tests():
    """Run basic tests to verify setup."""
    print("Running basic tests...")
    try:
        subprocess.check_call([sys.executable, "-m", "tests.test_basic"])
        print("✓ Basic tests passed")
    except subprocess.CalledProcessError:
        print("Warning: Some tests failed, but setup should still work")


def main():
    """Main setup function."""
    print("OPC UA CNC Server Setup")
    print("=" * 30)
    
    check_python_version()
    install_requirements()
    create_directories()
    check_config()
    run_basic_tests()
    
    print("\n" + "=" * 30)
    print("Setup complete!")
    print("\nTo start the server:")
    print("  python -m server.main")
    print("\nTo test the server:")
    print("  python -m server.client_test")
    print("\nTo use Docker:")
    print("  docker build -t opcua-cnc-server .")
    print("  docker run -p 4840:4840 opcua-cnc-server")


if __name__ == "__main__":
    main()
