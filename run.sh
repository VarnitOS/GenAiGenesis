#!/bin/bash

# Check if .env file exists in backend directory
if [ ! -f "./backend/.env" ]; then
  echo "Error: .env file not found in ./backend/"
  echo "Please create it by copying .env.example and adding your API keys"
  echo "cp ./backend/.env.example ./backend/.env"
  exit 1
fi

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed. Please install Docker first."
  exit 1
fi

if ! command -v docker-compose &> /dev/null; then
  echo "Docker Compose is not installed. Please install Docker Compose first."
  exit 1
fi

# Build and start the containers
echo "Starting LegalMind AI system with Redis..."
docker-compose up --build -d

# Wait for the containers to start
sleep 5

# Show the container status
docker-compose ps

# Print the access URLs
echo ""
echo "LegalMind AI system is running!"
echo "API is available at: http://localhost:8080"
echo "Redis GUI is available at: http://localhost:8001"
echo ""
echo "To stop the system, run: docker-compose down" 