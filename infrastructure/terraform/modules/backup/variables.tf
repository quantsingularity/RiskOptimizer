variable "environment" {
  description = "Environment name"
  type        = string
}

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "name_prefix" {
  description = "Name prefix for resources"
  type        = string
}

variable "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  type        = string
  default     = null
}

variable "backup_vault_name" {
  description = "Name of the AWS Backup vault"
  type        = string
}

variable "backup_role_arn" {
  description = "ARN of the backup IAM role"
  type        = string
  default     = null
}

variable "backup_plans" {
  description = "Map of backup plan configurations"
  type = map(object({
    schedule                          = string
    start_window                      = number
    completion_window                 = number
    delete_after                      = number
    copy_action_destination_vault_arn = optional(string, null)
  }))
  default = {}
}

variable "backup_resources" {
  description = "List of resource ARNs to backup"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
