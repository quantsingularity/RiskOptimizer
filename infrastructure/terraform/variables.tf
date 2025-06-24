# Enhanced Terraform Variables for RiskOptimizer Infrastructure
# This file defines all variables with security and compliance considerations

# Environment Configuration
variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "riskoptimizer"
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.app_name))
    error_message = "App name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.aws_region))
    error_message = "AWS region must be a valid region identifier."
  }
}

# Security and Compliance Configuration
variable "compliance_level" {
  description = "Compliance level (basic, standard, strict)"
  type        = string
  default     = "strict"
  validation {
    condition     = contains(["basic", "standard", "strict"], var.compliance_level)
    error_message = "Compliance level must be one of: basic, standard, strict."
  }
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
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  validation {
    condition     = length(var.public_subnet_cidrs) >= 2
    error_message = "At least 2 public subnets are required for high availability."
  }
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
  validation {
    condition     = length(var.private_subnet_cidrs) >= 2
    error_message = "At least 2 private subnets are required for high availability."
  }
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
  validation {
    condition     = length(var.database_subnet_cidrs) >= 2
    error_message = "At least 2 database subnets are required for high availability."
  }
}

# EKS Configuration
variable "eks_cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
  validation {
    condition     = can(regex("^1\\.(2[4-9]|[3-9][0-9])$", var.eks_cluster_version))
    error_message = "EKS cluster version must be 1.24 or higher."
  }
}

variable "eks_node_instance_types" {
  description = "Instance types for EKS node groups"
  type        = list(string)
  default     = ["m5.large", "m5.xlarge"]
  validation {
    condition     = length(var.eks_node_instance_types) > 0
    error_message = "At least one instance type must be specified."
  }
}

variable "eks_node_group_min_size" {
  description = "Minimum number of nodes in EKS node group"
  type        = number
  default     = 3
  validation {
    condition     = var.eks_node_group_min_size >= 1
    error_message = "Minimum node group size must be at least 1."
  }
}

variable "eks_node_group_max_size" {
  description = "Maximum number of nodes in EKS node group"
  type        = number
  default     = 10
  validation {
    condition     = var.eks_node_group_max_size >= var.eks_node_group_min_size
    error_message = "Maximum node group size must be greater than or equal to minimum size."
  }
}

variable "eks_node_group_desired_size" {
  description = "Desired number of nodes in EKS node group"
  type        = number
  default     = 3
  validation {
    condition = (
      var.eks_node_group_desired_size >= var.eks_node_group_min_size &&
      var.eks_node_group_desired_size <= var.eks_node_group_max_size
    )
    error_message = "Desired node group size must be between minimum and maximum sizes."
  }
}

# Database Configuration
variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "15.4"
  validation {
    condition     = can(regex("^1[5-9]\\.[0-9]+$", var.db_engine_version))
    error_message = "Database engine version must be PostgreSQL 15.0 or higher."
  }
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.r6g.large"
  validation {
    condition     = can(regex("^db\\.[a-z0-9]+\\.(micro|small|medium|large|xlarge|[0-9]+xlarge)$", var.db_instance_class))
    error_message = "Database instance class must be a valid RDS instance type."
  }
}

variable "db_allocated_storage" {
  description = "Initial allocated storage for RDS instance (GB)"
  type        = number
  default     = 100
  validation {
    condition     = var.db_allocated_storage >= 20
    error_message = "Allocated storage must be at least 20 GB."
  }
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS instance (GB)"
  type        = number
  default     = 1000
  validation {
    condition     = var.db_max_allocated_storage >= var.db_allocated_storage
    error_message = "Maximum allocated storage must be greater than or equal to initial allocated storage."
  }
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "riskoptimizer"
  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]*$", var.db_name))
    error_message = "Database name must start with a letter and contain only letters, numbers, and underscores."
  }
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "riskoptimizer_admin"
  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9_]*$", var.db_username))
    error_message = "Database username must start with a letter and contain only letters, numbers, and underscores."
  }
}

# Redis Configuration
variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.r6g.large"
  validation {
    condition     = can(regex("^cache\\.[a-z0-9]+\\.(micro|small|medium|large|xlarge|[0-9]+xlarge)$", var.redis_node_type))
    error_message = "Redis node type must be a valid ElastiCache node type."
  }
}

