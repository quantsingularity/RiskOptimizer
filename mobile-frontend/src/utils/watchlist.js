import AsyncStorage from '@react-native-async-storage/async-storage';

const WATCHLIST_KEY = '@RiskOptimizer:watchlist';

// Get the current watchlist (array of symbols)
export const getWatchlist = async () => {
    try {
        const jsonValue = await AsyncStorage.getItem(WATCHLIST_KEY);
        return jsonValue != null ? JSON.parse(jsonValue) : [];
    } catch (e) {
        console.error('Failed to load watchlist from storage', e);
        return [];
    }
};

// Add a symbol to the watchlist
export const addToWatchlist = async (symbol) => {
    if (!symbol) return;
    try {
        const currentWatchlist = await getWatchlist();
        if (!currentWatchlist.includes(symbol)) {
            const newWatchlist = [...currentWatchlist, symbol];
            const jsonValue = JSON.stringify(newWatchlist);
            await AsyncStorage.setItem(WATCHLIST_KEY, jsonValue);
            console.log(`${symbol} added to watchlist`);
            return true;
        }
    } catch (e) {
        console.error(`Failed to add ${symbol} to watchlist`, e);
    }
    return false;
};

// Remove a symbol from the watchlist
export const removeFromWatchlist = async (symbol) => {
    if (!symbol) return;
    try {
        const currentWatchlist = await getWatchlist();
        if (currentWatchlist.includes(symbol)) {
            const newWatchlist = currentWatchlist.filter(s => s !== symbol);
            const jsonValue = JSON.stringify(newWatchlist);
            await AsyncStorage.setItem(WATCHLIST_KEY, jsonValue);
            console.log(`${symbol} removed from watchlist`);
            return true;
        }
    } catch (e) {
        console.error(`Failed to remove ${symbol} from watchlist`, e);
    }
    return false;
};

// Check if a symbol is in the watchlist
export const isInWatchlist = async (symbol) => {
    if (!symbol) return false;
    try {
        const currentWatchlist = await getWatchlist();
        return currentWatchlist.includes(symbol);
    } catch (e) {
        console.error(`Failed to check watchlist status for ${symbol}`, e);
        return false;
    }
};
