# RiskOptimizer Backend API Documentation

## Overview

The RiskOptimizer backend is a comprehensive financial risk management and portfolio optimization system built with FastAPI, Celery, and modern Python technologies. It provides asynchronous task processing for computationally intensive financial calculations, real-time monitoring, and scalable architecture.

## Architecture

### System Components

1. **API Layer** - FastAPI-based REST API
2. **Task Queue** - Celery with Redis broker for asynchronous processing
3. **Database** - PostgreSQL for persistent data storage
4. **Cache** - Redis for caching and session management
5. **Monitoring** - Prometheus metrics and Grafana dashboards
6. **Authentication** - JWT-based authentication with RBAC

### Key Features

- **Asynchronous Risk Calculations**: Monte Carlo simulations, VaR/CVaR calculations
- **Portfolio Optimization**: Multiple optimization algorithms (Mean-Variance, Risk Parity, etc.)
- **Performance Analysis**: Comprehensive portfolio performance metrics
- **Report Generation**: Automated PDF and Excel report generation
- **Real-time Monitoring**: System health checks and performance metrics
- **Scalable Architecture**: Kubernetes-ready with horizontal scaling

## Installation and Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15+
- Redis 7+

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/abrar2030/RiskOptimizer.git
   cd RiskOptimizer/code/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r tests/requirements-test.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start services with Docker Compose**
   ```bash
   docker-compose up -d postgres redis
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the application**
   ```bash
   # Start API server
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   
   # Start Celery worker (in another terminal)
   celery -A tasks.celery_app worker --loglevel=info
   
   # Start Celery beat scheduler (in another terminal)
   celery -A tasks.celery_app beat --loglevel=info
   ```

### Docker Deployment

1. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Flower (Celery monitoring): http://localhost:5555
   - Grafana: http://localhost:3000

### Kubernetes Deployment

1. **Apply Kubernetes manifests**
   ```bash
   kubectl apply -f deployment/kubernetes.yaml
   ```

2. **Configure ingress and SSL**
   ```bash
   # Update ingress configuration for your domain
   kubectl apply -f deployment/ingress.yaml
   ```

## API Documentation

### Authentication

All API endpoints require authentication using JWT tokens.

```bash
# Login to get access token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}'

# Use token in subsequent requests
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/portfolios"
```

### Core Endpoints

#### Portfolio Management
- `GET /api/v1/portfolios` - List portfolios
- `POST /api/v1/portfolios` - Create portfolio
- `GET /api/v1/portfolios/{id}` - Get portfolio details
- `PUT /api/v1/portfolios/{id}` - Update portfolio
- `DELETE /api/v1/portfolios/{id}` - Delete portfolio

#### Risk Analysis
- `POST /api/v1/tasks/risk/monte-carlo` - Start Monte Carlo simulation
- `POST /api/v1/tasks/risk/var-cvar` - Calculate VaR/CVaR
- `POST /api/v1/tasks/risk/stress-test` - Run stress tests
- `POST /api/v1/tasks/risk/efficient-frontier` - Calculate efficient frontier

#### Portfolio Optimization
- `POST /api/v1/tasks/portfolio/optimize` - Optimize portfolio allocation
- `POST /api/v1/tasks/portfolio/rebalance` - Calculate rebalancing transactions
- `POST /api/v1/tasks/portfolio/performance-analysis` - Analyze performance

#### Task Management
- `GET /api/v1/tasks/{task_id}/status` - Get task status
- `GET /api/v1/tasks/{task_id}/result` - Get task result
- `DELETE /api/v1/tasks/{task_id}` - Cancel task
- `GET /api/v1/tasks/active` - List active tasks

#### Monitoring
- `GET /api/v1/monitoring/health` - System health check
- `GET /api/v1/monitoring/performance` - Performance metrics
- `GET /api/v1/monitoring/system` - System resource usage

### Example API Usage

#### Monte Carlo Simulation

```python
import requests

# Start Monte Carlo simulation
response = requests.post(
    "http://localhost:8000/api/v1/tasks/risk/monte-carlo",
    headers={"Authorization": "Bearer <token>"},
    json={
        "portfolio_data": {
            "weights": [0.4, 0.3, 0.3],
            "historical_returns": [[0.01, 0.02, -0.01], ...]
        },
        "num_simulations": 10000,
        "time_horizon": 252
    }
)