variable "redis_num_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 3
  validation {
    condition     = var.redis_num_nodes >= 1 && var.redis_num_nodes <= 20
    error_message = "Number of Redis nodes must be between 1 and 20."
  }
}

# Vault Configuration
variable "vault_address" {
  description = "Vault server address"
  type        = string
  default     = "https://vault.riskoptimizer.com:8200"
  validation {
    condition     = can(regex("^https://", var.vault_address))
    error_message = "Vault address must use HTTPS protocol."
  }
}

variable "vault_namespace" {
  description = "Vault namespace"
  type        = string
  default     = "riskoptimizer"
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.vault_namespace))
    error_message = "Vault namespace must contain only lowercase letters, numbers, and hyphens."
  }
}

# IAM Configuration
variable "assume_role_arn" {
  description = "ARN of IAM role to assume for cross-account access"
  type        = string
  default     = null
  validation {
    condition = var.assume_role_arn == null || can(regex("^arn:aws:iam::[0-9]{12}:role/", var.assume_role_arn))
    error_message = "Assume role ARN must be a valid IAM role ARN or null."
  }
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
  validation {
    condition = alltrue([
      for endpoint in var.notification_endpoints :
      contains(["email", "sms", "slack", "pagerduty"], endpoint.type)
    ])
    error_message = "Notification endpoint type must be one of: email, sms, slack, pagerduty."
  }
}

# Backup Configuration
variable "cross_region_backup_vault_arn" {
  description = "ARN of cross-region backup vault for disaster recovery"
  type        = string
  default     = null
  validation {
    condition = var.cross_region_backup_vault_arn == null || can(regex("^arn:aws:backup:", var.cross_region_backup_vault_arn))
    error_message = "Cross-region backup vault ARN must be a valid AWS Backup vault ARN or null."
  }
}

# Certificate Configuration
variable "domain_name" {
  description = "Primary domain name for SSL certificate"
  type        = string
  default     = "riskoptimizer.com"
  validation {
    condition     = can(regex("^[a-z0-9.-]+\\.[a-z]{2,}$", var.domain_name))
    error_message = "Domain name must be a valid domain."
  }
}

variable "subject_alternative_names" {
  description = "Subject alternative names for SSL certificate"
  type        = list(string)
  default     = ["*.riskoptimizer.com", "api.riskoptimizer.com", "app.riskoptimizer.com"]
  validation {
    condition = alltrue([
      for san in var.subject_alternative_names :
      can(regex("^(\\*\\.)?[a-z0-9.-]+\\.[a-z]{2,}$", san))
    ])
    error_message = "All subject alternative names must be valid domain names or wildcard domains."
  }
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
  validation {
    condition = alltrue([
      for key, value in var.default_tags :
      can(regex("^[a-zA-Z0-9+\\-=._:/@\\s]+$", key)) && can(regex("^[a-zA-Z0-9+\\-=._:/@\\s]+$", value))
    ])
    error_message = "Tag keys and values must contain only valid characters."
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
  validation {
    condition     = var.spot_instance_percentage >= 0 && var.spot_instance_percentage <= 100
    error_message = "Spot instance percentage must be between 0 and 100."
  }
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
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.dr_region))
    error_message = "DR region must be a valid AWS region identifier."
  }
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
  validation {
    condition     = can(regex("^(mon|tue|wed|thu|fri|sat|sun):[0-2][0-9]:[0-5][0-9]-(mon|tue|wed|thu|fri|sat|sun):[0-2][0-9]:[0-5][0-9]$", var.maintenance_window))
    error_message = "Maintenance window must be in the format 'ddd:hh:mm-ddd:hh:mm'."
  }
}

variable "backup_window" {
  description = "Preferred backup window for RDS"
  type        = string
  default     = "03:00-04:00"
  validation {
    condition     = can(regex("^[0-2][0-9]:[0-5][0-9]-[0-2][0-9]:[0-5][0-9]$", var.backup_window))
    error_message = "Backup window must be in the format 'hh:mm-hh:mm'."
  }
}

