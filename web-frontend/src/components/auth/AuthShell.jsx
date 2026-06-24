import { Box, Card, Container, Stack, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

// Shared two-column shell for the sign-in and sign-up pages.
const AuthShell = ({ title, subtitle, children }) => {
  const navigate = useNavigate();
  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        bgcolor: "background.default",
      }}
    >
      <Box
        sx={{
          flex: 1,
          display: { xs: "none", md: "flex" },
          flexDirection: "column",
          justifyContent: "space-between",
          p: 6,
          background:
            "radial-gradient(800px 400px at 20% 10%, rgba(91,141,239,0.18), transparent 60%), #0A0F1E",
          borderRight: "1px solid",
          borderColor: "divider",
        }}
      >
        <Typography
          variant="h6"
          sx={{ fontWeight: 700, cursor: "pointer" }}
          onClick={() => navigate("/")}
        >
          Risk<span style={{ color: "#5B8DEF" }}>Optimizer</span>
        </Typography>
        <Box>
          <Typography variant="h3" sx={{ mb: 2, lineHeight: 1.1 }}>
            The numbers
            <br />
            behind the position.
          </Typography>
          <Typography color="text.secondary" sx={{ maxWidth: 420 }}>
            Value at risk, expected shortfall, Sharpe, and drawdown on your own
            return series, computed and returned with full precision.
          </Typography>
        </Box>
        <Typography variant="caption" color="text.secondary">
          For research and educational use; not investment advice.
        </Typography>
      </Box>

      <Box
        sx={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          p: { xs: 2, sm: 4 },
        }}
      >
        <Container maxWidth="xs" disableGutters>
          <Card sx={{ p: { xs: 3, sm: 4 } }}>
            <Stack spacing={0.5} sx={{ mb: 3 }}>
              <Typography
                variant="h6"
                sx={{
                  display: { xs: "block", md: "none" },
                  fontWeight: 700,
                  mb: 1,
                }}
              >
                Risk<span style={{ color: "#5B8DEF" }}>Optimizer</span>
              </Typography>
              <Typography variant="h5">{title}</Typography>
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            </Stack>
            {children}
          </Card>
        </Container>
      </Box>
    </Box>
  );
};

export default AuthShell;
