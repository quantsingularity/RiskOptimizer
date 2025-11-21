import React from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Divider,
  Button,
  IconButton,
  TextField,
  Switch,
  FormControlLabel,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tabs,
  Tab,
} from "@mui/material";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import SecurityIcon from "@mui/icons-material/Security";
import NotificationsIcon from "@mui/icons-material/Notifications";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import ApiIcon from "@mui/icons-material/Api";
import DarkModeIcon from "@mui/icons-material/DarkMode";
import LanguageIcon from "@mui/icons-material/Language";
import StorageIcon from "@mui/icons-material/Storage";
import VpnKeyIcon from "@mui/icons-material/VpnKey";
import SaveIcon from "@mui/icons-material/Save";

const Settings = () => {
  const [tabValue, setTabValue] = React.useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Box className="fade-in">
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4" component="h1" gutterBottom>
          Settings
        </Typography>
        <Button variant="contained" startIcon={<SaveIcon />}>
          Save Changes
        </Button>
      </Box>

      <Card>
        <Box sx={{ borderBottom: 1, borderColor: "divider" }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            aria-label="settings tabs"
          >
            <Tab
              label="Account"
              icon={<AccountCircleIcon />}
              iconPosition="start"
            />
            <Tab
              label="Preferences"
              icon={<DarkModeIcon />}
              iconPosition="start"
            />
            <Tab
              label="API Connections"
              icon={<ApiIcon />}
              iconPosition="start"
            />
            <Tab
              label="Security"
              icon={<SecurityIcon />}
              iconPosition="start"
            />
            <Tab
              label="Notifications"
              icon={<NotificationsIcon />}
              iconPosition="start"
            />
          </Tabs>
        </Box>
        <CardContent>
          {tabValue === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Account Settings
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Full Name"
                    defaultValue="John Doe"
                    margin="normal"
                    variant="outlined"
                  />
                  <TextField
                    fullWidth
                    label="Email Address"
                    defaultValue="john.doe@example.com"
                    margin="normal"
                    variant="outlined"
                  />
                  <TextField
                    fullWidth
                    label="Phone Number"
                    defaultValue="+1 (555) 123-4567"
                    margin="normal"
                    variant="outlined"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card
                    variant="outlined"
                    sx={{ mb: 2, backgroundColor: "background.default" }}
                  >
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        Account Information
                      </Typography>
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Account Type
                        </Typography>
                        <Typography variant="body1">Premium</Typography>
                      </Box>
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Member Since
                        </Typography>
                        <Typography variant="body1">April 15, 2023</Typography>
                      </Box>
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          Last Login
                        </Typography>
                        <Typography variant="body1">
                          April 9, 2025, 12:34 PM
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>

                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mt: 2,
                    }}
                  >
                    <Button variant="outlined" color="error">
                      Delete Account
                    </Button>
                    <Button variant="contained">Update Profile</Button>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          )}

          {tabValue === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Preferences
              </Typography>

              <List>
                <ListItem>
                  <ListItemIcon>
                    <DarkModeIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Dark Mode"
                    secondary="Enable dark mode for better visibility in low light"
                  />
                  <Switch defaultChecked />
                </ListItem>

                <Divider variant="inset" component="li" />

                <ListItem>
                  <ListItemIcon>
                    <LanguageIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Language"
                    secondary="Select your preferred language"
                  />
                  <TextField
                    select
                    SelectProps={{
                      native: true,
                    }}
                    defaultValue="en"
                    variant="outlined"
                    size="small"
                    sx={{ width: 150 }}
                  >
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                    <option value="zh">Chinese</option>
                  </TextField>
                </ListItem>

                <Divider variant="inset" component="li" />

                <ListItem>
                  <ListItemIcon>
                    <StorageIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Data Refresh Rate"
                    secondary="How often to refresh market data"
                  />
                  <TextField
                    select
                    SelectProps={{
                      native: true,
                    }}
                    defaultValue="5"
                    variant="outlined"
                    size="small"
                    sx={{ width: 150 }}
                  >
                    <option value="1">1 minute</option>
                    <option value="5">5 minutes</option>
                    <option value="15">15 minutes</option>
                    <option value="30">30 minutes</option>
                    <option value="60">1 hour</option>
                  </TextField>
                </ListItem>
              </List>

              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Chart Preferences
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="Show tooltips on charts"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="Enable chart animations"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="Show grid lines"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControlLabel
                      control={<Switch />}
                      label="Use logarithmic scale"
                    />
                  </Grid>
                </Grid>
              </Box>
            </Box>
          )}

          {tabValue === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                API Connections
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined" sx={{ mb: 2 }}>
                    <CardContent>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          mb: 2,
                        }}
                      >
                        <Typography variant="subtitle1">
                          Blockchain Connection
                        </Typography>
                        <Switch defaultChecked />
                      </Box>
                      <TextField
                        fullWidth
                        label="Ethereum RPC URL"
                        defaultValue="https://mainnet.infura.io/v3/your-api-key"
                        margin="normal"
                        variant="outlined"
                        size="small"
                      />
                      <TextField
                        fullWidth
                        label="Wallet Address"
                        defaultValue="0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
                        margin="normal"
                        variant="outlined"
                        size="small"
                      />
                      <Button variant="outlined" fullWidth sx={{ mt: 2 }}>
                        Test Connection
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card variant="outlined" sx={{ mb: 2 }}>
                    <CardContent>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          mb: 2,
                        }}
                      >
                        <Typography variant="subtitle1">
                          Market Data API
                        </Typography>
                        <Switch defaultChecked />
                      </Box>
                      <TextField
                        fullWidth
                        label="API Provider"
                        defaultValue="Alpha Vantage"
                        margin="normal"
                        variant="outlined"
                        size="small"
                      />
                      <TextField
                        fullWidth
                        label="API Key"
                        defaultValue="••••••••••••••••"
                        margin="normal"
                        variant="outlined"
                        size="small"
                        type="password"
                      />
                      <Button variant="outlined" fullWidth sx={{ mt: 2 }}>
                        Verify API Key
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12}>
                  <Button variant="contained" fullWidth>
                    Connect New API
                  </Button>
                </Grid>
              </Grid>
            </Box>
          )}

          {tabValue === 3 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Security Settings
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Change Password
                  </Typography>
                  <TextField
                    fullWidth
                    label="Current Password"
                    type="password"
                    margin="normal"
                    variant="outlined"
                  />
                  <TextField
                    fullWidth
                    label="New Password"
                    type="password"
                    margin="normal"
                    variant="outlined"
                  />
                  <TextField
                    fullWidth
                    label="Confirm New Password"
                    type="password"
                    margin="normal"
                    variant="outlined"
                  />
                  <Button
                    variant="contained"
                    fullWidth
                    sx={{ mt: 2 }}
                    startIcon={<VpnKeyIcon />}
                  >
                    Update Password
                  </Button>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Two-Factor Authentication
                  </Typography>
                  <Card
                    variant="outlined"
                    sx={{ mb: 2, backgroundColor: "background.default" }}
                  >
                    <CardContent>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          mb: 2,
                        }}
                      >
                        <Typography variant="body1">2FA Status</Typography>
                        <Typography
                          variant="body1"
                          color="success.main"
                          sx={{ fontWeight: 600 }}
                        >
                          Enabled
                        </Typography>
                      </Box>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        paragraph
                      >
                        Two-factor authentication adds an extra layer of
                        security to your account by requiring more than just a
                        password to sign in.
                      </Typography>
                      <Button variant="outlined" color="error" fullWidth>
                        Disable 2FA
                      </Button>
                    </CardContent>
                  </Card>

                  <Typography variant="subtitle2" gutterBottom>
                    Session Management
                  </Typography>
                  <Button variant="outlined" color="error" fullWidth>
                    Log Out All Other Devices
                  </Button>
                </Grid>
              </Grid>
            </Box>
          )}

          {tabValue === 4 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Notification Settings
              </Typography>

              <List>
                <ListItem>
                  <ListItemText
                    primary="Email Notifications"
                    secondary="Receive important updates via email"
                  />
                  <Switch defaultChecked />
                </ListItem>

                <Divider component="li" />

                <ListItem>
                  <ListItemText
                    primary="Portfolio Alerts"
                    secondary="Get notified about significant changes in your portfolio"
                  />
                  <Switch defaultChecked />
                </ListItem>

                <Divider component="li" />

                <ListItem>
                  <ListItemText
                    primary="Market Updates"
                    secondary="Receive daily market summaries and news"
                  />
                  <Switch />
                </ListItem>

                <Divider component="li" />

                <ListItem>
                  <ListItemText
                    primary="Risk Threshold Alerts"
                    secondary="Get notified when portfolio risk exceeds your threshold"
                  />
                  <Switch defaultChecked />
                </ListItem>

                <Divider component="li" />

                <ListItem>
                  <ListItemText
                    primary="Optimization Suggestions"
                    secondary="Receive AI-generated portfolio optimization suggestions"
                  />
                  <Switch defaultChecked />
                </ListItem>
              </List>

              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Notification Frequency
                </Typography>
                <TextField
                  select
                  label="Email Digest Frequency"
                  defaultValue="daily"
                  SelectProps={{
                    native: true,
                  }}
                  fullWidth
                  variant="outlined"
                  margin="normal"
                >
                  <option value="realtime">Real-time</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </TextField>
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Settings;
