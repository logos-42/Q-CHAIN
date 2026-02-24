using System;
using System.Text.Json.Serialization;

namespace QuantumBlockchain.Models
{
    /// <summary>
    /// 交易模型
    /// 代表区块链中的一个交易记录
    /// </summary>
    public class Transaction
    {
        /// <summary>
        /// 交易ID（哈希值）
        /// </summary>
        public string Id { get; set; }

        /// <summary>
        /// 交易类型
        /// </summary>
        public TransactionType Type { get; set; }

        /// <summary>
        /// 发送方地址
        /// </summary>
        public string From { get; set; }

        /// <summary>
        /// 接收方地址
        /// </summary>
        public string To { get; set; }

        /// <summary>
        /// 交易金额
        /// </summary>
        public decimal Amount { get; set; }

        /// <summary>
        /// 交易费用
        /// </summary>
        public decimal Fee { get; set; }

        /// <summary>
        /// 交易时间戳
        /// </summary>
        public DateTime Timestamp { get; set; }

        /// <summary>
        /// 交易数据（JSON字符串）
        /// </summary>
        public string Data { get; set; } = string.Empty;

        /// <summary>
        /// 交易签名
        /// </summary>
        public string Signature { get; set; } = string.Empty;

        /// <summary>
        /// 量子签名（使用量子算法生成）
        /// </summary>
        public string QuantumSignature { get; set; } = string.Empty;

        /// <summary>
        /// 交易状态
        /// </summary>
        public TransactionStatus Status { get; set; } = TransactionStatus.Pending;

        /// <summary>
        /// 区块高度（交易被打包的区块高度）
        /// </summary>
        public int? BlockHeight { get; set; }

        /// <summary>
        /// 交易在区块中的索引
        /// </summary>
        public int? TransactionIndex { get; set; }

        /// <summary>
        /// 构造函数
        /// </summary>
        public Transaction()
        {
            Timestamp = DateTime.UtcNow;
            Id = GenerateTransactionId();
        }

        /// <summary>
        /// 生成交易ID
        /// </summary>
        private string GenerateTransactionId()
        {
            // 使用时间戳和随机数生成唯一ID
            var random = new Random();
            var timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
            var randomPart = random.Next(1000, 9999);
            return $"TX_{timestamp}_{randomPart}";
        }

        /// <summary>
        /// 计算交易的字符串表示（用于哈希计算）
        /// </summary>
        /// <returns>交易的字符串表示</returns>
        public string ToTransactionString()
        {
            return $"{Type}{From}{To}{Amount}{Fee}{Timestamp.ToUniversalTime().ToString("o")}{Data}";
        }

        /// <summary>
        /// 验证交易的完整性
        /// </summary>
        /// <returns>验证结果</returns>
        public bool Validate()
        {
            // 检查基本字段
            if (string.IsNullOrEmpty(Id))
                return false;

            if (string.IsNullOrEmpty(From) || string.IsNullOrEmpty(To))
                return false;

            if (Amount <= 0)
                return false;

            if (Fee < 0)
                return false;

            // 检查时间戳
            if (Timestamp > DateTime.UtcNow.AddMinutes(10))
                return false;

            return true;
        }

        /// <summary>
        /// 估算交易大小
        /// </summary>
        /// <returns>交易大小（字节）</returns>
        public long EstimateSize()
        {
            long size = 0;
            
            size += (Id?.Length ?? 0) * 2;
            size += (From?.Length ?? 0) * 2;
            size += (To?.Length ?? 0) * 2;
            size += (Data?.Length ?? 0) * 2;
            size += (Signature?.Length ?? 0) * 2;
            size += (QuantumSignature?.Length ?? 0) * 2;
            
            size += sizeof(decimal) * 2; // Amount + Fee
            size += sizeof(long); // Timestamp ticks
            size += sizeof(int) * 2; // Type + Status

            return size;
        }

        /// <summary>
        /// 获取交易的详细信息
        /// </summary>
        /// <returns>交易详细信息字符串</returns>
        public string GetDetails()
        {
            return $@"
交易ID: {Id}
类型: {Type}
发送方: {From}
接收方: {To}
金额: {Amount}
费用: {Fee}
时间: {Timestamp:yyyy-MM-dd HH:mm:ss}
状态: {Status}
区块高度: {BlockHeight ?? 0}
交易索引: {TransactionIndex ?? 0}
";
        }
    }

    /// <summary>
    /// 交易类型枚举
    /// </summary>
    [JsonConverter(typeof(JsonStringEnumConverter))]
    public enum TransactionType
    {
        /// <summary>
        /// 转账交易
        /// </summary>
        Transfer,

        /// <summary>
        /// 挖矿奖励
        /// </summary>
        Coinbase,

        /// <summary>
        /// 消息交易
        /// </summary>
        Message,

        /// <summary>
        /// 智能合约调用
        /// </summary>
        ContractCall,

        /// <summary>
        /// 代币转账
        /// </summary>
        TokenTransfer,

        /// <summary>
        /// 代币创建
        /// </summary>
        TokenCreation
    }

    /// <summary>
    /// 交易状态枚举
    /// </summary>
    [JsonConverter(typeof(JsonStringEnumConverter))]
    public enum TransactionStatus
    {
        /// <summary>
        /// 待处理
        /// </summary>
        Pending,

        /// <summary>
        /// 已确认
        /// </summary>
        Confirmed,

        /// <summary>
        /// 失败
        /// </summary>
        Failed,

        /// <summary>
        /// 已取消
        /// </summary>
        Cancelled
    }
}