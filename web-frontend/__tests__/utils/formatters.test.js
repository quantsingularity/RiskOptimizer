import { describe, it, expect } from "vitest";
import {
  formatCurrency,
  formatPercentage,
  formatLargeNumber,
  formatDate,
  formatAddress,
  formatRiskScore,
  formatSharpeRatio,
  formatBasisPoints,
  formatDuration,
} from "../../src/utils/formatters";

describe("Formatters", () => {
  describe("formatCurrency", () => {
    it("should format positive currency values", () => {
      expect(formatCurrency(1234.56)).toBe("$1,234.56");
    });

    it("should format negative currency values", () => {
      expect(formatCurrency(-1234.56)).toBe("-$1,234.56");
    });

    it("should handle zero", () => {
      expect(formatCurrency(0)).toBe("$0.00");
    });

    it("should handle null/undefined", () => {
      expect(formatCurrency(null)).toBe("$0.00");
      expect(formatCurrency(undefined)).toBe("$0.00");
    });

    it("should format with custom decimals", () => {
      expect(formatCurrency(1234.5678, "USD", 0)).toBe("$1,235");
      expect(formatCurrency(1234.5678, "USD", 4)).toBe("$1,234.5678");
    });
  });

  describe("formatPercentage", () => {
    it("should format positive percentages", () => {
      expect(formatPercentage(12.345)).toBe("12.35%");
    });

    it("should format negative percentages", () => {
      expect(formatPercentage(-5.67)).toBe("-5.67%");
    });

    it("should show plus sign when requested", () => {
      expect(formatPercentage(12.34, 2, true)).toBe("+12.34%");
      expect(formatPercentage(-5.67, 2, true)).toBe("-5.67%");
    });

    it("should handle custom decimals", () => {
      expect(formatPercentage(12.3456, 3)).toBe("12.346%");
    });

    it("should handle null/undefined", () => {
      expect(formatPercentage(null)).toBe("0.00%");
    });
  });

  describe("formatLargeNumber", () => {
    it("should format billions", () => {
      expect(formatLargeNumber(1234567890)).toBe("1.2B");
    });

    it("should format millions", () => {
      expect(formatLargeNumber(1234567)).toBe("1.2M");
    });

    it("should format thousands", () => {
      expect(formatLargeNumber(1234)).toBe("1.2K");
    });

    it("should format small numbers without suffix", () => {
      expect(formatLargeNumber(123)).toBe("123.0");
    });

    it("should handle negative numbers", () => {
      expect(formatLargeNumber(-1234567)).toBe("-1.2M");
    });

    it("should handle null/undefined", () => {
      expect(formatLargeNumber(null)).toBe("0");
    });
  });

  describe("formatDate", () => {
    const testDate = new Date("2024-01-15T14:30:00Z");

    it("should format short date", () => {
      const result = formatDate(testDate, "short");
      expect(result).toContain("2024");
      expect(result).toContain("Jan");
    });

    it("should format long date", () => {
      const result = formatDate(testDate, "long");
      expect(result).toContain("2024");
    });

    it("should format time", () => {
      const result = formatDate(testDate, "time");
      expect(result).toMatch(/\d{1,2}:\d{2}:\d{2}/);
    });

    it("should handle string dates", () => {
      const result = formatDate("2024-01-15", "short");
      expect(result).toContain("2024");
    });

    it("should handle invalid dates", () => {
      expect(formatDate("invalid")).toBe("");
      expect(formatDate(null)).toBe("");
    });
  });

  describe("formatAddress", () => {
    const address = "0x1234567890abcdef1234567890abcdef12345678";

    it("should shorten long addresses", () => {
      const result = formatAddress(address);
      expect(result).toBe("0x1234...5678");
      expect(result.length).toBeLessThan(address.length);
    });

    it("should use custom character counts", () => {
      const result = formatAddress(address, 4, 4);
      expect(result).toBe("0x12...5678");
    });

    it("should handle short addresses", () => {
      const shortAddress = "0x123";
      expect(formatAddress(shortAddress)).toBe(shortAddress);
    });

    it("should handle null/undefined", () => {
      expect(formatAddress(null)).toBe("");
      expect(formatAddress(undefined)).toBe("");
    });
  });

  describe("formatRiskScore", () => {
    it("should categorize low risk", () => {
      const result = formatRiskScore(20);
      expect(result.category).toBe("Low");
      expect(result.color).toBe("success");
    });

    it("should categorize moderate risk", () => {
      const result = formatRiskScore(50);
      expect(result.category).toBe("Moderate");
      expect(result.color).toBe("warning");
    });

    it("should categorize high risk", () => {
      const result = formatRiskScore(80);
      expect(result.category).toBe("High");
      expect(result.color).toBe("error");
    });

    it("should handle null/undefined", () => {
      const result = formatRiskScore(null);
      expect(result.category).toBe("Unknown");
      expect(result.color).toBe("grey");
    });
  });

  describe("formatSharpeRatio", () => {
    it("should rate excellent sharpe ratio", () => {
      const result = formatSharpeRatio(2.5);
      expect(result.interpretation).toBe("Excellent");
      expect(result.color).toBe("success");
    });

    it("should rate good sharpe ratio", () => {
      const result = formatSharpeRatio(1.5);
      expect(result.interpretation).toBe("Good");
      expect(result.color).toBe("success");
    });

    it("should rate fair sharpe ratio", () => {
      const result = formatSharpeRatio(0.5);
      expect(result.interpretation).toBe("Fair");
      expect(result.color).toBe("warning");
    });

    it("should rate poor sharpe ratio", () => {
      const result = formatSharpeRatio(-0.5);
      expect(result.interpretation).toBe("Poor");
      expect(result.color).toBe("error");
    });
  });

  describe("formatBasisPoints", () => {
    it("should format basis points", () => {
      expect(formatBasisPoints(0.0025)).toBe("25 bps");
    });

    it("should handle negative basis points", () => {
      expect(formatBasisPoints(-0.0015)).toBe("-15 bps");
    });

    it("should handle zero", () => {
      expect(formatBasisPoints(0)).toBe("0 bps");
    });

    it("should handle null/undefined", () => {
      expect(formatBasisPoints(null)).toBe("0 bps");
    });
  });

  describe("formatDuration", () => {
    it("should format days", () => {
      expect(formatDuration(86400)).toBe("1d");
    });

    it("should format hours", () => {
      expect(formatDuration(3600)).toBe("1h");
    });

    it("should format minutes", () => {
      expect(formatDuration(60)).toBe("1m");
    });

    it("should format seconds", () => {
      expect(formatDuration(30)).toBe("30s");
    });

    it("should format complex durations", () => {
      const result = formatDuration(90061); // 1d 1h 1m 1s
      expect(result).toContain("1d");
      expect(result).toContain("1h");
      expect(result).toContain("1m");
      expect(result).toContain("1s");
    });

    it("should handle zero", () => {
      expect(formatDuration(0)).toBe("0s");
    });

    it("should handle negative", () => {
      expect(formatDuration(-100)).toBe("0s");
    });
  });
});
