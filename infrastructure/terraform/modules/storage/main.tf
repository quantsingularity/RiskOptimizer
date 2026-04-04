resource "aws_s3_bucket" "buckets" {
  for_each = var.buckets
  bucket   = "${var.name_prefix}-${each.key}"

  tags = merge(var.tags, {
    Name        = "${var.name_prefix}-${each.key}"
    Environment = var.environment
  })
}

resource "aws_s3_bucket_versioning" "buckets" {
  for_each = var.buckets
  bucket   = aws_s3_bucket.buckets[each.key].id

  versioning_configuration {
    status = each.value.versioning_enabled ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "buckets" {
  for_each = var.buckets
  bucket   = aws_s3_bucket.buckets[each.key].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_key_arn != null ? "aws:kms" : "AES256"
      kms_master_key_id = var.kms_key_arn
    }
    bucket_key_enabled = var.kms_key_arn != null ? true : false
  }
}

resource "aws_s3_bucket_public_access_block" "buckets" {
  for_each                = var.buckets
  bucket                  = aws_s3_bucket.buckets[each.key].id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "buckets" {
  for_each = {
    for k, v in var.buckets : k => v if length(v.lifecycle_rules) > 0
  }
  bucket = aws_s3_bucket.buckets[each.key].id

  dynamic "rule" {
    for_each = each.value.lifecycle_rules
    content {
      id     = rule.value.id
      status = rule.value.status

      dynamic "transition" {
        for_each = try(rule.value.transition, [])
        content {
          days          = transition.value.days
          storage_class = transition.value.storage_class
        }
      }

      dynamic "expiration" {
        for_each = try(rule.value.expiration, [])
        content {
          days = expiration.value.days
        }
      }
    }
  }

  depends_on = [aws_s3_bucket_versioning.buckets]
}

resource "aws_s3_bucket_policy" "buckets" {
  for_each = var.buckets
  bucket   = aws_s3_bucket.buckets[each.key].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyNonTLS"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          "${aws_s3_bucket.buckets[each.key].arn}",
          "${aws_s3_bucket.buckets[each.key].arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      },
      {
        Sid       = "DenyWeakTLS"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          "${aws_s3_bucket.buckets[each.key].arn}",
          "${aws_s3_bucket.buckets[each.key].arn}/*"
        ]
        Condition = {
          NumericLessThan = {
            "s3:TlsVersion" = "1.2"
          }
        }
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.buckets]
}
