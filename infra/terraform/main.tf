# Root Terraform Module

module "network" {
  source = "./modules/network"
  environment = var.environment
  region = var.region
}

module "postgres" {
  source = "./modules/postgres"
  environment = var.environment
  db_instance_class = var.db_instance_class
  vpc_id = module.network.vpc_id
}

module "redis" {
  source = "./modules/redis"
  environment = var.environment
  redis_instance_class = var.redis_instance_class
  vpc_id = module.network.vpc_id
}

module "app" {
  source = "./modules/app"
  environment = var.environment
  app_name = var.app_name
  image_tag = var.image_tag
  db_endpoint = module.postgres.endpoint
  redis_endpoint = module.redis.endpoint
  vpc_id = module.network.vpc_id
}

module "cloudflare" {
  source = "./modules/cloudflare"
  domain = var.domain
  cloudflare_config = var.cloudflare_config
}
