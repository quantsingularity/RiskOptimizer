import React, { useState, useEffect } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Alert,
  CircularProgress,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import RefreshIcon from "@mui/icons-material/Refresh";
import { usePortfolio } from "../context/PortfolioContext";
import { useAuth } from "../context/AuthContext";
import { formatCurrency, formatPercentage } from "../utils/formatters";

const PortfolioManagement = () => {
  const { user } = useAuth();
  const { portfolio, loading, error, fetchPortfolio, savePortfolio } =
    usePortfolio();
  const [openDialog, setOpenDialog] = useState(false);
  const [currentAsset, setCurrentAsset] = useState(null);
  const [formData, setFormData] = useState({
    symbol: "",
    name: "",
    quantity: "",
    purchasePrice: "",
  });

  useEffect(() => {
    if (user?.address) {
      fetchPortfolio(user.address);
    }
  }, [user, fetchPortfolio]);

  const handleOpenDialog = (asset = null) => {
    if (asset) {
      setCurrentAsset(asset);
      setFormData({
        symbol: asset.symbol || "",
        name: asset.name || "",
        quantity: asset.quantity || "",
        purchasePrice: asset.purchasePrice || "",
      });
    } else {
      setCurrentAsset(null);
      setFormData({
        symbol: "",
        name: "",
        quantity: "",
        purchasePrice: "",
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setCurrentAsset(null);
  };

  const handleInputChange = (field) => (event) => {
    setFormData((prev) => ({
      ...prev,
      [field]: event.target.value,
    }));
  };

  const handleSaveAsset = () => {
    // Save asset logic
    const newAsset = {
      id: currentAsset?.id || Date.now(),
      ...formData,
      quantity: parseFloat(formData.quantity),
      purchasePrice: parseFloat(formData.purchasePrice),
      currentPrice: parseFloat(formData.purchasePrice), // Mock current price
    };

    // Calculate total value
    newAsset.totalValue = newAsset.quantity * newAsset.currentPrice;
    newAsset.gain =
      (newAsset.currentPrice - newAsset.purchasePrice) * newAsset.quantity;
    newAsset.gainPercent =
      ((newAsset.currentPrice - newAsset.purchasePrice) /
        newAsset.purchasePrice) *
      100;

    // Update portfolio
    const updatedAssets = currentAsset
      ? portfolio.assets.map((a) => (a.id === currentAsset.id ? newAsset : a))
      : [...(portfolio?.assets || []), newAsset];

    savePortfolio({
      ...portfolio,
      assets: updatedAssets,
    });

    handleCloseDialog();
  };

  const handleDeleteAsset = (assetId) => {
    const updatedAssets = portfolio.assets.filter((a) => a.id !== assetId);
    savePortfolio({
      ...portfolio,
      assets: updatedAssets,
    });
  };

  const calculateTotalValue = () => {
    return (
      portfolio?.assets?.reduce(
        (sum, asset) => sum + (asset.totalValue || 0),
        0,
      ) || 0
    );
  };

  const calculateTotalGain = () => {
    return (
      portfolio?.assets?.reduce((sum, asset) => sum + (asset.gain || 0), 0) || 0
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

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
        <Typography variant="h4" component="h1">
          Portfolio Management
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => fetchPortfolio(user.address)}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Add Asset
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Portfolio Summary */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                Total Portfolio Value
              </Typography>
              <Typography variant="h4" sx={{ my: 1 }}>
                {formatCurrency(calculateTotalValue())}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                Total Gain/Loss
              </Typography>
              <Typography
                variant="h4"
                sx={{ my: 1 }}
                color={
                  calculateTotalGain() >= 0 ? "success.main" : "error.main"
                }
              >
                {formatCurrency(calculateTotalGain())}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                Number of Assets
              </Typography>
              <Typography variant="h4" sx={{ my: 1 }}>
                {portfolio?.assets?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Assets Table */}
      <Card>
        <CardHeader title="Your Assets" />
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Asset</TableCell>
                <TableCell align="right">Quantity</TableCell>
                <TableCell align="right">Purchase Price</TableCell>
                <TableCell align="right">Current Price</TableCell>
                <TableCell align="right">Total Value</TableCell>
                <TableCell align="right">Gain/Loss</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {portfolio?.assets?.length > 0 ? (
                portfolio.assets.map((asset) => (
                  <TableRow key={asset.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {asset.symbol}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {asset.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="right">{asset.quantity}</TableCell>
                    <TableCell align="right">
                      {formatCurrency(asset.purchasePrice)}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(asset.currentPrice)}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(asset.totalValue)}
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${formatPercentage(asset.gainPercent, 2, true)} (${formatCurrency(asset.gain)})`}
                        color={asset.gain >= 0 ? "success" : "error"}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(asset)}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteAsset(asset.id)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No assets found. Click "Add Asset" to get started.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Add/Edit Asset Dialog */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {currentAsset ? "Edit Asset" : "Add New Asset"}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Symbol"
            value={formData.symbol}
            onChange={handleInputChange("symbol")}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Asset Name"
            value={formData.name}
            onChange={handleInputChange("name")}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Quantity"
            type="number"
            value={formData.quantity}
            onChange={handleInputChange("quantity")}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Purchase Price"
            type="number"
            value={formData.purchasePrice}
            onChange={handleInputChange("purchasePrice")}
            margin="normal"
            required
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveAsset}>
            {currentAsset ? "Save Changes" : "Add Asset"}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PortfolioManagement;