task_id = response.json()["data"]["task_id"]

# Check task status
status_response = requests.get(
    f"http://localhost:8000/api/v1/tasks/{task_id}/status",
    headers={"Authorization": "Bearer <token>"}
)

# Get results when complete
if status_response.json()["data"]["status"] == "SUCCESS":
    result_response = requests.get(
        f"http://localhost:8000/api/v1/tasks/{task_id}/result",
        headers={"Authorization": "Bearer <token>"}
    )
    results = result_response.json()["data"]["result"]
```

#### Portfolio Optimization

```python
# Optimize portfolio allocation
response = requests.post(
    "http://localhost:8000/api/v1/tasks/portfolio/optimize",
    headers={"Authorization": "Bearer <token>"},
    json={
        "assets_data": {
            "returns": [[0.01, 0.02, 0.015], ...],
            "asset_names": ["Stock_A", "Stock_B", "Bond_A"]
        },
        "optimization_params": {
            "method": "mean_variance",
            "target_return": 0.08,
            "max_weight_per_asset": 0.4
        }
    }
)
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/riskoptimizer

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Security
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# External APIs
MARKET_DATA_API_KEY=your-api-key
```

### Application Configuration

The application uses a hierarchical configuration system:

1. **Default settings** in `config.py`
2. **Environment-specific** settings in `config/{environment}.py`
3. **Environment variables** override file settings

## Task Processing

### Celery Configuration

The application uses Celery for asynchronous task processing with the following queues:

- **default**: General tasks
- **risk_calculations**: Monte Carlo, VaR/CVaR calculations
- **portfolio_operations**: Optimization, rebalancing
- **report_generation**: PDF/Excel report generation
- **maintenance**: System maintenance tasks

### Task Types

#### Risk Calculation Tasks
- `monte_carlo_simulation`: Run Monte Carlo simulations
- `calculate_var_cvar`: Calculate Value at Risk and Conditional VaR
- `efficient_frontier_calculation`: Calculate efficient frontier
- `stress_test_portfolio`: Run portfolio stress tests

#### Portfolio Management Tasks
- `optimize_portfolio`: Optimize portfolio allocation
- `rebalance_portfolio`: Calculate rebalancing transactions
- `analyze_portfolio_performance`: Comprehensive performance analysis

#### Report Generation Tasks
- `generate_portfolio_report`: Generate PDF portfolio reports
- `generate_risk_report`: Generate risk analysis reports
- `export_portfolio_data`: Export data to Excel/CSV

#### Maintenance Tasks
- `cleanup_expired_tasks`: Clean up old task results
- `update_market_data`: Update market data from external sources
- `cache_warmup`: Warm up frequently accessed cache entries
- `system_health_check`: Comprehensive system health check

### Task Monitoring

Monitor task execution using:

1. **Flower**: Web-based Celery monitoring at http://localhost:5555
2. **API endpoints**: Task status and result endpoints
3. **Prometheus metrics**: Task execution metrics
4. **Grafana dashboards**: Visual monitoring dashboards

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Exclude slow tests

# Run with coverage
pytest --cov=. --cov-report=html

# Run performance tests
pytest -m slow --benchmark-only
```

### Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_risk_tasks.py       # Risk calculation task tests
├── test_portfolio_tasks.py  # Portfolio management task tests
├── test_integration.py      # Integration tests
├── requirements-test.txt    # Test dependencies
└── performance/
    └── locustfile.py        # Load testing configuration
