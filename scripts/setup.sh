#!/bin/bash
# Setup script for Industrial DevOps Platform
# Automates initial configuration and deployment

set -e

echo "========================================"
echo "Industrial DevOps Platform Setup"
echo "========================================"
echo ""

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker Engine 24.0+"
        exit 1
    fi
    echo "✓ Docker found: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose not found. Please install Docker Compose 2.0+"
        exit 1
    fi
    echo "✓ Docker Compose found"
    
    # Check available memory
    total_mem=$(free -m | awk '/^Mem:/{print $2}')
    if [ "$total_mem" -lt 4096 ]; then
        echo "⚠️  Warning: Less than 4GB RAM detected. Recommended: 8GB+"
    else
        echo "✓ Memory: ${total_mem}MB"
    fi
    
    echo ""
}

# Generate secrets
generate_secrets() {
    echo "Generating security secrets..."
    
    SECRET_KEY=$(openssl rand -base64 32)
    JWT_SECRET=$(openssl rand -base64 32)
    
    echo "✓ Generated SECRET_KEY"
    echo "✓ Generated LFS_JWT_SECRET"
    echo ""
    echo "Please update config/forgejo/app.ini with these values:"
    echo "SECRET_KEY = $SECRET_KEY"
    echo "LFS_JWT_SECRET = $JWT_SECRET"
    echo ""
    read -p "Press Enter after updating app.ini..."
}

# Create data directories
create_directories() {
    echo "Creating data directories..."
    
    mkdir -p data/{forgejo,postgres,minio,elasticsearch,oxidized}
    mkdir -p logs
    
    echo "✓ Directories created"
    echo ""
}

# Initialize MinIO buckets
init_minio() {
    echo "Initializing MinIO..."
    
    # Wait for MinIO to be ready
    echo "Waiting for MinIO to start..."
    sleep 10
    
    # Create LFS bucket
    docker exec forgejo-minio mc alias set local http://localhost:9000 minioadmin minioadmin 2>/dev/null || true
    docker exec forgejo-minio mc mb local/forgejo-lfs 2>/dev/null || echo "Bucket already exists"
    docker exec forgejo-minio mc policy set download local/forgejo-lfs
    
    echo "✓ MinIO configured"
    echo ""
}

# Start services
start_services() {
    echo "Starting services..."
    
    docker-compose up -d
    
    echo "✓ Services started"
    echo ""
    echo "Waiting for services to be ready (30s)..."
    sleep 30
}

# Display access information
show_access_info() {
    echo "========================================"
    echo "Setup Complete!"
    echo "========================================"
    echo ""
    echo "Access URLs:"
    echo "  Forgejo:        http://localhost:3000"
    echo "  MinIO Console:  http://localhost:9001 (minioadmin/minioadmin)"
    echo "  Keycloak:       http://localhost:8080 (admin/admin)"
    echo "  Elasticsearch:  http://localhost:9200"
    echo ""
    echo "Next Steps:"
    echo "1. Visit http://localhost:3000 to complete Forgejo setup"
    echo "2. Create an admin account"
    echo "3. Configure OAuth2 with Keycloak (see docs/GETTING-STARTED.md)"
    echo "4. Test Git LFS with a sample repository"
    echo ""
    echo "Documentation: docs/GETTING-STARTED.md"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    
    read -p "Generate new secrets? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        generate_secrets
    fi
    
    create_directories
    start_services
    
    read -p "Initialize MinIO? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        init_minio
    fi
    
    show_access_info
}

main "$@"
