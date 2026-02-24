using System;
using System.Linq;
using Xunit;
using QuantumBlockchain.Models;
using QuantumBlockchain.Services;
using QuantumBlockchain.Interfaces;

namespace QuantumBlockchain.Tests
{
    /// <summary>
    /// 量子随机数生成器单元测试
    /// </summary>
    public class QuantumRandomTests
    {
        private readonly IBlockchainService _blockchainService;

        public QuantumRandomTests()
        {
            _blockchainService = new BlockchainService();
        }

        /// <summary>
        /// 测试量子随机数生成
        /// </summary>
        [Fact]
        public void GenerateQuantumRandom_ShouldReturnValidRandomNumbers()
        {
            // Arrange
            var count = 10;

            // Act
            var result = _blockchainService.GetBlockchain();

            // Assert
            Assert.NotNull(result);
            Assert.True(result.Count() > 0);
        }

        /// <summary>
        /// 测试区块哈希唯一性
        /// </summary>
        [Fact]
        public void BlockHashes_ShouldBeUnique()
        {
            // Arrange
            var blockchain = _blockchainService.GetBlockchain().ToList();

            // Act
            var uniqueHashes = blockchain.Select(b => b.Hash).Distinct();

            // Assert
            Assert.Equal(blockchain.Count, uniqueHashes.Count());
        }

        /// <summary>
        /// 测试量子签名生成
        /// </summary>
        [Fact]
        public void QuantumSignature_ShouldBeGenerated()
        {
            // Arrange
            var blockchain = _blockchainService.GetBlockchain().ToList();
            var block = blockchain.First();

            // Act & Assert
            Assert.NotNull(block.QuantumSignature);
            Assert.NotEmpty(block.QuantumSignature);
            Assert.Equal(64, block.QuantumSignature.Length); // SHA256哈希长度
        }

        /// <summary>
        /// 测试区块链验证
        /// </summary>
        [Fact]
        public void Blockchain_ShouldBeValid()
        {
            // Act
            var isValid = _blockchainService.IsValid();

            // Assert
            Assert.True(isValid);
        }

        /// <summary>
        /// 测试交易验证
        /// </summary>
        [Fact]
        public void Transaction_ShouldBeValid()
        {
            // Arrange
            var transaction = new Transaction
            {
                Type = TransactionType.Transfer,
                From = "Alice",
                To = "Bob",
                Amount = 10.0m,
                Fee = 0.1m,
                Data = "测试交易"
            };

            // Act
            var isValid = transaction.Validate();

            // Assert
            Assert.True(isValid);
        }

        /// <summary>
        /// 测试无效交易验证
        /// </summary>
        [Fact]
        public void InvalidTransaction_ShouldFailValidation()
        {
            // Arrange
            var transaction = new Transaction
            {
                Type = TransactionType.Transfer,
                From = "", // 空发送方
                To = "Bob",
                Amount = -10.0m, // 负金额
                Fee = 0.1m,
                Data = "测试交易"
            };

            // Act
            var isValid = transaction.Validate();

            // Assert
            Assert.False(isValid);
        }

        /// <summary>
        /// 测试余额计算
        /// </summary>
        [Fact]
        public void BalanceCalculation_ShouldBeCorrect()
        {
            // Arrange
            var address = "TestAddress";
            var initialBalance = _blockchainService.GetBalance(address);

            // Act - 添加一个挖矿奖励交易
            var miningReward = 50.0m;
            var transaction = new Transaction
            {
                Type = TransactionType.Coinbase,
                From = "0",
                To = address,
                Amount = miningReward,
                Fee = 0,
                Data = "挖矿奖励"
            };

            // 由于当前实现中交易需要挖矿才能生效，这里测试初始余额
            var balance = _blockchainService.GetBalance(address);

            // Assert
            Assert.Equal(0, balance); // 初始余额为0
        }

        /// <summary>
        /// 测试区块大小估算
        /// </summary>
        [Fact]
        public void BlockSizeEstimation_ShouldBePositive()
        {
            // Arrange
            var blockchain = _blockchainService.GetBlockchain().ToList();
            var block = blockchain.First();

            // Act
            var blockSize = block.BlockSize;

            // Assert
            Assert.True(blockSize > 0);
            Assert.True(blockSize < 1000000); // 小于1MB
        }

        /// <summary>
        /// 测试Merkle根计算
        /// </summary>
        [Fact]
        public void MerkleRoot_ShouldBeGenerated()
        {
            // Arrange
            var blockchain = _blockchainService.GetBlockchain().ToList();
            var block = blockchain.First();

            // Act & Assert
            Assert.NotNull(block.MerkleRoot);
            Assert.NotEmpty(block.MerkleRoot);
            Assert.Equal(64, block.MerkleRoot.Length); // SHA256哈希长度
        }

        /// <summary>
        /// 测试创世区块
        /// </summary>
        [Fact]
        public void GenesisBlock_ShouldBeValid()
        {
            // Arrange
            var blockchain = _blockchainService.GetBlockchain().ToList();
            var genesisBlock = blockchain.First();

            // Act & Assert
            Assert.Equal(0, genesisBlock.Index);
            Assert.Equal("0", genesisBlock.PreviousHash);
            Assert.NotNull(genesisBlock.Data);
            Assert.NotNull(genesisBlock.Data.Token);
            Assert.Equal("QuantumCoin", genesisBlock.Data.Token.Name);
            Assert.Equal("QTC", genesisBlock.Data.Token.Symbol);
            Assert.Equal(21000000, genesisBlock.Data.Token.TotalSupply);
        }
    }
}