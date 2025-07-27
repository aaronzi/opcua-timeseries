# OPC UA Time Series with InfluxDB Example

This example demonstrates how to run the OPC UA Time Series server alongside InfluxDB for data storage and Grafana for visualization.

## Quick Start

1. **Build and publish your Docker image** (do this from the project root):
   ```bash
   # Build the image
   docker build -t aaronzi/opcua-timeseries:1.0.0 .
   
   # Tag for latest
   docker tag aaronzi/opcua-timeseries:1.0.0 aaronzi/opcua-timeseries:latest
   
   # Push to Docker Hub
   docker push aaronzi/opcua-timeseries:1.0.0
   docker push aaronzi/opcua-timeseries:latest
   ```

2. **Start the services**:
   ```bash
   cd examples/influxdb
   docker-compose up -d
   ```

3. **Access the services**:
   - **OPC UA Server**: `opc.tcp://localhost:4840`
   - **InfluxDB UI**: http://localhost:8086
   - **Grafana**: http://localhost:3000 (admin/admin)

## Configuration

### InfluxDB Setup
- **Organization**: opcua-org
- **Bucket**: opcua-timeseries
- **Retention**: 1 week
- **Admin Token**: `opcua-admin-token-please-change-this` (⚠️ Change in production!)

### Grafana Setup
- **Default credentials**: admin/admin
- **InfluxDB datasource** will need to be configured manually:
  - URL: `http://influxdb:8086`
  - Organization: `opcua-org`
  - Token: `opcua-admin-token-please-change-this`
  - Default Bucket: `opcua-timeseries`

## Data Flow

1. **OPC UA Server** generates time series data
2. **InfluxDB** stores the time series data
3. **Grafana** visualizes the data from InfluxDB

## Customization

### Environment Variables
You can customize the setup by modifying the environment variables in `docker-compose.yml`:

- `DOCKER_INFLUXDB_INIT_USERNAME`: InfluxDB admin username
- `DOCKER_INFLUXDB_INIT_PASSWORD`: InfluxDB admin password
- `DOCKER_INFLUXDB_INIT_ORG`: InfluxDB organization name
- `DOCKER_INFLUXDB_INIT_BUCKET`: Default bucket name
- `DOCKER_INFLUXDB_INIT_TOKEN`: Admin token for API access

### Volumes
- `./logs`: OPC UA server logs
- `./data`: OPC UA server data files
- `./config`: OPC UA server configuration
- `influxdb-data`: InfluxDB persistent data
- `grafana-data`: Grafana persistent data

## Production Considerations

1. **Change default passwords** and tokens
2. **Use environment files** (.env) for sensitive data
3. **Configure proper backup** for volumes
4. **Set up monitoring** and alerting
5. **Use reverse proxy** (nginx/traefik) for SSL termination
6. **Restrict network access** as needed

## Troubleshooting

### Check service status:
```bash
docker-compose ps
```

### View logs:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs opcua-server
docker-compose logs influxdb
docker-compose logs grafana
```

### Restart services:
```bash
docker-compose restart
```

### Stop and remove everything:
```bash
docker-compose down -v  # -v removes volumes too
```
