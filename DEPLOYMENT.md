# Geo Risk Application - Deployment Guide

Complete Docker deployment guide for the Geo Risk Simulation Application with FastAPI backend, React frontend, PostgreSQL database, and Nginx reverse proxy.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Nginx Reverse Proxy                     │
│                    (Port 80 - External)                     │
└──────────┬────────────────────────────────┬─────────────────┘
           │                                │
           ▼                                ▼
  ┌────────────────┐              ┌──────────────────┐
  │   Frontend     │              │    Backend       │
  │  (React/Nginx) │              │  (FastAPI)       │
  │   Port 3000    │              │   Port 8000      │
  └────────────────┘              └─────────┬────────┘
                                            │
                                            ▼
                                   ┌────────────────┐
                                   │   PostgreSQL   │
                                   │   Port 5432    │
                                   └────────────────┘
```

## 📋 Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Ports Available**: 80, 3000, 5432, 8000

Verify installation:
```bash
docker --version
docker-compose --version
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd geo_risk_app
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your settings:

```bash
# Database (CHANGE IN PRODUCTION!)
POSTGRES_USER=georisk
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=georisk_db

# Backend
SECRET_KEY=your-super-secret-key-minimum-32-characters
DEBUG=false

# Frontend
REACT_APP_API_URL=/api
```

### 3. Build and Start Services

```bash
# Build all containers
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Verify Deployment

```bash
# Check all services are running
docker-compose ps

# Test health endpoints
curl http://localhost/health
curl http://localhost:8000/health
curl http://localhost:3000/health
```

## 🔍 Service Details

### Database (PostgreSQL)

- **Container**: `georisk_db`
- **Image**: `postgres:15-alpine`
- **Port**: 5432 (internal), configurable externally
- **Volume**: `postgres_data` (persistent storage)
- **Health Check**: `pg_isready` every 10s

**Initialization**:
- Runs `init-scripts/01-init.sql` on first start
- Creates database and extensions
- Sets up user privileges

### Backend (FastAPI)

- **Container**: `georisk_backend`
- **Build**: `./backend/Dockerfile`
- **Port**: 8000 (internal), configurable externally
- **Health Check**: `curl http://localhost:8000/health` every 30s

**Features**:
- Multi-stage Docker build for smaller image
- Automatic database initialization with sample data
- Hot reload in development mode
- Comprehensive API documentation at `/docs`

**API Endpoints**:
- `POST /api/assess-risk` - Risk assessment
- `GET/POST/PUT/DELETE /api/locations` - Location management
- `GET /api/hazards` - Hazard types
- `GET/POST /api/historical` - Historical data
- `GET /health` - Health check
- `GET /docs` - Interactive API docs

### Frontend (React)

- **Container**: `georisk_frontend`
- **Build**: `./frontend/Dockerfile`
- **Port**: 80 (internal), 3000 (external)
- **Health Check**: `wget http://localhost:80/health` every 30s

**Features**:
- Multi-stage build (Node build + Nginx serve)
- SPA routing with fallback to index.html
- Static asset caching (1 year)
- Gzip compression

### Nginx Reverse Proxy

- **Container**: `georisk_nginx`
- **Image**: `nginx:alpine`
- **Port**: 80 (external)
- **Config**: `nginx/conf.d/default.conf`

**Routing**:
- `/` → Frontend (React SPA)
- `/api/*` → Backend API
- `/docs` → API documentation
- `/health` → Nginx health check

**Features**:
- CORS header management
- Request timeouts (60s)
- Client body size limit (10MB)
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)

## 🔧 Development Workflow

### Start in Development Mode

```bash
# Start with hot reload
docker-compose up

# Backend changes auto-reload via uvicorn --reload
# Frontend requires rebuild for changes
```

### Rebuild After Code Changes

```bash
# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Access Database

```bash
# Connect to PostgreSQL container
docker-compose exec db psql -U georisk -d georisk_db

# Run queries
\dt  # List tables
SELECT * FROM locations;
SELECT * FROM hazards;
```

### Run Tests

```bash
# Backend tests inside container
docker-compose exec backend pytest -v

# Or create a test-specific compose file
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🧪 Testing Deployment

### Health Checks

```bash
# Main nginx proxy
curl http://localhost/health
# Expected: "healthy"

# Backend API
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Frontend
curl http://localhost:3000/health
# Expected: "healthy"
```

### API Testing

```bash
# List locations
curl http://localhost/api/locations

# Assess risk
curl -X POST http://localhost/api/assess-risk \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": 1,
    "hazard_types": ["earthquake", "flood"]
  }'

# API documentation
open http://localhost/docs  # or http://localhost:8000/docs
```

