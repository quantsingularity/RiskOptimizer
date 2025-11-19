# Firewall Configuration for RiskOptimizer Infrastructure

## UFW (Uncomplicated Firewall) Rules

# Default policies
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw default deny forward

# SSH access (restrict to management networks)
ufw allow from 10.0.0.0/8 to any port 22 proto tcp comment 'SSH from management network'
ufw allow from 172.16.0.0/12 to any port 22 proto tcp comment 'SSH from private network'
ufw allow from 192.168.0.0/16 to any port 22 proto tcp comment 'SSH from local network'

# HTTP/HTTPS for web services
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Vault access (restrict to application networks)
ufw allow from 10.0.0.0/8 to any port 8200 proto tcp comment 'Vault API'
ufw allow from 172.16.0.0/12 to any port 8200 proto tcp comment 'Vault API'

# Database access (restrict to application servers)
ufw allow from 10.0.1.0/24 to any port 5432 proto tcp comment 'PostgreSQL from app servers'
ufw allow from 10.0.1.0/24 to any port 3306 proto tcp comment 'MySQL from app servers'

# Redis access (restrict to application servers)
ufw allow from 10.0.1.0/24 to any port 6379 proto tcp comment 'Redis from app servers'

# Kubernetes API server
ufw allow from 10.0.0.0/8 to any port 6443 proto tcp comment 'Kubernetes API'

# Kubernetes node communication
ufw allow from 10.0.0.0/8 to any port 10250 proto tcp comment 'Kubelet API'
ufw allow from 10.0.0.0/8 to any port 10251 proto tcp comment 'kube-scheduler'
ufw allow from 10.0.0.0/8 to any port 10252 proto tcp comment 'kube-controller-manager'

# etcd communication
ufw allow from 10.0.0.0/8 to any port 2379:2380 proto tcp comment 'etcd'

# Monitoring and logging
ufw allow from 10.0.2.0/24 to any port 9090 proto tcp comment 'Prometheus'
ufw allow from 10.0.2.0/24 to any port 3000 proto tcp comment 'Grafana'
ufw allow from 10.0.2.0/24 to any port 9200 proto tcp comment 'Elasticsearch'
ufw allow from 10.0.2.0/24 to any port 5601 proto tcp comment 'Kibana'

# Application-specific ports
ufw allow from 10.0.1.0/24 to any port 8080 proto tcp comment 'Application backend'
ufw allow from 10.0.1.0/24 to any port 8000 proto tcp comment 'Application API'

# Deny all other traffic
ufw --force enable

# Rate limiting for SSH
ufw limit ssh comment 'Rate limit SSH connections'

# Logging
ufw logging on
