module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",    // Localhost (default: none)
      port: 7545,           // Ganache default port
      network_id: "*",      // Any network (default: none)
      from: "0xe8B282EF76A9b61f1240d933737FeDc5f9f43f45",  // Your account address from Ganache
      gas: 6721975,         // Gas limit (default: 6721975)
      gasPrice: 20000000000 // Gas price in wei (default: 20000000000)
    }
  },

  compilers: {
    solc: {
      version: "0.8.0"  // Specify the Solidity version
    }
  }
};
