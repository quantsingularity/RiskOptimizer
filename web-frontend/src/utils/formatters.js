/**
 * Utility functions for formatting data display
 */

/**
 * Format currency value with symbol and decimals
 * @param {number} value - The numeric value to format
 * @param {string} currency - Currency code (default: 'USD')
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (value, currency = "USD", decimals = 2) => {
  if (value === null || value === undefined || isNaN(value)) {
    return "$0.00";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

/**
 * Format percentage value
 * @param {number} value - The numeric value to format as percentage
 * @param {number} decimals - Number of decimal places (default: 2)
 * @param {boolean} showSign - Show + sign for positive values (default: false)
 * @returns {string} Formatted percentage string
 */
export const formatPercentage = (value, decimals = 2, showSign = false) => {
  if (value === null || value === undefined || isNaN(value)) {
    return "0.00%";
  }

  const formatted = value.toFixed(decimals);
  const sign = showSign && value > 0 ? "+" : "";
  return `${sign}${formatted}%`;
};

/**
 * Format large numbers with K, M, B suffixes
 * @param {number} value - The numeric value to format
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted number string
 */
export const formatLargeNumber = (value, decimals = 1) => {
  if (value === null || value === undefined || isNaN(value)) {
    return "0";
  }

  const absValue = Math.abs(value);

  if (absValue >= 1e9) {
    return `${(value / 1e9).toFixed(decimals)}B`;
  } else if (absValue >= 1e6) {
    return `${(value / 1e6).toFixed(decimals)}M`;
  } else if (absValue >= 1e3) {
    return `${(value / 1e3).toFixed(decimals)}K`;
  }

  return value.toFixed(decimals);
};

/**
 * Format date to readable string
 * @param {string|Date} date - Date to format
 * @param {string} format - Format type: 'short', 'long', 'time' (default: 'short')
 * @returns {string} Formatted date string
 */
export const formatDate = (date, format = "short") => {
  if (!date) return "";

  const dateObj = typeof date === "string" ? new Date(date) : date;

  if (isNaN(dateObj.getTime())) {
    return "";
  }

  switch (format) {
    case "long":
      return new Intl.DateTimeFormat("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }).format(dateObj);

    case "time":
      return new Intl.DateTimeFormat("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }).format(dateObj);

    case "short":
    default:
      return new Intl.DateTimeFormat("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      }).format(dateObj);
  }
};

/**
 * Format wallet address (shorten for display)
 * @param {string} address - Full wallet address
 * @param {number} startChars - Number of characters to show at start (default: 6)
 * @param {number} endChars - Number of characters to show at end (default: 4)
 * @returns {string} Shortened address
 */
export const formatAddress = (address, startChars = 6, endChars = 4) => {
  if (!address || address.length < startChars + endChars) {
    return address || "";
  }

  return `${address.slice(0, startChars)}...${address.slice(-endChars)}`;
};

/**
 * Format risk score to category
 * @param {number} score - Risk score (0-100)
 * @returns {object} Category name and color
 */
export const formatRiskScore = (score) => {
  if (score === null || score === undefined || isNaN(score)) {
    return { category: "Unknown", color: "grey" };
  }

  if (score < 30) {
    return { category: "Low", color: "success" };
  } else if (score < 60) {
    return { category: "Moderate", color: "warning" };
  } else {
    return { category: "High", color: "error" };
  }
};

/**
 * Format sharpe ratio with interpretation
 * @param {number} sharpe - Sharpe ratio value
 * @returns {object} Interpretation and color
 */
export const formatSharpeRatio = (sharpe) => {
  if (sharpe === null || sharpe === undefined || isNaN(sharpe)) {
    return { interpretation: "Unknown", color: "grey" };
  }

  if (sharpe > 2) {
    return { interpretation: "Excellent", color: "success" };
  } else if (sharpe > 1) {
    return { interpretation: "Good", color: "success" };
  } else if (sharpe > 0) {
    return { interpretation: "Fair", color: "warning" };
  } else {
    return { interpretation: "Poor", color: "error" };
  }
};

/**
 * Format decimal to basis points
 * @param {number} decimal - Decimal value (e.g., 0.0025)
 * @returns {string} Basis points string (e.g., '25 bps')
 */
export const formatBasisPoints = (decimal) => {
  if (decimal === null || decimal === undefined || isNaN(decimal)) {
    return "0 bps";
  }

  const bps = Math.round(decimal * 10000);
  return `${bps} bps`;
};

/**
 * Format time duration to human readable
 * @param {number} seconds - Duration in seconds
 * @returns {string} Human readable duration
 */
export const formatDuration = (seconds) => {
  if (!seconds || seconds < 0) return "0s";

  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  const parts = [];
  if (days > 0) parts.push(`${days}d`);
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (secs > 0 || parts.length === 0) parts.push(`${secs}s`);

  return parts.join(" ");
};

export default {
  formatCurrency,
  formatPercentage,
  formatLargeNumber,
  formatDate,
  formatAddress,
  formatRiskScore,
  formatSharpeRatio,
  formatBasisPoints,
  formatDuration,
};
