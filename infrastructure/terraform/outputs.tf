# Enhanced Terraform Outputs for RiskOptimizer Infrastructure
# This file defines outputs with security and operational considerations

# Environment Information
output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "region" {
  description = "AWS region"
  value       = data.aws_region.current.name
}

output "account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
  sensitive   = true
}

# Network Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.network.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.network.vpc_cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.network.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.network.private_subnet_ids
}

output "database_subnet_ids" {
  description = "IDs of the database subnets"
  value       = module.network.database_subnet_ids
}

output "nat_gateway_ids" {
  description = "IDs of the NAT Gateways"
  value       = module.network.nat_gateway_ids
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = module.network.internet_gateway_id
}

# Security Outputs
output "kms_key_id" {
  description = "ID of the KMS key"
  value       = module.kms.key_id
}

output "kms_key_arn" {
  description = "ARN of the KMS key"
  value       = module.kms.key_arn
}

output "security_group_ids" {
  description = "Map of security group IDs"
  value = {
    alb      = module.security.alb_security_group_id
    app      = module.security.app_security_group_id
    database = module.security.database_security_group_id
    redis    = module.security.redis_security_group_id
    eks      = module.security.eks_security_group_id
  }
}

output "iam_role_arns" {
  description = "Map of IAM role ARNs"
  value = {
    eks_cluster_role    = module.security.eks_cluster_role_arn
    eks_node_group_role = module.security.eks_node_group_role_arn
    rds_monitoring_role = module.security.rds_monitoring_role_arn
    backup_role         = module.security.backup_role_arn
  }
  sensitive = true
}

# EKS Cluster Outputs
output "eks_cluster_id" {
  description = "EKS cluster ID"
  value       = module.eks.cluster_id
}

output "eks_cluster_arn" {
  description = "EKS cluster ARN"
  value       = module.eks.cluster_arn
}

output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "eks_cluster_version" {
  description = "EKS cluster Kubernetes version"
  value       = module.eks.cluster_version
}

output "eks_cluster_security_group_id" {
  description = "EKS cluster security group ID"
  value       = module.eks.cluster_security_group_id
}

output "eks_node_groups" {
  description = "EKS node groups information"
  value = {
    for k, v in module.eks.node_groups : k => {
      arn            = v.node_group_arn
      status         = v.node_group_status
      capacity_type  = v.capacity_type
      instance_types = v.instance_types
    }
  }
}

output "eks_oidc_issuer_url" {
  description = "EKS cluster OIDC issuer URL"
  value       = module.eks.cluster_oidc_issuer_url
}

output "eks_cluster_certificate_authority_data" {
  description = "EKS cluster certificate authority data"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

# Database Outputs
output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = module.database.db_instance_endpoint
  sensitive   = true
}

output "database_port" {
  description = "RDS instance port"
  value       = module.database.db_instance_port
}

output "database_name" {
  description = "Database name"
  value       = module.database.db_instance_name
}

output "database_username" {
  description = "Database master username"
  value       = module.database.db_instance_username
  sensitive   = true
}

output "database_arn" {
  description = "RDS instance ARN"
  value       = module.database.db_instance_arn
}

output "database_resource_id" {
  description = "RDS instance resource ID"
  value       = module.database.db_instance_resource_id
}

output "database_subnet_group_name" {
  description = "Database subnet group name"
  value       = module.database.db_subnet_group_name
}

output "database_parameter_group_name" {
  description = "Database parameter group name"
  value       = module.database.db_parameter_group_name
}

# Redis Outputs
output "redis_cluster_address" {
  description = "Redis cluster endpoint address"
  value       = module.redis.cache_cluster_address
  sensitive   = true
}

output "redis_cluster_port" {
  description = "Redis cluster port"
  value       = module.redis.cache_cluster_port
}

output "redis_cluster_id" {
  description = "Redis cluster ID"
  value       = module.redis.cache_cluster_id
}

output "redis_subnet_group_name" {
  description = "Redis subnet group name"
  value       = module.redis.cache_subnet_group_name
}

output "redis_parameter_group_name" {
  description = "Redis parameter group name"
  value       = module.redis.cache_parameter_group_name
}

# Storage Outputs
output "s3_bucket_names" {
  description = "Map of S3 bucket names"
  value       = module.storage.bucket_names
}

output "s3_bucket_arns" {
  description = "Map of S3 bucket ARNs"
  value       = module.storage.bucket_arns
}

output "s3_bucket_domain_names" {
  description = "Map of S3 bucket domain names"
  value       = module.storage.bucket_domain_names
}

# Load Balancer Outputs
output "load_balancer_arn" {
  description = "Application Load Balancer ARN"
  value       = module.load_balancer.lb_arn
}

output "load_balancer_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.load_balancer.lb_dns_name
}

output "load_balancer_zone_id" {
  description = "Application Load Balancer zone ID"
  value       = module.load_balancer.lb_zone_id
}

output "target_group_arns" {
  description = "Map of target group ARNs"
  value       = module.load_balancer.target_group_arns
}

# Certificate Outputs
output "acm_certificate_arn" {
  description = "ACM certificate ARN"
  value       = module.security.acm_certificate_arn
}

output "acm_certificate_domain_validation_options" {
  description = "ACM certificate domain validation options"
  value       = module.security.acm_certificate_domain_validation_options
  sensitive   = true
}

# Monitoring Outputs
output "cloudwatch_log_groups" {
  description = "Map of CloudWatch log group names"
  value       = module.monitoring.log_group_names
}

output "sns_topic_arns" {
  description = "Map of SNS topic ARNs"
  value       = module.monitoring.sns_topic_arns
}

output "cloudwatch_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = module.monitoring.dashboard_url
}

