# Plantos MCP Server Infrastructure

Deploy Plantos MCP server to AWS, your own servers, or locally with Docker Compose.

## Quick Start

### 1. Install OpenTofu
```bash
brew install opentofu  # macOS
```

### 2. Deploy to AWS
```bash
cd infrastructure
tofu init
tofu apply
```

### 3. Deploy to Your Own Server
```bash
cd infrastructure
tofu init
tofu apply -var="deployment_target=generic" -var="server_ip=YOUR_IP"
```

### 4. Deploy Locally
```bash
cp .env.example .env
docker-compose up -d
```

## See full documentation in this directory
