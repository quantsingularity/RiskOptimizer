# Contributing to RiskOptimizer

Thank you for considering contributing to RiskOptimizer! This document provides guidelines and instructions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow project guidelines

## Getting Started

1. **Fork the repository**

```bash
# On GitHub, click "Fork" button
```

2. **Clone your fork**

```bash
git clone https://github.com/quantsingularity/RiskOptimizer.git
cd RiskOptimizer
```

3. **Set up development environment**

```bash
./scripts/setup_dev_environment.sh
```

4. **Create a branch**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

## Development Workflow

### 1. Install Pre-commit Hooks

```bash
pre-commit install
```

### 2. Make Changes

- Write code following our standards
- Add tests for new functionality
- Update documentation

### 3. Run Tests

```bash
# All tests
./scripts/run_tests.sh

# Specific component
./scripts/run_tests.sh -c backend --coverage
```

### 4. Check Code Quality

```bash
./scripts/code_quality.sh
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new risk calculation method"

# Commit message format:
# <type>: <description>
#
# Types: feat, fix, docs, style, refactor, test, chore
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Code Style

**Follow PEP 8** with these tools:

- `black` for formatting
- `flake8` for linting
- `isort` for import sorting
- `pylint` for static analysis

```python
# Example: Good code style
from typing import List, Optional

import numpy as np
from riskoptimizer.core.logging import get_logger

logger = get_logger(__name__)


class RiskCalculator:
    """Calculate portfolio risk metrics."""

    def __init__(self, confidence: float = 0.95) -> None:
        """Initialize calculator with confidence level."""
        self.confidence = confidence

    def calculate_var(self, returns: List[float]) -> float:
        """
        Calculate Value at Risk.

        Args:
            returns: List of historical returns

        Returns:
            VaR value at configured confidence level
        """
        if not returns:
            raise ValueError("Returns list cannot be empty")

        var = np.percentile(returns, (1 - self.confidence) * 100)
        logger.info(f"Calculated VaR: {var:.4f}")
        return var
```

**Key principles:**

- Type hints for function arguments and return values
- Docstrings for all public methods (Google style)
- Meaningful variable names
- Keep functions small and focused
- Handle errors appropriately
- Log important operations

### JavaScript/TypeScript Style

**Use ESLint and Prettier:**

```javascript
// Example: Good React component
import React, { useState, useEffect } from "react";
import { calculateVaR } from "../services/apiService";

/**
 * Portfolio risk display component.
 */
export const RiskMetrics = ({ portfolioId }) => {
  const [var95, setVar95] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRisk = async () => {
      setLoading(true);
      try {
        const result = await calculateVaR(portfolioId, 0.95);
        setVar95(result.var);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchRisk();
  }, [portfolioId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h3>Value at Risk (95%)</h3>
      <p>{var95?.toFixed(4)}</p>
    </div>
  );
};
```

## Testing

### Writing Tests

**Backend tests (pytest):**

```python
# tests/test_risk_service.py
import pytest
from riskoptimizer.domain.services.risk_service import risk_service


class TestRiskService:
    """Test risk calculation service."""

    def test_calculate_var_valid_input(self):
        """Test VaR calculation with valid returns."""
        returns = [-0.02, 0.01, -0.015, 0.03, -0.01]
        var = risk_service.calculate_var(returns, confidence=0.95)

        assert var < 0  # VaR should be negative
        assert isinstance(var, (int, float))

    def test_calculate_var_empty_returns(self):
        """Test VaR calculation with empty returns raises error."""
        with pytest.raises(ValidationError):
            risk_service.calculate_var([], confidence=0.95)

    def test_calculate_var_invalid_confidence(self):
        """Test VaR calculation with invalid confidence."""
        returns = [-0.02, 0.01]
        with pytest.raises(ValidationError):
            risk_service.calculate_var(returns, confidence=1.5)
```

**Frontend tests (Jest):**

```javascript
// __tests__/RiskMetrics.test.jsx
import { render, screen, waitFor } from "@testing-library/react";
import { RiskMetrics } from "../components/RiskMetrics";
import * as apiService from "../services/apiService";

jest.mock("../services/apiService");

describe("RiskMetrics", () => {
  it("displays VaR value when loaded", async () => {
    apiService.calculateVaR.mockResolvedValue({ var: -0.0234 });

    render(<RiskMetrics portfolioId={1} />);

    await waitFor(() => {
      expect(screen.getByText(/-0.0234/)).toBeInTheDocument();
    });
  });

  it("displays error message on failure", async () => {
    apiService.calculateVaR.mockRejectedValue(new Error("API Error"));

    render(<RiskMetrics portfolioId={1} />);

    await waitFor(() => {
      expect(screen.getByText(/Error: API Error/)).toBeInTheDocument();
    });
  });
});
```

### Test Coverage

Maintain **85%+ test coverage:**

```bash
./scripts/run_tests.sh --coverage
```

## Pull Request Process

1. **Update documentation** for any changed functionality
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Run code quality checks**
5. **Update CHANGELOG.md** with your changes
6. **Create PR** with clear description:

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

How was this tested?

## Checklist

- [ ] Tests pass
- [ ] Code follows style guide
- [ ] Documentation updated
```

## Documentation

Update documentation for:

- New features
- API changes
- Configuration options
- Usage examples

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add diagrams where helpful
- Keep table of contents updated
- Test all code examples

### Where to Update

| Change Type          | Files to Update                               |
| -------------------- | --------------------------------------------- |
| New API endpoint     | `docs/API.md`, `docs/USAGE.md`                |
| New CLI command      | `docs/CLI.md`                                 |
| Configuration option | `docs/CONFIGURATION.md`                       |
| New feature          | `docs/FEATURE_MATRIX.md`, `docs/CHANGELOG.md` |
| Architecture change  | `docs/ARCHITECTURE.md`                        |

## Release Process

Maintainers will:

1. Review and merge PR
2. Update version number
3. Tag release
4. Deploy to environments
5. Announce release

## Questions?

- Open an issue for discussion
- Join discussions on GitHub
- Check existing documentation
