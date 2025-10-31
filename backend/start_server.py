#!/usr/bin/env python3
"""
Startup script for Integraite Backend with SRE Agent
Installs dependencies and starts the server
"""

import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and handle errors"""
    logger.info(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return None

def main():
    """Main startup function"""
    logger.info("🚀 Starting Integraite Backend with SRE Agent")
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    logger.info(f"📁 Working directory: {backend_dir}")
    
    # Install/update dependencies
    pip_output = run_command("pip install -e .", "Installing dependencies")
    if pip_output is None:
        logger.error("Failed to install dependencies")
        sys.exit(1)
    
    # Check if database exists
    db_path = os.path.join(backend_dir, "integraite.db")
    if not os.path.exists(db_path):
        logger.info("🗄️ Database not found, creating initial database...")
        init_output = run_command("python -c \"from app.core.init_db import init_db; init_db()\"", "Creating initial database")
        if init_output is None:
            logger.warning("Database initialization may have failed, but continuing...")
    
    # Run migrations
    logger.info("🔄 Running database migrations...")
    migration_output = run_command("alembic upgrade head", "Running migrations")
    if migration_output is None:
        logger.warning("Migrations may have failed, but continuing...")
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        logger.warning("The SRE agent may not function properly without these variables")
        logger.info("Set them in your environment or .env file")
    
    # Start the server
    logger.info("🌐 Starting FastAPI server...")
    logger.info("Access the API at: http://localhost:8000")
    logger.info("API docs available at: http://localhost:8000/docs")
    logger.info("SRE Agent webhook: http://localhost:8000/api/v1/incident/trigger-agent")
    logger.info("")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        # Start uvicorn server
        subprocess.run([
            "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()