### Frontend Testing

```bash
# Access the application
open http://localhost

# Check if static assets load
curl -I http://localhost/static/js/main.js
# Should return 200 OK with cache headers
```

### Database Testing

```bash
# Check database connection
docker-compose exec backend python -c "
from app.db.session import engine_sync
from sqlalchemy import text
with engine_sync.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM locations'))
    print(f'Locations count: {result.scalar()}')
"
```

## 🔒 Production Deployment

### Security Checklist

- [ ] Change `POSTGRES_PASSWORD` to strong password
- [ ] Set `SECRET_KEY` to random 32+ character string
- [ ] Set `DEBUG=false`
- [ ] Review CORS origins in `BACKEND_CORS_ORIGINS`
- [ ] Enable HTTPS (add SSL certificates to nginx)
- [ ] Set up firewall rules (only allow ports 80, 443)
- [ ] Configure database backups
- [ ] Set resource limits in docker-compose.yml
- [ ] Review nginx security headers

### Generate Secure Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate POSTGRES_PASSWORD
openssl rand -base64 32
```

### Environment Variables

Create production `.env`:

```bash
# Database
POSTGRES_USER=georisk_prod
POSTGRES_PASSWORD=<generated-secure-password>
POSTGRES_DB=georisk_production
POSTGRES_PORT=5432

# Backend
BACKEND_PORT=8000
SECRET_KEY=<generated-secret-key>
DEBUG=false
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]

# Frontend
FRONTEND_PORT=3000
REACT_APP_API_URL=/api

# Nginx
NGINX_PORT=80
```

### Production Docker Compose

Add resource limits and restart policies:

```yaml
services:
  backend:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### SSL/HTTPS Setup

1. Obtain SSL certificates (Let's Encrypt):
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com
```

2. Update nginx configuration:
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    
    # ... rest of config
}
```

3. Mount certificates in docker-compose.yml:
```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

### Database Backups

```bash
# Manual backup
docker-compose exec db pg_dump -U georisk georisk_db > backup.sql

# Automated backup script
#!/bin/bash
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U georisk georisk_db | gzip > $BACKUP_DIR/georisk_$DATE.sql.gz

# Add to crontab for daily backups
0 2 * * * /path/to/backup-script.sh
```

### Monitoring

Add monitoring containers to docker-compose.yml:

```yaml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    depends_on:
      - prometheus
```

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check logs for errors
docker-compose logs

# Verify environment variables
docker-compose config

# Check port conflicts
sudo lsof -i :80
sudo lsof -i :8000
sudo lsof -i :5432
```

### Database Connection Errors

```bash
# Verify database is healthy
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection manually
docker-compose exec backend python -c "
from app.db.session import engine_sync
print(engine_sync.url)
"
```

### Frontend Not Loading

```bash
# Check nginx logs
docker-compose logs nginx

# Verify build completed
docker-compose exec frontend ls -la /usr/share/nginx/html

# Check nginx config syntax
docker-compose exec nginx nginx -t
```

### API Endpoints Return 502

```bash
# Verify backend is running
curl http://localhost:8000/health

# Check backend logs for errors
docker-compose logs backend

# Verify nginx upstream configuration
docker-compose exec nginx cat /etc/nginx/conf.d/default.conf
```

### Permission Errors

```bash
# Fix ownership of volumes
sudo chown -R $USER:$USER .

# Rebuild with --no-cache
docker-compose build --no-cache
```

## 📊 Performance Tuning

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_locations_lat_lon ON locations(latitude, longitude);
CREATE INDEX idx_historical_location ON historical_data(location_id);
CREATE INDEX idx_historical_hazard ON historical_data(hazard_id);
```

### Nginx Caching

Add to nginx config:
```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m;

location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    add_header X-Cache-Status $upstream_cache_status;
}
```

### Backend Workers

Update backend command for production:
```yaml
command: >
  sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"
```

## 🔄 Updates and Maintenance

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Run database migrations if needed
docker-compose exec backend alembic upgrade head
```

### Clean Up

```bash
# Remove stopped containers
docker-compose down

# Remove volumes (WARNING: deletes data!)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Full cleanup
docker system prune -a --volumes
```

## 📚 Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Docker Docs**: https://docs.docker.com/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Nginx Docs**: https://nginx.org/en/docs/

## 🆘 Support

For issues and questions:
1. Check logs: `docker-compose logs`
2. Verify health checks: `curl http://localhost/health`
3. Review environment variables: `docker-compose config`
4. Check application logs in containers

---

**Last Updated**: November 2024
**Version**: 1.0.0
