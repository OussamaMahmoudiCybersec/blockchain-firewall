const path = require('path');

function buildCCPOrg1() {
    const ccpPath = path.resolve(__dirname, 'connection-org1.json');
    const ccp = JSON.parse(fs.readFileSync(ccpPath, 'utf8'));
    return ccp;
}

module.exports.buildCCPOrg1 = buildCCPOrg1;
