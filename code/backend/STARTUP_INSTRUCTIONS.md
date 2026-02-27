# RiskOptimizer Backend - Startup Instructions

## Prerequisites

- Python 3.8 or higher (tested with Python 3.12)
- pip (Python package manager)
- Virtual environment support

## Installation and Startup

### 1. Create Virtual Environment

```bash
cd /path/to/backend
python3 -m venv .venv
```

### 2. Activate Virtual Environment

**Linux/Mac:**

```bash
source .venv/bin/activate
```

**Windows:**

```cmd
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -e .
```

### 4. Configure Environment

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

**IMPORTANT:** For production use, you MUST generate secure keys:

```bash
# Generate SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate DATA_ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print('DATA_ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
```

Update these values in your `.env` file.

### 5. Start the Application

**Development Mode (Flask built-in server):**

```bash
python app.py
```

**Production Mode (using Gunicorn):**

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:app"
```

The server will start on `http://0.0.0.0:5000`

### 6. Verify Installation

**Test health endpoint:**

```bash
curl http://127.0.0.1:5000/health
```

**Expected response:**

```json
{
  "cache": true,
  "database": true,
  "status": "ok",
  "version": "1.0.0"
}
```

**Test root endpoint:**

```bash
curl http://127.0.0.1:5000/
```

**Expected response:**

```json
{
  "documentation": "/apidocs/",
  "name": "RiskOptimizer API",
  "version": "1.0.0"
}
```

**Access API Documentation:**
Open browser to: `http://127.0.0.1:5000/apidocs/`

## Configuration Notes

### Database

By default, the application uses **SQLite** for local development (configured via `DB_USE_SQLITE=true` in `.env`). The database file will be created as `riskoptimizer.db` in the backend directory.

To use PostgreSQL instead:

1. Set `DB_USE_SQLITE=false` in `.env`
2. Configure PostgreSQL connection parameters:
   - `DB_HOST`
   - `DB_PORT`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`

### Redis/Caching

The application will attempt to connect to Redis for caching. If Redis is not available, it automatically falls back to an **in-memory cache** for development purposes. This is suitable for testing but not recommended for production.

To use Redis:

1. Install and start Redis locally or use a remote Redis instance
2. Configure Redis connection in `.env`:
   - `REDIS_HOST`
   - `REDIS_PORT`
   - `REDIS_DB`
   - `REDIS_PASSWORD` (if authentication is enabled)

### AI Models

The application references an AI optimization model file. If this file is not present, the application will start successfully but AI optimization features will be unavailable. A warning will be logged at startup.

To enable AI features:

1. Train an optimization model using the training scripts in `/code/ai_models/training_scripts/`
2. Place the trained model file at the path specified by `MODEL_PATH` in `.env`, or at the default location: `/code/ai_models/optimization_model.pkl`

## Troubleshooting

### Import Errors

If you encounter module import errors:

```bash
# Ensure the package is installed in editable mode
pip install -e .
```

### Database Connection Errors

If SQLite is enabled but you see connection errors:

- Ensure the backend directory is writable
- Check that `DB_USE_SQLITE=true` is set in `.env`

### Port Already in Use

If port 5000 is already in use, change it in `.env`:

```
API_PORT=8000
```

Then restart the application.

### Missing Dependencies

If you see import errors for specific packages:

```bash
# Reinstall all requirements
pip install -r requirements.txt
```

## Production Deployment

For production deployment, consider:

1. **Use Gunicorn or uWSGI** instead of Flask's development server
2. **Enable HTTPS** with a reverse proxy (nginx, Apache)
3. **Use PostgreSQL** instead of SQLite
4. **Set up Redis** for caching and session storage
5. **Configure proper logging** (see logging configuration in code)
6. **Set DEBUG_MODE=false** in environment
7. **Use strong, randomly generated keys** for all security parameters
8. **Set up proper monitoring** (the app includes Prometheus metrics endpoints)

## Additional Resources

- API Documentation: Available at `/apidocs/` when server is running
- Main README: See `README.md` for overall project documentation
- Configuration reference: See `.env.example` for all available configuration options
