#!/bin/bash
# AWS Setup Script for Plantos MCP Server

set -e

echo "🚀 Setting up AWS infrastructure for Plantos MCP Server"
echo ""

# Set your AWS region
AWS_REGION="us-east-1"  # Change this to your preferred region

echo "1️⃣  Creating ECR repository..."
aws ecr create-repository \
    --repository-name plantos-mcp-server \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256

ECR_URI=$(aws ecr describe-repositories \
    --repository-names plantos-mcp-server \
    --region $AWS_REGION \
    --query 'repositories[0].repositoryUri' \
    --output text)

echo "✅ ECR repository created: $ECR_URI"
echo ""

echo "📝 Save these values for GitHub Secrets:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "AWS_REGION=$AWS_REGION"
echo "ECR_REPOSITORY=plantos-mcp-server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Next steps:"
echo "1. Set up your EC2 instance (see EC2 setup instructions)"
echo "2. Add secrets to GitHub (see GitHub secrets instructions)"
echo "3. Push to main branch to trigger deployment"
