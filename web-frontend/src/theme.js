import { createTheme } from "@mui/material/styles";

// Palette: an institutional "quant risk terminal".
// Ink navy surfaces, a calm institutional blue primary, a gold market accent,
// and green/red reserved strictly for gains and losses.
const ink = "#0A0F1E";
const surface = "#121A2E";
const elevated = "#19233B";
const border = "rgba(148, 163, 184, 0.14)";
const primary = "#5B8DEF";
const accent = "#E5B567";
const positive = "#34C77B";
const negative = "#F2555A";

const display = '"Space Grotesk", "Inter", sans-serif';
const body = '"Inter", -apple-system, BlinkMacSystemFont, sans-serif';
export const mono = '"JetBrains Mono", "SFMono-Regular", Menlo, monospace';

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: primary, light: "#84ABF5", dark: "#3F6FD1" },
    secondary: { main: accent, light: "#F0CB8B", dark: "#C9963F" },
    success: { main: positive },
    error: { main: negative },
    warning: { main: "#E5B567" },
    info: { main: primary },
    background: { default: ink, paper: surface },
    divider: border,
    text: { primary: "#E6EAF2", secondary: "#8A93A6" },
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily: body,
    h1: { fontFamily: display, fontWeight: 700, letterSpacing: "-0.02em" },
    h2: { fontFamily: display, fontWeight: 700, letterSpacing: "-0.02em" },
    h3: { fontFamily: display, fontWeight: 600, letterSpacing: "-0.01em" },
    h4: { fontFamily: display, fontWeight: 600, letterSpacing: "-0.01em" },
    h5: { fontFamily: display, fontWeight: 600 },
    h6: { fontFamily: display, fontWeight: 600 },
    button: { textTransform: "none", fontWeight: 600 },
    overline: { letterSpacing: "0.18em", fontWeight: 600 },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage:
            "radial-gradient(1200px 600px at 80% -10%, rgba(91,141,239,0.10), transparent 60%)",
          scrollbarColor: "rgba(148,163,184,0.3) transparent",
        },
        // Tabular figures everywhere numbers are shown in mono
        ".mono": { fontFamily: mono, fontVariantNumeric: "tabular-nums" },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: "rgba(10,15,30,0.85)",
          backdropFilter: "blur(10px)",
          borderBottom: `1px solid ${border}`,
          boxShadow: "none",
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: { backgroundColor: surface, borderRight: `1px solid ${border}` },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 14,
          backgroundColor: surface,
          backgroundImage: "none",
          border: `1px solid ${border}`,
          boxShadow:
            "0 1px 0 rgba(255,255,255,0.03), 0 12px 32px rgba(0,0,0,0.35)",
        },
      },
    },
    MuiPaper: {
      styleOverrides: { root: { backgroundImage: "none" } },
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 9, paddingInline: 18 },
        containedPrimary: {
          boxShadow: "0 6px 18px rgba(91,141,239,0.30)",
          "&:hover": { boxShadow: "0 8px 22px rgba(91,141,239,0.40)" },
        },
      },
    },
    MuiTextField: {
      defaultProps: { variant: "outlined" },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: { backgroundColor: elevated, borderRadius: 9 },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          backgroundColor: "rgba(148,163,184,0.05)",
          fontWeight: 700,
          color: "#8A93A6",
          fontSize: "0.72rem",
          textTransform: "uppercase",
          letterSpacing: "0.06em",
        },
        body: { borderColor: border },
      },
    },
    MuiChip: { styleOverrides: { root: { borderRadius: 7, fontWeight: 600 } } },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: elevated,
          border: `1px solid ${border}`,
          fontSize: "0.75rem",
        },
      },
    },
  },
});

export default theme;
