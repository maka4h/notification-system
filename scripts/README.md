# 📋 Convenience Scripts

This folder contains convenience shell scripts to manage the Docker-based notification system.

## Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `start.sh` | Start all services | `./scripts/start.sh` |
| `stop.sh` | Stop all services | `./scripts/stop.sh` |
| `build.sh` | Build Docker images | `./scripts/build.sh` |
| `restart.sh` | Complete restart (stop, build, start) | `./scripts/restart.sh` |
| `clean-restart.sh` | Clean restart (removes all data) | `./scripts/clean-restart.sh` |
| `status.sh` | Check system status and health | `./scripts/status.sh` |
| `logs.sh` | View service logs | `./scripts/logs.sh [service-name]` |
| `test.sh` | Run tests with optional cleanup | `./scripts/test.sh [--clean] [--frontend] [--backend] [--coverage]` |
| `create-zip.sh` | Create deployment archive | `./scripts/create-zip.sh` |

## Script Details

### 🚀 `start.sh`
- Starts all Docker services in detached mode
- Shows service status after startup
- Creates necessary Docker networks

### 🛑 `stop.sh` 
- Gracefully stops all running services
- Preserves data volumes

### 🔨 `build.sh`
- Builds fresh Docker images for all services
- Useful after code changes
- Uses Docker Compose build command

### 🔄 `restart.sh`
- Performs complete restart: stop → build → start
- Ideal for applying code changes
- Preserves data volumes

### 🧹 `clean-restart.sh`
- **WARNING**: Removes all data volumes
- Performs clean rebuild from scratch
- Use when you need a fresh environment

### 📊 `status.sh`
- Shows status of all Docker containers
- Displays health check information
- Lists running services and ports

### 📋 `logs.sh`
- View logs for all services or a specific service
- Usage: `./scripts/logs.sh` (all services)
- Usage: `./scripts/logs.sh demo-ui` (specific service)
- Available services: `notification-service`, `demo-ui`, `event-generator`, `postgres`, `nats`

### 🧪 `test.sh`
- Runs backend and/or frontend tests
- Optional test artifact cleanup with `--clean` flag
- Supports coverage reports with `--coverage` flag
- Can run specific test suites with `--frontend` or `--backend`
- Automatically detects and sets up test environments
- Cleans up pytest cache, coverage files, test databases, and temp files

### 📦 `create-zip.sh`
- Creates a deployment archive of the project
- Excludes development files and dependencies
- Useful for distribution

## Usage Examples

```bash
# Start the system
./scripts/start.sh

# View all logs
./scripts/logs.sh

# View specific service logs  
./scripts/logs.sh notification-service

# Run all tests
./scripts/test.sh

# Run tests with cleanup
./scripts/test.sh --clean

# Run only backend tests with coverage
./scripts/test.sh --backend --coverage --clean

# Run only frontend tests
./scripts/test.sh --frontend

# Check system status
./scripts/status.sh

# Restart after code changes
./scripts/restart.sh

# Complete clean restart (removes all data)
./scripts/clean-restart.sh
```

## Notes

- All scripts should be run from the project root directory
- Scripts require Docker and Docker Compose to be installed
- Some scripts may require sudo permissions depending on your Docker setup
- The `clean-restart.sh` script will permanently delete all application data
