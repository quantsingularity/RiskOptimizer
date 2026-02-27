const PortfolioTracker = artifacts.require("PortfolioTracker");

contract("PortfolioTracker", (accounts) => {
  it("should update portfolio", async () => {
    const portfolioTrackerInstance = await PortfolioTracker.deployed();

    const assets = ["BTC", "ETH"];
    const allocations = [5000, 5000];

    await portfolioTrackerInstance.updatePortfolio(assets, allocations, {
      from: accounts[0],
    });

    const portfolio = await portfolioTrackerInstance.getPortfolio(accounts[0]);

    assert.deepEqual(portfolio[0], assets, "Assets do not match");
    assert.deepEqual(
      portfolio[1].map((a) => a.toNumber()),
      allocations,
      "Allocations do not match",
    );
  });

  it("should fail with invalid input", async () => {
    const portfolioTrackerInstance = await PortfolioTracker.deployed();

    const assets = ["BTC", "ETH"];
    const allocations = [5000];

    try {
      await portfolioTrackerInstance.updatePortfolio(assets, allocations, {
        from: accounts[0],
      });
      assert.fail("The transaction should have failed");
    } catch (error) {
      assert.include(
        error.message,
        "Invalid input",
        "Error message should contain 'Invalid input'",
      );
    }
  });

  it("should fail if allocations do not sum to 10000", async () => {
    const portfolioTrackerInstance = await PortfolioTracker.deployed();

    const assets = ["BTC", "ETH"];
    const allocations = [5000, 4000];

    try {
      await portfolioTrackerInstance.updatePortfolio(assets, allocations, {
        from: accounts[0],
      });
      assert.fail("The transaction should have failed");
    } catch (error) {
      assert.include(
        error.message,
        "Allocations must sum to 100%",
        "Error message should contain 'Allocations must sum to 100%'",
      );
    }
  });
});
