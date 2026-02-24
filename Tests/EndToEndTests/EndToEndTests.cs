using System; 
using Xunit; 
using QuantumAlgorithms; 
 
namespace QuantumBlockchain.EndToEndTests { 
class EndToEndTests { 
[Fact] 
public void CompleteSystemTest_ShouldPass() { 
var blockchain = new Blockchain(); 
var quantumRandom = new QuantumRandom(); 
var quantumHash = new QuantumHash(); 
