resource "aws_backup_vault" "main" {
  name        = var.backup_vault_name
  kms_key_arn = var.kms_key_arn

  tags = merge(var.tags, {
    Name        = var.backup_vault_name
    Environment = var.environment
  })
}

resource "aws_backup_vault_lock_configuration" "main" {
  backup_vault_name   = aws_backup_vault.main.name
  changeable_for_days = var.environment == "production" ? 3 : null
  min_retention_days  = 7
  max_retention_days  = 2555
}

resource "aws_backup_plan" "plans" {
  for_each = var.backup_plans
  name     = "${var.name_prefix}-backup-plan-${each.key}"

  rule {
    rule_name         = each.key
    target_vault_name = aws_backup_vault.main.name
    schedule          = each.value.schedule
    start_window      = each.value.start_window
    completion_window = each.value.completion_window

    lifecycle {
      delete_after = each.value.delete_after
    }

    dynamic "copy_action" {
      for_each = each.value.copy_action_destination_vault_arn != null ? [1] : []
      content {
        destination_vault_arn = each.value.copy_action_destination_vault_arn
        lifecycle {
          delete_after = each.value.delete_after
        }
      }
    }
  }

  tags = merge(var.tags, {
    Name        = "${var.name_prefix}-backup-plan-${each.key}"
    Environment = var.environment
  })
}

resource "aws_backup_selection" "resources" {
  for_each     = length(var.backup_resources) > 0 ? var.backup_plans : {}
  name         = "${var.name_prefix}-backup-selection-${each.key}"
  iam_role_arn = var.backup_role_arn
  plan_id      = aws_backup_plan.plans[each.key].id

  resources = var.backup_resources
}
