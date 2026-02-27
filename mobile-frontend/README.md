# RiskOptimizer Mobile Frontend

Mobile application for RiskOptimizer - AI-Powered Portfolio Risk Management Platform.

## Overview

This is a React Native mobile application built with Expo that provides a mobile interface for the RiskOptimizer platform. It allows users to manage investment portfolios, analyze risk, optimize allocations, and monitor market data on the go.

## Features

- **Authentication**: Secure login with JWT token management
- **Dashboard**: Overview of portfolio performance and key metrics
- **Portfolio Management**: Create, view, and manage investment portfolios
- **Asset Management**: Add and track individual assets within portfolios
- **Risk Analysis**: View risk metrics and perform stress testing
- **Portfolio Optimization**: Get AI-powered optimization recommendations
- **Market Data**: Real-time market data and asset search
- **Blockchain Integration**: Transaction history and portfolio integrity verification
- **Theme Support**: Light/Dark mode with system preference detection

## Technology Stack

- **Framework**: React Native with Expo SDK 50
- **Navigation**: React Navigation 6.x (Native Stack + Bottom Tabs)
- **UI Library**: React Native Elements (@rneui/themed)
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Storage**: Expo SecureStore (for tokens), AsyncStorage (for preferences)
- **Testing**: Jest + React Native Testing Library

## Prerequisites

- Node.js >= 18
- npm or yarn
- Expo CLI (optional, but recommended)
- For iOS: Mac with Xcode
- For Android: Android Studio with SDK

## Installation

1. **Clone and navigate to the mobile-frontend directory**

   ```bash
   cd mobile-frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Configure environment variables**
   Copy `.env.example` to `.env` and update with your backend URL:

   ```bash
   cp .env.example .env
   ```

   Edit `.env`:

   ```
   API_BASE_URL=http://localhost:5000/api/v1
   ```

   For physical device testing, replace `localhost` with your computer's IP address:

   ```
   API_BASE_URL=http://192.168.1.XXX:5000/api/v1
   ```

## Running the Application

### Development Mode

Start the Expo development server:

```bash
npm start
```

This will open Expo Dev Tools in your browser. From there you can:

- Press `a` to open on Android emulator
- Press `i` to open on iOS simulator
- Scan QR code with Expo Go app on physical device

### Platform-Specific Commands

**Android**:

```bash
npm run android
```

**iOS** (Mac only):

```bash
npm run ios
```

**Web** (experimental):

```bash
npm run web
```

## Testing

### Run all tests

```bash
npm test
```

### Run tests in watch mode

```bash
npm run test:watch
```

### Generate coverage report

```bash
npm run test:coverage
```

## Running with Backend

### Start the Backend Server

1. Navigate to the backend directory:

   ```bash
   cd ../backend
   ```

2. Install backend dependencies (if not already done):

   ```bash
   pip install -r requirements.txt
   ```

3. Configure backend environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your database and configuration settings
   ```

4. Initialize the database:

   ```bash
   python -m riskoptimizer.infrastructure.database.init_db
   ```

5. Start the backend server:

   ```bash
   python app.py
   ```

   The backend should start on `http://localhost:5000`

### Connect Mobile App to Backend

1. Ensure the mobile app's `.env` file has the correct `API_BASE_URL`
2. For emulator: Use `http://localhost:5000/api/v1` (Android) or `http://localhost:5000/api/v1` (iOS)
3. For physical device: Use `http://YOUR_COMPUTER_IP:5000/api/v1`

## Project Structure

```
mobile-frontend/
├── src/
│   ├── context/          # React Context providers (Auth, Theme)
│   ├── navigation/       # Navigation configuration
│   ├── screens/          # Screen components
│   │   ├── Auth/        # Login and authentication screens
│   │   ├── Dashboard/   # Dashboard and overview
│   │   ├── Market/      # Market data and search
│   │   ├── Optimize/    # Optimization and risk analysis
│   │   ├── Portfolios/  # Portfolio management screens
│   │   └── Settings/    # App settings
│   ├── services/        # API service layer
│   ├── styles/          # Theme and style configurations
│   └── utils/           # Utility functions
├── __tests__/           # Test files
├── assets/              # Images, fonts, and other assets
├── App.js               # Application entry point
├── app.json             # Expo configuration
├── package.json         # Dependencies and scripts
└── README.md           # This file
```

## API Integration

The mobile app communicates with the backend via REST API. Key endpoints:

### Authentication

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - User logout

### Portfolios

- `GET /api/v1/portfolios` - List user portfolios
- `POST /api/v1/portfolios` - Create portfolio
- `GET /api/v1/portfolios/:id` - Get portfolio details
- `PUT /api/v1/portfolios/:id` - Update portfolio
- `DELETE /api/v1/portfolios/:id` - Delete portfolio
- `POST /api/v1/portfolios/:id/assets` - Add asset to portfolio

### Risk & Optimization

- `GET /api/v1/risk/metrics/:portfolioId` - Get risk metrics
- `POST /api/v1/risk/optimize` - Get optimization recommendations
- `POST /api/v1/risk/var/:portfolioId` - Calculate Value at Risk
- `POST /api/v1/risk/stress-test/:portfolioId` - Perform stress test

### Market Data

- `GET /api/v1/market/search` - Search for assets
- `GET /api/v1/market/history/:symbol` - Get price history
- `GET /api/v1/market/overview` - Get market overview

## Development Notes

### Simulation Mode

The app includes simulation/fallback mode for market data when the backend is unavailable. This allows frontend development to continue without a fully running backend for market data endpoints.

### Theme Customization

The app uses React Native Elements with custom theme configuration. Theme can be modified in `src/styles/theme.js`.

### Adding New Screens

1. Create screen component in appropriate `src/screens/` subdirectory
2. Add route in `src/navigation/AppNavigator.js`
3. Update navigation typing if using TypeScript

## Troubleshooting

### Common Issues

**1. "Unable to connect to server"**

- Verify backend is running on the correct port
- Check `API_BASE_URL` in `.env`
- For physical devices, use computer's IP instead of localhost
- Ensure firewall allows connections on port 5000

**2. "Metro bundler failed to start"**

- Clear Metro cache: `npx expo start -c`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

**3. "Build failed" on Android**

- Ensure Android SDK is properly installed
- Check `ANDROID_HOME` environment variable
- Run `npx expo prebuild` to regenerate native folders if needed

**4. Tests failing**

- Clear Jest cache: `npm test -- --clearCache`
- Ensure all dependencies are installed
- Check mock implementations in `jest.setup.js`

### Getting Help

- Check the main project repository: [github.com/quantsingularity/RiskOptimizer](https://github.com/quantsingularity/RiskOptimizer)
- Review Expo documentation: [docs.expo.dev](https://docs.expo.dev)
- React Native Elements docs: [reactnativeelements.com](https://reactnativeelements.com)

## Building for Production

### Android APK

```bash
eas build --platform android --profile preview
```

### iOS IPA

```bash
eas build --platform ios --profile preview
```

Note: Requires Expo Application Services (EAS) configuration. See [Expo EAS Build docs](https://docs.expo.dev/build/introduction/) for setup.

## Contributing

1. Create a feature branch
2. Make your changes
3. Add/update tests
4. Ensure tests pass: `npm test`
5. Submit a pull request

## License

This project is part of the RiskOptimizer platform. See the main repository for license information.
