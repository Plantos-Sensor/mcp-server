# AWS Module for Plantos MCP Server

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
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

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.small"
}

# Data sources
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security Group
resource "aws_security_group" "mcp_server" {
  name_prefix = "plantos-mcp-${var.environment}-"
  description = "Security group for Plantos MCP server"

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH (for management)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # TODO: Restrict to your IP
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "plantos-mcp-${var.environment}"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# EC2 Instance
resource "aws_instance" "mcp_server" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.mcp_server.id]

  user_data = <<-EOF
    #!/bin/bash
    # Update system
    yum update -y
    
    # Install Docker
    yum install -y docker
    systemctl start docker
    systemctl enable docker
    usermod -a -G docker ec2-user
    
    # Install Docker Compose
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Create app directory
    mkdir -p /opt/plantos-mcp
    cd /opt/plantos-mcp
    
    # Create docker-compose.yml
    cat > docker-compose.yml << 'COMPOSE_EOF'
version: '3.8'
services:
  plantos-mcp:
    image: ghcr.io/plantos-sensor/mcp-server:latest
    container_name: plantos-mcp-server
    ports:
      - "80:8080"
    environment:
      - MCP_TRANSPORT=http
      - PORT=8080
      - HOST=0.0.0.0
      - PLANTOS_API_URL=${var.plantos_api_url}
    restart: unless-stopped
COMPOSE_EOF
    
    # Start the service
    docker-compose up -d
  EOF

  tags = {
    Name        = "plantos-mcp-${var.environment}"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# Elastic IP (optional - for stable IP)
resource "aws_eip" "mcp_server" {
  instance = aws_instance.mcp_server.id
  domain   = "vpc"

  tags = {
    Name        = "plantos-mcp-${var.environment}"
    Environment = var.environment
    ManagedBy   = "OpenTofu"
  }
}

# Outputs
output "server_url" {
  value = "https://${var.domain_name}"
}

output "server_ip" {
  value = aws_eip.mcp_server.public_ip
}

output "instance_id" {
  value = aws_instance.mcp_server.id
}
