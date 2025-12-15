# Enhanced Terraform Variables for RiskOptimizer Infrastructure
# This file defines all variables with security and compliance considerations

# Environment Configuration
variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "riskoptimizer"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

# Security and Compliance Configuration
variable "compliance_level" {
  description = "Compliance level (basic, standard, strict)"
  type        = string
  default     = "strict"
}

variable "enable_encryption" {
  description = "Enable encryption for all supported resources"
  type        = bool
  default     = true
}

variable "enable_audit_logging" {
  description = "Enable comprehensive audit logging"
  type        = bool
  default     = true
}

variable "enable_monitoring" {
  description = "Enable comprehensive monitoring and alerting"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automated backup for all supported resources"
  type        = bool
  default     = true
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
}

# EKS Configuration
variable "eks_cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
}

variable "eks_node_instance_types" {
  description = "Instance types for EKS node groups"
  type        = list(string)
  default     = ["m5.large", "m5.xlarge"]
}

variable "eks_node_group_min_size" {
  description = "Minimum number of nodes in EKS node group"
  type        = number
  default     = 3
# VALIDATION DISABLED: }
# VALIDATION DISABLED: 
# VALIDATION DISABLED: variable "eks_node_group_max_size" {
# VALIDATION DISABLED:   description = "Maximum number of nodes in EKS node group"
# VALIDATION DISABLED:   type        = number
# VALIDATION DISABLED:   default     = 10
# VALIDATION DISABLED: }
# VALIDATION DISABLED: 
# VALIDATION DISABLED: variable "eks_node_group_desired_size" {
# VALIDATION DISABLED:   description = "Desired number of nodes in EKS node group"
# VALIDATION DISABLED:   type        = number
# VALIDATION DISABLED:   default     = 3
}

# Database Configuration
variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.4"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.large"
}

variable "db_allocated_storage" {
  description = "Initial allocated storage for RDS instance (GB)"
  type        = number
  default     = 100
# VALIDATION DISABLED: }
# VALIDATION DISABLED: 
# VALIDATION DISABLED: variable "db_max_allocated_storage" {
# VALIDATION DISABLED:   description = "Maximum allocated storage for RDS instance (GB)"
# VALIDATION DISABLED:   type        = number
# VALIDATION DISABLED:   default     = 1000
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "riskoptimizer"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "riskoptimizer_admin"
}

# Redis Configuration
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.r6g.large"
}

variable "redis_num_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 3
}

# Vault Configuration
variable "vault_address" {
  description = "Vault server address"
  type        = string
  default     = "https://vault.riskoptimizer.com:8200"
}

variable "vault_namespace" {
  description = "Vault namespace"
  type        = string
  default     = "riskoptimizer"
}

# IAM Configuration
variable "assume_role_arn" {
  description = "ARN of IAM role to assume for cross-account access"
  type        = string
  default     = null
}

variable "external_id" {
  description = "External ID for assume role"
  type        = string
  default     = null
  sensitive   = true
}

# Monitoring and Alerting Configuration
variable "notification_endpoints" {
  description = "List of notification endpoints for alerts"
  type = list(object({
    type     = string
    endpoint = string
  }))
  default = [
    {
      type     = "email"
      endpoint = "alerts@riskoptimizer.com"
    }
  ]
}

# Backup Configuration
variable "cross_region_backup_vault_arn" {
  description = "ARN of cross-region backup vault for disaster recovery"
  type        = string
  default     = null
}

# Certificate Configuration
variable "domain_name" {
  description = "Primary domain name for SSL certificate"
  type        = string
  default     = "riskoptimizer.com"
}

variable "subject_alternative_names" {
  description = "Subject alternative names for SSL certificate"
  type        = list(string)
  default     = ["*.riskoptimizer.com", "api.riskoptimizer.com", "app.riskoptimizer.com"]
}

# Default Tags
variable "default_tags" {
  description = "Default tags to apply to all resources"
  type        = map(string)
  default = {
    Project             = "RiskOptimizer"
    Owner              = "DevOps Team"
    CostCenter         = "Engineering"
    BusinessUnit       = "Technology"
    DataClassification = "Confidential"
    BackupRequired     = "true"
    MonitoringEnabled  = "true"
  }
}

# Feature Flags
variable "enable_waf" {
  description = "Enable AWS WAF for application protection"
  type        = bool
  default     = true
}

variable "enable_shield" {
  description = "Enable AWS Shield Advanced for DDoS protection"
  type        = bool
  default     = false
}

variable "enable_guardduty" {
  description = "Enable AWS GuardDuty for threat detection"
  type        = bool
  default     = true
}

variable "enable_security_hub" {
  description = "Enable AWS Security Hub for security posture management"
  type        = bool
  default     = true
}

variable "enable_config" {
  description = "Enable AWS Config for compliance monitoring"
  type        = bool
  default     = true
}

variable "enable_cloudtrail" {
  description = "Enable AWS CloudTrail for API logging"
  type        = bool
  default     = true
}

variable "enable_vpc_flow_logs" {
  description = "Enable VPC Flow Logs for network monitoring"
  type        = bool
  default     = true
}

# Cost Optimization
variable "enable_cost_optimization" {
  description = "Enable cost optimization features (Spot instances, etc.)"
  type        = bool
  default     = false
}

variable "spot_instance_percentage" {
  description = "Percentage of Spot instances in EKS node groups"
  type        = number
  default     = 0
}

# Development and Testing
variable "enable_debug_mode" {
  description = "Enable debug mode for development environments"
  type        = bool
  default     = false
}

variable "enable_test_data" {
  description = "Enable test data generation for non-production environments"
  type        = bool
  default     = false
}

# Disaster Recovery
variable "enable_cross_region_replication" {
  description = "Enable cross-region replication for disaster recovery"
  type        = bool
  default     = false
}

variable "dr_region" {
  description = "Disaster recovery region"
  type        = string
  default     = "us-east-1"
}

# Performance Configuration
variable "enable_performance_insights" {
  description = "Enable Performance Insights for RDS"
  type        = bool
  default     = true
}

variable "enable_enhanced_monitoring" {
  description = "Enable enhanced monitoring for RDS"
  type        = bool
  default     = true
}

# Maintenance Windows
variable "maintenance_window" {
  description = "Preferred maintenance window for RDS and ElastiCache"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

variable "backup_window" {
  description = "Preferred backup window for RDS"
  type        = string
  default     = "03:00-04:00"
}
