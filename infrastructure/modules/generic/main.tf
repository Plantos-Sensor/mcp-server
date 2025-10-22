# Generic/Self-Hosted Module for Plantos MCP Server
# Use this for deploying to your own servers, DigitalOcean, Linode, etc.

terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.0"
    }
  }
}

variable "environment" {
  type = string
}

variable "domain_name" {
  type = string
}

variable "plantos_api_url" {
  type = string
}

variable "container_port" {
  type = number
}

variable "server_ip" {
  description = "IP address of your server"
  type        = string
}

variable "ssh_user" {
  description = "SSH user for server access"
  type        = string
  default     = "root"
}

variable "ssh_private_key_path" {
  description = "Path to SSH private key"
  type        = string
  default     = "~/.ssh/id_rsa"
}

# Deploy using SSH
resource "null_resource" "deploy_mcp" {
  triggers = {
    always_run = timestamp()
  }

  connection {
    type        = "ssh"
    host        = var.server_ip
    user        = var.ssh_user
    private_key = file(var.ssh_private_key_path)
  }

  provisioner "remote-exec" {
    inline = [
      # Install Docker if not present
      "command -v docker || (curl -fsSL https://get.docker.com | sh)",
      
      # Install Docker Compose if not present
      "command -v docker-compose || (curl -L 'https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)' -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose)",
      
      # Create app directory
      "mkdir -p /opt/plantos-mcp",
      "cd /opt/plantos-mcp",
      
      # Create docker-compose.yml
      <<-COMPOSE_EOF
cat > docker-compose.yml << 'END_COMPOSE'
version: '3.8'
services:
  plantos-mcp:
    image: ghcr.io/plantos-sensor/mcp-server:latest
    container_name: plantos-mcp-server
    ports:
      - "80:8080"
      - "443:8080"
    environment:
      - MCP_TRANSPORT=http
      - PORT=8080
      - HOST=0.0.0.0
      - PLANTOS_API_URL=${var.plantos_api_url}
    restart: unless-stopped
END_COMPOSE
COMPOSE_EOF
      ,
      
      # Pull latest image and restart
      "docker-compose pull",
      "docker-compose up -d"
    ]
  }
}

# Outputs
output "server_url" {
  value = "https://${var.domain_name}"
}

output "server_ip" {
  value = var.server_ip
}
