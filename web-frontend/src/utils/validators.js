/**
 * Validation utility functions
 */

/**
 * Validate Ethereum wallet address
 * @param {string} address - Address to validate
 * @returns {boolean} True if valid
 */
export const isValidAddress = (address) => {
  if (!address || typeof address !== "string") {
    return false;
  }

  // Basic Ethereum address validation (0x + 40 hex characters)
  const ethereumRegex = /^0x[a-fA-F0-9]{40}$/;
  return ethereumRegex.test(address);
};

/**
 * Validate email address
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid
 */
export const isValidEmail = (email) => {
  if (!email || typeof email !== "string") {
    return false;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate percentage value (0-100)
 * @param {number} value - Value to validate
 * @returns {boolean} True if valid
 */
export const isValidPercentage = (value) => {
  return (
    typeof value === "number" && value >= 0 && value <= 100 && !isNaN(value)
  );
};

/**
 * Validate positive number
 * @param {number} value - Value to validate
 * @returns {boolean} True if valid
 */
export const isPositiveNumber = (value) => {
  return typeof value === "number" && value > 0 && !isNaN(value);
};

/**
 * Validate non-negative number
 * @param {number} value - Value to validate
 * @returns {boolean} True if valid
 */
export const isNonNegativeNumber = (value) => {
  return typeof value === "number" && value >= 0 && !isNaN(value);
};

/**
 * Validate portfolio allocation (sum should be 100%)
 * @param {Array} allocations - Array of allocation objects with 'percentage' field
 * @param {number} tolerance - Allowed tolerance (default: 0.01)
 * @returns {object} Validation result with isValid and error message
 */
export const validateAllocation = (allocations, tolerance = 0.01) => {
  if (!Array.isArray(allocations) || allocations.length === 0) {
    return {
      isValid: false,
      error: "Allocations must be a non-empty array",
    };
  }

  const total = allocations.reduce((sum, item) => {
    const percentage = parseFloat(item.percentage || 0);
    return sum + percentage;
  }, 0);

  const diff = Math.abs(total - 100);

  if (diff > tolerance) {
    return {
      isValid: false,
      error: `Allocation total is ${total.toFixed(2)}%, must be 100%`,
    };
  }

  // Check individual percentages
  for (const item of allocations) {
    if (!isValidPercentage(item.percentage)) {
      return {
        isValid: false,
        error: `Invalid percentage for ${item.asset || "asset"}: ${item.percentage}`,
      };
    }
  }

  return { isValid: true };
};

/**
 * Validate date range
 * @param {Date|string} startDate - Start date
 * @param {Date|string} endDate - End date
 * @returns {object} Validation result
 */
export const validateDateRange = (startDate, endDate) => {
  const start = new Date(startDate);
  const end = new Date(endDate);

  if (isNaN(start.getTime())) {
    return {
      isValid: false,
      error: "Invalid start date",
    };
  }

  if (isNaN(end.getTime())) {
    return {
      isValid: false,
      error: "Invalid end date",
    };
  }

  if (start > end) {
    return {
      isValid: false,
      error: "Start date must be before end date",
    };
  }

  return { isValid: true };
};

/**
 * Validate required field
 * @param {any} value - Value to validate
 * @param {string} fieldName - Field name for error message
 * @returns {object} Validation result
 */
export const validateRequired = (value, fieldName = "Field") => {
  if (value === null || value === undefined || value === "") {
    return {
      isValid: false,
      error: `${fieldName} is required`,
    };
  }

  return { isValid: true };
};

/**
 * Validate string length
 * @param {string} value - String to validate
 * @param {number} min - Minimum length
 * @param {number} max - Maximum length
 * @param {string} fieldName - Field name for error message
 * @returns {object} Validation result
 */
export const validateLength = (value, min, max, fieldName = "Field") => {
  if (typeof value !== "string") {
    return {
      isValid: false,
      error: `${fieldName} must be a string`,
    };
  }

  if (value.length < min) {
    return {
      isValid: false,
      error: `${fieldName} must be at least ${min} characters`,
    };
  }

  if (value.length > max) {
    return {
      isValid: false,
      error: `${fieldName} must be at most ${max} characters`,
    };
  }

  return { isValid: true };
};

/**
 * Validate confidence level (typically 0.90, 0.95, 0.99)
 * @param {number} value - Confidence level
 * @returns {boolean} True if valid
 */
export const isValidConfidenceLevel = (value) => {
  const validLevels = [0.9, 0.95, 0.99];
  return validLevels.includes(value);
};

/**
 * Validate risk tolerance (0-100 scale)
 * @param {number} value - Risk tolerance value
 * @returns {object} Validation result
 */
export const validateRiskTolerance = (value) => {
  if (!isNonNegativeNumber(value)) {
    return {
      isValid: false,
      error: "Risk tolerance must be a non-negative number",
    };
  }

  if (value > 100) {
    return {
      isValid: false,
      error: "Risk tolerance cannot exceed 100",
    };
  }

  return { isValid: true };
};

export default {
  isValidAddress,
  isValidEmail,
  isValidPercentage,
  isPositiveNumber,
  isNonNegativeNumber,
  validateAllocation,
  validateDateRange,
  validateRequired,
  validateLength,
  isValidConfidenceLevel,
  validateRiskTolerance,
};
