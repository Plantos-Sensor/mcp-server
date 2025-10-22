# Plantos MCP Server Configuration

# Deployment target
deployment_target = "aws"
environment       = "production"

# Domain configuration
domain_name = "mcp.plantos.co"

# API configuration
plantos_api_url = "https://api.plantos.co"
container_port  = 8080

# AWS-specific configuration
aws_region    = "us-east-1"  # Change to your region
instance_type = "t3.micro"   # Lightweight and cost-effective
