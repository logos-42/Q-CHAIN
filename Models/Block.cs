using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace QuantumBlockchain.Models
{
    /// <summary>
    /// 区块链区块模型
    /// 包含区块的基本信息和量子特性
    /// </summary>
    public class Block
    {
        /// <summary>
        /// 区块索引
        /// </summary>
        public int Index { get; set; }

        /// <summary>
        /// 区块创建时间戳
        /// </summary>
        public DateTime Timestamp { get; set; }

        /// <summary>
        /// 区块数据
        /// </summary>
        public BlockData Data { get; set; }

        /// <summary>
        /// 前一个区块的哈希值
        /// </summary>
        public string PreviousHash { get; set; }

        /// <summary>
        /// 当前区块的哈希值
        /// </summary>
        public string Hash { get; set; }

        /// <summary>
        /// 量子签名
        /// 使用量子算法生成的不可伪造签名
        /// </summary>
        public string QuantumSignature { get; set; }

        /// <summary>
        /// 随机数（用于挖矿）
        /// </summary>
        public long Nonce { get; set; }

        /// <summary>
        /// Merkle树根哈希
        /// </summary>
        public string MerkleRoot { get; set; }

        /// <summary>
        /// 区块高度（与Index相同，但更语义化）
        /// </summary>
        [JsonIgnore]
        public int Height => Index;

        /// <summary>
        /// 交易数量
        /// </summary>
        [JsonIgnore]
        public int TransactionCount => Data?.Transactions?.Count ?? 0;

        /// <summary>
        /// 区块大小（估算）
        /// </summary>
        [JsonIgnore]
        public long BlockSize => CalculateBlockSize();

        /// <summary>
        /// 构造函数
        /// </summary>
        public Block()
        {
            Timestamp = DateTime.UtcNow;
            Data = new BlockData();
            PreviousHash = string.Empty;
            Hash = string.Empty;
            QuantumSignature = string.Empty;
            Nonce = 0;
            MerkleRoot = string.Empty;
        }

        /// <summary>
        /// 计算区块大小
        /// </summary>
        private long CalculateBlockSize()
        {
            long size = 0;
            
            // 基本字段大小估算
            size += sizeof(int); // Index
            size += sizeof(long); // Timestamp ticks
            size += sizeof(long); // Nonce
            size += (PreviousHash?.Length ?? 0) * 2; // Unicode
            size += (Hash?.Length ?? 0) * 2;
            size += (QuantumSignature?.Length ?? 0) * 2;
            size += (MerkleRoot?.Length ?? 0) * 2;

            // 数据大小
            if (Data != null)
            {
                size += Data.EstimateSize();
            }

            return size;
        }

        /// <summary>
        /// 计算区块的字符串表示（用于哈希计算）
        /// </summary>
        /// <returns>区块的字符串表示</returns>
        public string ToBlockString()
        {
            return $"{Index}{Timestamp.ToUniversalTime().ToString("o")}{Data?.ToJson() ?? ""}{PreviousHash}{Nonce}";
        }

        /// <summary>
        /// 验证区块的完整性
        /// </summary>
        /// <returns>验证结果</returns>
        public bool Validate()
        {
            // 检查基本字段
            if (string.IsNullOrEmpty(Hash) || Hash.Length != 64)
                return false;

            if (string.IsNullOrEmpty(PreviousHash))
                return false;

            // 检查时间戳
            if (Timestamp > DateTime.UtcNow.AddMinutes(10))
                return false;

            // 检查数据
            if (Data == null)
                return false;

            // 检查量子签名
            if (string.IsNullOrEmpty(QuantumSignature))
                return false;

            return true;
        }

        /// <summary>
        /// 获取区块的详细信息
        /// </summary>
        /// <returns>区块详细信息字符串</returns>
        public string GetDetails()
        {
            return $@"
区块高度: {Index}
时间戳: {Timestamp:yyyy-MM-dd HH:mm:ss}
交易数量: {TransactionCount}
区块大小: {BlockSize} 字节
前一区块哈希: {PreviousHash}
当前区块哈希: {Hash}
量子签名: {QuantumSignature}
随机数: {Nonce}
Merkle根: {MerkleRoot}
";
        }
    }

    /// <summary>
    /// 区块数据模型
    /// </summary>
    public class BlockData
    {
        /// <summary>
        /// 区块消息
        /// </summary>
        public string Message { get; set; } = "量子区块链区块";

        /// <summary>
        /// 交易列表
        /// </summary>
        public List<Transaction> Transactions { get; set; } = new List<Transaction>();

        /// <summary>
        /// 量子密钥
        /// </summary>
        public string QuantumKey { get; set; } = string.Empty;

        /// <summary>
        /// 代币信息（如果这是创世区块）
        /// </summary>
        public TokenInfo Token { get; set; }

        /// <summary>
        /// 额外的元数据
        /// </summary>
        public Dictionary<string, object> Metadata { get; set; } = new Dictionary<string, object>();

        /// <summary>
        /// 构造函数
        /// </summary>
        public BlockData()
        {
            Timestamp = DateTime.UtcNow;
        }

        /// <summary>
        /// 时间戳
        /// </summary>
        public DateTime Timestamp { get; set; }

        /// <summary>
        /// 估算数据大小
        /// </summary>
        public long EstimateSize()
        {
            long size = 0;
            
            size += (Message?.Length ?? 0) * 2;
            size += (QuantumKey?.Length ?? 0) * 2;
            
            if (Token != null)
            {
                size += 100; // 粗略估算
            }

            foreach (var transaction in Transactions)
            {
                size += transaction.EstimateSize();
            }

            return size;
        }

        /// <summary>
        /// 转换为JSON字符串
        /// </summary>
        public string ToJson()
        {
            return System.Text.Json.JsonSerializer.Serialize(this);
        }
    }

    /// <summary>
    /// 代币信息模型
    /// </summary>
    public class TokenInfo
    {
        /// <summary>
        /// 代币名称
        /// </summary>
        public string Name { get; set; } = "QuantumCoin";

        /// <summary>
        /// 代币符号
        /// </summary>
        public string Symbol { get; set; } = "QTC";

        /// <summary>
        /// 总供应量
        /// </summary>
        public long TotalSupply { get; set; } = 21000000;

        /// <summary>
        /// 小数位数
        /// </summary>
        public int Decimals { get; set; } = 8;

        /// <summary>
        /// 创建者地址
        /// </summary>
        public string Creator { get; set; } = "量子创世地址";
    }
}