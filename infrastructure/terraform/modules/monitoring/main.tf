resource "aws_cloudwatch_log_group" "application" {
  name              = "/aws/riskoptimizer/${var.environment}/application"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn

  tags = merge(var.tags, {
    Name        = "${var.name_prefix}-app-logs"
    Environment = var.environment
  })
}

resource "aws_cloudwatch_log_group" "security" {
  name              = "/aws/riskoptimizer/${var.environment}/security"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn

  tags = merge(var.tags, {
    Name        = "${var.name_prefix}-security-logs"
    Environment = var.environment
  })
}

resource "aws_sns_topic" "alerts" {
  name              = "${var.name_prefix}-alerts"
  kms_master_key_id = var.kms_key_arn

  tags = merge(var.tags, {
    Name        = "${var.name_prefix}-alerts"
    Environment = var.environment
  })
}

resource "aws_sns_topic_subscription" "alerts" {
  for_each  = { for idx, ep in var.notification_endpoints : idx => ep }
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = each.value.type
  endpoint  = each.value.endpoint
}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.name_prefix}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "CPU utilization is above 80%"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "high_memory" {
  alarm_name          = "${var.name_prefix}-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "CWAgent"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Memory utilization is above 85%"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  tags = var.tags
}

resource "aws_cloudwatch_dashboard" "main" {
  count          = var.create_dashboard ? 1 : 0
  dashboard_name = "${var.name_prefix}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        x    = 0
        y    = 0
        width  = 12
        height = 6
        properties = {
          title  = "CPU Utilization"
          view   = "timeSeries"
          region = "us-west-2"
          metrics = [["AWS/EC2", "CPUUtilization"]]
          period = 300
          stat   = "Average"
        }
      },
      {
        type = "metric"
        x    = 12
        y    = 0
        width  = 12
        height = 6
        properties = {
          title  = "Memory Utilization"
          view   = "timeSeries"
          region = "us-west-2"
          metrics = [["CWAgent", "MemoryUtilization"]]
          period = 300
          stat   = "Average"
        }
      }
    ]
  })
}