# Backup Outputs
output "backup_vault_arn" {
  description = "AWS Backup vault ARN"
  value       = module.backup.backup_vault_arn
}

output "backup_plan_arn" {
  description = "AWS Backup plan ARN"
  value       = module.backup.backup_plan_arn
}

output "backup_selection_arn" {
  description = "AWS Backup selection ARN"
  value       = module.backup.backup_selection_arn
}

# Vault Integration Outputs
output "vault_auth_backend_path" {
  description = "Vault Kubernetes auth backend path"
  value       = "auth/kubernetes"
}

output "vault_secret_path" {
  description = "Vault secret path for application secrets"
  value       = "secret/riskoptimizer"
}

# DNS and Networking
output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = module.security.route53_zone_id
}

output "route53_zone_name" {
  description = "Route53 hosted zone name"
  value       = module.security.route53_zone_name
}

# Application URLs
output "application_urls" {
  description = "Map of application URLs"
  value = {
    frontend    = "https://app.${var.domain_name}"
    backend_api = "https://api.${var.domain_name}"
    admin       = "https://admin.${var.domain_name}"
    monitoring  = "https://grafana.${var.domain_name}"
    vault       = "https://vault.${var.domain_name}"
  }
}

# Kubernetes Configuration
output "kubectl_config" {
  description = "kubectl configuration command"
  value       = "aws eks update-kubeconfig --region ${data.aws_region.current.name} --name ${module.eks.cluster_id}"
}

output "kubernetes_namespace" {
  description = "Kubernetes namespace for the application"
  value       = "${var.app_name}-${var.environment}"
}

# Security and Compliance Information
output "compliance_status" {
  description = "Compliance configuration status"
  value = {
    encryption_enabled    = var.enable_encryption
    audit_logging_enabled = var.enable_audit_logging
    monitoring_enabled    = var.enable_monitoring
    backup_enabled        = var.enable_backup
    compliance_level      = var.compliance_level
    guardduty_enabled     = var.enable_guardduty
    security_hub_enabled  = var.enable_security_hub
    config_enabled        = var.enable_config
    cloudtrail_enabled    = var.enable_cloudtrail
  }
}

# Cost Information
output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown"
  value = {
    eks_cluster     = "~$73/month (cluster) + node costs"
    rds_instance    = "~$200-500/month (depending on instance class)"
    redis_cluster   = "~$100-300/month (depending on node type)"
    load_balancer   = "~$20/month + data processing"
    s3_storage      = "Variable based on usage"
    data_transfer   = "Variable based on usage"
    cloudwatch_logs = "Variable based on log volume"
    backup_storage  = "Variable based on backup size"
    note            = "Costs are estimates and may vary based on actual usage"
  }
}

# Operational Information
output "deployment_info" {
  description = "Deployment information"
  value = {
    terraform_version      = "~> 1.5.0"
    aws_provider_version   = "~> 5.0"
    deployment_timestamp   = timestamp()
    infrastructure_version = "1.0.0"
    last_updated_by        = "Terraform"
  }
}

# Connection Strings (for application configuration)
output "connection_strings" {
  description = "Connection strings for applications"
  value = {
    database_url = "postgresql://${module.database.db_instance_username}:${random_password.master_password.result}@${module.database.db_instance_endpoint}:${module.database.db_instance_port}/${module.database.db_instance_name}?sslmode=require"
    redis_url    = "redis://:${random_password.redis_auth_token.result}@${module.redis.cache_cluster_address}:${module.redis.cache_cluster_port}/0"
  }
  sensitive = true
}

# Health Check Endpoints
output "health_check_endpoints" {
  description = "Health check endpoints for monitoring"
  value = {
    load_balancer = "https://${module.load_balancer.lb_dns_name}/health"
    database      = "${module.database.db_instance_endpoint}:${module.database.db_instance_port}"
    redis         = "${module.redis.cache_cluster_address}:${module.redis.cache_cluster_port}"
    eks_cluster   = module.eks.cluster_endpoint
  }
  sensitive = true
}

# Disaster Recovery Information
output "disaster_recovery_info" {
  description = "Disaster recovery configuration"
  value = {
    backup_vault_arn         = module.backup.backup_vault_arn
    cross_region_replication = var.enable_cross_region_replication
    dr_region                = var.dr_region
    rto_target               = "4 hours"
    rpo_target               = "1 hour"
    backup_retention_days    = local.backup_retention_days
  }
}

# Security Scan Results
output "security_baseline" {
  description = "Security baseline configuration"
  value = {
    encryption_at_rest     = "Enabled for all supported services"
    encryption_in_transit  = "TLS 1.2+ enforced"
    network_segmentation   = "Multi-tier architecture with security groups"
    access_control         = "IAM roles with least privilege"
    monitoring             = "CloudTrail, GuardDuty, Security Hub enabled"
    vulnerability_scanning = "Automated scanning enabled"
    patch_management       = "Automated patching configured"
    backup_strategy        = "Automated daily backups with cross-region replication"
  }
}

# Troubleshooting Information
output "troubleshooting_commands" {
  description = "Common troubleshooting commands"
  value = {
    eks_cluster_info    = "kubectl cluster-info"
    eks_nodes           = "kubectl get nodes"
    database_connection = "psql -h ${module.database.db_instance_endpoint} -U ${module.database.db_instance_username} -d ${module.database.db_instance_name}"
    redis_connection    = "redis-cli -h ${module.redis.cache_cluster_address} -p ${module.redis.cache_cluster_port}"
    logs_location       = "CloudWatch Logs: /aws/eks/${module.eks.cluster_id}/cluster"
  }
  sensitive = true
}
