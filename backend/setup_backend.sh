#!/bin/bash

# Integraite Backend Setup Script
# This script pulls code from GitHub and sets up the Python environment

set -e  # Exit on any error

# Configuration
REPO_URL="https://github.com/integraitepro/integraite.git"  # Update with your actual repo URL
PROJECT_DIR="/root/integraite"
BACKEND_DIR="$PROJECT_DIR/backend"
PYTHON_VERSION="3.11"

echo "🚀 Starting Integraite Backend Setup..."

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script with sudo"
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install required system dependencies
echo "🔧 Installing system dependencies..."
apt install -y \
    git \
    curl \
    build-essential \
    software-properties-common \
    ca-certificates \
    gnupg \
    lsb-release

# Install Python 3.11 if not available
echo "🐍 Setting up Python $PYTHON_VERSION..."
if ! command -v python3.11 &> /dev/null; then
    add-apt-repository ppa:deadsnakes/ppa -y
    apt update
    apt install -y python3.11 python3.11-venv python3.11-dev
fi

# Install UV package manager
echo "⚡ Installing UV package manager..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    # Make UV available for all users
    ln -sf $HOME/.cargo/bin/uv /usr/local/bin/uv
fi

# Create project directory
echo "📁 Creating project directory..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Clone or update repository
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "🔄 Updating existing repository..."
    git pull origin main
else
    echo "📥 Cloning repository..."
    # Remove directory if it exists but is not a git repo
    rm -rf $PROJECT_DIR
    git clone $REPO_URL $PROJECT_DIR
fi

# Navigate to backend directory
cd $BACKEND_DIR

# Create virtual environment using Python 3.11
echo "🌐 Creating virtual environment..."
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install UV in the virtual environment
echo "⚡ Installing UV in virtual environment..."
pip install uv

# Install dependencies using UV
echo "📚 Installing Python dependencies with UV..."
if [ -f "pyproject.toml" ]; then
    uv pip install -e .
elif [ -f "requirements.txt" ]; then
    uv pip install -r requirements.txt
else
    echo "⚠️  No pyproject.toml or requirements.txt found. Installing common dependencies..."
    uv pip install \
        fastapi \
        uvicorn[standard] \
        sqlalchemy[asyncio] \
        aiosqlite \
        alembic \
        pydantic \
        pydantic-settings \
        python-jose[cryptography] \
        passlib[bcrypt] \
        python-multipart \
        email-validator
fi

# Create necessary directories
echo "📂 Creating necessary directories..."
mkdir -p data logs

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating environment file..."
    if [ -f "env.example" ]; then
        cp env.example .env
    else
        cat > .env << EOL
# Environment Configuration
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite+aiosqlite:///./data/integraite.db
CORS_ORIGINS=["https://integraite.pro", "https://api.integraite.pro"]
EOL
    fi
    echo "⚠️  Please review and update .env file with your configuration"
fi

# Set proper permissions
echo "🔐 Setting permissions..."
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod 600 $BACKEND_DIR/.env

# Create systemd service file
echo "⚙️  Creating systemd service..."
cat > /etc/systemd/system/integraite-backend.service << EOL
[Unit]
Description=Integraite Backend API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
ExecStart=$BACKEND_DIR/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd
systemctl daemon-reload

# Initialize database (if init script exists)
echo "🗄️  Initializing database..."
if [ -f "app/core/init_db.py" ]; then
    su -s /bin/bash www-data -c "cd $BACKEND_DIR && source venv/bin/activate && python -c 'import asyncio; from app.core.init_db import init_database; asyncio.run(init_database())'"
fi

echo ""
echo "✅ Backend setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "  1. Review configuration:    sudo nano $BACKEND_DIR/.env"
echo "  2. Start the service:       sudo systemctl start integraite-backend"
echo "  3. Enable auto-start:       sudo systemctl enable integraite-backend"
echo "  4. Check status:            sudo systemctl status integraite-backend"
echo "  5. View logs:               sudo journalctl -u integraite-backend -f"
echo ""
echo "🌐 The backend will be available at: http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo ""
EOL
