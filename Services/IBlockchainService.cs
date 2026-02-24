using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using QuantumBlockchain.Models;

namespace QuantumBlockchain.Interfaces
{
    /// <summary>
    /// 区块链服务接口
    /// 定义区块链的核心业务逻辑
    /// </summary>
    public interface IBlockchainService
    {
        /// <summary>
        /// 获取区块链
        /// </summary>
        /// <returns>区块链列表</returns>
        IEnumerable<Block> GetBlockchain();

        /// <summary>
        /// 获取最新区块
        /// </summary>
        /// <returns>最新区块</returns>
        Block GetLatestBlock();

        /// <summary>
        /// 获取区块数量
        /// </summary>
        /// <returns>区块数量</returns>
        int GetBlockCount();

        /// <summary>
        /// 添加交易到待处理队列
        /// </summary>
        /// <param name="transaction">交易</param>
        /// <returns>是否成功</returns>
        Task<bool> AddTransactionAsync(Transaction transaction);

        /// <summary>
        /// 挖矿
        /// </summary>
        /// <param name="minerAddress">矿工地址</param>
        /// <param name="cancellationToken">取消令牌</param>
        /// <returns>挖矿结果</returns>
        Task<MiningResult> MineAsync(string minerAddress, CancellationToken cancellationToken = default);

        /// <summary>
        /// 验证区块链的完整性
        /// </summary>
        /// <returns>验证结果</returns>
        bool IsValid();

        /// <summary>
        /// 获取地址余额
        /// </summary>
        /// <param name="address">地址</param>
        /// <returns>余额</returns>
        decimal GetBalance(string address);

        /// <summary>
        /// 获取地址的交易历史
        /// </summary>
        /// <param name="address">地址</param>
        /// <returns>交易历史</returns>
        IEnumerable<Transaction> GetTransactionsByAddress(string address);
    }
}