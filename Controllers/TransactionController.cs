using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using QuantumBlockchain.Dtos;
using QuantumBlockchain.Interfaces;
using QuantumBlockchain.Models;

namespace QuantumBlockchain.Controllers
{
    /// <summary>
    /// 交易API控制器
    /// 提供交易相关的API接口
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    public class TransactionController : ControllerBase
    {
        private readonly IBlockchainService _blockchainService;

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="blockchainService">区块链服务</param>
        public TransactionController(IBlockchainService blockchainService)
        {
            _blockchainService = blockchainService;
        }

        /// <summary>
        /// 获取所有交易
        /// </summary>
        /// <returns>交易列表</returns>
        [HttpGet]
        [ProducesResponseType(typeof(IEnumerable<Transaction>), 200)]
        public async Task<ActionResult<IEnumerable<Transaction>>> GetAllTransactions()
        {
            try
            {
                var blockchain = _blockchainService.GetBlockchain();
                var transactions = blockchain
                    .SelectMany(block => block.Data.Transactions)
                    .ToList();

                return Ok(transactions);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"获取交易列表失败: {ex.Message}" });
            }
        }

        /// <summary>
        /// 根据ID获取交易
        /// </summary>
        /// <param name="id">交易ID</param>
        /// <returns>交易信息</returns>
        [HttpGet("{id}")]
        [ProducesResponseType(typeof(Transaction), 200)]
        [ProducesResponseType(404, Type = typeof(string))]
        public async Task<ActionResult<Transaction>> GetTransaction(string id)
        {
            try
            {
                var blockchain = _blockchainService.GetBlockchain();
                var transaction = blockchain
                    .SelectMany(block => block.Data.Transactions)
                    .FirstOrDefault(tx => tx.Id == id);

                if (transaction == null)
                {
                    return NotFound($"交易 {id} 不存在");
                }

                return Ok(transaction);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"获取交易失败: {ex.Message}" });
            }
        }

        /// <summary>
        /// 获取地址的交易历史
        /// </summary>
        /// <param name="address">地址</param>
        /// <returns>交易历史</returns>
        [HttpGet("address/{address}")]
        [ProducesResponseType(typeof(AddressTransactions), 200)]
        [ProducesResponseType(400, Type = typeof(string))]
        public async Task<ActionResult<AddressTransactions>> GetTransactionsByAddress(string address)
        {
            try
            {
                if (string.IsNullOrWhiteSpace(address))
                {
                    return BadRequest("地址不能为空");
                }

                var transactions = _blockchainService.GetTransactionsByAddress(address);
                var balance = _blockchainService.GetBalance(address);

                var result = new AddressTransactions
                {
                    Address = address,
                    Balance = balance,
                    Transactions = transactions.ToList(),
                    IncomingTransactions = transactions.Where(tx => tx.To == address).ToList(),
                    OutgoingTransactions = transactions.Where(tx => tx.From == address).ToList()
                };

                return Ok(result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"获取地址交易历史失败: {ex.Message}" });
            }
        }

        /// <summary>
        /// 创建新交易
        /// </summary>
        /// <param name="createTransactionDto">创建交易DTO</param>
        /// <returns>交易结果</returns>
        [HttpPost]
        [ProducesResponseType(typeof(TransactionResult), 200)]
        [ProducesResponseType(400, Type = typeof(string))]
        public async Task<ActionResult<TransactionResult>> CreateTransaction([FromBody] CreateTransactionDto createTransactionDto)
        {
            try
            {
                if (!ModelState.IsValid)
                {
                    return BadRequest(ModelState);
                }

                var transaction = new Transaction
                {
                    Type = createTransactionDto.Type,
                    From = createTransactionDto.From,
                    To = createTransactionDto.To,
                    Amount = createTransactionDto.Amount,
                    Fee = createTransactionDto.Fee,
                    Data = createTransactionDto.Data ?? string.Empty,
                    Timestamp = DateTime.UtcNow
                };

                var success = await _blockchainService.AddTransactionAsync(transaction);

                if (success)
                {
                    var result = new TransactionResult
                    {
                        Success = true,
                        Message = "交易创建成功",
                        Transaction = transaction
                    };

                    return Ok(result);
                }
                else
                {
                    return BadRequest(new TransactionResult
                    {
                        Success = false,
                        Message = "交易创建失败，可能是余额不足或交易无效"
                    });
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, new TransactionResult
                {
                    Success = false,
                    Message = $"创建交易失败: {ex.Message}"
                });
            }
        }

        /// <summary>
        /// 获取交易统计信息
        /// </summary>
        /// <returns>统计信息</returns>
        [HttpGet("stats")]
        [ProducesResponseType(typeof(TransactionStats), 200)]
        public async Task<ActionResult<TransactionStats>> GetTransactionStats()
        {
            try
            {
                var blockchain = _blockchainService.GetBlockchain();
                var allTransactions = blockchain
                    .SelectMany(block => block.Data.Transactions)
                    .ToList();

                var stats = new TransactionStats
                {
                    TotalTransactions = allTransactions.Count,
                    TotalAmount = allTransactions.Sum(tx => tx.Amount),
                    TotalFees = allTransactions.Sum(tx => tx.Fee),
                    AverageAmount = allTransactions.Any() ? allTransactions.Average(tx => tx.Amount) : 0,
                    AverageFee = allTransactions.Any() ? allTransactions.Average(tx => tx.Fee) : 0,
                    TransactionTypes = allTransactions
                        .GroupBy(tx => tx.Type)
                        .Select(g => new TransactionTypeStats
                        {
                            Type = g.Key,
                            Count = g.Count(),
                            TotalAmount = g.Sum(tx => tx.Amount),
                            TotalFees = g.Sum(tx => tx.Fee)
                        })
                        .ToList(),
                    DailyStats = allTransactions
                        .GroupBy(tx => tx.Timestamp.Date)
                        .Select(g => new DailyTransactionStats
                        {
                            Date = g.Key,
                            Count = g.Count(),
                            TotalAmount = g.Sum(tx => tx.Amount),
                            TotalFees = g.Sum(tx => tx.Fee)
                        })
                        .OrderBy(d => d.Date)
                        .ToList()
                };

                return Ok(stats);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"获取交易统计失败: {ex.Message}" });
            }
        }

        /// <summary>
        /// 获取待处理交易
        /// </summary>
        /// <returns>待处理交易列表</returns>
        [HttpGet("pending")]
        [ProducesResponseType(typeof(IEnumerable<Transaction>), 200)]
        public async Task<ActionResult<IEnumerable<Transaction>>> GetPendingTransactions()
        {
            try
            {
                // 注意：当前实现中，待处理交易在挖矿后会被清空
                // 这里返回所有未确认的交易（状态为Pending的交易）
                var blockchain = _blockchainService.GetBlockchain();
                var pendingTransactions = blockchain
                    .SelectMany(block => block.Data.Transactions)
                    .Where(tx => tx.Status == TransactionStatus.Pending)
                    .ToList();

                return Ok(pendingTransactions);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = $"获取待处理交易失败: {ex.Message}" });
            }
        }
    }

    /// <summary>
    /// 地址交易信息
    /// </summary>
    public class AddressTransactions
    {
        /// <summary>
        /// 地址
        /// </summary>
        public string Address { get; set; }

        /// <summary>
        /// 余额
        /// </summary>
        public decimal Balance { get; set; }

        /// <summary>
        /// 所有交易
        /// </summary>
        public List<Transaction> Transactions { get; set; }

        /// <summary>
        /// 收入交易
        /// </summary>
        public List<Transaction> IncomingTransactions { get; set; }

        /// <summary>
        /// 支出交易
        /// </summary>
        public List<Transaction> OutgoingTransactions { get; set; }
    }

    /// <summary>
    /// 交易结果
    /// </summary>
    public class TransactionResult
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
        /// 交易信息
        /// </summary>
        public Transaction Transaction { get; set; }
    }

    /// <summary>
    /// 交易统计信息
    /// </summary>
    public class TransactionStats
    {
        /// <summary>
        /// 总交易数量
        /// </summary>
        public int TotalTransactions { get; set; }

        /// <summary>
        /// 总金额
        /// </summary>
        public decimal TotalAmount { get; set; }

        /// <summary>
        /// 总费用
        /// </summary>
        public decimal TotalFees { get; set; }

        /// <summary>
        /// 平均金额
        /// </summary>
        public decimal AverageAmount { get; set; }

        /// <summary>
        /// 平均费用
        /// </summary>
        public decimal AverageFee { get; set; }

        /// <summary>
        /// 按类型统计
        /// </summary>
        public List<TransactionTypeStats> TransactionTypes { get; set; }

        /// <summary>
        /// 按日期统计
        /// </summary>
        public List<DailyTransactionStats> DailyStats { get; set; }
    }

    /// <summary>
    /// 交易类型统计
    /// </summary>
    public class TransactionTypeStats
    {
        /// <summary>
        /// 交易类型
        /// </summary>
        public TransactionType Type { get; set; }

        /// <summary>
        /// 数量
        /// </summary>
        public int Count { get; set; }

        /// <summary>
        /// 总金额
        /// </summary>
        public decimal TotalAmount { get; set; }

        /// <summary>
        /// 总费用
        /// </summary>
        public decimal TotalFees { get; set; }
    }

    /// <summary>
    /// 每日交易统计
    /// </summary>
    public class DailyTransactionStats
    {
        /// <summary>
        /// 日期
        /// </summary>
        public DateTime Date { get; set; }

        /// <summary>
        /// 交易数量
        /// </summary>
        public int Count { get; set; }

        /// <summary>
        /// 总金额
        /// </summary>
        public decimal TotalAmount { get; set; }

        /// <summary>
        /// 总费用
        /// </summary>
        public decimal TotalFees { get; set; }
    }
}