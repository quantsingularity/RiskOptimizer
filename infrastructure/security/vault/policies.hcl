# Vault Policies for RiskOptimizer

## Admin Policy
path "auth/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

path "sys/auth/*" {
  capabilities = ["create", "update", "delete", "sudo"]
}

path "sys/auth" {
  capabilities = ["read"]
}

path "sys/policies/acl/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

path "sys/policies/acl" {
  capabilities = ["list"]
}

path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "sys/mounts/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}

path "sys/mounts" {
  capabilities = ["read"]
}

## Application Policy
path "secret/data/riskoptimizer/app/*" {
  capabilities = ["read"]
}

path "secret/metadata/riskoptimizer/app/*" {
  capabilities = ["list"]
}

path "database/creds/riskoptimizer-app" {
  capabilities = ["read"]
}

path "pki/issue/riskoptimizer-app" {
  capabilities = ["create", "update"]
}

## Database Policy
path "secret/data/riskoptimizer/database/*" {
  capabilities = ["read"]
}

path "database/config/riskoptimizer-db" {
  capabilities = ["read"]
}

path "database/creds/riskoptimizer-db-admin" {
  capabilities = ["read"]
}

## DevOps Policy
path "secret/data/riskoptimizer/devops/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "secret/metadata/riskoptimizer/devops/*" {
  capabilities = ["list"]
}

path "auth/kubernetes/role/riskoptimizer-*" {
  capabilities = ["read", "update"]
}

path "pki/issue/riskoptimizer-devops" {
  capabilities = ["create", "update"]
}

## Audit Policy
path "secret/data/riskoptimizer/audit/*" {
  capabilities = ["read"]
}

path "sys/audit" {
  capabilities = ["read", "list"]
}

path "sys/audit/*" {
  capabilities = ["read", "list"]
}

## Compliance Policy
path "secret/data/riskoptimizer/compliance/*" {
  capabilities = ["read"]
}

path "secret/metadata/riskoptimizer/compliance/*" {
  capabilities = ["list"]
}

path "pki/cert/ca" {
  capabilities = ["read"]
}

path "pki/ca/pem" {
  capabilities = ["read"]
}

