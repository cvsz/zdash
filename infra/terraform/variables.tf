variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "zdash"
}

variable "environment" {
  description = "Deployment environment (e.g., production, staging)"
  type        = string
  default     = "production"
}

variable "region" {
  description = "Cloud region for deployment"
  type        = string
  default     = "us-west-2"
}

variable "domain" {
  description = "Domain name for the application"
  type        = string
  default     = "zdash.zeaz.dev"
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "db_instance_class" {
  description = "Database sizing"
  type        = string
  default     = "small"
}

variable "redis_instance_class" {
  description = "Redis sizing"
  type        = string
  default     = "small"
}

variable "cloudflare_config" {
  description = "Cloudflare configuration"
  type        = map(string)
  default = {
    account_id = ""
    zone_id    = ""
    tunnel_name= "zdash"
  }
}
