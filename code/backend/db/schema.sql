
-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    wallet_address VARCHAR(42) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Portfolio Metadata
CREATE TABLE IF NOT EXISTS portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_address VARCHAR(42) NOT NULL, -- For backward compatibility, consider removing if not strictly needed
    name VARCHAR(255) NOT NULL DEFAULT 'Default Portfolio',
    description TEXT,
    total_value NUMERIC(18, 4) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Asset Allocations
CREATE TABLE IF NOT EXISTS allocations (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    asset_symbol VARCHAR(20) NOT NULL,
    asset_name VARCHAR(255),
    percentage NUMERIC(10, 4) NOT NULL CHECK (percentage >= 0 AND percentage <= 100),
    amount NUMERIC(18, 4),
    current_price NUMERIC(18, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (portfolio_id, asset_symbol)
);

-- Risk Assessments
CREATE TABLE IF NOT EXISTS risk_assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) NOT NULL,
    confidence_level NUMERIC(5, 4),
    time_horizon INTEGER,
    value_at_risk NUMERIC(18, 4),
    conditional_var NUMERIC(18, 4),
    expected_return NUMERIC(18, 4),
    volatility NUMERIC(18, 4),
    sharpe_ratio NUMERIC(18, 4),
    max_drawdown NUMERIC(18, 4),
    beta NUMERIC(18, 4),
    alpha NUMERIC(18, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Market Data
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date TIMESTAMP NOT NULL,
    open_price NUMERIC(18, 4),
    high_price NUMERIC(18, 4),
    low_price NUMERIC(18, 4),
    close_price NUMERIC(18, 4) NOT NULL,
    volume NUMERIC(18, 4),
    adjusted_close NUMERIC(18, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (symbol, date)
);

-- Optimization Results
CREATE TABLE IF NOT EXISTS optimization_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    portfolio_id INTEGER NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    optimization_type VARCHAR(50) NOT NULL,
    objective_value NUMERIC(18, 4),
    expected_return NUMERIC(18, 4),
    expected_volatility NUMERIC(18, 4),
    sharpe_ratio NUMERIC(18, 4),
    weights TEXT, -- JSON string of asset weights
    constraints TEXT, -- JSON string of constraints used
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task Results
CREATE TABLE IF NOT EXISTS task_results (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL,
    result TEXT,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Log Table for Financial Transactions and Key Actions
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action_type VARCHAR(100) NOT NULL, -- e.g., 'PORTFOLIO_CREATE', 'ASSET_ADD', 'LOGIN_SUCCESS', 'LOGIN_FAILURE'
    entity_type VARCHAR(100), -- e.g., 'PORTFOLIO', 'USER', 'ALLOCATION'
    entity_id INTEGER, -- ID of the entity affected
    details JSONB, -- JSONB for flexible storage of action details (e.g., old_value, new_value, IP address)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
