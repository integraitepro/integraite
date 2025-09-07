# Integraite Backend Setup Guide

This guide explains how to set up and run the Integraite backend on Ubuntu using the provided scripts.

## Prerequisites

- Ubuntu 20.04+ server
- Root/sudo access
- Git repository URL for your project

## Quick Setup

### Step 1: Download and Setup

```bash
# Download the setup script (replace with your actual repo URL)
wget https://raw.githubusercontent.com/your-username/integraite/main/backend/setup_backend.sh

# Make it executable
chmod +x setup_backend.sh

# Edit the script to update your GitHub repository URL
nano setup_backend.sh
# Update line: REPO_URL="https://github.com/your-username/integraite.git"

# Run the setup
sudo ./setup_backend.sh
```

### Step 2: Configure Environment

```bash
# Edit the environment file
sudo nano /opt/integraite/backend/.env

# Update the following values:
# - SECRET_KEY (generated automatically)
# - JWT_SECRET_KEY (generated automatically) 
# - CORS_ORIGINS (add your frontend domains)
# - Database settings if needed
```

### Step 3: Start the Backend

```bash
# Download the run script
cd /opt/integraite/backend
wget https://raw.githubusercontent.com/your-username/integraite/main/backend/run_backend.sh
chmod +x run_backend.sh

# Start the backend
sudo ./run_backend.sh start

# Check status
./run_backend.sh status
```

## Script Details

### setup_backend.sh

This script:
- ✅ Installs Python 3.11 and system dependencies
- ✅ Installs UV package manager for fast Python package management
- ✅ Clones your GitHub repository
- ✅ Creates Python virtual environment
- ✅ Installs all Python dependencies using UV
- ✅ Creates necessary directories (data, logs)
- ✅ Sets up environment configuration
- ✅ Creates systemd service for automatic startup
- ✅ Initializes the database
- ✅ Sets proper permissions

**Configuration Required:**
- Update `REPO_URL` with your actual GitHub repository URL

### run_backend.sh

This script provides easy management of the backend service:

```bash
# Start the backend
sudo ./run_backend.sh start

# Stop the backend  
sudo ./run_backend.sh stop

# Restart the backend
sudo ./run_backend.sh restart

# Check status and test connectivity
./run_backend.sh status

# View live logs
./run_backend.sh logs

# Update code from GitHub and restart
sudo ./run_backend.sh update
```

## File Locations

- **Project Directory**: `/opt/integraite/`
- **Backend Code**: `/opt/integraite/backend/`
- **Virtual Environment**: `/opt/integraite/backend/venv/`
- **Environment File**: `/opt/integraite/backend/.env`
- **Database**: `/opt/integraite/backend/data/integraite.db`
- **Logs**: `/var/log/integraite-backend.log`
- **PID File**: `/var/run/integraite-backend.pid`
- **Systemd Service**: `/etc/systemd/system/integraite-backend.service`

## Service Management

The backend runs as a systemd service for better reliability:

```bash
# Service commands
sudo systemctl start integraite-backend
sudo systemctl stop integraite-backend
sudo systemctl restart integraite-backend
sudo systemctl status integraite-backend

# Enable auto-start on boot
sudo systemctl enable integraite-backend

# View service logs
sudo journalctl -u integraite-backend -f
```

## Troubleshooting

### Check if backend is running
```bash
./run_backend.sh status
curl http://localhost:8000/health
```

### View logs
```bash
# Service logs
sudo journalctl -u integraite-backend -f

# Or direct log file
tail -f /var/log/integraite-backend.log
```

### Common issues

1. **Permission errors**: Make sure files are owned by `www-data`
   ```bash
   sudo chown -R www-data:www-data /opt/integraite
   ```

2. **Port conflicts**: Check if port 8000 is in use
   ```bash
   sudo netstat -tulpn | grep :8000
   ```

3. **Database issues**: Reinitialize database
   ```bash
   cd /opt/integraite/backend
   sudo -u www-data bash -c "source venv/bin/activate && python -c 'import asyncio; from app.core.init_db import init_database; asyncio.run(init_database())'"
   ```

4. **Dependency issues**: Reinstall packages
   ```bash
   cd /opt/integraite/backend
   sudo -u www-data bash -c "source venv/bin/activate && uv pip install -e ."
   ```

## Updating the Backend

To update your backend with new code from GitHub:

```bash
# Using the run script (recommended)
sudo ./run_backend.sh update

# Or manually
cd /opt/integraite
sudo git pull origin main
cd backend
sudo -u www-data bash -c "source venv/bin/activate && uv pip install -e ."
sudo ./run_backend.sh restart
```

## Security Considerations

- The service runs as `www-data` user (non-root)
- Environment file has restricted permissions (600)
- Database files are in a protected directory
- Logs are accessible only to authorized users

## Integration with Nginx

If you're using Nginx as reverse proxy:

1. The backend runs on `localhost:8000`
2. Nginx should proxy requests to this address
3. Set proper headers for HTTPS termination
4. Configure rate limiting in Nginx

Example Nginx location block:
```nginx
location / {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```
