output "application_log_group_name" {
  description = "Name of the application CloudWatch log group"
  value       = aws_cloudwatch_log_group.application.name
}

output "security_log_group_name" {
  description = "Name of the security CloudWatch log group"
  value       = aws_cloudwatch_log_group.security.name
}

output "alerts_topic_arn" {
  description = "ARN of the SNS alerts topic"
  value       = aws_sns_topic.alerts.arn
}
