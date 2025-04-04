module.exports = {
    networks: {
      development: {
        host: "127.0.0.1",
        port: 8545,
        network_id: "*"
      },
      solana: {
        provider: () => new HDWalletProvider(
          process.env.MNEMONIC,
          `https://api.mainnet-beta.solana.com`
        ),
        network_id: 1,
        gas: 5500000,
        gasPrice: 1000000000
      }
    },
    compilers: {
      solc: {
        version: "0.8.0",
        settings: { optimizer: { enabled: true, runs: 200 } }
      }
    }
  };