resource "aws_eks_cluster" "main" {
  name     = "${var.name_prefix}-eks"
  role_arn = var.cluster_role_arn
  version  = var.cluster_version

  vpc_config {
    subnet_ids              = var.control_plane_subnet_ids
    endpoint_public_access  = false
    endpoint_private_access = true
    security_group_ids      = []
  }

  enabled_cluster_log_types = var.cluster_enabled_log_types

  dynamic "encryption_config" {
    for_each = var.cluster_encryption_config
    content {
      resources = encryption_config.value.resources
      provider {
        key_arn = encryption_config.value.provider_key_arn
      }
    }
  }

  tags = merge(var.tags, {
    Name        = "${var.name_prefix}-eks"
    Environment = var.environment
  })
}

resource "aws_eks_node_group" "main" {
  for_each = var.node_groups

  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.name_prefix}-${each.key}"
  node_role_arn   = var.node_group_role_arn
  subnet_ids      = var.subnet_ids

  instance_types = try(each.value.instance_types, ["m5.large"])
  capacity_type  = try(each.value.capacity_type, "ON_DEMAND")

  scaling_config {
    min_size     = try(each.value.min_size, 1)
    max_size     = try(each.value.max_size, 5)
    desired_size = try(each.value.desired_size, 2)
  }

  update_config {
    max_unavailable = 1
  }

  dynamic "taint" {
    for_each = try(each.value.taints, [])
    content {
      key    = taint.value.key
      value  = taint.value.value
      effect = taint.value.effect
    }
  }

  labels = try(each.value.labels, {})

  tags = merge(var.tags, {
    Name        = "${var.name_prefix}-${each.key}-node-group"
    Environment = var.environment
  })

  lifecycle {
    ignore_changes = [scaling_config[0].desired_size]
  }
}

resource "aws_eks_addon" "addons" {
  for_each = var.cluster_addons

  cluster_name             = aws_eks_cluster.main.name
  addon_name               = each.key
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = merge(var.tags, {
    Environment = var.environment
  })

  depends_on = [aws_eks_node_group.main]
}
