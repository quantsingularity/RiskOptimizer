import React, { useState } from 'react';
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
    Alert,
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import SecurityIcon from '@mui/icons-material/Security';
import NotificationsIcon from '@mui/icons-material/Notifications';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import ApiIcon from '@mui/icons-material/Api';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LanguageIcon from '@mui/icons-material/Language';
import StorageIcon from '@mui/icons-material/Storage';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import SaveIcon from '@mui/icons-material/Save';

const Settings = () => {
    const [tabValue, setTabValue] = useState(0);
    const [isSaved, setIsSaved] = useState(false);

    const handleTabChange = (event, newValue) => {
        setTabValue(newValue);
    };

    const handleSave = () => {
        // Simulate saving settings
        setIsSaved(true);
        setTimeout(() => setIsSaved(false), 3000);
    };

    return (
        <Box className="fade-in">
            <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mb: 3,
                }}
            >
                <Typography variant="h4" component="h1" gutterBottom>
                    Settings
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {isSaved && (
                        <Alert severity="success" sx={{ mr: 2, py: 0 }}>
                            Settings saved!
                        </Alert>
                    )}
                    <Button variant="contained" startIcon={<SaveIcon />} onClick={handleSave}>
                        Save Changes
                    </Button>
                </Box>
            </Box>

            <Card>
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={tabValue} onChange={handleTabChange} aria-label="settings tabs">
                        <Tab label="Account" icon={<AccountCircleIcon />} iconPosition="start" />
                        <Tab label="Preferences" icon={<DarkModeIcon />} iconPosition="start" />
                        <Tab label="API Connections" icon={<ApiIcon />} iconPosition="start" />
                        <Tab label="Security" icon={<SecurityIcon />} iconPosition="start" />
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
                                        sx={{ mb: 2, backgroundColor: 'background.default' }}
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
                                                <Typography variant="body1">
                                                    April 15, 2023
                                                </Typography>
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
                                            display: 'flex',
                                            justifyContent: 'space-between',
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
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center',
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
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center',
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
                                                label="API Endpoint"
                                                defaultValue="https://api.marketdata.com/v1"
                                                margin="normal"
                                                variant="outlined"
                                                size="small"
                                            />
                                            <TextField
                                                fullWidth
                                                label="API Key"
                                                type="password"
                                                defaultValue="****************"
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
                            </Grid>
                        </Box>
                    )}

                    {tabValue === 3 && (
                        <Box>
                            <Typography variant="h6" gutterBottom>
                                Security Settings
                            </Typography>
                            <List>
                                <ListItem>
                                    <ListItemIcon>
                                        <VpnKeyIcon />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="Two-Factor Authentication (2FA)"
                                        secondary="Add an extra layer of security to your account"
                                    />
                                    <Button variant="outlined" size="small">
                                        Enable 2FA
                                    </Button>
                                </ListItem>
                                <Divider variant="inset" component="li" />
                                <ListItem>
                                    <ListItemIcon>
                                        <SecurityIcon />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="Change Password"
                                        secondary="Update your account password"
                                    />
                                    <Button variant="outlined" size="small">
                                        Change Password
                                    </Button>
                                </ListItem>
                            </List>
                        </Box>
                    )}

                    {tabValue === 4 && (
                        <Box>
                            <Typography variant="h6" gutterBottom>
                                Notification Settings
                            </Typography>
                            <List>
                                <ListItem>
                                    <ListItemIcon>
                                        <NotificationsIcon />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="Email Notifications"
                                        secondary="Receive alerts and updates via email"
                                    />
                                    <Switch defaultChecked />
                                </ListItem>
                                <Divider variant="inset" component="li" />
                                <ListItem>
                                    <ListItemIcon>
                                        <NotificationsIcon />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="Optimization Completion"
                                        secondary="Notify me when a portfolio optimization run is complete"
                                    />
                                    <Switch defaultChecked />
                                </ListItem>
                                <Divider variant="inset" component="li" />
                                <ListItem>
                                    <ListItemIcon>
                                        <NotificationsIcon />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary="Risk Threshold Alerts"
                                        secondary="Notify me when portfolio risk exceeds a set threshold"
                                    />
                                    <Switch />
                                </ListItem>
                            </List>
                        </Box>
                    )}
                </CardContent>
            </Card>
        </Box>
    );
};

export default Settings;
