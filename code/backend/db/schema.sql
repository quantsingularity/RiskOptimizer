-- Portfolio Metadata
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_address VARCHAR(42) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Asset Allocations
CREATE TABLE allocations (
    portfolio_id INTEGER REFERENCES portfolios(id),
    asset_symbol VARCHAR(10) NOT NULL,
    percentage DECIMAL(5,2) CHECK (percentage >= 0 AND percentage <= 100),
    PRIMARY KEY (portfolio_id, asset_symbol)
);