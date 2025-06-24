# HashiCorp Vault Configuration

# Vault server configuration for production deployment
storage "consul" {
  address = "127.0.0.1:8500"
  path    = "vault/"
  
  # Enable TLS for Consul communication
  scheme = "https"
  tls_ca_file = "/opt/vault/tls/consul-ca.pem"
  tls_cert_file = "/opt/vault/tls/consul-cert.pem"
  tls_key_file = "/opt/vault/tls/consul-key.pem"
}

# High availability configuration
ha_storage "consul" {
  address = "127.0.0.1:8500"
  path    = "vault/"
  
  scheme = "https"
  tls_ca_file = "/opt/vault/tls/consul-ca.pem"
  tls_cert_file = "/opt/vault/tls/consul-cert.pem"
  tls_key_file = "/opt/vault/tls/consul-key.pem"
}

# Listener configuration with TLS
listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/opt/vault/tls/vault-cert.pem"
  tls_key_file  = "/opt/vault/tls/vault-key.pem"
  tls_min_version = "tls12"
  tls_cipher_suites = "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384"
}

# Seal configuration using AWS KMS for auto-unseal
seal "awskms" {
  region     = "us-west-2"
  kms_key_id = "alias/vault-unseal-key"
}

# API address for cluster communication
api_addr = "https://vault.riskoptimizer.com:8200"
cluster_addr = "https://vault.riskoptimizer.com:8201"

# UI configuration
ui = true

# Logging configuration
log_level = "INFO"
log_format = "json"

# Telemetry for monitoring
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = true
}

# Maximum lease TTL
max_lease_ttl = "768h"
default_lease_ttl = "168h"

# Disable mlock for containerized environments (adjust for production)
disable_mlock = false

# Plugin directory
plugin_directory = "/opt/vault/plugins"

