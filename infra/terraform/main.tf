# Roadfare AWS infra: ECS Fargate + RDS Postgres/PostGIS + ElastiCache Redis + S3 + CloudFront.

terraform {
  required_version = ">= 1.7"
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

module "network" {
  source             = "./modules/network"
  project            = var.project
  environment        = var.environment
  azs                = var.azs
  single_nat_gateway = var.environment != "production"
}

module "secrets" {
  source      = "./modules/secrets"
  project     = var.project
  environment = var.environment
}

module "rds" {
  source             = "./modules/rds"
  project            = var.project
  environment        = var.environment
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  security_group_id  = module.network.rds_security_group_id
  instance_class     = var.rds_instance_class
  multi_az           = var.environment == "production"
  db_password        = var.db_password
}

module "redis" {
  source             = "./modules/redis"
  project            = var.project
  environment        = var.environment
  private_subnet_ids = module.network.private_subnet_ids
  security_group_id  = module.network.redis_security_group_id
  node_type          = var.redis_node_type
  num_cache_nodes    = var.redis_num_cache_nodes
}

module "s3_cloudfront" {
  source      = "./modules/s3_cloudfront"
  project     = var.project
  environment = var.environment
}

module "ecs" {
  source                 = "./modules/ecs"
  project                = var.project
  environment            = var.environment
  vpc_id                 = module.network.vpc_id
  public_subnet_ids      = module.network.public_subnet_ids
  private_subnet_ids     = module.network.private_subnet_ids
  alb_security_group_id  = module.network.alb_security_group_id
  ecs_security_group_id  = module.network.ecs_security_group_id
  backend_image          = var.backend_image
  frontend_image         = var.frontend_image
  backend_desired_count  = var.backend_desired_count
  frontend_desired_count = var.frontend_desired_count
  secret_arns            = module.secrets.parameter_arns
  database_url           = "postgis://${var.db_username}:${var.db_password}@${module.rds.endpoint}/${module.rds.db_name}"
  redis_url              = "redis://${module.redis.primary_endpoint}:${module.redis.port}/0"
}
