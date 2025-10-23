#!/bin/bash

# 🚀 Dermalens Quick Start Script
# This script sets up the entire Dermalens application for development

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_header "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed. Elasticsearch will not be available."
    fi
    
    print_status "Dependencies check completed"
}

# Setup backend
setup_backend() {
    print_header "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    print_status "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Set up environment
    print_status "Setting up environment variables..."
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Please edit backend/.env with your API keys"
    fi
    
    cd ..
    print_status "Backend setup completed"
}

# Setup frontend
setup_frontend() {
    print_header "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Set up environment
    print_status "Setting up environment variables..."
    if [ ! -f .env.local ]; then
        cp .env.example .env.local
        print_warning "Please edit frontend/.env.local with your API keys"
    fi
    
    cd ..
    print_status "Frontend setup completed"
}

# Start Elasticsearch
start_elasticsearch() {
    print_header "Starting Elasticsearch..."
    
    if command -v docker &> /dev/null; then
        # Check if Elasticsearch is already running
        if docker ps | grep -q elasticsearch; then
            print_status "Elasticsearch is already running"
        else
            print_status "Starting Elasticsearch container..."
            docker run -d \
                --name elasticsearch \
                -p 9200:9200 \
                -p 9300:9300 \
                -e "discovery.type=single-node" \
                -e "xpack.security.enabled=false" \
                -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
                elasticsearch:8.11.0
            
            # Wait for Elasticsearch to start
            print_status "Waiting for Elasticsearch to start..."
            sleep 30
            
            # Test connection
            if curl -s http://localhost:9200/ > /dev/null; then
                print_status "Elasticsearch is running"
            else
                print_error "Failed to start Elasticsearch"
                return 1
            fi
        fi
    else
        print_warning "Docker not available. Please start Elasticsearch manually"
    fi
}

# Seed sample data
seed_data() {
    print_header "Seeding sample data..."
    
    cd backend
    source venv/bin/activate
    
    # Check if Elasticsearch is running
    if curl -s http://localhost:9200/ > /dev/null; then
        print_status "Seeding Elasticsearch with sample data..."
        python seed_elasticsearch_data.py
    else
        print_warning "Elasticsearch not running. Skipping data seeding."
    fi
    
    cd ..
}

# Test setup
test_setup() {
    print_header "Testing setup..."
    
    cd backend
    source venv/bin/activate
    
    # Test Gemini integration
    print_status "Testing Gemini integration..."
    python test_gemini_integration.py
    
    cd ..
}

# Start services
start_services() {
    print_header "Starting services..."
    
    # Start backend in background
    print_status "Starting backend server..."
    cd backend
    source venv/bin/activate
    python main.py &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    sleep 10
    
    # Start frontend
    print_status "Starting frontend server..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    print_status "Waiting for frontend to start..."
    sleep 10
    
    # Test services
    print_status "Testing services..."
    
    # Test backend
    if curl -s http://localhost:8000/health > /dev/null; then
        print_status "✅ Backend is running at http://localhost:8000"
    else
        print_error "❌ Backend failed to start"
    fi
    
    # Test frontend
    if curl -s http://localhost:3000 > /dev/null; then
        print_status "✅ Frontend is running at http://localhost:3000"
    else
        print_error "❌ Frontend failed to start"
    fi
    
    # Test Elasticsearch
    if curl -s http://localhost:9200/ > /dev/null; then
        print_status "✅ Elasticsearch is running at http://localhost:9200"
    else
        print_warning "⚠️ Elasticsearch is not running"
    fi
    
    print_status "Services started successfully!"
    print_status "Press Ctrl+C to stop all services"
    
    # Wait for user to stop
    wait
}

# Cleanup function
cleanup() {
    print_status "Stopping services..."
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Stop Elasticsearch container
    if docker ps | grep -q elasticsearch; then
        docker stop elasticsearch
        docker rm elasticsearch
    fi
    
    print_status "Cleanup completed"
}

# Main function
main() {
    echo "🔬 Dermalens Quick Start"
    echo "========================"
    echo ""
    
    # Set up signal handlers
    trap cleanup EXIT INT TERM
    
    # Run setup steps
    check_dependencies
    setup_backend
    setup_frontend
    start_elasticsearch
    seed_data
    test_setup
    start_services
}

# Show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --backend-only Setup only the backend"
    echo "  --frontend-only Setup only the frontend"
    echo "  --no-elasticsearch Skip Elasticsearch setup"
    echo "  --no-data      Skip data seeding"
    echo "  --no-test      Skip testing"
    echo ""
    echo "Examples:"
    echo "  $0                    # Full setup"
    echo "  $0 --backend-only     # Setup only backend"
    echo "  $0 --no-elasticsearch # Setup without Elasticsearch"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --backend-only)
            check_dependencies
            setup_backend
            exit 0
            ;;
        --frontend-only)
            check_dependencies
            setup_frontend
            exit 0
            ;;
        --no-elasticsearch)
            SKIP_ELASTICSEARCH=true
            shift
            ;;
        --no-data)
            SKIP_DATA=true
            shift
            ;;
        --no-test)
            SKIP_TEST=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main
