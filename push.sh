#!/bin/bash
USERNAME="eb300" 

echo "Building agent image..."
docker compose build agent

echo "Tagging image..."
docker tag ai-agent-mvp-agent:latest $USERNAME/ai-agent:latest

echo "Pushing to Docker Hub..."
docker push $USERNAME/ai-agent:latest

echo "Done! Image available at: $USERNAME/ai-agent:latest"