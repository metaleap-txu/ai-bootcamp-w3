#!/usr/bin/env bash

#############################################
# Docker Image Rebuild Script
# Purpose: Rebuild Docker images for services when dependencies change
# Usage: ./scripts/rebuild.sh [backend|frontend|all]
#############################################

set -euo pipefail

#############################################
# Color Output Functions
#############################################

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}${1}${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo ""
}

#############################################
# Validation Functions
#############################################

check_docker_daemon() {
    print_info "Checking Docker daemon..."
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker daemon is not running"
        print_info "Please start Docker Desktop and try again"
        print_info "macOS: open -a Docker"
        exit 1
    fi
    print_success "Docker daemon is running"
}

check_docker_compose_file() {
    print_info "Checking docker-compose.yml..."
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml not found in current directory"
        print_info "Please run this script from the repository root"
        exit 1
    fi
    print_success "Found docker-compose.yml"
}

#############################################
# Core Functions
#############################################

rebuild_service() {
    local service=$1
    
    print_header "Rebuilding ${service} image"
    
    print_info "Building ${service} with --no-cache to ensure fresh dependencies..."
    
    if docker compose build --no-cache "${service}"; then
        print_success "${service} image rebuilt successfully!"
        return 0
    else
        print_error "Failed to rebuild ${service} image"
        return 1
    fi
}

rebuild_all() {
    print_header "Rebuilding all images"
    
    print_info "Building all services with --no-cache..."
    
    if docker compose build --no-cache; then
        print_success "All images rebuilt successfully!"
        return 0
    else
        print_error "Failed to rebuild images"
        return 1
    fi
}

show_usage() {
    cat << EOF
Usage: $0 [backend|frontend|all]

Rebuild Docker images for services when dependencies change.

Arguments:
    backend     Rebuild only the backend image (when Python dependencies change)
    frontend    Rebuild only the frontend image (when npm dependencies change)
    all         Rebuild all images (default if no argument provided)

Examples:
    $0 backend              # Rebuild backend after updating pyproject.toml
    $0 frontend             # Rebuild frontend after updating package.json
    $0 all                  # Rebuild everything
    $0                      # Same as 'all'

Note: This script uses --no-cache to ensure dependencies are reinstalled fresh.
EOF
}

#############################################
# Main Function
#############################################

main() {
    local service="${1:-all}"
    
    # Show help if requested
    if [[ "${service}" == "-h" ]] || [[ "${service}" == "--help" ]]; then
        show_usage
        exit 0
    fi
    
    # Validate service argument
    if [[ ! "${service}" =~ ^(backend|frontend|all)$ ]]; then
        print_error "Invalid argument: ${service}"
        echo ""
        show_usage
        exit 1
    fi
    
    print_header "Docker Image Rebuild Script"
    
    # Run validation checks
    check_docker_daemon
    check_docker_compose_file
    
    echo ""
    
    # Rebuild based on service argument
    local build_success=true
    
    if [[ "${service}" == "all" ]]; then
        if ! rebuild_all; then
            build_success=false
        fi
    else
        if ! rebuild_service "${service}"; then
            build_success=false
        fi
    fi
    
    echo ""
    
    # Show results and next steps
    if $build_success; then
        print_header "Rebuild Complete!"
        
        print_success "Images have been rebuilt successfully"
        echo ""
        print_info "Next steps:"
        echo "  1. Restart services to use new images:"
        echo "     ${BLUE}docker compose down && docker compose up -d${NC}"
        echo ""
        echo "  2. Or if already running, recreate containers:"
        echo "     ${BLUE}docker compose up -d --force-recreate${NC}"
        echo ""
        print_warning "Note: Restarting will briefly interrupt running services"
        
        exit 0
    else
        print_header "Rebuild Failed"
        
        print_error "Image rebuild failed - see errors above"
        echo ""
        print_info "Common issues:"
        echo "  • Check docker-compose.yml syntax"
        echo "  • Verify Dockerfile syntax in backend/ and frontend/"
        echo "  • Check Docker daemon logs for more details"
        echo ""
        print_info "For help, run: $0 --help"
        
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
