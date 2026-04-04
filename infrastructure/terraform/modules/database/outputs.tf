output "db_instance_endpoint" {
  description = "Endpoint of the database instance"
  value       = aws_db_instance.main.endpoint
}

output "db_instance_arn" {
  description = "ARN of the database instance"
  value       = aws_db_instance.main.arn
}

output "db_instance_port" {
  description = "Port of the database instance"
  value       = aws_db_instance.main.port
}

output "db_instance_id" {
  description = "ID of the database instance"
  value       = aws_db_instance.main.id
}

output "db_name" {
  description = "Name of the database"
  value       = aws_db_instance.main.db_name
}

output "db_username" {
  description = "Master username of the database"
  value       = aws_db_instance.main.username
  sensitive   = true
}

output "db_subnet_group_name" {
  description = "Name of the DB subnet group"
  value       = aws_db_subnet_group.main.name
}
