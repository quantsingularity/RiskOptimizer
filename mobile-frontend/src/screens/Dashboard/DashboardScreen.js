import React, { useEffect, useState, useCallback } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    ActivityIndicator,
    RefreshControl,
} from 'react-native';
import { Card, Button, Icon, useTheme } from '@rneui/themed'; // Import useTheme
import { useAuth } from '../../context/AuthContext';
import apiService from '../../services/apiService';
import { useFocusEffect } from '@react-navigation/native';
// Import chart component later
// import PerformanceChart from '../components/dashboard/PerformanceChart';

const DashboardScreen = ({ navigation }) => {
    const { user } = useAuth();
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState('');
    const { theme } = useTheme(); // Access the theme

    const fetchData = useCallback(async () => {
        setError('');
        try {
            // Fetch necessary data for dashboard - API might need a dedicated dashboard endpoint
            // For now, let's assume we fetch portfolios and calculate total value
            const portfolioResponse = await apiService.getPortfolios();
            const portfolios = portfolioResponse.data.portfolios || [];

            let totalValue = 0;
            portfolios.forEach((p) => {
                totalValue += p.total_value || 0;
            });

            // Placeholder for other dashboard metrics
            setDashboardData({
                totalPortfolioValue: totalValue,
                currency: portfolios.length > 0 ? portfolios[0].currency : 'USD',
                overallChange: 1.5, // Placeholder
                topPerformer: { symbol: 'AAPL', change: 5.2 }, // Placeholder
                riskScore: 0.7, // Placeholder
            });
        } catch (err) {
            console.error('Failed to fetch dashboard data:', err);
            setError('Could not load dashboard data.');
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, []); // Add dependencies if user context changes affect data

    useFocusEffect(
        useCallback(() => {
            setLoading(true);
            fetchData();
        }, [fetchData]),
    );

    const onRefresh = useCallback(() => {
        setRefreshing(true);
        fetchData();
    }, [fetchData]);

    // Define styles using the theme
    const styles = StyleSheet.create({
        container: {
            flex: 1,
            backgroundColor: theme.colors.background, // Use theme background
        },
        centered: {
            flex: 1,
            justifyContent: 'center',
            alignItems: 'center',
            backgroundColor: theme.colors.background,
            padding: 20,
        },
        welcomeText: {
            fontSize: 26, // Slightly larger welcome text
            fontWeight: '600', // Semibold
            marginVertical: 20,
            marginHorizontal: 15,
            color: theme.colors.black, // Use theme black
        },
        summaryCard: {
            // Theme handles card styling
            alignItems: 'center',
            marginBottom: 20, // Increased margin
        },
        summaryLabel: {
            fontSize: 16,
            color: theme.colors.grey0, // Use theme grey
            marginBottom: 5,
        },
        summaryValue: {
            fontSize: 32, // Larger value text
            fontWeight: 'bold',
            color: theme.colors.black,
        },
        // chartCard: { // Styles for chart card if implemented
        //   // Theme handles card styling
        //   marginBottom: 20,
        // },
        quickActionsContainer: {
            flexDirection: 'row',
            justifyContent: 'space-around',
            marginHorizontal: 15,
            marginBottom: 20,
        },
        actionButton: {
            // Theme handles most button styling (borderRadius, padding)
            backgroundColor: theme.colors.primary, // Use theme primary
            flex: 1,
            marginHorizontal: 5,
        },
        optimizeButton: {
            backgroundColor: theme.colors.success, // Use theme success for optimize
        },
        metricCard: {
            // Theme handles card styling
            marginBottom: 20,
        },
        metricRow: {
            flexDirection: 'row',
            justifyContent: 'space-between',
            paddingVertical: 10, // Increased padding
        },
        metricLabel: {
            fontSize: 16,
            color: theme.colors.grey0, // Use theme grey
        },
        metricValue: {
            fontSize: 16,
            fontWeight: '600', // Semibold
            color: theme.colors.black,
        },
        errorText: {
            color: theme.colors.error, // Use theme error color
            fontSize: 16,
            textAlign: 'center',
        },
        changeContainer: {
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'center',
            marginTop: 8,
        },
        changeText: {
            fontSize: 18,
            fontWeight: '600',
            marginLeft: 4,
        },
    });

    if (loading && !refreshing) {
        // Show full screen loader only on initial load
        return (
            <View style={styles.centered}>
                <ActivityIndicator size="large" color={theme.colors.primary} />
            </View>
        );
    }

    if (error && !dashboardData) {
        // Show error only if no data is available
        return (
            <View style={styles.centered}>
                <Text style={styles.errorText}>{error}</Text>
                <Button title="Retry" onPress={fetchData} />
            </View>
        );
    }

    return (
        <ScrollView
            style={styles.container}
            refreshControl={
                <RefreshControl
                    refreshing={refreshing}
                    onRefresh={onRefresh}
                    tintColor={theme.colors.primary}
                />
            }
        >
            <Text style={styles.welcomeText}>Welcome, {user?.name || 'User'}!</Text>

            <Card containerStyle={styles.summaryCard}>
                <Text style={styles.summaryLabel}>Total Portfolio Value</Text>
                <Text style={styles.summaryValue}>
                    {dashboardData?.currency}{' '}
                    {dashboardData?.totalPortfolioValue?.toLocaleString(undefined, {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                    }) || '0.00'}
                </Text>
                {dashboardData?.overallChange !== undefined && (
                    <View style={styles.changeContainer}>
                        <Icon
                            name={dashboardData.overallChange >= 0 ? 'arrow-up' : 'arrow-down'}
                            type="feather"
                            size={16}
                            color={
                                dashboardData.overallChange >= 0
                                    ? theme.colors.success
                                    : theme.colors.error
                            }
                        />
                        <Text
                            style={[
                                styles.changeText,
                                {
                                    color:
                                        dashboardData.overallChange >= 0
                                            ? theme.colors.success
                                            : theme.colors.error,
                                },
                            ]}
                        >
                            {Math.abs(dashboardData.overallChange).toFixed(2)}%
                        </Text>
                    </View>
                )}
            </Card>

            {/* Placeholder for Performance Chart */}
            {/* <Card containerStyle={styles.chartCard}>
        <Card.Title>Overall Performance</Card.Title>
        <Card.Divider />
        <PerformanceChart />
      </Card> */}

            <View style={styles.quickActionsContainer}>
                <Button
                    title="View Portfolios"
                    icon={
                        <Icon
                            name="briefcase-outline"
                            type="material-community"
                            color={theme.colors.white}
                        />
                    } // Use theme white for icon
                    buttonStyle={styles.actionButton}
                    onPress={() => navigation.navigate('Portfolios')}
                    // Theme handles styling
                />
                <Button
                    title="Optimize"
                    icon={
                        <Icon
                            name="chart-line"
                            type="material-community"
                            color={theme.colors.white}
                        />
                    } // Use theme white for icon
                    buttonStyle={[styles.actionButton, styles.optimizeButton]}
                    onPress={() => navigation.navigate('Optimize')}
                    // Theme handles styling
                />
            </View>

            <Card containerStyle={styles.metricCard}>
                <Card.Title>Quick Metrics</Card.Title>
                <Card.Divider />
                {error && (
                    <Text style={[styles.errorText, { marginBottom: 10 }]}>{error}</Text>
                )}{' '}
                {/* Show error within card if data exists */}
                <View style={styles.metricRow}>
                    <Text style={styles.metricLabel}>Overall Risk Score:</Text>
                    <Text style={styles.metricValue}>
                        {dashboardData?.riskScore?.toFixed(2) || 'N/A'}
                    </Text>
                </View>
                <View style={styles.metricRow}>
                    <Text style={styles.metricLabel}>Top Performer (24h):</Text>
                    <Text style={styles.metricValue}>
                        {dashboardData?.topPerformer?.symbol || 'N/A'} (+
                        {dashboardData?.topPerformer?.change || 0}%)
                    </Text>
                </View>
                {/* Add more metrics as needed */}
            </Card>
        </ScrollView>
    );
};

export default DashboardScreen;
