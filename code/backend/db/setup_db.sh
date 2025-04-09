#!/bin/bash

# Create database schema
echo "Creating database schema..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install it first."
    exit 1
fi

# Create database if it doesn't exist
echo "Creating database if it doesn't exist..."
psql -U postgres -c "SELECT 1 FROM pg_database WHERE datname = 'riskoptimizer'" | grep -q 1 || psql -U postgres -c "CREATE DATABASE riskoptimizer"

# Apply schema
echo "Applying schema..."
psql -U postgres -d riskoptimizer -f schema.sql

echo "Database setup complete!"
