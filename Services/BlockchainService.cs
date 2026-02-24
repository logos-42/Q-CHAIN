using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using QuantumBlockchain.Models;
using QuantumBlockchain.Interfaces;

namespace QuantumBlockchain.Services
{
    /// <summary>
    /// 区块链服务实现
    /// 负责区块链的核心业务逻辑
    /// </summary>
    public class BlockchainService : IBlockchainService
    {
        private readonly List<Block> _chain;
        private readonly List<Transaction> _pendingTransactions;
        private readonly object _lock = new object();
        private readonly int _difficulty;
        private readonly decimal _miningReward;
        private readonly string _targetPrefix;

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="difficulty">挖矿难度</param>
        /// <param name="miningReward">挖矿奖励</param>
        public BlockchainService(int difficulty = 4, decimal miningReward = 50.0m)
        {
            _chain = new List<Block>();
            _pendingTransactions = new List<Transaction>();
            _difficulty = difficulty;
            _miningReward = miningReward;
            _targetPrefix = new string('0', _difficulty);
            
            // 初始化创世区块
            CreateGenesisBlock();
        }

        /// <summary>
        /// 创建创世区块
        /// </summary>
        private void CreateGenesisBlock()
        {
            var genesisData = new BlockData
            {
                Message = "量子区块链创世区块",
                QuantumKey = GenerateQuantumKey(),
                Token = new TokenInfo
                {
                    Name = "QuantumCoin",
                    Symbol = "QTC",
                    TotalSupply = 21000000,
                    Decimals = 8,
                    Creator = "量子创世地址"
                }
            };

            var genesisBlock = new Block
            {
                Index = 0,
                Timestamp = DateTime.UtcNow,
                Data = genesisData,
                PreviousHash = "0",
                Hash = CalculateHash(0, DateTime.UtcNow, genesisData, "0", 0),
                QuantumSignature = GenerateQuantumSignature(genesisData),
                Nonce = 0,
                MerkleRoot = CalculateMerkleRoot(genesisData.Transactions)
            };

            _chain.Add(genesisBlock);
        }

        /// <summary>
        /// 获取区块链
        /// </summary>
        public IEnumerable<Block> GetBlockchain()
        {
            lock (_lock)
            {
                return _chain.ToList();
            }
        }

        /// <summary>
        /// 获取最新区块
        /// </summary>
        public Block GetLatestBlock()
        {
            lock (_lock)
            {
                return _chain.LastOrDefault();
            }
        }

        /// <summary>
        /// 获取区块数量
        /// </summary>
        public int GetBlockCount()
        {
            lock (_lock)
            {
                return _chain.Count;
            }
        }

        /// <summary>
        /// 添加交易到待处理队列
        /// </summary>
        /// <param name="transaction">交易</param>
        /// <returns>是否成功</returns>
        public Task<bool> AddTransactionAsync(Transaction transaction)
        {
            if (!transaction.Validate())
                return Task.FromResult(false);

            lock (_lock)
            {
                // 检查余额（包含待处理交易）
                if (transaction.Type == TransactionType.Transfer)
                {
                    var balance = GetBalanceWithPending(transaction.From);
                    if (balance < transaction.Amount + transaction.Fee)
                        return Task.FromResult(false);
                }

                _pendingTransactions.Add(transaction);
                return Task.FromResult(true);
            }
        }

