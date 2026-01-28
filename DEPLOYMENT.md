# NewsGenie Production Deployment Guide

## 🏗️ Enterprise Production Setup

This directory contains all the necessary files for enterprise-grade deployment of NewsGenie.

## 📋 Prerequisites

- Docker and Docker Compose
- At least 4GB RAM
- Valid API keys (OpenAI, NewsAPI, Tavily)
- Domain name (for production)
- SSL certificates (for HTTPS)

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your actual API keys
nano .env
```

### 2. Local Development
```bash
# Build and run locally
docker-compose up -d

# Access application
http://localhost:8501
```

### 3. Production Deployment
```bash
# Make deployment script executable
chmod +x deploy.sh

# Deploy to production
./deploy.sh production

# Access application
http://localhost (via Nginx)
```

## 🔧 Configuration Files

### Core Files
- `Dockerfile` - Production-ready container image
- `docker-compose.yml` - Multi-service orchestration
- `nginx.conf` - Reverse proxy and load balancing
- `requirements.txt` - Python dependencies with versions

### Database
- `init-db.sql` - PostgreSQL initialization
- SQLite fallback for development

### Monitoring
- `prometheus.yml` - Metrics collection
- Health checks and observability

### Security
- Non-root user in containers
- Security headers in Nginx
- Rate limiting
- Environment variable separation

## 🚢 Deployment Options

### Option 1: Docker Compose (Recommended for small-medium scale)
```bash
# Production stack with all services
docker-compose up -d

# Services included:
# - NewsGenie app (Streamlit)
# - PostgreSQL database
# - Redis cache
# - Nginx proxy
# - Prometheus monitoring
```

### Option 2: Kubernetes (Enterprise scale)
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s-deployment.yaml

# Features:
# - Auto-scaling (2-10 replicas)
# - Rolling updates
# - Health checks
# - Persistent storage
```

### Option 3: Cloud Deployment
```bash
# AWS ECS/Fargate
aws ecs create-service --cli-input-json file://aws-ecs.json

# Google Cloud Run
gcloud run deploy newsgenie --image gcr.io/project/newsgenie

# Azure Container Instances
az container create --resource-group myRG --name newsgenie
```

## 📊 Monitoring & Observability

### Built-in Monitoring
- **Health Checks**: `GET /_stcore/health`
- **Prometheus Metrics**: `:9090/metrics`
- **Application Logs**: Docker logs

### Custom Metrics
- Response times
- API call counts
- Error rates
- User sessions

### Alerting (Configure with your monitoring system)
- High response times (>5s)
- API failures (>5% error rate)
- High memory usage (>80%)
- Database connection issues

## 🔐 Security Considerations

### Application Security
- Non-root containers
- API key encryption
- Input validation
- Rate limiting (10 req/s per IP)

### Network Security
- HTTPS only in production
- Security headers
- CORS protection
- Firewall rules

### Data Security
- Database encryption at rest
- Secure API key storage
- Session management
- Audit logging

## 🔄 CI/CD Pipeline

### GitHub Actions (`.github/workflows/ci-cd.yml`)
1. **Test**: Python linting, security scans
2. **Build**: Docker image creation
3. **Deploy**: Automatic deployment to staging/production
4. **Verify**: Health checks and monitoring

### Pipeline Stages
```
Push → Test → Security Scan → Build → Deploy → Health Check
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Multiple app instances behind load balancer
- Database read replicas
- Redis cluster for caching
- CDN for static content

### Vertical Scaling
- Increase container resources
- Optimize database queries
- Implement caching strategies
- Use async processing

## 🗄️ Database Options

### Development: SQLite
```
DATABASE_URL=sqlite:///./data/newsgenie_sessions.db
```

### Production: PostgreSQL
```
DATABASE_URL=postgresql://user:pass@postgres:5432/newsgenie
```

### Migration
Use included `init-db.sql` for PostgreSQL setup with proper indexes and constraints.

## 🔧 Troubleshooting

### Common Issues
1. **Port conflicts**: Change ports in docker-compose.yml
2. **API limits**: Check rate limiting and quotas
3. **Memory issues**: Increase container memory limits
4. **SSL problems**: Verify certificate paths

### Health Check Commands
```bash
# Check application health
curl http://localhost:8501/_stcore/health

# Check database connectivity
docker-compose exec postgres pg_isready

# Check Redis
docker-compose exec redis redis-cli ping

# View logs
docker-compose logs -f newsgenie-app
```

### Performance Optimization
1. Enable Redis caching
2. Optimize database queries
3. Use CDN for static files
4. Implement request caching
5. Monitor and tune resource limits

## 📝 Maintenance

### Regular Tasks
- Monitor resource usage
- Update dependencies
- Backup database
- Review security logs
- Update SSL certificates

### Backup Strategy
```bash
# Create backup
./deploy.sh backup

# Restore from backup
./restore.sh backups/20240128_120000/
```

## 🆘 Support

### Documentation
- API documentation: `/docs`
- Health status: `/_stcore/health`
- Metrics: `/metrics`

### Monitoring Dashboards
- Application: http://localhost:8501
- Prometheus: http://localhost:9090
- Database: via admin tools

### Contact
For enterprise support and custom deployment assistance, please contact your system administrator or DevOps team.

---

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database backup strategy implemented
- [ ] Monitoring and alerting configured
- [ ] Security scans completed
- [ ] Performance testing done
- [ ] Documentation updated
- [ ] Team training completed

**Ready for Enterprise Production! 🚀**