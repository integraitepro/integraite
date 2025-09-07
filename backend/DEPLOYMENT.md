# Integraite Backend - EC2 Deployment Guide

This guide covers deploying the Integraite backend application to an EC2 instance using Docker.

## Prerequisites

### EC2 Instance Requirements
- **OS**: Ubuntu 20.04 LTS or later (recommended)
- **Instance Type**: t3.medium or larger (minimum 2GB RAM)
- **Storage**: 20GB+ EBS volume
- **Security Group**: 
  - Port 22 (SSH)
  - Port 8000 (API)
  - Port 80/443 (if using reverse proxy)

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl

## Quick Start

### 1. Install Dependencies on EC2

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install other tools
sudo apt install -y git curl

# Log out and back in for Docker group changes to take effect
exit
```

### 2. Clone and Deploy

```bash
# Clone the repository
git clone <your-repo-url>
cd integraite/backend

# Create environment file
cp env.production .env
# Edit .env with your configuration
nano .env

# Deploy using the script
chmod +x deploy.sh
./deploy.sh
```

### 3. Verify Deployment

```bash
# Check container status
docker ps

# Check health endpoint
curl http://localhost:8000/health

# View API documentation
curl http://localhost:8000/docs
```

## Deployment Methods

### Method 1: Using Deployment Script (Recommended)

```bash
./deploy.sh
```

This script:
- Stops and removes existing containers
- Builds a new Docker image
- Creates persistent storage directories
- Starts the container with proper configuration
- Initializes the database
- Performs health checks

### Method 2: Using Docker Compose

```bash
# Create environment file
cp env.production .env
nano .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Method 3: Manual Docker Commands

```bash
# Build image
docker build -t integraite-backend .

# Create directories
mkdir -p data logs

# Run container
docker run -d \
  --name integraite-backend-container \
  --restart unless-stopped \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  integraite-backend
```

## Configuration

### Environment Variables

Key variables in `.env`:

```bash
# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secret-key

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/integraite.db

# Security
CORS_ORIGINS=["https://yourdomain.com"]

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### SSL/HTTPS Setup (Optional)

For production, consider using a reverse proxy like Nginx:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring & Management

### Container Management

```bash
# View logs
docker logs integraite-backend-container

# Follow logs in real-time
docker logs -f integraite-backend-container

# Restart container
docker restart integraite-backend-container

# Stop container
docker stop integraite-backend-container

# Start container
docker start integraite-backend-container

# Execute commands in container
docker exec -it integraite-backend-container bash
```

### Health Monitoring

The application includes a health check endpoint:

```bash
# Check health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "environment": "production",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Database Management

```bash
# Access database in container
docker exec -it integraite-backend-container python -c "
from app.core.database import AsyncSessionLocal
import asyncio

async def main():
    async with AsyncSessionLocal() as db:
        # Your database operations here
        pass

asyncio.run(main())
"
```

## Backup & Recovery

### Database Backup

```bash
# Backup SQLite database
cp data/integraite.db data/integraite_backup_$(date +%Y%m%d_%H%M%S).db

# Or using container
docker exec integraite-backend-container cp /app/data/integraite.db /app/data/backup.db
docker cp integraite-backend-container:/app/data/backup.db ./backup.db
```

### Application Data Backup

```bash
# Backup entire data directory
tar -czf integraite_backup_$(date +%Y%m%d_%H%M%S).tar.gz data/ logs/
```

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   docker logs integraite-backend-container
   ```

2. **Database connection issues**
   - Check if `data/` directory exists and is writable
   - Verify `DATABASE_URL` in `.env`

3. **Port conflicts**
   ```bash
   sudo netstat -tulpn | grep :8000
   ```

4. **Memory issues**
   ```bash
   docker stats integraite-backend-container
   ```

### Performance Tuning

For production workloads:

1. **Resource Limits**
   ```bash
   docker run ... --memory=2g --cpus=1.0 integraite-backend
   ```

2. **Database Optimization**
   - Consider migrating to PostgreSQL for better performance
   - Regular database maintenance

3. **Logging**
   - Configure log rotation
   - Monitor disk usage

## Security Considerations

1. **Environment Variables**
   - Use strong, unique secrets
   - Don't commit `.env` files to version control

2. **Network Security**
   - Use security groups to restrict access
   - Consider VPC setup for multi-tier architecture

3. **Updates**
   - Regularly update base images
   - Monitor for security vulnerabilities

4. **Backup Security**
   - Encrypt backup files
   - Store backups in secure locations

## Scaling

For high-traffic scenarios:

1. **Load Balancer**: Use AWS Application Load Balancer
2. **Database**: Migrate to RDS PostgreSQL
3. **Caching**: Add Redis for session/data caching
4. **CDN**: Use CloudFront for static assets

---

For issues or questions, refer to the main project documentation or create an issue in the repository.
