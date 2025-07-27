# OPC UA Time Series Server

A comprehensive OPC UA server implementation simulating a CNC machining center that produces realistic manufacturing time series data. Built with Python 3.13 and asyncua, designed for testing, development, and demonstration of industrial IoT applications.

## Features

- **Realistic CNC Simulation**: Simulates a DMG MORI CTX 650 CNC lathe with authentic operating characteristics
- **Comprehensive Data Model**: Includes spindle, feed system, tool management, vibration monitoring, and production metrics
- **Time Series Data**: Generates realistic time-varying data with noise and correlations between parameters
- **OPC UA Compliance**: Full OPC UA server implementation with methods, variables, and folder organization
- **Docker Support**: Ready-to-deploy Docker container with development container support
- **Extensible Architecture**: Modular design allows easy addition of new machine types and parameters

## Machine Simulation

The server simulates a CNC machining center with the following subsystems:

### Spindle System
- Speed (RPM) with realistic acceleration/deceleration
- Load percentage based on cutting conditions
- Torque and power calculations
- Temperature monitoring with thermal modeling

### Feed System
- Variable feed rates (mm/min)
- 3-axis position tracking (X, Y, Z)
- Feed override controls
- Realistic motion profiles

### Tool Management
- Tool wear simulation (X and Z axes)
- Tool life monitoring
- Tool state tracking (New, Good, Worn, Broken)
- Tool change operations

### Vibration Monitoring
- 3-axis vibration sensors (mm/s RMS)
- Overall vibration calculation
- Correlation with spindle speed and tool wear

### Production Metrics
- Parts produced counter
- Cycle time measurement
- Good/rejected parts tracking
- Efficiency calculations

### Auxiliary Systems
- Coolant level and temperature
- Air pressure monitoring
- Hydraulic pressure tracking

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd opcua-timeseries
   ```

2. **Build and run with Docker:**
   ```bash
   docker build -t opcua-cnc-server .
   docker run -p 4840:4840 opcua-cnc-server
   ```

3. **Or use Docker Compose:**
   ```bash
   docker-compose up
   ```

### Using Dev Container

1. **Open in VS Code with Dev Containers extension**
2. **Reopen in Container** when prompted
3. **Run the server:**
   ```bash
   python -m server.main
   ```

### Local Development

1. **Install Python 3.13**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the server:**
   ```bash
   python -m server.main
   ```

## Usage

### Server Connection

The OPC UA server runs on `opc.tcp://localhost:4840/freeopcua/server/` by default.

### Client Examples

#### Basic Connection Test
```bash
python -m server.client_test
```

#### Data Collection Example
```bash
python examples/client_example.py
```

#### Using OPC UA Client Tools
- **UaExpert**: Professional OPC UA client for browsing and monitoring
- **FreeOpcUa Client**: Python-based client library

### Node Structure

```
CNC Machine/
├── Information/
│   ├── Manufacturer
│   ├── Model
│   └── SerialNumber
├── State/
│   └── CurrentState
├── Spindle/
│   ├── Speed
│   ├── Load
│   ├── Torque
│   ├── Power
│   └── Temperature
├── FeedSystem/
│   ├── FeedRate
│   ├── Override
│   └── Position/
│       ├── X
│       ├── Y
│       └── Z
├── Tool/
│   ├── Number
│   ├── LifeRemaining
│   ├── WearX
│   ├── WearZ
│   └── State
├── Vibration/
│   ├── X_Axis
│   ├── Y_Axis
│   ├── Z_Axis
│   └── Overall
├── Production/
│   ├── PartsProduced
│   ├── CycleTime
│   ├── GoodParts
│   ├── RejectedParts
│   └── Efficiency
├── AuxiliarySystems/
│   ├── CoolantLevel
│   ├── CoolantTemperature
│   ├── AirPressure
│   └── HydraulicPressure
└── Methods/
    ├── ResetProductionCounters
    ├── EmergencyStop
    └── ChangeTool
```

## Configuration

Server configuration is managed through `config/server_config.yaml`:

```yaml
server:
  name: "CNC Machining Center OPC UA Server"
  endpoint: "opc.tcp://0.0.0.0:4840/freeopcua/server/"
  namespace: "http://manufacturing.example.com/cnc"

machine:
  name: "DMG MORI CTX 650 CNC Lathe"
  model: "CTX650"
  manufacturer: "DMG MORI"
  serial_number: "CTX650-2024-001"

simulation:
  update_interval: 1.0  # seconds
  noise_factor: 0.05    # 5% noise on sensor readings
```

## Development

### Project Structure
```
opcua-timeseries/
├── server/                 # Main server implementation
│   ├── __init__.py
│   ├── main.py            # Entry point
│   ├── config.py          # Configuration management
│   ├── simulation.py      # CNC simulation logic
│   ├── opcua_server.py    # OPC UA server implementation
│   └── client_test.py     # Client testing utilities
├── config/                # Configuration files
│   └── server_config.yaml
├── examples/              # Usage examples
│   └── client_example.py
├── scripts/               # Utility scripts
│   ├── run_server.sh
│   └── run_server.bat
├── .devcontainer/         # VS Code dev container
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container
├── docker-compose.yml    # Docker Compose configuration
└── README.md
```

### Adding New Machine Types

1. **Extend the simulation models** in `server/simulation.py`
2. **Update the OPC UA node structure** in `server/opcua_server.py`
3. **Add new configuration parameters** in `config/server_config.yaml`
4. **Update documentation** and examples

### Testing

Run the test client to verify server functionality:
```bash
python -m server.client_test
```

## Integration Examples

### With InfluxDB
The Docker Compose configuration includes an optional InfluxDB service for time series data storage.

### With Grafana
Create dashboards by connecting Grafana to InfluxDB or directly to the OPC UA server using OPC UA data sources.

### With Industrial Systems
- **SCADA Systems**: Connect using OPC UA client capabilities
- **MES Systems**: Integrate production data through OPC UA
- **Condition Monitoring**: Use vibration and temperature data for predictive maintenance

## License

[Include your license information here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues, questions, or contributions, please use the GitHub issue tracker.