```

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Load and stress testing
- **Security Tests**: Security vulnerability testing

## Monitoring and Observability

### Metrics Collection

The application exposes Prometheus metrics at `/metrics`:

- **Request metrics**: Response times, error rates
- **Task metrics**: Task execution times, queue lengths
- **System metrics**: CPU, memory, disk usage
- **Business metrics**: Portfolio calculations, user activity

### Health Checks

Multiple health check endpoints:

- `/health`: Basic application health
- `/health/detailed`: Comprehensive health check
- `/api/v1/monitoring/system`: System resource usage
- `/api/v1/monitoring/database`: Database health

### Logging

Structured JSON logging with:

- **Request ID tracking**: Trace requests across services
- **Contextual information**: User, portfolio, task details
- **Performance metrics**: Response times, query performance
- **Error tracking**: Detailed error information

### Alerting

Configure alerts for:

- **High error rates**: > 5% error rate
- **Slow response times**: > 1 second average
- **Queue buildup**: > 100 pending tasks
- **Resource usage**: > 80% CPU/memory usage
- **Failed tasks**: > 10% task failure rate

## Security

### Authentication and Authorization

- **JWT tokens**: Stateless authentication
- **Role-based access control**: User, manager, admin roles
- **Token refresh**: Automatic token renewal
- **Session management**: Secure session handling

### Security Headers

- **CORS**: Cross-origin resource sharing configuration
- **CSP**: Content Security Policy headers
- **HSTS**: HTTP Strict Transport Security
- **Rate limiting**: Request rate limiting per user/IP

### Data Protection

- **Input validation**: Comprehensive input sanitization
- **SQL injection protection**: Parameterized queries
- **XSS protection**: Output encoding
- **Encryption**: Sensitive data encryption at rest

### Security Scanning

Regular security scans using:

- **OWASP ZAP**: Web application security testing
- **Bandit**: Python security linting
- **Safety**: Dependency vulnerability scanning
- **Trivy**: Container image scanning

## Performance Optimization

### Caching Strategy

Multi-level caching:

1. **Application cache**: In-memory caching for frequently accessed data
2. **Redis cache**: Distributed caching for computed results
3. **Database query cache**: Query result caching
4. **CDN cache**: Static asset caching

### Database Optimization

- **Connection pooling**: Efficient database connections
- **Query optimization**: Optimized database queries
- **Indexing**: Strategic database indexing
- **Read replicas**: Read-only database replicas

### Task Optimization

- **Queue prioritization**: Priority-based task queues
- **Result caching**: Cache expensive computation results
- **Batch processing**: Batch similar tasks together
- **Resource limits**: Memory and CPU limits per task

## Troubleshooting

### Common Issues

#### Task Queue Issues

```bash
# Check Celery worker status
celery -A tasks.celery_app inspect active

# Check queue lengths
celery -A tasks.celery_app inspect reserved

# Purge queue
celery -A tasks.celery_app purge
```

#### Database Issues

```bash
# Check database connections
SELECT * FROM pg_stat_activity;

# Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC;
```

#### Cache Issues

```bash
# Check Redis status
redis-cli ping

# Check cache hit rate
redis-cli info stats

# Clear cache
redis-cli flushall
```

### Performance Issues

1. **High response times**
   - Check database query performance
   - Review cache hit rates
   - Monitor system resources

2. **Task queue buildup**
   - Scale Celery workers
   - Optimize task execution
   - Check for failed tasks

3. **Memory usage**
   - Monitor task memory consumption
   - Implement result streaming for large datasets
   - Optimize data structures

### Debugging

Enable debug mode for detailed error information:

```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

Use application logs for troubleshooting:

```bash
# View application logs
docker-compose logs api

# View worker logs
docker-compose logs worker

# View real-time logs
docker-compose logs -f
```

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes** and add tests
4. **Run tests**: `pytest`
5. **Run linting**: `flake8 . && black . && isort .`
6. **Commit changes**: `git commit -m "Add new feature"`
7. **Push branch**: `git push origin feature/new-feature`
8. **Create pull request**

### Code Standards

- **PEP 8**: Python code style guidelines
- **Type hints**: Use type annotations
- **Docstrings**: Document all functions and classes
- **Test coverage**: Maintain > 90% test coverage
- **Security**: Follow OWASP guidelines

### Pull Request Process

1. **Update documentation** for any API changes
2. **Add tests** for new functionality
3. **Update changelog** with changes
4. **Ensure CI passes** all checks
5. **Request review** from maintainers

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- **Documentation**: https://docs.riskoptimizer.com
- **Issues**: https://github.com/abrar2030/RiskOptimizer/issues
- **Discussions**: https://github.com/abrar2030/RiskOptimizer/discussions
- **Email**: support@riskoptimizer.com

