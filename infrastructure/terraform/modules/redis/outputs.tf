output "cache_cluster_address" {
  description = "Primary endpoint address of the Redis cluster"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
}

output "cache_cluster_port" {
  description = "Port of the Redis cluster"
  value       = var.port
}

output "replication_group_id" {
  description = "ID of the replication group"
  value       = aws_elasticache_replication_group.main.id
}

output "reader_endpoint_address" {
  description = "Reader endpoint address for read replicas"
  value       = aws_elasticache_replication_group.main.reader_endpoint_address
}
