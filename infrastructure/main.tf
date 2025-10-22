# Plantos MCP Server Infrastructure
# Provider-agnostic configuration using OpenTofu

terraform {
  required_version = ">= 1.6.0"
  
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
  
  # Backend configuration for state storage
  # Uncomment and configure for remote state
  # backend "s3" {
  #   bucket = "plantos-terraform-state"
  #   key    = "mcp-server/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

# Variables
variable "deployment_target" {
  description = "Where to deploy: aws, digitalocean, self-hosted"
  type        = string
  default     = "aws"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "domain_name" {
  description = "Domain name for MCP server"
  type        = string
  default     = "mcp.plantos.co"
}

variable "plantos_api_url" {
  description = "Plantos API base URL"
  type        = string
  default     = "https://api.plantos.co"
}

variable "container_port" {
  description = "Container port for MCP server"
  type        = number
  default     = 8080
}

# Module selection based on deployment target
module "deployment" {
  source = "./modules/${var.deployment_target}"
  
  environment      = var.environment
  domain_name      = var.domain_name
  plantos_api_url  = var.plantos_api_url
  container_port   = var.container_port
}

# Outputs
output "server_url" {
  description = "MCP server URL"
  value       = module.deployment.server_url
}

output "server_ip" {
  description = "MCP server IP address"
  value       = module.deployment.server_ip
}