        /// <summary>
        /// 挖矿
        /// </summary>
        /// <param name="minerAddress">矿工地址</param>
        /// <param name="cancellationToken">取消令牌</param>
        /// <returns>挖矿结果</returns>
        public Task<MiningResult> MineAsync(string minerAddress, CancellationToken cancellationToken = default)
        {
            lock (_lock)
            {
                // 创建挖矿奖励交易
                var miningRewardTransaction = new Transaction
                {
                    Type = TransactionType.Coinbase,
                    From = "0", // 系统地址
                    To = minerAddress,
                    Amount = _miningReward,
                    Fee = 0,
                    Data = "挖矿奖励",
                    Timestamp = DateTime.UtcNow
                };

                // 创建新区块
                var latestBlock = GetLatestBlock();
                var newBlock = new Block
                {
                    Index = latestBlock.Index + 1,
                    Timestamp = DateTime.UtcNow,
                    Data = new BlockData
                    {
                        Message = $"区块 #{latestBlock.Index + 1}",
                        Transactions = new List<Transaction>(_pendingTransactions),
                        QuantumKey = GenerateQuantumKey()
                    },
                    PreviousHash = latestBlock.Hash
                };

                // 添加挖矿奖励交易
                newBlock.Data.Transactions.Insert(0, miningRewardTransaction);

                // 计算Merkle根
                newBlock.MerkleRoot = CalculateMerkleRoot(newBlock.Data.Transactions);

                // 执行挖矿（寻找合适的Nonce）
                var miningResult = MineBlock(newBlock, cancellationToken);

                if (miningResult.Success)
                {
                    // 添加到区块链
                    _chain.Add(miningResult.Block);
                    
                    // 清空待处理交易
                    _pendingTransactions.Clear();

                    return Task.FromResult(miningResult);
                }

                return Task.FromResult(new MiningResult { Success = false, Message = "挖矿失败" });
            }
        }

        /// <summary>
        /// 执行挖矿算法
        /// </summary>
        /// <param name="block">区块</param>
        /// <param name="cancellationToken">取消令牌</param>
        /// <returns>挖矿结果</returns>
        private MiningResult MineBlock(Block block, CancellationToken cancellationToken)
        {
            var startTime = DateTime.UtcNow;

            while (!cancellationToken.IsCancellationRequested)
            {
                // 检查是否超过最大Nonce值
                if (block.Nonce >= long.MaxValue)
                {
                    return new MiningResult
                    {
                        Success = false,
                        Message = "Nonce溢出，挖矿失败"
                    };
                }

                // 计算哈希
                var hash = CalculateHash(block.Index, block.Timestamp, block.Data, block.PreviousHash, block.Nonce);

                // 检查是否满足难度要求
                if (hash.StartsWith(_targetPrefix))
                {
                    var endTime = DateTime.UtcNow;
                    var duration = endTime - startTime;

                    block.Hash = hash;
                    block.QuantumSignature = GenerateQuantumSignature(block.Data);

                    return new MiningResult
                    {
                        Success = true,
                        Block = block,
                        Hash = hash,
                        Nonce = block.Nonce,
                        Duration = duration,
                        Message = $"挖矿成功！找到有效哈希：{hash}"
                    };
                }

                block.Nonce++;
            }

            return new MiningResult
            {
                Success = false,
                Message = "挖矿已取消"
            };
        }

        /// <summary>
        /// 验证区块链的完整性
        /// </summary>
        /// <returns>验证结果</returns>
        public bool IsValid()
        {
            lock (_lock)
            {
                for (int i = 1; i < _chain.Count; i++)
                {
                    var currentBlock = _chain[i];
                    var previousBlock = _chain[i - 1];

                    // 验证区块哈希
                    var hash = CalculateHash(currentBlock.Index, currentBlock.Timestamp, currentBlock.Data, currentBlock.PreviousHash, currentBlock.Nonce);
                    if (hash != currentBlock.Hash)
                        return false;

                    // 验证区块链接
                    if (currentBlock.PreviousHash != previousBlock.Hash)
                        return false;

                    // 验证区块内容
                    if (!currentBlock.Validate())
                        return false;
                }

                return true;
            }
        }

        /// <summary>
        /// 获取地址余额（包含待处理交易）
        /// </summary>
        /// <param name="address">地址</param>
        /// <returns>余额</returns>
        public decimal GetBalance(string address)
        {
            lock (_lock)
            {
                return GetBalanceWithPending(address);
            }
        }

