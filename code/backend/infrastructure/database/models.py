from datetime import datetime
from typing import List

from riskoptimizer.infrastructure.database.session import Base
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        Numeric, String, Text)
from sqlalchemy.orm import relationship


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    wallet_address = Column(String(42), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String(50), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    portfolios = relationship(
        "Portfolio", back_populates="user", cascade="all, delete-orphan"
    )
    risk_assessments = relationship(
        "RiskAssessment", back_populates="user", cascade="all, delete-orphan"
    )


class Portfolio(Base):
    """Portfolio model for storing user portfolio data."""

    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_address = Column(
        String(42), index=True, nullable=False
    )  # For backward compatibility
    name = Column(String(255), nullable=False, default="Default Portfolio")
    description = Column(Text)
    total_value = Column(
        Numeric(precision=18, scale=4), default=0.0
    )  # Changed from Float to Numeric
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="portfolios")
    allocations = relationship(
        "Allocation", back_populates="portfolio", cascade="all, delete-orphan"
    )
    risk_assessments = relationship(
        "RiskAssessment", back_populates="portfolio", cascade="all, delete-orphan"
    )


class Allocation(Base):
    """Allocation model for storing asset allocations within a portfolio."""

    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    asset_symbol = Column(String(20), nullable=False)
    asset_name = Column(String(255))
    percentage = Column(
        Numeric(precision=10, scale=4), nullable=False
    )  # Changed from Float to Numeric
    amount = Column(Numeric(precision=18, scale=4))  # Changed from Float to Numeric
    current_price = Column(
        Numeric(precision=18, scale=4)
    )  # Changed from Float to Numeric
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="allocations")


class RiskAssessment(Base):
    """Risk assessment model for storing risk calculation results."""

    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    assessment_type = Column(
        String(50), nullable=False
    )  # e.g., \'var\', \'cvar\', \'sharpe\'
    confidence_level = Column(
        Numeric(precision=5, scale=4)
    )  # Changed from Float to Numeric
    time_horizon = Column(Integer)  # in days
    value_at_risk = Column(
        Numeric(precision=18, scale=4)
    )  # Changed from Float to Numeric
    conditional_var = Column(
        Numeric(precision=18, scale=4)
    )  # Changed from Float to Numeric
    expected_return = Column(
        Numeric(precision=18, scale=4)
    )  # Changed from Float to Numeric
    volatility = Column(Numeric(precision=18, scale=4))  # Changed from Float to Numeric
    sharpe_ratio = Column(
        Numeric(precision=18, scale=4)
    )  # Changed from Float to Numeric
    max_drawdown = Column(
        Numeric(precision=18, scale=4)
    )  # Changed from Float to Numeric
    beta = Column(Numeric(precision=18, scale=4))  # Changed from Float to Numeric
    alpha = Column(Numeric(precision=18, scale=4))  # Changed from Float to Numeric
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="risk_assessments")
    portfolio = relationship("Portfolio", back_populates="risk_assessments")


class MarketData(Base):
    """Market data model for storing historical price data."""

    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    open_price = Column(Numeric(precision=18, scale=4))  # Changed from Float to Numeric
    high_price = Column(Numeric(precision=18, scale=4))  # Changed from Float to Numeric
    low_price = Column(Numeric(precision=18, scale=4))  # Changed from Float to Numeric
    close_price = Column(
        Numeric(precision=18, scale=4), nullable=False
    )  # Changed from Float to Numeric
    volume = Column(Numeric(precision=18, scale=4))  # Changed from Float to Numeric
    adjusted_close = Column(
        Numeric(precision=18, scale=4)
    )  # Changed from Float to Numeric
    created_at = Column(DateTime, default=datetime.utcnow)

    # Composite index for symbol and date
    __table_args__ = {"extend_existing": True}


class OptimizationResult(Base):
    """Optimization result model for storing portfolio optimization results."""

    __tablename__ = "optimization_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    optimization_type = Column(
        String(50), nullable=False
    )  # e.g., \'max_sharpe\', \'min_variance\'
    objective_value = Column(
        Numeric(precision=18, scale=4)
    )  # Changed from Float to Numeric
    expected_return = Column(
        Numeric(precision=18, scale=4)
    )  # Changed from Float to Numeric
    expected_volatility = Column(
        Numeric(precision=18, scale=4)
    )  # Changed from Float to Numeric
    sharpe_ratio = Column(
        Numeric(precision=18, scale=4)
    )  # Changed from Float to Numeric
    weights = Column(Text)  # JSON string of asset weights
    constraints = Column(Text)  # JSON string of constraints used
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    portfolio = relationship("Portfolio")


class TaskResult(Base):
    """Task result model for storing background task results."""

    __tablename__ = "task_results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True, nullable=False)
    task_type = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(
        String(50), nullable=False
    )  # \'pending\', \'running\', \'success\', \'failure\'
    result = Column(Text)  # JSON string of task result
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
