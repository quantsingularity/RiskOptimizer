const RiskManagement = artifacts.require("RiskManagement");

contract("RiskManagement", (accounts) => {
  let instance;
  const ETH_USD_FEED = "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"; // Chainlink Mainnet

  before(async () => {
    instance = await RiskManagement.new(ETH_USD_FEED);
  });

  it("should calculate volatility", async () => {
    const volatility = await instance.calculateVolatility(30);
    assert(volatility > 0, "Invalid volatility calculation");
  });
});
