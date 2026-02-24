// ============================================================================
// 量子区块链 Q# 驱动程序
// 用于从经典代码调用 Q# 量子算法
// ============================================================================

using System;
using Microsoft.Quantum.Simulation.Core;
using Microsoft.Quantum.Simulation.Simulators;
using QuantumBlockchain.Core;

namespace QuantumBlockchain.Driver
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("========================================");
            Console.WriteLine("   量子区块链 Q# 算法驱动程序");
            Console.WriteLine("========================================");
            Console.WriteLine();

            // 创建量子模拟器
            using var simulator = new QuantumSimulator();

            // 运行完整的量子区块链演示
            Console.WriteLine("运行量子区块链核心算法演示...\n");
            DemoQuantumBlockchain.Run(simulator).Wait();

            Console.WriteLine();
            Console.WriteLine("按任意键退出...");
            Console.ReadKey();
        }
    }
}
