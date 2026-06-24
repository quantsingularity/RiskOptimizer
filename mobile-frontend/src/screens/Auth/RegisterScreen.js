import { StatusBar } from "expo-status-bar";
import { useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { useAuth } from "../../context/AuthContext";
import colors from "../../theme/colors";

// Mirrors the backend policy: 12+ chars, upper, lower, digit, special.
function passwordIssues(pw) {
  const issues = [];
  if (pw.length < 12) issues.push("12+ characters");
  if (!/[A-Z]/.test(pw)) issues.push("an uppercase letter");
  if (!/[a-z]/.test(pw)) issues.push("a lowercase letter");
  if (!/[0-9]/.test(pw)) issues.push("a digit");
  if (!/[^A-Za-z0-9]/.test(pw)) issues.push("a symbol");
  return issues;
}

const RegisterScreen = ({ navigation }) => {
  const { register, error: authError, clearError } = useAuth();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [localError, setLocalError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async () => {
    setLocalError("");
    clearError?.();
    if (!username || !email || !password) {
      setLocalError("Fill in every field to create your account.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setLocalError("Enter a valid email address.");
      return;
    }
    const issues = passwordIssues(password);
    if (issues.length) {
      setLocalError(`Your password needs ${issues.join(", ")}.`);
      return;
    }
    setSubmitting(true);
    const ok = await register(email, username, password);
    setSubmitting(false);
    // On success the navigator swaps to the authenticated stack automatically.
    if (!ok) setLocalError(authError || "Could not create your account.");
  };

  const displayError = localError || authError;

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.brand}>
          Risk<Text style={{ color: colors.primary }}>Optimizer</Text>
        </Text>
        <Text style={styles.title}>Create your account</Text>
        <Text style={styles.subtitle}>
          Set up a workspace and run your first risk report.
        </Text>

        {displayError ? (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>{displayError}</Text>
          </View>
        ) : null}

        <Text style={styles.label}>Username</Text>
        <TextInput
          style={styles.input}
          placeholder="yourname"
          placeholderTextColor={colors.textMuted}
          autoCapitalize="none"
          value={username}
          onChangeText={setUsername}
          testID="input-Username"
        />

        <Text style={styles.label}>Email</Text>
        <TextInput
          style={styles.input}
          placeholder="you@example.com"
          placeholderTextColor={colors.textMuted}
          autoCapitalize="none"
          keyboardType="email-address"
          value={email}
          onChangeText={setEmail}
          testID="input-Email"
        />

        <Text style={styles.label}>Password</Text>
        <TextInput
          style={styles.input}
          placeholder="At least 12 characters"
          placeholderTextColor={colors.textMuted}
          secureTextEntry
          value={password}
          onChangeText={setPassword}
          testID="input-Password"
        />
        <Text style={styles.hint}>
          12+ characters with upper, lower, a digit, and a symbol.
        </Text>

        <TouchableOpacity
          style={[styles.primaryBtn, submitting && { opacity: 0.7 }]}
          onPress={onSubmit}
          disabled={submitting}
          testID="button"
        >
          {submitting ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.primaryBtnText}>Create account</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.linkRow}
          onPress={() => navigation.navigate("Login")}
        >
          <Text style={styles.linkMuted}>Already have an account? </Text>
          <Text style={styles.link}>Sign in</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.ink },
  content: { padding: 24, paddingTop: 72 },
  brand: {
    fontSize: 20,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 28,
  },
  title: {
    fontSize: 26,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 6,
  },
  subtitle: { fontSize: 15, color: colors.textMuted, marginBottom: 24 },
  label: {
    color: colors.textMuted,
    fontSize: 13,
    marginBottom: 6,
    marginTop: 14,
  },
  input: {
    backgroundColor: colors.elevated,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 13,
    color: colors.text,
    fontSize: 16,
  },
  hint: { color: colors.textMuted, fontSize: 12, marginTop: 6 },
  primaryBtn: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: "center",
    marginTop: 24,
  },
  primaryBtnText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  linkRow: { flexDirection: "row", justifyContent: "center", marginTop: 22 },
  linkMuted: { color: colors.textMuted, fontSize: 14 },
  link: { color: colors.primary, fontSize: 14, fontWeight: "600" },
  errorBox: {
    backgroundColor: "rgba(242,85,90,0.12)",
    borderColor: "rgba(242,85,90,0.4)",
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
  },
  errorText: { color: colors.negative, fontSize: 14 },
});

export default RegisterScreen;
