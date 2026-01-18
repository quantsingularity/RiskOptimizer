# Troubleshooting Guide

Common issues and their solutions for RiskOptimizer.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Database Issues](#database-issues)
- [API Issues](#api-issues)
- [Authentication Issues](#authentication-issues)
- [Performance Issues](#performance-issues)
- [Blockchain Issues](#blockchain-issues)
- [Frontend Issues](#frontend-issues)

## Installation Issues

### Issue: Python version incompatible

**Symptoms:**

```
ERROR: This package requires Python 3.8+
```

**Solution:**

```bash
# Check Python version
python --version

# Install Python 3.10 (Ubuntu)
sudo apt-get install python3.10 python3.10-venv

# Use specific Python version
python3.10 -m venv venv
```

---

### Issue: pip install fails

**Symptoms:**

```
ERROR: Could not find a version that satisfies the requirement...
```

**Solution:**

```bash
# Upgrade pip
pip install --upgrade pip

# Install with --no-cache-dir
pip install --no-cache-dir -r requirements.txt

# If specific package fails, try installing separately
pip install numpy scipy pandas
pip install -r requirements.txt
```

---

### Issue: Module not found after installation

**Symptoms:**

```
ModuleNotFoundError: No module named 'riskoptimizer'
```

**Solution:**

```bash
cd code/backend
pip install -e .
```

## Database Issues

### Issue: Database connection failed

**Symptoms:**

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Solution 1: Use SQLite for development**

```bash
# Add to .env
DB_USE_SQLITE=true
SQLITE_DB_PATH=riskoptimizer.db
```

**Solution 2: Fix PostgreSQL connection**

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Verify credentials in .env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=riskoptimizer
DB_USER=postgres
DB_PASSWORD=your_password
```

---

###Issue: Database tables not created

**Symptoms:**

```
sqlalchemy.exc.ProgrammingError: relation "users" does not exist
```

**Solution:**

```bash
cd code/backend
python -c "from riskoptimizer.infrastructure.database.session import init_db; init_db()"
```

## API Issues

### Issue: Port already in use

**Symptoms:**

```
OSError: [Errno 48] Address already in use
```

**Solution:**

```bash
# Find process using port
lsof -ti:5000

# Kill process
kill -9 $(lsof -ti:5000)

# Or use different port
API_PORT=5001 python app.py
```

---

### Issue: CORS errors in browser

**Symptoms:**

```
Access to XMLHttpRequest... has been blocked by CORS policy
```

**Solution:**

```bash
# Add to .env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Or allow all (development only)
CORS_ORIGINS=*
```

---

### Issue: 429 Too Many Requests

**Symptoms:**

```
{"status": "error", "error": {"code": "RATE_LIMIT_EXCEEDED"}}
```

**Solution:**

```bash
# Increase rate limit in .env
RATE_LIMIT_PER_MINUTE=120

# Or wait 60 seconds before retrying
```

## Authentication Issues

### Issue: JWT token invalid

**Symptoms:**

```
{"status": "error", "error": {"code": "INVALID_TOKEN"}}
```

**Solution:**

1. Check token hasn't expired (1 hour default)
2. Use refresh token to get new access token
3. Ensure `JWT_SECRET_KEY` is consistent across restarts
4. Clear old tokens and re-login

```bash
curl -X POST http://localhost:5000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

---

### Issue: Password validation fails

**Symptoms:**

```
{"status": "error", "error": {"code": "VALIDATION_ERROR", "field": "password"}}
```

**Requirements:**

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character

**Solution:**
Use a stronger password, e.g., `SecureP@ss123`

## Performance Issues

### Issue: Slow API responses

**Symptoms:**

- Responses taking >1 second
- Database queries timing out

**Solutions:**

**1. Enable Redis caching:**

```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
redis-server

# Configure in .env
REDIS_HOST=localhost
REDIS_PORT=6379
```

**2. Increase database connection pool:**

```bash
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

**3. Use production database:**

```bash
DB_USE_SQLITE=false
# Configure PostgreSQL
```

---

### Issue: High memory usage

**Symptoms:**

- Application crashes with `MemoryError`
- System becomes slow

**Solutions:**

**1. Reduce Celery workers:**

```bash
celery -A riskoptimizer.tasks.celery_app worker --concurrency=2
```

**2. Limit request size:**

```bash
MAX_CONTENT_LENGTH=8388608  # 8MB instead of 16MB
```

**3. Close unused connections:**

```bash
DB_POOL_RECYCLE=1800  # Recycle every 30 minutes
```

## Blockchain Issues

### Issue: Web3 connection failed

**Symptoms:**

```
web3.exceptions.ProviderConnectionError: Could not connect to Ethereum node
```

**Solution:**

```bash
# For local development, start Hardhat node
cd code/blockchain
npx hardhat node

# Update .env
BLOCKCHAIN_PROVIDER_URL=http://localhost:8545
```

---

### Issue: Transaction failed

**Symptoms:**

```
ValueError: insufficient funds for gas * price + value
```

**Solutions:**

**1. Check account balance**
**2. Reduce gas limit:**

```bash
GAS_LIMIT=300000  # Instead of 500000
```

**3. Use testnet faucet to get test ETH**

## Frontend Issues

### Issue: npm install fails

**Symptoms:**

```
npm ERR! code ERESOLVE
```

**Solution:**

```bash
# Clear cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Or use --legacy-peer-deps
npm install --legacy-peer-deps
```

---

### Issue: Frontend not connecting to API

**Symptoms:**

- Network errors in browser console
- API calls fail

**Solution:**

**1. Check API is running:**

```bash
curl http://localhost:5000/health
```

**2. Update API URL in frontend:**

```javascript
// In .env or config file
REACT_APP_API_URL=http://localhost:5000/api/v1
```

**3. Check CORS configuration:**

```bash
# In backend .env
CORS_ORIGINS=http://localhost:3000
```

## Docker Issues

### Issue: Docker Compose fails to start

**Symptoms:**

```
ERROR: for backend  Cannot start service backend: ...
```

**Solutions:**

**1. Check Docker is running:**

```bash
docker --version
docker-compose --version
```

**2. Rebuild containers:**

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**3. Check logs:**

```bash
docker-compose logs backend
```

**4. Remove old volumes:**

```bash
docker-compose down -v
docker-compose up -d
```

## General Troubleshooting Tips

1. **Check logs:**

```bash
# Backend logs
tail -f logs/app.log

# Docker logs
docker-compose logs -f backend
```

2. **Verify environment variables:**

```bash
# Print loaded config
cd code/backend
python -c "from riskoptimizer.core.config import config; print(config.database.url)"
```

3. **Test API health:**

```bash
curl http://localhost:5000/health
```

4. **Clear cache:**

```bash
# Redis
redis-cli FLUSHDB

# Python cache
find . -type d -name __pycache__ -exec rm -r {} +
```

5. **Run tests:**

```bash
./scripts/run_tests.sh -c backend
```

## Getting Help

If issues persist:

1. **Check GitHub Issues:** https://github.com/quantsingularity/RiskOptimizer/issues
2. **Search documentation:** Use Ctrl+F in docs
3. **Enable debug logging:**

```bash
DEBUG=true python app.py
```

4. **Create minimal reproduction** and report issue
5. **Include:**
    - Error message
    - Steps to reproduce
    - Environment (OS, Python version, etc.)
    - Relevant logs

## See Also

- [INSTALLATION.md](INSTALLATION.md) - Installation guide
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration options
- [API.md](API.md) - API documentation
