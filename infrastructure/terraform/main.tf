terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    vault = {
      source  = "hashicorp/vault"
      version = "~> 3.20"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }

  backend "s3" {
    # Configure via backend-prod.hcl or environment-specific backend config
    # terraform init -backend-config=backend-prod.hcl
    bucket         = "riskoptimizer-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "riskoptimizer-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = merge(var.default_tags, {
      Environment        = var.environment
      Project            = "RiskOptimizer"
      ManagedBy          = "Terraform"
      SecurityBaseline   = "CIS-AWS-Foundations"
      ComplianceLevel    = var.compliance_level
      DataClassification = "Confidential"
      BackupRequired     = "true"
      MonitoringEnabled  = "true"
    })
  }

  dynamic "assume_role" {
    for_each = var.assume_role_arn != null ? [1] : []
    content {
      role_arn     = var.assume_role_arn
      session_name = "terraform-riskoptimizer"
      external_id  = var.external_id
    }
  }
}

provider "vault" {
  address   = var.vault_address
  namespace = var.vault_namespace

  auth_login {
    path = "auth/aws/login"
    parameters = {
      role = "terraform-riskoptimizer"
    }
  }
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

resource "random_password" "master_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "random_password" "redis_auth_token" {
  length  = 32
  special = false
}

locals {
  account_id  = data.aws_caller_identity.current.account_id
  region      = data.aws_region.current.name
  name_prefix = "${var.app_name}-${var.environment}"

  vpc_cidr = var.vpc_cidr
  azs      = slice(data.aws_availability_zones.available.names, 0, 3)

  enable_encryption = var.environment == "production" ? true : var.enable_encryption
  enable_logging    = true
  enable_monitoring = true

  compliance_tags = {
    "compliance:gdpr"    = "true"
    "compliance:pci-dss" = "true"
    "compliance:sox"     = var.environment == "production" ? "true" : "false"
    "compliance:dora"    = var.environment == "production" ? "true" : "false"
  }

  backup_retention_days = var.environment == "production" ? 2555 : 90
}

module "kms" {
  source = "./modules/kms"

  environment     = var.environment
  app_name        = var.app_name
  name_prefix     = local.name_prefix
  account_id      = local.account_id
  enable_rotation = local.enable_encryption

  tags = merge(var.default_tags, local.compliance_tags)
}

module "network" {
  source = "./modules/network"

  environment           = var.environment
  app_name              = var.app_name
  name_prefix           = local.name_prefix
  vpc_cidr              = local.vpc_cidr
  availability_zones    = local.azs

  public_subnet_cidrs   = var.public_subnet_cidrs
  private_subnet_cidrs  = var.private_subnet_cidrs
  database_subnet_cidrs = var.database_subnet_cidrs

  enable_dns_hostnames = true
  enable_dns_support   = true
  enable_nat_gateway   = true
  single_nat_gateway   = var.environment != "production"
  enable_vpn_gateway   = false

  enable_flow_log                          = true
  flow_log_destination_type                = "cloud-watch-logs"
  flow_log_cloudwatch_log_group_kms_key_id = module.kms.key_arn

  tags = merge(var.default_tags, local.compliance_tags)
}

module "security" {
  source = "./modules/security"

  environment = var.environment
  app_name    = var.app_name
  name_prefix = local.name_prefix
  vpc_id      = module.network.vpc_id
  vpc_cidr    = local.vpc_cidr

  kms_key_arn = module.kms.key_arn

  enable_guardduty    = var.enable_guardduty
  enable_security_hub = var.enable_security_hub
  enable_config       = var.enable_config
  enable_cloudtrail   = var.enable_cloudtrail

  tags = merge(var.default_tags, local.compliance_tags)
}

module "eks" {
  source = "./modules/eks"

  environment = var.environment
  app_name    = var.app_name
  name_prefix = local.name_prefix

  vpc_id                   = module.network.vpc_id
  subnet_ids               = module.network.private_subnet_ids
  control_plane_subnet_ids = module.network.private_subnet_ids

  cluster_version   = var.eks_cluster_version
  cluster_role_arn  = module.security.eks_cluster_role_arn
  node_group_role_arn = module.security.eks_node_group_role_arn

  cluster_encryption_config = [
    {
      provider_key_arn = module.kms.key_arn
      resources        = ["secrets"]
    }
  ]

  cluster_enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  node_groups = {
    main = {
      instance_types = var.eks_node_instance_types
      capacity_type  = "ON_DEMAND"
      min_size       = var.eks_node_group_min_size
      max_size       = var.eks_node_group_max_size
      desired_size   = var.eks_node_group_desired_size
      taints = var.environment == "production" ? [
        {
          key    = "dedicated"
          value  = "riskoptimizer"
          effect = "NO_SCHEDULE"
        }
      ] : []
    }
  }

  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
    aws-ebs-csi-driver = {
      most_recent = true
    }
  }

  tags = merge(var.default_tags, local.compliance_tags)
}

module "database" {
  source = "./modules/database"

  environment = var.environment
  app_name    = var.app_name
  name_prefix = local.name_prefix

  vpc_id     = module.network.vpc_id
  subnet_ids = module.network.database_subnet_ids

