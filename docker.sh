#!/bin/bash

# LinkBay CMS Docker Management Script
# Usage: ./docker.sh [command]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project info
PROJECT_NAME="LinkBay CMS"
DEV_COMPOSE="docker-compose.dev.yml"
PROD_COMPOSE="docker-compose.prod.yml"

# Helper functions
print_header() {
    echo -e "${BLUE}🐳 $PROJECT_NAME Docker Manager${NC}"
    echo -e "${BLUE}=================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Development environment commands
dev_up() {
    print_info "Starting development environment..."
    check_docker
    docker-compose -f $DEV_COMPOSE up -d
    print_success "Development environment started!"
    print_info "Services available at:"
    echo "  🏠 Landing:  http://localhost:3001"
    echo "  🏢 Agency:   http://localhost:3002"
    echo "  👤 Customer: http://localhost:3003"
    echo "  🌐 Websites: http://localhost:3004"
    echo "  🔧 Backend:  http://localhost:3000"
    echo "  🗄️  Database: localhost:5432"
    echo "  📦 Redis:    localhost:6379"
}

dev_down() {
    print_info "Stopping development environment..."
    docker-compose -f $DEV_COMPOSE down
    print_success "Development environment stopped!"
}

dev_restart() {
    print_info "Restarting development environment..."
    docker-compose -f $DEV_COMPOSE restart
    print_success "Development environment restarted!"
}

dev_logs() {
    print_info "Showing development logs..."
    docker-compose -f $DEV_COMPOSE logs -f
}

dev_build() {
    print_info "Building development images..."
    docker-compose -f $DEV_COMPOSE build --no-cache
    print_success "Development images built!"
}

# Production environment commands
prod_up() {
    print_info "Starting production environment..."
    check_docker
    docker-compose -f $PROD_COMPOSE up -d
    print_success "Production environment started!"
    print_info "Services available at:"
    echo "  🏠 Landing:  https://linkbay-cms.com"
    echo "  🏢 Agency:   https://app.linkbay-cms.com"
    echo "  👤 Customer: https://manage.linkbay-cms.com"
    echo "  🌐 Websites: https://sites.linkbay-cms.com"
}

prod_down() {
    print_info "Stopping production environment..."
    docker-compose -f $PROD_COMPOSE down
    print_success "Production environment stopped!"
}

prod_restart() {
    print_info "Restarting production environment..."
    docker-compose -f $PROD_COMPOSE restart
    print_success "Production environment restarted!"
}

prod_logs() {
    print_info "Showing production logs..."
    docker-compose -f $PROD_COMPOSE logs -f
}

prod_build() {
    print_info "Building production images..."
    docker-compose -f $PROD_COMPOSE build --no-cache
    print_success "Production images built!"
}

# Utility commands
status() {
    print_info "Docker containers status:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

cleanup() {
    print_warning "Cleaning up Docker system..."
    docker system prune -f
    docker volume prune -f
    print_success "Cleanup completed!"
}

setup() {
    print_info "Setting up LinkBay CMS Docker environment..."
    
    # Create required directories
    mkdir -p nginx/sites-enabled nginx/ssl nginx/logs
    mkdir -p backend/uploads backend/logs
    mkdir -p database
    
    # Copy Dockerfile templates if they don't exist
    for folder in landing agency customer websites; do
        if [ ! -f "$folder/Dockerfile.dev" ]; then
            cp frontend_dockerfile_dev.dockerfile "$folder/Dockerfile.dev"
        fi
        if [ ! -f "$folder/Dockerfile.prod" ]; then
            cp frontend_dockerfile_prod.dockerfile "$folder/Dockerfile.prod"
        fi
        if [ ! -f "$folder/nginx.conf" ]; then
            cp nginx.conf "$folder/nginx.conf"
        fi
    done
    
    print_success "Setup completed!"
}

health() {
    print_info "Checking health of all services..."
    
    # Check development services
    if docker-compose -f $DEV_COMPOSE ps | grep -q "Up"; then
        print_info "Development services:"
        docker-compose -f $DEV_COMPOSE ps --services | while read service; do
            if docker-compose -f $DEV_COMPOSE ps $service | grep -q "Up (healthy)"; then
                print_success "$service: Healthy"
            elif docker-compose -f $DEV_COMPOSE ps $service | grep -q "Up"; then
                print_warning "$service: Running (health unknown)"
            else
                print_error "$service: Not running"
            fi
        done
    fi
    
    # Check production services
    if docker-compose -f $PROD_COMPOSE ps | grep -q "Up"; then
        print_info "Production services:"
        docker-compose -f $PROD_COMPOSE ps --services | while read service; do
            if docker-compose -f $PROD_COMPOSE ps $service | grep -q "Up (healthy)"; then
                print_success "$service: Healthy"
            elif docker-compose -f $PROD_COMPOSE ps $service | grep -q "Up"; then
                print_warning "$service: Running (health unknown)"
            else
                print_error "$service: Not running"
            fi
        done
    fi
}

# Database utility commands
db_migrate() {
    print_info "Running database migrations..."
    docker-compose -f $DEV_COMPOSE exec backend npm run migrate
    print_success "Migrations completed!"
}

db_seed() {
    print_info "Seeding database..."
    docker-compose -f $DEV_COMPOSE exec backend npm run seed
    print_success "Database seeded!"
}

db_reset() {
    print_warning "Resetting database (THIS WILL DELETE ALL DATA)..."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f $DEV_COMPOSE exec postgres psql -U root -d linkbaycms -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        db_migrate
        db_seed
        print_success "Database reset completed!"
    else
        print_info "Operation cancelled."
    fi
}

# Show help
show_help() {
    print_header
    echo
    echo "Usage: ./docker.sh [command]"
    echo
    echo "🚀 Development Commands:"
    echo "  dev:up      - Start development environment"
    echo "  dev:down    - Stop development environment"
    echo "  dev:restart - Restart development environment"
    echo "  dev:logs    - Show development logs"
    echo "  dev:build   - Build development images"
    echo
    echo "🏭 Production Commands:"
    echo "  prod:up     - Start production environment"
    echo "  prod:down   - Stop production environment"
    echo "  prod:restart- Restart production environment"
    echo "  prod:logs   - Show production logs"
    echo "  prod:build  - Build production images"
    echo
    echo "🛠️  Utility Commands:"
    echo "  setup       - Initial setup (create directories, copy files)"
    echo "  status      - Show containers status"
    echo "  health      - Check services health"
    echo "  cleanup     - Clean Docker system"
    echo
    echo "🗄️  Database Commands:"
    echo "  db:migrate  - Run database migrations"
    echo "  db:seed     - Seed database with sample data"
    echo "  db:reset    - Reset database (DESTRUCTIVE)"
    echo
    echo "📋 Examples:"
    echo "  ./docker.sh dev:up     # Start development"
    echo "  ./docker.sh prod:build # Build for production"
    echo "  ./docker.sh status     # Check status"
    echo
}

# Main command router
case "$1" in
    # Development
    "dev:up"|"dev:start")
        dev_up
        ;;
    "dev:down"|"dev:stop")
        dev_down
        ;;
    "dev:restart")
        dev_restart
        ;;
    "dev:logs")
        dev_logs
        ;;
    "dev:build")
        dev_build
        ;;
    
    # Production
    "prod:up"|"prod:start")
        prod_up
        ;;
    "prod:down"|"prod:stop")
        prod_down
        ;;
    "prod:restart")
        prod_restart
        ;;
    "prod:logs")
        prod_logs
        ;;
    "prod:build")
        prod_build
        ;;
    
    # Utilities
    "setup")
        setup
        ;;
    "status")
        status
        ;;
    "health")
        health
        ;;
    "cleanup")
        cleanup
        ;;
    
    # Database
    "db:migrate")
        db_migrate
        ;;
    "db:seed")
        db_seed
        ;;
    "db:reset")
        db_reset
        ;;
    
    # Help
    "help"|"-h"|"--help"|"")
        show_help
        ;;
    
    *)
        print_error "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac