const PortfolioTracker = artifacts.require("PortfolioTracker");
const RiskManagement = artifacts.require("RiskManagement");

module.exports = async function (deployer) {
  await deployer.deploy(PortfolioTracker);
  await deployer.deploy(
    RiskManagement,
    "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",
  ); // ETH/USD Price Feed
};
