import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useAuth } from '../context/AuthContext';
import { Icon } from '@rneui/themed';

// Import Screens (create placeholder files first)
import LoginScreen from '../screens/Auth/LoginScreen';
import DashboardScreen from '../screens/Dashboard/DashboardScreen';
import PortfolioListScreen from '../screens/Portfolios/PortfolioListScreen';
import PortfolioDetailScreen from '../screens/Portfolios/PortfolioDetailScreen';
import OptimizationScreen from '../screens/Optimize/OptimizationScreen';
import MarketScreen from '../screens/Market/MarketScreen';
import SettingsScreen from '../screens/Settings/SettingsScreen';
import AddAssetScreen from '../screens/Portfolios/AddAssetScreen'; // Placeholder
import CreatePortfolioScreen from '../screens/Portfolios/CreatePortfolioScreen'; // Placeholder
import AssetDetailScreen from '../screens/Portfolios/AssetDetailScreen'; // Placeholder
import RiskAnalysisScreen from '../screens/RiskAnalysisScreen'; // Placeholder
import TransactionHistoryScreen from '../screens/TransactionHistoryScreen'; // Placeholder

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// --- Stack Navigators for each Tab ---

const DashboardStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="DashboardHome" component={DashboardScreen} />
    {/* Add other screens navigable from Dashboard if needed */}
  </Stack.Navigator>
);

const PortfolioStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: true }}>
    <Stack.Screen name="PortfolioList" component={PortfolioListScreen} options={{ title: 'Portfolios' }} />
    <Stack.Screen name="PortfolioDetail" component={PortfolioDetailScreen} options={{ title: 'Portfolio Details' }} />
    <Stack.Screen name="CreatePortfolio" component={CreatePortfolioScreen} options={{ title: 'Create Portfolio' }} />
    <Stack.Screen name="AddAsset" component={AddAssetScreen} options={{ title: 'Add Asset' }} />
    <Stack.Screen name="RiskAnalysis" component={RiskAnalysisScreen} options={{ title: 'Risk Analysis' }} />
    <Stack.Screen name="TransactionHistory" component={TransactionHistoryScreen} options={{ title: 'Transactions' }} />
    {/* AssetDetail might be shared, potentially move to MarketStack or a shared stack */}
    <Stack.Screen name="AssetDetailPortfolio" component={AssetDetailScreen} options={{ title: 'Asset Details' }} />
  </Stack.Navigator>
);

const OptimizationStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="OptimizationHome" component={OptimizationScreen} />
    {/* Add results screen if separate */}
  </Stack.Navigator>
);

const MarketStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: true }}>
    <Stack.Screen name="MarketHome" component={MarketScreen} options={{ title: 'Market Data' }}/>
    <Stack.Screen name="AssetDetailMarket" component={AssetDetailScreen} options={{ title: 'Asset Details' }} />
  </Stack.Navigator>
);

const SettingsStack = () => (
  <Stack.Navigator screenOptions={{ headerShown: false }}>
    <Stack.Screen name="SettingsHome" component={SettingsScreen} />
    {/* Add profile edit, preferences screens etc. */}
  </Stack.Navigator>
);

// --- Bottom Tab Navigator ---

const AppTabs = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      headerShown: false, // Headers are handled by individual stacks
      tabBarIcon: ({ focused, color, size }) => {
        let iconName;
        let iconType = 'material-community'; // Default type

        if (route.name === 'Dashboard') {
          iconName = focused ? 'view-dashboard' : 'view-dashboard-outline';
        } else if (route.name === 'Portfolios') {
          iconName = focused ? 'briefcase' : 'briefcase-outline';
        } else if (route.name === 'Optimize') {
          iconName = focused ? 'chart-line' : 'chart-line';
        } else if (route.name === 'Market') {
          iconName = focused ? 'finance' : 'finance';
        } else if (route.name === 'Settings') {
          iconName = focused ? 'cog' : 'cog-outline';
        }

        return <Icon name={iconName} type={iconType} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#007AFF', // Example active color
      tabBarInactiveTintColor: 'gray',
    })}
  >
    <Tab.Screen name="Dashboard" component={DashboardStack} />
    <Tab.Screen name="Portfolios" component={PortfolioStack} />
    <Tab.Screen name="Optimize" component={OptimizationStack} />
    <Tab.Screen name="Market" component={MarketStack} />
    <Tab.Screen name="Settings" component={SettingsStack} />
  </Tab.Navigator>
);

// --- Main App Navigator (Handles Auth) ---

const AppNavigator = () => {
  const { authenticated, loading } = useAuth();

  if (loading) {
    // Optionally return a loading spinner screen here
    return null;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {authenticated ? (
          <Stack.Screen name="App" component={AppTabs} />
        ) : (
          <Stack.Screen name="Login" component={LoginScreen} />
        )}
        {/* Add other non-tab screens like Modals here if needed */}
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;

