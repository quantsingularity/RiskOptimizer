output "backup_vault_arn" {
  description = "ARN of the backup vault"
  value       = aws_backup_vault.main.arn
}

output "backup_vault_name" {
  description = "Name of the backup vault"
  value       = aws_backup_vault.main.name
}

output "backup_plan_arns" {
  description = "ARNs of the backup plans"
  value       = { for k, v in aws_backup_plan.plans : k => v.arn }
}
