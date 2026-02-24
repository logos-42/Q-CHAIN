using System; 
using Xunit; 
using QuantumAlgorithms; 
 
namespace QuantumBlockchain.IntegrationTests { 
class BlockchainIntegrationTests { 
[Fact] 
public void FullBlockchainWorkflow_ShouldWorkCorrectly() { 
var blockchain = new Blockchain(); 
blockchain.AddBlock("Transaction 1"); 
blockchain.AddBlock("Transaction 2"); 
blockchain.AddBlock("Transaction 3"); 
Assert.True(blockchain.IsValid()); 
Assert.Equal(4, blockchain.Chain.Count); 
} 
} 
} 
