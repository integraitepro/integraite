#!/bin/bash

# Integraite Backend Run Script
# This script runs the backend application in background using uvicorn

set -e  # Exit on any error

# Configuration
BACKEND_DIR="/root/integraite/backend"
PID_FILE="/var/run/integraite-backend.pid"
LOG_FILE="/var/log/integraite-backend.log"
HOST="0.0.0.0"
PORT="8000"
WORKERS="2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Please run this script with sudo"
        exit 1
    fi
}

# Check if backend directory exists
check_backend() {
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        print_warning "Please run setup_backend.sh first"
        exit 1
    fi
}

# Check if virtual environment exists
check_venv() {
    if [ ! -f "$BACKEND_DIR/venv/bin/activate" ]; then
        print_error "Virtual environment not found"
        print_warning "Please run setup_backend.sh first"
        exit 1
    fi
}

# Start the backend service
start_service() {
    print_status "Starting Integraite Backend..."
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            print_warning "Backend is already running (PID: $PID)"
            return 0
        else
            print_warning "Removing stale PID file"
            rm -f $PID_FILE
        fi
    fi
    
    # Create log directory
    mkdir -p $(dirname $LOG_FILE)
    
    # Start using systemd service (preferred method)
    if systemctl is-active --quiet integraite-backend; then
        print_success "Backend service is already running"
        return 0
    fi
    
    if [ -f "/etc/systemd/system/integraite-backend.service" ]; then
        print_status "Starting systemd service..."
        systemctl start integraite-backend
        systemctl enable integraite-backend
        
        # Wait a moment for service to start
        sleep 3
        
        if systemctl is-active --quiet integraite-backend; then
            print_success "Backend service started successfully"
            print_status "Service status:"
            systemctl status integraite-backend --no-pager -l
        else
            print_error "Failed to start backend service"
            print_status "Check logs with: sudo journalctl -u integraite-backend -f"
            exit 1
        fi
    else
        # Fallback: Start manually
        print_status "Starting backend manually..."
        start_manual
    fi
}

# Start backend manually (fallback method)
start_manual() {
    cd $BACKEND_DIR
    
    # Activate virtual environment and start uvicorn in background
    su -s /bin/bash www-data -c "
        cd $BACKEND_DIR && 
        source venv/bin/activate && 
        nohup uvicorn app.main:app \
            --host $HOST \
            --port $PORT \
            --workers $WORKERS \
            --access-log \
            --log-level info \
            > $LOG_FILE 2>&1 & 
        echo \$! > $PID_FILE
    "
    
    # Wait a moment for startup
    sleep 3
    
    # Check if process is running
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            print_success "Backend started successfully (PID: $PID)"
        else
            print_error "Failed to start backend"
            exit 1
        fi
    else
        print_error "Failed to create PID file"
        exit 1
    fi
}

# Stop the backend service
stop_service() {
    print_status "Stopping Integraite Backend..."
    
    # Try systemd service first
    if systemctl is-active --quiet integraite-backend; then
        systemctl stop integraite-backend
        print_success "Backend service stopped"
        return 0
    fi
    
    # Fallback: Stop manually
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            sleep 2
            
            # Force kill if still running
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID
                print_warning "Force killed backend process"
            fi
            
            rm -f $PID_FILE
            print_success "Backend stopped"
        else
            print_warning "Backend not running"
            rm -f $PID_FILE
        fi
    else
        print_warning "PID file not found"
    fi
}

# Restart the backend service
restart_service() {
    print_status "Restarting Integraite Backend..."
    stop_service
    sleep 2
    start_service
}

# Check backend status
status_service() {
    print_status "Checking Integraite Backend status..."
    
    # Check systemd service
    if [ -f "/etc/systemd/system/integraite-backend.service" ]; then
        if systemctl is-active --quiet integraite-backend; then
            print_success "Backend service is running"
            systemctl status integraite-backend --no-pager -l
            return 0
        else
            print_warning "Backend service is not running"
        fi
    fi
    
    # Check manual process
    if [ -f "$PID_FILE" ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            print_success "Backend is running (PID: $PID)"
            ps -p $PID -o pid,ppid,cmd --no-headers
        else
            print_error "Backend is not running (stale PID file)"
            rm -f $PID_FILE
        fi
    else
        print_error "Backend is not running"
    fi
    
    # Test HTTP endpoint
    print_status "Testing HTTP endpoint..."
    if curl -s http://localhost:$PORT/health > /dev/null; then
        print_success "Backend is responding on http://localhost:$PORT"
    else
        print_error "Backend is not responding on http://localhost:$PORT"
    fi
}

# Show logs
show_logs() {
    if systemctl is-active --quiet integraite-backend; then
        print_status "Showing systemd service logs..."
        journalctl -u integraite-backend -f
    elif [ -f "$LOG_FILE" ]; then
        print_status "Showing log file..."
        tail -f $LOG_FILE
    else
        print_error "No logs found"
    fi
}

# Update backend code
update_backend() {
    print_status "Updating backend code..."
    
    # Stop service
    stop_service
    
    # Pull latest code
    cd /opt/integraite
    git pull origin main
    
    # Update dependencies
    cd $BACKEND_DIR
    source venv/bin/activate
    uv pip install -e .
    
    # Restart service
    start_service
    
    print_success "Backend updated successfully"
}

# Main script logic
case "$1" in
    start)
        check_root
        check_backend
        check_venv
        start_service
        ;;
    stop)
        check_root
        stop_service
        ;;
    restart)
        check_root
        check_backend
        check_venv
        restart_service
        ;;
    status)
        status_service
        ;;
    logs)
        show_logs
        ;;
    update)
        check_root
        check_backend
        check_venv
        update_backend
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|update}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the backend service"
        echo "  stop     - Stop the backend service"
        echo "  restart  - Restart the backend service"
        echo "  status   - Show service status and test connectivity"
        echo "  logs     - Show live logs"
        echo "  update   - Pull latest code and restart service"
        echo ""
        echo "Examples:"
        echo "  sudo $0 start"
        echo "  sudo $0 status"
        echo "  $0 logs"
        echo ""
        exit 1
        ;;
esac

exit 0
