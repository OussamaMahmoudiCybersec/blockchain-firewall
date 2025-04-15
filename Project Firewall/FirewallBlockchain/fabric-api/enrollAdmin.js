const fs = require('fs'); // Make sure this line is at the top
const path = require('path');
const { FileSystemWallet, Gateway } = require('fabric-network');
const FabricCAServices = require('fabric-ca-client');
const { buildCCPOrg1 } = require('./AppUtil.js'); // Utility to build connection profile

async function enrollAdmin() {
    try {
        console.log('Starting enrollment process for admin...');

        // Build the connection profile for Org1
        const ccp = buildCCPOrg1();

        // Create a new CA client for interacting with the CA.
        const caInfo = ccp.certificateAuthorities['ca.org1.example.com'];
        const ca = new FabricCAServices(caInfo.url, {
            trustedRoots: caInfo.tlsCACerts.pem,
            verify: false // Disable certificate verification
        }, caInfo.caName);

        // Create a wallet to hold the credentials of the admin user
        const walletPath = path.join(__dirname, 'wallet');
        const wallet = new FileSystemWallet(walletPath);

        // Check if the admin user is already enrolled
        const adminExists = await wallet.exists('admin');
        if (adminExists) {
            console.log('Admin user already exists in the wallet');
            return;
        }

        // Enroll the admin user
        console.log('Enrolling admin...');
        const enrollment = await ca.enroll({
            enrollmentID: 'admin',
            enrollmentSecret: 'adminpw',
        });

        // Add the admin credentials to the wallet
        const identity = {
            credentials: {
                certificate: enrollment.certificate,
                privateKey: enrollment.key.toBytes(),
            },
            mspId: 'Org1MSP',
            type: 'X.509',
        };
        await wallet.import('admin', identity);
        console.log('Admin enrolled successfully!');
    } catch (error) {
        console.error(`Failed to enroll admin: ${error}`);
    }
}

enrollAdmin();
