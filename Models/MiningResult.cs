using System;

namespace QuantumBlockchain.Models
{
    /// <summary>
    /// 挖矿结果
    /// </summary>
    public class MiningResult
    {
        /// <summary>
        /// 是否成功
        /// </summary>
        public bool Success { get; set; }

        /// <summary>
        /// 消息
        /// </summary>
        public string Message { get; set; }

        /// <summary>
        /// 挖到的区块
        /// </summary>
        public Block Block { get; set; }

        /// <summary>
        /// 区块哈希
        /// </summary>
        public string Hash { get; set; }

        /// <summary>
        /// 使用的Nonce值
        /// </summary>
        public long Nonce { get; set; }

        /// <summary>
        /// 挖矿耗时
        /// </summary>
        public TimeSpan Duration { get; set; }
    }
}
