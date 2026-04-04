# Terraform variables for staging environment
environment = "staging"
app_name    = "riskoptimizer"
aws_region  = "us-west-2"

# Network
vpc_cidr              = "10.1.0.0/16"
public_subnet_cidrs   = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
private_subnet_cidrs  = ["10.1.11.0/24", "10.1.12.0/24", "10.1.13.0/24"]
database_subnet_cidrs = ["10.1.21.0/24", "10.1.22.0/24", "10.1.23.0/24"]

# Database (PostgreSQL)
db_engine_version        = "15.4"
db_instance_class        = "db.t3.large"
db_name                  = "riskoptimizerdb"
db_username              = "riskoptimizer_admin"
db_allocated_storage     = 50
db_max_allocated_storage = 500

# Redis
redis_node_type = "cache.t3.medium"
redis_num_nodes = 1

# EKS
eks_cluster_version         = "1.28"
eks_node_instance_types     = ["t3.large"]
eks_node_group_min_size     = 1
eks_node_group_max_size     = 5
eks_node_group_desired_size = 2

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
enable_debug_mode = false

# Tags
default_tags = {
  Project     = "RiskOptimizer"
  Environment = "staging"
  Owner       = "DevOps Team"
  CostCenter  = "Engineering"
  ManagedBy   = "Terraform"
}
