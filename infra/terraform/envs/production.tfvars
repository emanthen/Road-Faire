environment = "production"
aws_region  = "us-east-1"
azs         = ["us-east-1a", "us-east-1b"]

rds_instance_class    = "db.r6g.large"
redis_node_type       = "cache.r6g.large"
redis_num_cache_nodes = 2

backend_desired_count  = 2
frontend_desired_count = 2

# db_password, backend_image, frontend_image are set via -var or TF_VAR_* env vars in
# CI, never committed here.