        /// <summary>
        /// 获取地址余额（包含待处理交易）
        /// </summary>
        /// <param name="address">地址</param>
        /// <returns>余额</returns>
        private decimal GetBalanceWithPending(string address)
        {
            decimal balance = 0;

            // 从已确认区块计算余额
            foreach (var block in _chain)
            {
                foreach (var transaction in block.Data.Transactions)
                {
                    if (transaction.From == address)
                        balance -= transaction.Amount + transaction.Fee;

                    if (transaction.To == address)
                        balance += transaction.Amount;
                }
            }

            // 加上待处理交易的影响
            foreach (var transaction in _pendingTransactions)
            {
                if (transaction.From == address)
                    balance -= transaction.Amount + transaction.Fee;

                if (transaction.To == address)
                    balance += transaction.Amount;
            }

            return balance;
        }

        /// <summary>
        /// 获取地址的交易历史
        /// </summary>
        /// <param name="address">地址</param>
        /// <returns>交易历史</returns>
        public IEnumerable<Transaction> GetTransactionsByAddress(string address)
        {
            lock (_lock)
            {
                return _chain
                    .SelectMany(block => block.Data.Transactions)
                    .Where(tx => tx.From == address || tx.To == address)
                    .ToList();
            }
        }

        /// <summary>
        /// 计算区块哈希
        /// </summary>
        /// <param name="index">索引</param>
        /// <param name="timestamp">时间戳</param>
        /// <param name="data">数据</param>
        /// <param name="previousHash">前一区块哈希</param>
        /// <param name="nonce">随机数</param>
        /// <returns>哈希值</returns>
        private string CalculateHash(int index, DateTime timestamp, BlockData data, string previousHash, long nonce)
        {
            var blockString = $"{index}{timestamp.ToUniversalTime().ToString("o")}{data.ToJson()}{previousHash}{nonce}";
            using var sha256 = SHA256.Create();
            var hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(blockString));
            return BitConverter.ToString(hashBytes).Replace("-", "").ToLower();
        }

        /// <summary>
        /// 生成量子密钥
        /// </summary>
        /// <returns>量子密钥</returns>
        private string GenerateQuantumKey()
        {
            // 这里应该调用Q#的量子随机数生成器
            // 目前使用伪随机数作为占位符
            using var rng = RandomNumberGenerator.Create();
            var bytes = new byte[32];
            rng.GetBytes(bytes);
            return BitConverter.ToString(bytes).Replace("-", "").ToLower();
        }

        /// <summary>
        /// 生成量子签名
        /// </summary>
        /// <param name="data">数据</param>
        /// <returns>量子签名</returns>
        private string GenerateQuantumSignature(BlockData data)
        {
            // 这里应该调用Q#的量子签名算法
            // 目前使用SHA256作为占位符
            var dataString = data.ToJson();
            using var sha256 = SHA256.Create();
            var hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(dataString));
            return BitConverter.ToString(hashBytes).Replace("-", "").ToLower();
        }

        /// <summary>
        /// 计算Merkle树根
        /// </summary>
        /// <param name="transactions">交易列表</param>
        /// <returns>Merkle根</returns>
        private string CalculateMerkleRoot(List<Transaction> transactions)
        {
            if (transactions == null || transactions.Count == 0)
                return string.Empty;

            var hashes = transactions.Select(tx => CalculateTransactionHash(tx)).ToList();

            while (hashes.Count > 1)
            {
                if (hashes.Count % 2 != 0)
                {
                    hashes.Add(hashes.Last()); // 复制最后一个元素
                }

                var newHashes = new List<string>();
                for (int i = 0; i < hashes.Count; i += 2)
                {
                    var combined = hashes[i] + hashes[i + 1];
                    using var sha256 = SHA256.Create();
                    var hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(combined));
                    newHashes.Add(BitConverter.ToString(hashBytes).Replace("-", "").ToLower());
                }

                hashes = newHashes;
            }

            return hashes[0];
        }

        /// <summary>
        /// 计算交易哈希
        /// </summary>
        /// <param name="transaction">交易</param>
        /// <returns>交易哈希</returns>
        private string CalculateTransactionHash(Transaction transaction)
        {
            var txString = transaction.ToTransactionString();
            using var sha256 = SHA256.Create();
            var hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(txString));
            return BitConverter.ToString(hashBytes).Replace("-", "").ToLower();
        }
    }
}