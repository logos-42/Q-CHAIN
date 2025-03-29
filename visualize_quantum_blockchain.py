#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子区块链可视化工具
用于展示量子区块链的结构和量子特性
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer  # 更新导入方式
from qiskit.visualization import plot_histogram, plot_bloch_multivector

# 导入我们的量子区块链实现
from quantum_blockchain import QuantumBlockchain, QuantumRandom, QuantumHash

def visualize_quantum_signature(quantum_signature: str):
    """
    可视化量子签名的位模式
    
    Args:
        quantum_signature: 二进制格式的量子签名
    """
    # 将二进制字符串转换为整数数组
    if len(quantum_signature) > 64:  # 限制大小以便于可视化
        quantum_signature = quantum_signature[:64]
    
    bits = np.array([int(bit) for bit in quantum_signature])
    
    # 创建图形
    plt.figure(figsize=(12, 4))
    plt.imshow(bits.reshape(1, -1), cmap='binary', aspect='auto')
    plt.title('量子签名位模式可视化')
    plt.xlabel('位索引')
    plt.yticks([])
    plt.colorbar(label='位值 (0/1)')
    plt.tight_layout()
    plt.savefig('quantum_signature_pattern.png')
    plt.close()
    print("量子签名位模式已保存为 'quantum_signature_pattern.png'")

def visualize_quantum_circuit():
    """可视化用于生成量子随机数的量子电路"""
    # 创建一个8量子比特的示例电路
    qc = QuantumCircuit(8, 8)
    
    # 添加门
    for i in range(8):
        qc.h(i)  # 哈达玛门（创建叠加）
    
    # 添加纠缠
    for i in range(7):
        qc.cx(i, i+1)  # CNOT门（创建纠缠）
    
    # 再次添加哈达玛门
    for i in range(8):
        qc.h(i)
    
    # 测量
    qc.measure(range(8), range(8))
    
    # 绘制电路
    circuit_diagram = qc.draw(output='mpl', filename='quantum_circuit.png')
    plt.close()  # 关闭自动显示的图形
    print("量子电路图已保存为 'quantum_circuit.png'")
    
    # 模拟电路并可视化结果分布
    simulator = Aer.get_backend('qasm_simulator')
    qc_compiled = transpile(qc, simulator)
    job = simulator.run(qc_compiled, shots=1024)
    result = job.result()
    counts = result.get_counts(qc)
    
    # 保存结果分布图
    plot_histogram(counts, filename='quantum_measurement_distribution.png', 
                  title='量子测量结果分布', figsize=(12, 6))
    plt.close()
    print("量子测量结果分布已保存为 'quantum_measurement_distribution.png'")

def visualize_blockchain_structure(blockchain):
    """
    可视化区块链结构
    
    Args:
        blockchain: QuantumBlockchain实例
    """
    chain_data = blockchain.get_chain_data()
    
    num_blocks = len(chain_data)
    if num_blocks == 0:
        print("区块链为空，无法可视化")
        return
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, num_blocks * 2))
    
    # 自定义颜色映射
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    # 为每个区块绘制一个矩形框
    for i, block in enumerate(chain_data):
        # 区块位置和大小
        rect = plt.Rectangle((0.1, i*1.5), 0.8, 1.0, facecolor=colors[i % len(colors)], 
                            alpha=0.7, edgecolor='black')
        ax.add_patch(rect)
        
        # 显示区块信息
        ax.text(0.5, i*1.5 + 0.5, 
               f"区块 #{block['index']}\n"
               f"哈希: {block['hash'][:8]}...\n"
               f"前一个哈希: {block['previous_hash'][:8]}...",
               ha='center', va='center', color='white', fontweight='bold')
        
        # 如果不是创世区块，绘制连接线
        if i > 0:
            ax.annotate('', xy=(0.5, i*1.5), xytext=(0.5, (i-1)*1.5 + 1.0),
                       arrowprops=dict(arrowstyle='->', color='black', lw=2))
    
    # 设置绘图区域
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, num_blocks * 1.5)
    ax.set_title('量子区块链结构')
    ax.set_aspect('equal')
    ax.set_axis_off()
    
    plt.tight_layout()
    plt.savefig('blockchain_structure.png')
    plt.close()
    print("区块链结构已保存为 'blockchain_structure.png'")

def visualize_quantum_state():
    """可视化量子状态的叠加和纠缠特性"""
    # 创建处于叠加态的两量子比特电路
    qc = QuantumCircuit(2)
    qc.h(0)  # 将第一个量子比特置于叠加态
    qc.cx(0, 1)  # 纠缠两个量子比特
    
    # 获取量子态向量
    simulator = Aer.get_backend('statevector_simulator')
    qc_compiled = transpile(qc, simulator)
    job = simulator.run(qc_compiled)
    result = job.result()
    statevector = result.get_statevector()
    
    # 绘制量子态的Bloch球表示
    bloch_fig = plot_bloch_multivector(statevector, filename='quantum_bloch_sphere.png')
    plt.close()
    print("量子状态的Bloch球表示已保存为 'quantum_bloch_sphere.png'")

def main():
    """主函数，展示量子区块链的可视化"""
    print("正在初始化量子区块链...")
    
    # 创建区块链实例
    blockchain = QuantumBlockchain()
    
    # 添加一些额外的区块用于演示
    blockchain.add_block({"message": "第一个交易区块", "amount": 50})
    blockchain.add_block({"message": "第二个交易区块", "amount": 100})
    
    print("\n开始可视化量子区块链特性...")
    
    # 可视化创世区块的量子签名
    genesis_block = blockchain.chain[0]
    visualize_quantum_signature(genesis_block.quantum_signature)
    
    # 可视化量子电路
    visualize_quantum_circuit()
    
    # 可视化区块链结构
    visualize_blockchain_structure(blockchain)
    
    # 可视化量子状态
    visualize_quantum_state()
    
    print("\n可视化完成！所有图像已保存。")
    
if __name__ == "__main__":
    main() 