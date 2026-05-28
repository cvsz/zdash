output "app_url" {
  description = "URL of the frontend application"
  value       = "https://${var.domain}"
}

output "backend_url" {
  description = "URL of the backend API"
  value       = "https://api.${var.domain}"
}

output "db_endpoint" {
  description = "Database connection endpoint"
  value       = module.postgres.endpoint
}

output "redis_endpoint" {
  description = "Redis connection endpoint"
  value       = module.redis.endpoint
}

output "cloudflare_hostname" {
  description = "Configured Cloudflare hostname"
  value       = module.cloudflare.hostname
}
