# VPC, subnets, NAT, security groups

variable "project" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "azs" {
  type        = list(string)
  description = "At least 2 availability zones."
}

variable "single_nat_gateway" {
  type        = bool
  description = "true = one NAT gateway shared across AZs (cheaper, staging). false = one per AZ (prod)."
  default     = true
}
