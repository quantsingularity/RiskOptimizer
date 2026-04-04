# Terraform variables for development environment
environment = "development"
app_name    = "riskoptimizer"
aws_region  = "us-west-2"

# Network
vpc_cidr              = "10.0.0.0/16"
public_subnet_cidrs   = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_subnet_cidrs  = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
database_subnet_cidrs = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]

# Database (PostgreSQL)
db_engine_version        = "15.4"
db_instance_class        = "db.t3.medium"
db_name                  = "riskoptimizerdb"
db_username              = "riskoptimizer_admin"
db_allocated_storage     = 20
db_max_allocated_storage = 100

# Redis
redis_node_type = "cache.t3.medium"
redis_num_nodes = 1

# EKS
eks_cluster_version         = "1.28"
eks_node_instance_types     = ["t3.medium"]
eks_node_group_min_size     = 1
eks_node_group_max_size     = 3
eks_node_group_desired_size = 1

# Security & Compliance
compliance_level    = "standard"
enable_encryption   = true
enable_guardduty    = false
enable_security_hub = false
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
enable_waf        = false
enable_shield     = false
enable_debug_mode = true

# Tags
default_tags = {
  Project     = "RiskOptimizer"
  Environment = "development"
  Owner       = "DevOps Team"
  CostCenter  = "Engineering"
  ManagedBy   = "Terraform"
}
