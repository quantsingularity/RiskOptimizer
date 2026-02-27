import React from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
} from "@mui/material";
import {
  Home as HomeIcon,
  TrendingUp as OptimizeIcon,
  Analytics as RiskIcon,
  Settings as SettingsIcon,
} from "@mui/icons-material";
import { Link } from "react-router-dom";

const drawerWidth = 240;

const navItems = [
  { name: "Dashboard", icon: <HomeIcon />, path: "/" },
  { name: "Portfolio Optimization", icon: <OptimizeIcon />, path: "/optimize" },
  { name: "Risk Analysis", icon: <RiskIcon />, path: "/risk" },
  { name: "Settings", icon: <SettingsIcon />, path: "/settings" },
];

const MainLayout = ({ children }) => {
  return (
    <Box sx={{ display: "flex" }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            RiskOptimizer
          </Typography>
          <Button color="inherit">Connect Wallet (Placeholder)</Button>
        </Toolbar>
      </AppBar>

      {/* Side Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            boxSizing: "border-box",
          },
        }}
      >
        <Toolbar /> {/* Spacer for the AppBar */}
        <Box sx={{ overflow: "auto" }}>
          <List>
            {navItems.map((item) => (
              <ListItem key={item.name} disablePadding>
                <ListItemButton component={Link} to={item.path}>
                  <ListItemIcon>{item.icon}</ListItemIcon>
                  <ListItemText primary={item.name} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
          <Divider />
          <List>
            <ListItem disablePadding>
              <ListItemButton>
                <ListItemText primary="Help & Support" />
              </ListItemButton>
            </ListItem>
          </List>
        </Box>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar /> {/* Spacer for the AppBar */}
        {children}
      </Box>
    </Box>
  );
};

export default MainLayout;
