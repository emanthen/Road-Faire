# RDS Postgres 16 + PostGIS param group

locals {
  name = "${var.project}-${var.environment}"
}

resource "aws_db_subnet_group" "this" {
  name       = "${local.name}-db"
  subnet_ids = var.private_subnet_ids
  tags       = { Name = "${local.name}-db" }
}

# PostGIS is a supported RDS extension (rds.extensions), enabled via the parameter
# group rather than a custom image or shared_preload_libraries.
resource "aws_db_parameter_group" "this" {
  name   = "${local.name}-postgres16"
  family = "postgres16"

  parameter {
    name  = "rds.extensions"
    value = "postgis"
  }
}

resource "aws_db_instance" "this" {
  identifier                = "${local.name}-db"
  engine                    = "postgres"
  engine_version            = "16"
  instance_class            = var.instance_class
  allocated_storage         = var.allocated_storage_gb
  storage_encrypted         = true
  db_name                   = var.db_name
  username                  = var.db_username
  password                  = var.db_password
  db_subnet_group_name      = aws_db_subnet_group.this.name
  vpc_security_group_ids    = [var.security_group_id]
  parameter_group_name      = aws_db_parameter_group.this.name
  multi_az                  = var.multi_az
  publicly_accessible       = false
  backup_retention_period   = var.backup_retention_days
  skip_final_snapshot       = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${local.name}-final" : null
  deletion_protection       = var.environment == "production"

  tags = { Name = "${local.name}-db" }
}
