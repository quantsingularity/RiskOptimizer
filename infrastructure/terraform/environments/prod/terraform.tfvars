# Terraform variables for production environment
environment = "production"
app_name    = "riskoptimizer"
aws_region  = "us-west-2"

# Network
vpc_cidr              = "10.2.0.0/16"
public_subnet_cidrs   = ["10.2.1.0/24", "10.2.2.0/24", "10.2.3.0/24"]
private_subnet_cidrs  = ["10.2.11.0/24", "10.2.12.0/24", "10.2.13.0/24"]
database_subnet_cidrs = ["10.2.21.0/24", "10.2.22.0/24", "10.2.23.0/24"]

# Database (PostgreSQL)
db_engine_version        = "15.4"
db_instance_class        = "db.r6g.large"
db_name                  = "riskoptimizerdb"
db_username              = "riskoptimizer_admin"
db_allocated_storage     = 100
db_max_allocated_storage = 1000

# Redis
redis_node_type = "cache.r6g.large"
redis_num_nodes = 3

# EKS
eks_cluster_version         = "1.28"
eks_node_instance_types     = ["m5.large"]
eks_node_group_min_size     = 3
eks_node_group_max_size     = 10
eks_node_group_desired_size = 3

# Security & Compliance
compliance_level    = "strict"
enable_encryption   = true
enable_guardduty    = true
enable_security_hub = true
enable_config       = true
enable_cloudtrail   = true

# Monitoring
notification_endpoints = [
  {
    type     = "email"
    endpoint = "alerts@riskoptimizer.com"
  }
]

# Feature flags
enable_waf        = true
enable_shield     = false
enable_debug_mode = false

# Tags
default_tags = {
  Project     = "RiskOptimizer"
  Environment = "production"
  Owner       = "DevOps Team"
  CostCenter  = "Engineering"
  ManagedBy   = "Terraform"
}
