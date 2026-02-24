import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// 区块链相关API
export const blockchainApi = {
  // 获取区块链
  getBlockchain: () => api.get('/blockchain'),
  
  // 获取区块链统计信息
  getStats: () => api.get('/blockchain/stats'),
  
  // 验证区块链
  validate: () => api.get('/blockchain/validate'),
};

// 区块相关API
export const blockApi = {
  // 获取最新区块
  getLatestBlock: () => api.get('/block/latest'),
  
  // 根据索引获取区块
  getBlock: (index) => api.get(`/block/${index}`),
  
  // 获取区块详情
  getBlockDetails: (index) => api.get(`/block/${index}/details`),
  
  // 获取区块范围
  getBlockRange: (start = 0, count = 10) => 
    api.get(`/block/range?start=${start}&count=${count}`),
  
  // 搜索区块
  searchBlocks: (query) => api.get(`/block/search?query=${encodeURIComponent(query)}`),
};

// 交易相关API
export const transactionApi = {
  // 获取所有交易
  getAllTransactions: () => api.get('/transaction'),
  
  // 根据ID获取交易
  getTransaction: (id) => api.get(`/transaction/${id}`),
  
  // 获取地址的交易历史
  getTransactionsByAddress: (address) => api.get(`/transaction/address/${address}`),
  
  // 创建新交易
  createTransaction: (transactionData) => api.post('/transaction', transactionData),
  
  // 获取交易统计
  getTransactionStats: () => api.get('/transaction/stats'),
  
  // 获取待处理交易
  getPendingTransactions: () => api.get('/transaction/pending'),
};

// 量子功能API
export const quantumApi = {
  // 生成量子随机数
  generateQuantumRandom: (count = 10) => api.get(`/quantum/random?count=${count}`),
  
  // 生成量子哈希
  generateQuantumHash: (input, outputSize = 64) => 
    api.post('/quantum/hash', { input, outputSize }),
  
  // 生成量子签名
  generateQuantumSignature: (message, privateKey) => 
    api.post('/quantum/sign', { message, privateKey }),
  
  // 量子密钥分发
  quantumKeyDistribution: (keyLength = 128) => 
    api.get(`/quantum/qkd?keyLength=${keyLength}`),
  
  // 量子挖矿
  quantumMining: (blockHash, difficulty = 4) => 
    api.post('/quantum/mine', { blockHash, difficulty }),
  
  // 生成量子纠缠态
  generateEntanglement: (stateType = 'bell', qubitCount = 2) => 
    api.get(`/quantum/entanglement?stateType=${stateType}&qubitCount=${qubitCount}`),
  
  // 生成量子时间戳
  generateQuantumTimestamp: () => api.get('/quantum/timestamp'),
};

// 导出默认API实例
export default api;