  engine         = "postgres"
  engine_version = var.db_engine_version
  db_instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = module.kms.key_arn

  db_name  = var.db_name
  username = var.db_username
  password = random_password.master_password.result

  vpc_security_group_ids = [module.security.database_security_group_id]

  backup_retention_period = local.backup_retention_days
  backup_window           = var.backup_window
  maintenance_window      = var.maintenance_window
  skip_final_snapshot     = var.environment != "production"

  enabled_cloudwatch_logs_exports = ["postgresql"]
  monitoring_interval             = 60
  monitoring_role_arn             = module.security.rds_monitoring_role_arn
  performance_insights_enabled    = var.enable_performance_insights
  performance_insights_kms_key_id = module.kms.key_arn

  multi_az            = var.environment == "production"
  deletion_protection = var.environment == "production"

  tags = merge(var.default_tags, local.compliance_tags)
}

module "redis" {
  source = "./modules/redis"

  environment = var.environment
  app_name    = var.app_name
  name_prefix = local.name_prefix

  vpc_id     = module.network.vpc_id
  subnet_ids = module.network.private_subnet_ids

  node_type            = var.redis_node_type
  num_cache_nodes      = var.redis_num_nodes
  parameter_group_name = "default.redis7"
  port                 = 6379

  security_group_ids         = [module.security.redis_security_group_id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = random_password.redis_auth_token.result
  kms_key_id                 = module.kms.key_arn

  snapshot_retention_limit = var.environment == "production" ? 7 : 1
  snapshot_window          = "03:00-05:00"

  tags = merge(var.default_tags, local.compliance_tags)
}

module "storage" {
  source = "./modules/storage"

  environment = var.environment
  app_name    = var.app_name
  name_prefix = local.name_prefix
  account_id  = local.account_id

  kms_key_arn = module.kms.key_arn

  buckets = {
    application-data = {
      versioning_enabled = true
      lifecycle_rules = [
        {
          id     = "transition_to_ia"
          status = "Enabled"
          transition = [
            { days = 30,  storage_class = "STANDARD_IA" },
            { days = 90,  storage_class = "GLACIER" },
            { days = 365, storage_class = "DEEP_ARCHIVE" }
          ]
          expiration = []
        }
      ]
    }
    backup-data = {
      versioning_enabled = true
      lifecycle_rules = [
        {
          id         = "backup_retention"
          status     = "Enabled"
          transition = []
          expiration = [{ days = local.backup_retention_days }]
        }
      ]
    }
    audit-logs = {
      versioning_enabled = true
      lifecycle_rules = [
        {
          id     = "audit_retention"
          status = "Enabled"
          transition = [{ days = 90, storage_class = "GLACIER" }]
          expiration = [{ days = 2555 }]
        }
      ]
    }
  }

  tags = merge(var.default_tags, local.compliance_tags)
}

module "load_balancer" {
  source = "./modules/load_balancer"

  environment = var.environment
  app_name    = var.app_name
  name_prefix = local.name_prefix

  vpc_id     = module.network.vpc_id
  subnet_ids = module.network.public_subnet_ids

  security_group_ids = [module.security.alb_security_group_id]

  certificate_arn = module.security.acm_certificate_arn
  ssl_policy      = "ELBSecurityPolicy-TLS13-1-2-2021-06"

  access_logs_enabled = true
  access_logs_bucket  = module.storage.bucket_names["audit-logs"]
  access_logs_prefix  = "alb-access-logs"

  target_port = 8080

  tags = merge(var.default_tags, local.compliance_tags)
}

module "monitoring" {
  source = "./modules/monitoring"

  environment = var.environment
  app_name    = var.app_name
  name_prefix = local.name_prefix

  kms_key_arn = module.kms.key_arn

  log_retention_days     = var.environment == "production" ? 2555 : 90
  notification_endpoints = var.notification_endpoints
  create_dashboard       = true

  tags = merge(var.default_tags, local.compliance_tags)
}

module "backup" {
  source = "./modules/backup"

  environment = var.environment
  app_name    = var.app_name
  name_prefix = local.name_prefix

  kms_key_arn       = module.kms.key_arn
  backup_vault_name = "${local.name_prefix}-backup-vault"
  backup_role_arn   = module.security.backup_role_arn

  backup_plans = {
    daily = {
      schedule                          = "cron(0 2 * * ? *)"
      start_window                      = 60
      completion_window                 = 120
      delete_after                      = local.backup_retention_days
      copy_action_destination_vault_arn = var.cross_region_backup_vault_arn
    }
  }

  backup_resources = [
    module.database.db_instance_arn,
  ]

  tags = merge(var.default_tags, local.compliance_tags)
}

resource "vault_generic_secret" "database_credentials" {
  path = "secret/riskoptimizer/database"

  data_json = jsonencode({
    username = var.db_username
    password = random_password.master_password.result
    host     = module.database.db_instance_endpoint
    port     = module.database.db_instance_port
    database = var.db_name
  })
}

resource "vault_generic_secret" "redis_credentials" {
  path = "secret/riskoptimizer/redis"

  data_json = jsonencode({
    host     = module.redis.cache_cluster_address
    port     = module.redis.cache_cluster_port
    password = random_password.redis_auth_token.result
  })
}
