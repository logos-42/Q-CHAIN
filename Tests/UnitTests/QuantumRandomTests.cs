using System; 
using Xunit; 
using FluentAssertions; 
using QuantumAlgorithms; 
 
namespace QuantumBlockchain.UnitTests { 
class QuantumRandomTests { 
[Fact] 
public void GenerateRandomNumber_ShouldReturnPositiveInteger() { 
var quantumRandom = new QuantumRandom(); 
var result = quantumRandom.GenerateRandomNumber(); 
result.Should().BeGreaterThan(0); 
} 
} 
} 
