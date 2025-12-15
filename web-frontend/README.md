# RiskOptimizer Web Frontend

## Overview

This is the fully-implemented web frontend for the RiskOptimizer platform - an AI-powered portfolio risk management system.

## Prerequisites

- Node.js 16+
- npm 8+

## Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Update .env with your API URL if different from default
```

## Development

```bash
# Start development server (runs on port 3000)
npm run dev

# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
web-frontend/
├── src/
│   ├── components/          # Reusable React components
│   │   ├── dashboard/       # Dashboard-specific components
│   │   ├── navigation/      # Header, Sidebar, Footer
│   │   └── common/          # Common shared components
│   ├── pages/               # Page components (routes)
│   │   ├── Dashboard.jsx
│   │   ├── PortfolioManagement.jsx
│   │   ├── RiskAnalysis.jsx
│   │   ├── Optimization.jsx
│   │   ├── Settings.jsx
│   │   ├── Login.jsx
│   │   └── NotFound.jsx
│   ├── context/             # React Context providers
│   │   ├── AuthContext.jsx
│   │   ├── PortfolioContext.jsx
│   │   └── RiskAnalysisContext.jsx
│   ├── services/            # API services
│   │   └── apiService.js
│   ├── utils/               # Utility functions
│   │   ├── formatters.js
│   │   └── validators.js
│   ├── hooks/               # Custom React hooks
│   ├── styles/              # Global styles
│   ├── App.jsx              # Main application component
│   └── index.jsx            # Application entry point
├── __tests__/               # Test files
├── public/                  # Static assets
├── .env.example             # Environment variables template
├── vite.config.js           # Vite configuration
├── vitest.config.js         # Vitest configuration
└── package.json             # Dependencies and scripts
```

## Key Features Implemented

### 1. Authentication

- Login/logout functionality
- Protected routes
- Session management with localStorage

### 2. Dashboard

- Real-time portfolio value display
- Performance metrics and charts
- Risk indicators
- Asset allocation visualization
- Recent transactions

### 3. Portfolio Management

- Add/edit/delete assets
- View portfolio composition
- Track gains/losses
- Real-time value calculations

### 4. Risk Analysis

- Value at Risk (VaR) calculations
- Stress testing scenarios
- Correlation analysis
- Risk contribution metrics

### 5. Portfolio Optimization

- Multiple optimization methods (Sharpe ratio, min risk, target return)
- Efficient frontier visualization
- Rebalancing recommendations
- Constraint management

### 6. Settings

- User preferences
- Notification settings
- Risk tolerance configuration
- Account management

## API Integration

The frontend integrates with the backend API at `http://localhost:5000` by default.

### API Endpoints Used

- **Auth**: `/api/v1/auth/*`
- **Portfolio**: `/api/v1/portfolios/*`
- **Risk**: `/api/v1/risk/*`
- **Optimization**: `/api/v1/optimization/*`
- **Market Data**: `/api/v1/market/*`

## Testing

The project includes comprehensive test coverage:

- **Unit Tests**: Component and utility function tests
- **Integration Tests**: API service and context tests
- **Test Framework**: Vitest + React Testing Library

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

## Technologies Used

- **React 18**: UI framework
- **Material-UI (MUI)**: Component library
- **React Router v6**: Routing
- **React Query**: Data fetching and caching
- **Axios**: HTTP client
- **Vite**: Build tool
- **Vitest**: Testing framework
- **@mui/x-charts**: Data visualization

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Optimization

- Code splitting with React.lazy
- Image optimization
- Tree shaking
- Minification in production builds
- Caching strategies

## Troubleshooting

### Build Issues

If you encounter build issues:

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear vite cache
rm -rf node_modules/.vite
```

### API Connection Issues

1. Ensure backend is running on port 5000
2. Check CORS configuration in backend
3. Verify API_URL in .env file

### Test Failures

```bash
# Clear test cache
npm run test -- --clearCache

# Run specific test file
npm test -- src/__tests__/specific-test.test.js
```

## Contributing

1. Create a feature branch
2. Make changes
3. Write/update tests
4. Ensure all tests pass
5. Submit pull request

## License

MIT License - see LICENSE file for details
