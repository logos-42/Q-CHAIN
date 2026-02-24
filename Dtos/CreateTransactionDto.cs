using System;
using QuantumBlockchain.Models;

namespace QuantumBlockchain.Dtos
{
    /// <summary>
    /// 创建交易数据传输对象
    /// </summary>
    public class CreateTransactionDto
    {
        /// <summary>
        /// 交易类型
        /// </summary>
        public TransactionType Type { get; set; } = TransactionType.Transfer;

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
        /// 交易数据
        /// </summary>
        public string Data { get; set; }
    }
}
