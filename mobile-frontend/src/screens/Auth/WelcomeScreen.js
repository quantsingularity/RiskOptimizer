import { StatusBar } from "expo-status-bar";
import {
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import colors from "../../theme/colors";

// Landing screen shown first. Routes to sign up / sign in.
const FEATURES = [
  ["Value at Risk", "Tail-risk on your own return series"],
  ["Sharpe and drawdown", "Risk-adjusted performance at a glance"],
  ["Efficient frontier", "See where an allocation sits vs the optimum"],
];

const WelcomeScreen = ({ navigation }) => {
  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.brandRow}>
          <Text style={styles.brand}>
            Risk<Text style={{ color: colors.primary }}>Optimizer</Text>
          </Text>
        </View>

        <View style={styles.hero}>
          <Text style={styles.eyebrow}>QUANTITATIVE PORTFOLIO RISK</Text>
          <Text style={styles.title}>
            Measure the risk before you commit the capital.
          </Text>
          <Text style={styles.subtitle}>
            Turn a return series into value at risk, expected shortfall, Sharpe,
            and drawdown. No spreadsheets, no guesswork.
          </Text>
        </View>

        <View style={styles.readout}>
          <View style={styles.readoutRow}>
            <Text style={styles.readoutLabel}>Value at Risk</Text>
            <Text style={[styles.readoutValue, { color: colors.negative }]}>
              -2.53%
            </Text>
          </View>
          <View style={styles.readoutRow}>
            <Text style={styles.readoutLabel}>Sharpe ratio</Text>
            <Text style={styles.readoutValue}>1.42</Text>
          </View>
          <View style={[styles.readoutRow, { borderBottomWidth: 0 }]}>
            <Text style={styles.readoutLabel}>Max drawdown</Text>
            <Text style={[styles.readoutValue, { color: colors.negative }]}>
              -11.7%
            </Text>
          </View>
        </View>

        <View style={styles.features}>
          {FEATURES.map(([t, d]) => (
            <View key={t} style={styles.feature}>
              <View style={styles.dot} />
              <View style={{ flex: 1 }}>
                <Text style={styles.featureTitle}>{t}</Text>
                <Text style={styles.featureBody}>{d}</Text>
              </View>
            </View>
          ))}
        </View>
      </ScrollView>

      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.primaryBtn}
          onPress={() => navigation.navigate("Register")}
          accessibilityRole="button"
        >
          <Text style={styles.primaryBtnText}>Get started</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.secondaryBtn}
          onPress={() => navigation.navigate("Login")}
          accessibilityRole="button"
        >
          <Text style={styles.secondaryBtnText}>I already have an account</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.ink },
  content: { padding: 24, paddingTop: 64, paddingBottom: 24 },
  brandRow: { marginBottom: 36 },
  brand: { fontSize: 20, fontWeight: "700", color: colors.text },
  hero: { marginBottom: 28 },
  eyebrow: {
    color: colors.primary,
    fontSize: 12,
    letterSpacing: 2,
    fontWeight: "700",
    marginBottom: 12,
  },
  title: {
    color: colors.text,
    fontSize: 32,
    fontWeight: "700",
    lineHeight: 38,
    marginBottom: 14,
  },
  subtitle: { color: colors.textMuted, fontSize: 16, lineHeight: 23 },
  readout: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 18,
    marginBottom: 28,
  },
  readoutRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  readoutLabel: { color: colors.textMuted, fontSize: 14 },
  readoutValue: {
    color: colors.text,
    fontSize: 16,
    fontWeight: "600",
    fontFamily: "monospace",
  },
  features: { gap: 16 },
  feature: { flexDirection: "row", alignItems: "flex-start", gap: 12 },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.primary,
    marginTop: 6,
  },
  featureTitle: { color: colors.text, fontSize: 15, fontWeight: "600" },
  featureBody: { color: colors.textMuted, fontSize: 13, marginTop: 2 },
  actions: {
    padding: 24,
    borderTopWidth: 1,
    borderTopColor: colors.border,
    gap: 12,
  },
  primaryBtn: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: "center",
  },
  primaryBtnText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  secondaryBtn: { paddingVertical: 14, alignItems: "center" },
  secondaryBtnText: {
    color: colors.textMuted,
    fontSize: 15,
    fontWeight: "600",
  },
});

export default WelcomeScreen;
