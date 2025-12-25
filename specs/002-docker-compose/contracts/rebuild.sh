#!/bin/bash
# Rebuild Script Contract
#
# Purpose: Rebuild Docker images for frontend and backend services
# Usage: ./scripts/rebuild.sh [service_name]
#        - No args: Rebuild both frontend and backend
#        - frontend: Rebuild only frontend
#        - backend: Rebuild only backend
# Exit Codes:
#   0: Success
#   1: Build failed
#   2: Invalid argument

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to rebuild a service
rebuild_service() {
    local service=$1
    print_info "Rebuilding ${service} image..."
    
    if docker compose build --no-cache "$service"; then
        print_success "${service} image rebuilt successfully!"
        return 0
    else
        print_error "${service} image build failed!"
        return 1
    fi
}

# Main script logic
main() {
    local service_name="${1:-all}"
    local exit_code=0
    
    print_info "Docker Image Rebuild Script"
    print_info "============================="
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found. Please run this script from the repository root."
        exit 1
    fi
    
    case "$service_name" in
        backend)
            print_info "Rebuilding backend service only..."
            rebuild_service "backend" || exit_code=1
            ;;
        
        frontend)
            print_info "Rebuilding frontend service only..."
            rebuild_service "frontend" || exit_code=1
            ;;
        
        all)
            print_info "Rebuilding all services (frontend and backend)..."
            rebuild_service "frontend" || exit_code=1
            rebuild_service "backend" || exit_code=1
            ;;
        
        *)
            print_error "Invalid service name: $service_name"
            echo ""
            echo "Usage: $0 [service_name]"
            echo "  service_name: 'frontend', 'backend', or omit for all"
            echo ""
            echo "Examples:"
            echo "  $0              # Rebuild both frontend and backend"
            echo "  $0 frontend     # Rebuild only frontend"
            echo "  $0 backend      # Rebuild only backend"
            exit 2
            ;;
    esac
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        print_success "All requested images rebuilt successfully!"
        print_info "Next steps:"
        print_info "  1. Stop running containers: docker compose down"
        print_info "  2. Start with new images: docker compose up"
        print_info "  Or in one command: docker compose up --force-recreate"
    else
        print_error "Some images failed to build. Check the error messages above."
        print_info "Troubleshooting:"
        print_info "  - Check Dockerfile syntax"
        print_info "  - Verify dependency files (package.json, pyproject.toml)"
        print_info "  - Ensure sufficient disk space"
        print_info "  - Check Docker daemon logs"
    fi
    
    exit $exit_code
}

# Run main function
main "$@"

# =============================================================================
# Notes:
# - This script MUST be executable (chmod +x scripts/rebuild.sh)
# - Run from repository root where docker-compose.yml is located
# - --no-cache ensures fresh builds (useful when dependencies change)
# - Errors are reported clearly with color-coded output
# - Exit code indicates success (0) or failure (1)
# =============================================================================
