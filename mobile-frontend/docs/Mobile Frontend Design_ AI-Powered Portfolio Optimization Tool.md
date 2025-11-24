## Mobile Frontend Design: AI-Powered Portfolio Optimization Tool

### 1. Overview

This document outlines the design for the mobile frontend of the AI-Powered Portfolio Optimization Tool. The goal is to create a modern, advanced, and intuitive application for both Android and iOS platforms, leveraging the existing backend API.

### 2. Technology Stack

- **Framework:** React Native (chosen for potential synergy with the existing React web frontend and cross-platform capabilities).
- **UI Library:** Consider using a library like React Native Elements, NativeBase, or React Native Paper for pre-built components and styling consistency.
- **Navigation:** React Navigation for handling screen transitions and navigation patterns (bottom tabs, stacks, modals).
- **State Management:** React Context API (as used in the web frontend) or potentially Redux/Zustand if complexity increases.
- **Charting:** A React Native compatible charting library (e.g., react-native-chart-kit, victory-native) for visualizing performance, risk metrics, and market data.

### 3. Key Features & Screens

The mobile app will mirror the core functionalities of the web application, adapted for a mobile experience.

**3.1. Authentication:**

- **Login Screen:** Email and password input, login button, link to registration (if applicable), potentially options for biometric login (Face ID/Touch ID) after initial login.
- **Registration Screen:** (If supported by API) Form for user registration.

**3.2. Main Navigation (Bottom Tab Bar):**

- **Dashboard:** Overview of the user's total portfolio value, overall performance, risk score, and quick access to key actions or insights.
- **Portfolios:** List of user portfolios, ability to navigate to details or create new ones.
- **Optimize:** Access to the portfolio optimization tool.
- **Market:** Browse or search for market data and asset information.
- **Settings:** User profile, preferences, security settings, logout.

**3.3. Dashboard Screen:**

- Display total portfolio value and overall change (e.g., 24h, 1w).
- Summary cards for key metrics (e.g., overall risk, top performing asset).
- Quick links to view portfolios or run optimization.
- Potentially a simplified performance chart.

**3.4. Portfolios Section:**

- **Portfolio List Screen:** Cards displaying each portfolio's name, total value, and perhaps a mini-chart or risk indicator. Floating action button (+) to create a new portfolio.
- **Portfolio Detail Screen:**
    - Header with portfolio name, value, currency.
    - Tabs or sections for:
        - **Overview:** Key metrics (risk score, performance summary).
        - **Assets:** List of assets (symbol, name, quantity, value, allocation %). Ability to tap an asset to view more details or navigate to Market Data screen. Button to add a new asset.
        - **Performance:** Detailed performance charts (daily, weekly, monthly, yearly, etc.).
        - **Risk:** Link to navigate to the detailed Risk Analysis screen for this portfolio.
        - **Transactions:** Link to view blockchain transaction history for this portfolio.
- **Create/Edit Portfolio Screen:** Form to input name, description, currency.
- **Add Asset Screen:** Form to search/input asset symbol, quantity, purchase price, purchase date.

**3.5. Optimization Section:**

- **Optimization Setup Screen:** Select portfolio, define risk tolerance, investment horizon, and any constraints (using sliders, dropdowns, input fields).
- **Optimization Results Screen:** Display recommended allocations, actions (buy/sell), expected return, optimized risk score, Sharpe ratio. Visualize the Efficient Frontier chart.

**3.6. Market Section:**

- **Market Overview/Search Screen:** Display trending assets or allow searching by symbol/name.
- **Asset Detail Screen:** Display asset name, symbol, current price, historical price chart (with selectable periods/intervals), key stats.

**3.7. Settings Section:**

- **Profile Screen:** View/Edit user name, email.
- **Preferences Screen:** Set risk tolerance, investment horizon defaults.
- **Security Screen:** Change password, manage biometric login.
- **Logout Button.**

**3.8. Blockchain Integration:**

- **Transaction History Screen:** Display list of blockchain transactions related to a portfolio (tx hash, timestamp, action, asset, quantity, value, status).
- **Verification Status:** Display portfolio integrity verification status (potentially on Portfolio Detail screen).

### 4. UI/UX Considerations

- **Mobile-First:** Design specifically for smaller screens and touch interaction.
- **Clarity:** Present financial data clearly and concisely. Use appropriate charts and visualizations.
- **Responsiveness:** Ensure layouts adapt well to different screen sizes and orientations (primarily portrait).
- **Performance:** Optimize for smooth navigation and fast loading times, especially for charts and large data lists.
- **Feedback:** Provide clear visual feedback for user actions (loading indicators, success/error messages).
- **Accessibility:** Follow accessibility guidelines (e.g., sufficient color contrast, font sizes, touch target sizes).

### 5. API Integration

- Implement authentication flow using JWT (store tokens securely using AsyncStorage or secure storage).
- Create service functions (similar to `apiService.js` in the web frontend) to interact with all required API endpoints.
- Handle API errors gracefully and provide informative messages to the user.

### 6. Next Steps

- Set up the React Native development environment.
- Begin implementing the core structure (navigation, basic screens).
- Implement authentication.
- Develop components for each feature, integrating with the API.
