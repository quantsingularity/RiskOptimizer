import React, {
  useState,
  useEffect,
  useCallback,
  useMemo,
  useLayoutEffect,
} from "react"; // Import useLayoutEffect
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
  TouchableOpacity,
} from "react-native"; // Import TouchableOpacity
import { Card, ButtonGroup, useTheme, Button, Icon } from "@rneui/themed"; // Import Icon
import { useFocusEffect } from "@react-navigation/native";
import apiService from "../../services/apiService";
import { LineChart } from "react-native-chart-kit";
import {
  getWatchlist,
  addToWatchlist,
  removeFromWatchlist,
  isInWatchlist,
} from "../utils/watchlist"; // Import watchlist functions

const screenWidth = Dimensions.get("window").width;

// Define available ranges and their corresponding intervals
const chartRanges = ["1d", "5d", "1mo", "6mo", "1y", "max"];
const getIntervalForRange = (range) => {
  switch (range) {
    case "1d":
      return "5m";
    case "5d":
      return "15m";
    case "1mo":
      return "1d";
    case "6mo":
      return "1d";
    case "1y":
      return "1d";
    case "max":
      return "1wk";
    default:
      return "1d";
  }
};

const AssetDetailScreen = ({ route, navigation }) => {
  const { symbol } = route.params;
  const [assetData, setAssetData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [selectedRangeIndex, setSelectedRangeIndex] = useState(4); // Default to '1y'
  const [isWatchlisted, setIsWatchlisted] = useState(false); // State for watchlist status

  const { theme } = useTheme();

  const selectedRange = chartRanges[selectedRangeIndex];
  const selectedInterval = getIntervalForRange(selectedRange);

  // Check watchlist status
  const checkWatchlistStatus = useCallback(async () => {
    const status = await isInWatchlist(symbol);
    setIsWatchlisted(status);
  }, [symbol]);

  // Toggle watchlist status
  const toggleWatchlist = useCallback(async () => {
    let success = false;
    if (isWatchlisted) {
      success = await removeFromWatchlist(symbol);
    } else {
      success = await addToWatchlist(symbol);
    }
    if (success) {
      setIsWatchlisted(!isWatchlisted);
    }
  }, [symbol, isWatchlisted]);

  // Update header with watchlist icon
  useLayoutEffect(() => {
    navigation.setOptions({
      title: assetData?.meta?.shortName || symbol || "Asset Details",
      headerRight: () => (
        <TouchableOpacity onPress={toggleWatchlist} style={{ marginRight: 15 }}>
          <Icon
            name={isWatchlisted ? "star" : "star-outline"}
            type="material-community"
            color={theme.colors.primary} // Use theme color
            size={28}
          />
        </TouchableOpacity>
      ),
    });
    // Add dependencies
  }, [
    navigation,
    symbol,
    assetData?.meta?.shortName,
    isWatchlisted,
    toggleWatchlist,
    theme.colors.primary,
  ]);

  const fetchAssetDetails = useCallback(
    async (range = selectedRange, interval = selectedInterval) => {
      setError("");
      try {
        const response = await apiService.getAssetPriceHistory(
          symbol,
          range,
          interval,
        );
        const result = response.data;

        if (!result || !result.timestamp || result.timestamp.length === 0) {
          setError("No data available for this asset.");
          setAssetData(null);
          return;
        }

        const timestamps = result.timestamp || [];
        const quotes = result.indicators?.quote?.[0];
        const closes = quotes?.close || [];
        const opens = quotes?.open || [];
        const highs = quotes?.high || [];
        const lows = quotes?.low || [];
        const volumes = quotes?.volume || [];

        if (closes.length === 0) {
          setError("Price data is missing.");
          setAssetData(null);
          return;
        }

        // Prepare chart data
        const chartLabels = timestamps.map((ts) => {
          const date = new Date(ts * 1000);
          if (interval.includes("m") || interval.includes("h")) {
            return date.toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            });
          }
          if (range === "1y" || range === "6mo" || range === "max") {
            return date.toLocaleDateString([], {
              month: "short",
              year: "numeric",
            });
          }
          return date.toLocaleDateString([], {
            month: "short",
            day: "numeric",
          });
        });
        const chartDataset = closes.map((c) => c || 0);

        const maxLabels = 6;
        let simplifiedLabels = chartLabels;
        let simplifiedData = chartDataset;
        if (chartLabels.length > maxLabels) {
          const skipCount = Math.ceil(chartLabels.length / maxLabels);
          simplifiedLabels = chartLabels.filter(
            (_, index) => index % skipCount === 0,
          );
        }

        const latestPrice =
          result.meta?.regularMarketPrice || closes[closes.length - 1];
        const previousClose =
          result.meta?.chartPreviousClose ||
          (closes.length > 1 ? closes[closes.length - 2] : latestPrice);
        const changePercent = previousClose
          ? ((latestPrice - previousClose) / previousClose) * 100
          : 0;
        const changeValue = latestPrice - previousClose;

        setAssetData({
          meta: result.meta,
          summary: {
            high:
              highs.length > 0
                ? Math.max(...highs.filter((h) => h !== null))
                : null,
            low:
              lows.length > 0
                ? Math.min(...lows.filter((l) => l !== null))
                : null,
            volume: volumes[volumes.length - 1],
            change_percentage: changePercent,
            change_value: changeValue,
            open: opens[opens.length - 1],
          },
          chartData: {
            labels: simplifiedLabels,
            datasets: [
              {
                data: simplifiedData,
                color: (opacity = 1) =>
                  changePercent >= 0
                    ? theme.colors.success
                    : theme.colors.error,
                strokeWidth: 2,
              },
            ],
            legend: [
              `${result.meta?.symbol || symbol} Price (${result.meta?.currency || "USD"})`,
            ],
          },
        });
      } catch (err) {
        console.error(`Failed to fetch asset details for ${symbol}:`, err);
        setError(`Could not load data for ${symbol}.`);
        setAssetData(null);
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [
      symbol,
      selectedRange,
      selectedInterval,
      theme.colors.success,
      theme.colors.error,
    ],
  );

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      checkWatchlistStatus(); // Check status on focus
      fetchAssetDetails(selectedRange, selectedInterval);
    }, [
      symbol,
      selectedRange,
      selectedInterval,
      fetchAssetDetails,
      checkWatchlistStatus,
    ]),
  );

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    checkWatchlistStatus(); // Re-check status on refresh
    fetchAssetDetails(selectedRange, selectedInterval);
  }, [
    selectedRange,
    selectedInterval,
    fetchAssetDetails,
    checkWatchlistStatus,
  ]);

  const handleRangeChange = (index) => {
    if (index !== selectedRangeIndex) {
      setSelectedRangeIndex(index);
      setLoading(true);
    }
  };

  const styles = useMemo(
    () =>
      StyleSheet.create({
        container: {
          flex: 1,
          backgroundColor: theme.colors.background,
        },
        centered: {
          flex: 1,
          justifyContent: "center",
          alignItems: "center",
          padding: 20,
          backgroundColor: theme.colors.background,
        },
        card: {
          padding: 15,
        },
        headerRow: {
          flexDirection: "row",
          alignItems: "baseline",
          justifyContent: "center",
          marginBottom: 5,
        },
        assetName: {
          fontSize: 24,
          fontWeight: "600",
          color: theme.colors.black,
          marginRight: 8,
        },
        assetSymbol: {
          fontSize: 18,
          color: theme.colors.grey0,
        },
        currentPriceRow: {
          flexDirection: "row",
          alignItems: "baseline",
          justifyContent: "center",
          marginBottom: 15,
        },
        currentPrice: {
          fontSize: 30,
          fontWeight: "bold",
          color: theme.colors.black,
          marginRight: 8,
        },
        priceChange: {
          fontSize: 16,
          fontWeight: "600",
        },
        positive: {
          color: theme.colors.success,
        },
        negative: {
          color: theme.colors.error,
        },
        chart: {
          marginVertical: 8,
          borderRadius: 16,
        },
        statsRow: {
          flexDirection: "row",
          justifyContent: "space-between",
          paddingVertical: 8,
        },
        statsLabel: {
          fontSize: 15,
          color: theme.colors.grey0,
        },
        statsValue: {
          fontSize: 15,
          fontWeight: "600",
          color: theme.colors.black,
        },
        errorText: {
          color: theme.colors.error,
          textAlign: "center",
          marginBottom: 10,
        },
        infoText: {
          textAlign: "center",
          color: theme.colors.grey0,
          paddingVertical: 20,
        },
        buttonGroupContainer: {
          marginBottom: 10,
          marginHorizontal: 5,
          borderRadius: 8,
        },
        buttonGroupSelected: {
          backgroundColor: theme.colors.primary,
        },
        buttonGroupText: {
          fontSize: 13,
        },
      }),
    [theme],
  );

  const chartConfig = useMemo(
    () => ({
      backgroundGradientFrom: theme.colors.white,
      backgroundGradientTo: theme.colors.white,
      decimalPlaces: 2,
      color: (opacity = 1) =>
        theme.mode === "dark"
          ? `rgba(255, 255, 255, ${opacity})`
          : `rgba(0, 0, 0, ${opacity})`,
      labelColor: (opacity = 1) => theme.colors.grey0,
      style: {
        borderRadius: 16,
      },
      propsForDots: {
        r: "3",
        strokeWidth: "1",
        stroke: theme.colors.primary,
      },
    }),
    [theme],
  );

  if (loading && !refreshing) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  if (error && !assetData) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>{error}</Text>
        <Button
          title="Retry"
          onPress={() => fetchAssetDetails(selectedRange, selectedInterval)}
        />
      </View>
    );
  }

  if (!assetData) {
    return (
      <View style={styles.centered}>
        <Text style={styles.infoText}>No data available.</Text>
      </View>
    );
  }

  const meta = assetData.meta || {};
  const summary = assetData.summary || {};
  const chartData = assetData.chartData;
  const latestPrice = meta.regularMarketPrice || 0;
  const currency = meta.currency || "USD";

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
      {error && (
        <Text style={[styles.errorText, { padding: 15 }]}>{error}</Text>
      )}
      <Card containerStyle={styles.card}>
        <View style={styles.headerRow}>
          <Text style={styles.assetName}>{meta.shortName || meta.symbol}</Text>
          <Text style={styles.assetSymbol}>({meta.symbol})</Text>
        </View>
        <View style={styles.currentPriceRow}>
          <Text style={styles.currentPrice}>
            {currency}{" "}
            {latestPrice?.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </Text>
          <Text
            style={[
              styles.priceChange,
              summary.change_percentage >= 0
                ? styles.positive
                : styles.negative,
            ]}
          >
            {summary.change_value >= 0 ? "+" : ""}
            {summary.change_value?.toFixed(2)} (
            {summary.change_percentage?.toFixed(2)}
            %)
          </Text>
        </View>
      </Card>

      <Card containerStyle={styles.card}>
        <ButtonGroup
          buttons={chartRanges.map((r) => r.toUpperCase())}
          selectedIndex={selectedRangeIndex}
          onPress={handleRangeChange}
          containerStyle={styles.buttonGroupContainer}
          selectedButtonStyle={styles.buttonGroupSelected}
          textStyle={styles.buttonGroupText}
        />
        {chartData && chartData.datasets[0].data.length > 0 ? (
          <LineChart
            data={chartData}
            width={screenWidth - 60}
            height={220}
            chartConfig={chartConfig}
            bezier
            style={styles.chart}
            withInnerLines={false}
            withOuterLines={false}
          />
        ) : (
          <Text style={styles.infoText}>
            Chart data not available for this range.
          </Text>
        )}
      </Card>

      <Card containerStyle={styles.card}>
        <Card.Title>Statistics</Card.Title>
        <Card.Divider />
        <View style={styles.statsRow}>
          <Text style={styles.statsLabel}>Open:</Text>
          <Text style={styles.statsValue}>
            {summary.open?.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }) || "N/A"}
          </Text>
        </View>
        <View style={styles.statsRow}>
          <Text style={styles.statsLabel}>
            High ({selectedRange.toUpperCase()}):
          </Text>
          <Text style={styles.statsValue}>
            {summary.high?.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }) || "N/A"}
          </Text>
        </View>
        <View style={styles.statsRow}>
          <Text style={styles.statsLabel}>
            Low ({selectedRange.toUpperCase()}):
          </Text>
          <Text style={styles.statsValue}>
            {summary.low?.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }) || "N/A"}
          </Text>
        </View>
        <View style={styles.statsRow}>
          <Text style={styles.statsLabel}>Prev. Close:</Text>
          <Text style={styles.statsValue}>
            {meta.chartPreviousClose?.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }) || "N/A"}
          </Text>
        </View>
        <View style={styles.statsRow}>
          <Text style={styles.statsLabel}>Volume:</Text>
          <Text style={styles.statsValue}>
            {meta.regularMarketVolume?.toLocaleString() ||
              summary.volume?.toLocaleString() ||
              "N/A"}
          </Text>
        </View>
        <View style={styles.statsRow}>
          <Text style={styles.statsLabel}>52 Week High:</Text>
          <Text style={styles.statsValue}>
            {meta.fiftyTwoWeekHigh?.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }) || "N/A"}
          </Text>
        </View>
        <View style={styles.statsRow}>
          <Text style={styles.statsLabel}>52 Week Low:</Text>
          <Text style={styles.statsValue}>
            {meta.fiftyTwoWeekLow?.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            }) || "N/A"}
          </Text>
        </View>
      </Card>
    </ScrollView>
  );
};

export default AssetDetailScreen;
