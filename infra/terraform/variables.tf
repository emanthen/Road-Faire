variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type = string
}

variable "project" {
  type    = string
  default = "roadfare"
}

variable "azs" {
  type        = list(string)
  description = "At least 2 availability zones in aws_region."
}

variable "rds_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "db_username" {
  type    = string
  default = "roadfare"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "redis_node_type" {
  type    = string
  default = "cache.t4g.micro"
}

variable "redis_num_cache_nodes" {
  type    = number
  default = 1
}

variable "backend_image" {
  type        = string
  description = "ECR image URI for the backend, set by CI after building."
}

variable "frontend_image" {
  type        = string
  description = "ECR image URI for the frontend, set by CI after building."
}

variable "backend_desired_count" {
  type    = number
  default = 1
}

variable "frontend_desired_count" {
  type    = number
  default = 1
}
