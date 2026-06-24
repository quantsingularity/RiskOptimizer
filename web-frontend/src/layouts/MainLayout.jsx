import { Box, useMediaQuery, useTheme } from "@mui/material";
import { useState } from "react";
import { Outlet } from "react-router-dom";
import Footer from "../components/navigation/Footer";
import Header from "../components/navigation/Header";
import Sidebar from "../components/navigation/Sidebar";

const DRAWER_WIDTH = 240;

const MainLayout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => setMobileOpen((prev) => !prev);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Header onMenuClick={handleDrawerToggle} />
      <Box sx={{ display: "flex", flex: 1 }}>
        <Sidebar
          mobileOpen={mobileOpen}
          onClose={handleDrawerToggle}
          isMobile={isMobile}
        />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            // The sidebar nav box already reserves its width in this flex row,
            // so the main area only needs to fill the remaining space. Adding a
            // left margin here would double-count the sidebar and leave a large
            // empty band between the sidebar and the page content.
            minWidth: 0,
            p: { xs: 2, sm: 3 },
            minHeight: "calc(100vh - 64px)",
          }}
        >
          {/* Spacer to clear the fixed AppBar */}
          <Box sx={{ mt: { xs: 7, sm: 8 }, mb: 2 }}>
            <Outlet />
          </Box>
        </Box>
      </Box>
      <Box sx={{ ml: { xs: 0, sm: `${DRAWER_WIDTH}px` } }}>
        <Footer />
      </Box>
    </Box>
  );
};

export default MainLayout;
