environment = "staging"
aws_region  = "us-east-1"
azs         = ["us-east-1a", "us-east-1b"]

rds_instance_class    = "db.t4g.micro"
redis_node_type       = "cache.t4g.micro"
redis_num_cache_nodes = 1

backend_desired_count  = 1
frontend_desired_count = 1

# db_password, backend_image, frontend_image are set via -var or TF_VAR_* env vars in
# CI, never committed here.
