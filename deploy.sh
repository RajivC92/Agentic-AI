#!/bin/bash

# NewsGenie Production Deployment Script
# Usage: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
echo "🚀 Deploying NewsGenie to $ENVIRONMENT environment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Copying from .env.example..."
        cp .env.example .env
        log_warning "Please update .env with your actual API keys before continuing"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Build and deploy
deploy() {
    log_info "Building NewsGenie application..."
    
    # Build the application
    docker-compose down --remove-orphans
    docker-compose build --no-cache
    
    log_success "Build completed"
    
    log_info "Starting services..."
    
    # Start services
    docker-compose up -d
    
    log_success "Services started"
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Health check
    if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        log_success "NewsGenie is running and healthy!"
        log_success "🌐 Access your application at: http://localhost"
        log_success "📊 Prometheus monitoring: http://localhost:9090"
    else
        log_error "Health check failed"
        log_info "Checking container logs..."
        docker-compose logs newsgenie-app
        exit 1
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    docker-compose down
    docker system prune -f
    log_success "Cleanup completed"
}

# Backup function
backup() {
    log_info "Creating backup..."
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    # Backup database
    docker-compose exec -T postgres pg_dump -U newsgenieuser newsgenie > $BACKUP_DIR/database.sql
    
    # Backup data directory
    cp -r data $BACKUP_DIR/
    
    log_success "Backup created at $BACKUP_DIR"
}

# Main execution
case "$ENVIRONMENT" in
    "production")
        check_prerequisites
        deploy
        ;;
    "cleanup")
        cleanup
        ;;
    "backup")
        backup
        ;;
    *)
        echo "Usage: $0 [production|cleanup|backup]"
        echo ""
        echo "Commands:"
        echo "  production  - Deploy to production environment"
        echo "  cleanup     - Clean up containers and images"
        echo "  backup      - Create backup of data and database"
        exit 1
        ;;
esac

log_success "Deployment script completed!"