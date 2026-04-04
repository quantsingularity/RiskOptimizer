output "bucket_names" {
  description = "Map of bucket names"
  value       = { for k, v in aws_s3_bucket.buckets : k => v.bucket }
}

output "bucket_arns" {
  description = "Map of bucket ARNs"
  value       = { for k, v in aws_s3_bucket.buckets : k => v.arn }
}

output "bucket_ids" {
  description = "Map of bucket IDs"
  value       = { for k, v in aws_s3_bucket.buckets : k => v.id }
}
