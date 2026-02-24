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
    /// 区块API控制器
    /// 提供区块相关的API接口
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    public class BlockController : ControllerBase
    {
        private readonly IBlockchainService _blockchainService;

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="blockchainService">区块链服务</param>
        public BlockController(IBlockchainService blockchainService)
        {
            _blockchainService = blockchainService;
        }

        /// <summary>
        /// 获取最新区块
        /// </summary>
        /// <returns>最新区块</returns>
        [HttpGet("latest")]
        [ProducesResponseType(typeof(Block), 200)]
        [ProducesResponseType(404, Type = typeof(string))]
        public async Task<ActionResult<Block>> GetLatestBlock()
        {
            try
            {
                var latestBlock = _blockchainService.GetLatestBlock();
                if (latestBlock == null)
                {
                    return NotFound("区块链为空");
                }

                return Ok(latestBlock);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"获取最新区块失败: {ex.Message}" });
            }
        }

        /// <summary>
        /// 根据索引获取区块
        /// </summary>
        /// <param name="index">区块索引</param>
        /// <returns>区块信息</returns>
        [HttpGet("{index}")]
        [ProducesResponseType(typeof(Block), 200)]
        [ProducesResponseType(404, Type = typeof(string))]
        public async Task<ActionResult<Block>> GetBlock(int index)
        {
            try
            {
                var blockchain = _blockchainService.GetBlockchain().ToList();
                
                if (index < 0 || index >= blockchain.Count)
                {
                    return NotFound($"区块索引 {index} 不存在");
                }

                var block = blockchain[index];
                return Ok(block);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"获取区块失败: {ex.Message}" });
            }
        }

        /// <summary>
        /// 获取区块详情
        /// </summary>
        /// <param name="index">区块索引</param>
        /// <returns>区块详情</returns>
        [HttpGet("{index}/details")]
        [ProducesResponseType(typeof(BlockDetails), 200)]
        [ProducesResponseType(404, Type = typeof(string))]
        public async Task<ActionResult<BlockDetails>> GetBlockDetails(int index)
        {
            try
            {
                var blockchain = _blockchainService.GetBlockchain().ToList();
                
                if (index < 0 || index >= blockchain.Count)
                {
                    return NotFound($"区块索引 {index} 不存在");
                }

                var block = blockchain[index];
                var details = new BlockDetails
                {
                    Block = block,
                    TransactionCount = block.Data.Transactions.Count,
                    TotalAmount = block.Data.Transactions.Sum(t => t.Amount),
                    TotalFee = block.Data.Transactions.Sum(t => t.Fee),
                    AverageTransactionSize = block.Data.Transactions.Any() 
                        ? block.Data.Transactions.Average(t => t.EstimateSize()) 
                        : 0
                };

                return Ok(details);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"获取区块详情失败: {ex.Message}" });
            }
        }

        /// <summary>
        /// 获取区块范围
        /// </summary>
        /// <param name="start">起始索引</param>
        /// <param name="count">数量</param>
        /// <returns>区块列表</returns>
        [HttpGet("range")]
        [ProducesResponseType(typeof(IEnumerable<Block>), 200)]
        public async Task<ActionResult<IEnumerable<Block>>> GetBlockRange(
            [FromQuery] int start = 0,
            [FromQuery] int count = 10)
        {
            try
            {
                var blockchain = _blockchainService.GetBlockchain().ToList();
                
                // 验证参数
                if (start < 0) start = 0;
                if (count <= 0) count = 10;
                if (count > 100) count = 100; // 限制最大数量

                var blocks = blockchain
                    .Skip(start)
                    .Take(count)
                    .ToList();

                return Ok(blocks);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"获取区块范围失败: {ex.Message}" });
            }
        }

        /// <summary>
        /// 搜索区块
        /// </summary>
        /// <param name="query">搜索关键词</param>
        /// <returns>搜索结果</returns>
        [HttpGet("search")]
        [ProducesResponseType(typeof(SearchResult), 200)]
        public async Task<ActionResult<SearchResult>> SearchBlocks([FromQuery] string query)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(query))
                {
                    return BadRequest("搜索关键词不能为空");
                }

                var blockchain = _blockchainService.GetBlockchain().ToList();
                var results = new SearchResult
                {
                    Query = query,
                    Blocks = new List<BlockSearchResult>(),
                    Transactions = new List<TransactionSearchResult>()
                };

                // 搜索区块
                foreach (var block in blockchain)
                {
                    if (block.Index.ToString() == query || 
                        block.Hash.Contains(query) ||
                        block.QuantumSignature.Contains(query))
                    {
                        results.Blocks.Add(new BlockSearchResult
                        {
                            BlockIndex = block.Index,
                            BlockHash = block.Hash,
                            Timestamp = block.Timestamp,
                            TransactionCount = block.Data.Transactions.Count
                        });
                    }

                    // 搜索区块内的交易
                    foreach (var transaction in block.Data.Transactions)
                    {
                        var transactionString = $"{transaction.Id}{transaction.From}{transaction.To}{transaction.Data}";
                        if (transactionString.Contains(query, StringComparison.OrdinalIgnoreCase))
                        {
                            results.Transactions.Add(new TransactionSearchResult
                            {
                                TransactionId = transaction.Id,
                                BlockIndex = block.Index,
                                BlockHash = block.Hash,
                                From = transaction.From,
                                To = transaction.To,
                                Amount = transaction.Amount,
                                Timestamp = transaction.Timestamp
                            });
                        }
                    }
                }

                return Ok(results);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"搜索失败: {ex.Message}" });
            }
        }
    }

    /// <summary>
    /// 区块详情
    /// </summary>
    public class BlockDetails
    {
        /// <summary>
        /// 区块信息
        /// </summary>
        public Block Block { get; set; }

        /// <summary>
        /// 交易数量
        /// </summary>
        public int TransactionCount { get; set; }

        /// <summary>
        /// 总金额
        /// </summary>
        public decimal TotalAmount { get; set; }

        /// <summary>
        /// 总费用
        /// </summary>
        public decimal TotalFee { get; set; }

        /// <summary>
        /// 平均交易大小
        /// </summary>
        public double AverageTransactionSize { get; set; }
    }

    /// <summary>
    /// 区块搜索结果
    /// </summary>
    public class BlockSearchResult
    {
        /// <summary>
        /// 区块索引
        /// </summary>
        public int BlockIndex { get; set; }

        /// <summary>
        /// 区块哈希
        /// </summary>
        public string BlockHash { get; set; }

        /// <summary>
        /// 时间戳
        /// </summary>
        public DateTime Timestamp { get; set; }

        /// <summary>
        /// 交易数量
        /// </summary>
        public int TransactionCount { get; set; }
    }

    /// <summary>
    /// 交易搜索结果
    /// </summary>
    public class TransactionSearchResult
    {
        /// <summary>
        /// 交易ID
        /// </summary>
        public string TransactionId { get; set; }

        /// <summary>
        /// 区块索引
        /// </summary>
        public int BlockIndex { get; set; }

        /// <summary>
        /// 区块哈希
        /// </summary>
        public string BlockHash { get; set; }

        /// <summary>
        /// 发送方
        /// </summary>
        public string From { get; set; }

        /// <summary>
        /// 接收方
        /// </summary>
        public string To { get; set; }

        /// <summary>
        /// 金额
        /// </summary>
        public decimal Amount { get; set; }

        /// <summary>
        /// 时间戳
        /// </summary>
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// 搜索结果
    /// </summary>
    public class SearchResult
    {
        /// <summary>
        /// 搜索关键词
        /// </summary>
        public string Query { get; set; }

        /// <summary>
        /// 区块搜索结果
        /// </summary>
        public List<BlockSearchResult> Blocks { get; set; }

        /// <summary>
        /// 交易搜索结果
        /// </summary>
        public List<TransactionSearchResult> Transactions { get; set; }
    }
}