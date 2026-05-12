// 組態檔案
const development = require('./development');

const ENV = process.env.NODE_ENV || 'development';

const envConfig = {
  development,
};

const config = envConfig[ENV];

// 合併密鑰；待辦：改用 './secretKey'
Object.assign(config, require('./_secretKey'));

module.exports = config;
