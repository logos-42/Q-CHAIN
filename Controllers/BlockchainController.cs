using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using QuantumBlockchain.Interfaces;
using QuantumBlockchain.Models;

namespace QuantumBlockchain.Controllers
{
    /// <summary>
    /// 区块链API控制器
    /// 提供区块链的核心API接口
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    public class BlockchainController : ControllerBase
    {
        private readonly IBlockchainService _blockchainService;

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="blockchainService">区块链服务</param>
        public BlockchainController(IBlockchainService blockchainService)
        {
            _blockchainService = blockchainService;
        }

        /// <summary>
        /// 获取完整区块链
        /// </summary>
        /// <returns>区块链数据</returns>
        [HttpGet]
        [ProducesResponseType(typeof(IEnumerable<Block>), 200)]
        public async Task<ActionResult<IEnumerable<Block>>> GetBlockchain()
        {
            try
            {
                var blockchain = _blockchainService.GetBlockchain();
                return Ok(blockchain);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"获取区块链失败: {ex.Message}" });
            }
        }

        /// <summary>
        /// 获取区块链统计信息
        /// </summary>
        /// <returns>统计信息</returns>
        [HttpGet("stats")]
        [ProducesResponseType(typeof(BlockchainStats), 200)]
        public async Task<ActionResult<BlockchainStats>> GetStats()
        {
            try
            {
                var stats = new BlockchainStats
                {
                    BlockCount = _blockchainService.GetBlockCount(),
                    IsValid = _blockchainService.IsValid(),
                    LatestBlock = _blockchainService.GetLatestBlock(),
                    TotalTransactions = _blockchainService.GetBlockchain()
                        .Sum(b => b.Data.Transactions.Count),
                    TotalSize = _blockchainService.GetBlockchain()
                        .Sum(b => b.BlockSize)
                };

                return Ok(stats);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"获取统计信息失败: {ex.Message}" });
            }
        }

        /// <summary>
        /// 验证区块链完整性
        /// </summary>
        /// <returns>验证结果</returns>
        [HttpGet("validate")]
        [ProducesResponseType(typeof(ValidationResult), 200)]
        public async Task<ActionResult<ValidationResult>> Validate()
        {
            try
            {
                var isValid = _blockchainService.IsValid();
                var result = new ValidationResult
                {
                    IsValid = isValid,
                    Message = isValid ? "区块链验证通过" : "区块链验证失败"
                };

                return Ok(result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"验证区块链失败: {ex.Message}" });
            }
        }
    }

    /// <summary>
    /// 区块链统计信息
    /// </summary>
    public class BlockchainStats
    {
        /// <summary>
        /// 区块数量
        /// </summary>
        public int BlockCount { get; set; }

        /// <summary>
        /// 区块链是否有效
        /// </summary>
        public bool IsValid { get; set; }

        /// <summary>
        /// 最新区块
        /// </summary>
        public Block LatestBlock { get; set; }

        /// <summary>
        /// 总交易数量
        /// </summary>
        public int TotalTransactions { get; set; }

        /// <summary>
        /// 总大小（字节）
        /// </summary>
        public long TotalSize { get; set; }
    }

    /// <summary>
    /// 验证结果
    /// </summary>
    public class ValidationResult
    {
        /// <summary>
        /// 是否有效
        /// </summary>
        public bool IsValid { get; set; }

        /// <summary>
        /// 消息
        /// </summary>
        public string Message { get; set; }
    }
}