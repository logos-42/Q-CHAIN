#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子区块链实现
这个程序展示了如何使用量子计算原理实现区块链的创世区块
"""

import hashlib
import json
import time
import datetime as dt
from typing import Dict, List, Any, Optional

# 量子计算相关库
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram

class QuantumRandom:
    """量子随机数生成器类"""
    
    @staticmethod
    def generate_random_bits(num_bits: int = 256) -> str:
        """
        使用量子电路生成随机比特串
        
        Args:
            num_bits: 要生成的随机比特数量
            
        Returns:
            一个随机的二进制字符串
        """
        # 每个块的最大量子比特数，避免超过模拟器的限制
        max_qubits_per_chunk = 16  # 安全值，低于Qiskit模拟器的28比特限制
        
        # 初始化结果存储
        result_bits = ""
        
        # 分块生成随机比特
        remaining_bits = num_bits
        while remaining_bits > 0:
            # 计算这个块需要多少比特
            chunk_size = min(remaining_bits, max_qubits_per_chunk)
            
            # 创建量子电路
            qc = QuantumCircuit(chunk_size, chunk_size)
            
            # 将所有量子位置于叠加态
            for i in range(chunk_size):
                qc.h(i)
                
            # 测量所有量子位
            qc.measure(range(chunk_size), range(chunk_size))
            
            # 在模拟器上执行电路
            simulator = Aer.get_backend('qasm_simulator')
            qc_compiled = transpile(qc, simulator)
            job = simulator.run(qc_compiled, shots=1)
            result = job.result()
            counts = result.get_counts(qc)
            
            # 获取唯一的测量结果（因为我们只有一个shot）
            chunk_bitstring = list(counts.keys())[0]
            
            # 确保长度正确（考虑到Qiskit可能会移除前导零）
            chunk_bitstring = chunk_bitstring.zfill(chunk_size)
            
            # 追加到结果
            result_bits += chunk_bitstring
            
            # 更新剩余比特数
            remaining_bits -= chunk_size
        
        return result_bits
    
    @staticmethod
    def bitstring_to_hex(bitstring: str) -> str:
        """
        将二进制字符串转换为十六进制表示
        
        Args:
            bitstring: 二进制字符串
            
        Returns:
            十六进制字符串
        """
        # 确保位字符串长度是4的倍数（16进制的一个字符对应4位二进制）
        padding = len(bitstring) % 4
        if padding != 0:
            bitstring = '0' * (4 - padding) + bitstring
            
        # 将二进制字符串转换为十六进制
        return hex(int(bitstring, 2))[2:]  # 去掉'0x'前缀

class QuantumHash:
    """量子哈希函数类"""
    
    @staticmethod
    def quantum_hash(data: str, output_size: int = 64) -> str:
        """
        对输入数据应用量子增强型哈希函数
        
        Args:
            data: 要哈希的数据
            output_size: 输出哈希的位数
            
        Returns:
            哈希字符串（十六进制）
        """
        # 首先使用传统哈希函数
        sha256_hash = hashlib.sha256(data.encode()).hexdigest()
        
        # 使用哈希结果生成量子电路的初始状态
        seed = int(sha256_hash, 16) % (2**32)
        np.random.seed(seed)
        
        # 创建量子电路 - 使用更小的量子比特数量
        num_qubits = 8  # 使用8个量子比特，安全地低于Qiskit模拟器的限制
        qc = QuantumCircuit(num_qubits, num_qubits)
        
        # 基于输入数据设置量子电路
        for i in range(num_qubits):
            if np.random.random() > 0.5:
                qc.x(i)  # 应用X门（比特翻转）
            qc.h(i)      # 应用H门（创建叠加）
            
        # 添加纠缠
        for i in range(num_qubits-1):
            qc.cx(i, i+1)
            
        # 基于原始数据的ASCII值进行额外的门操作
        for char in data:
            ascii_val = ord(char)
            target_qubit = ascii_val % num_qubits
            
            # 根据ASCII值选择不同的量子门
            op_selector = (ascii_val // num_qubits) % 4
            if op_selector == 0:
                qc.x(target_qubit)
            elif op_selector == 1:
                qc.z(target_qubit)
            elif op_selector == 2:
                qc.h(target_qubit)
            else:
                if target_qubit < num_qubits - 1:
                    qc.cx(target_qubit, (target_qubit + 1) % num_qubits)
                    
        # 最终的哈希步骤
        for i in range(num_qubits):
            qc.h(i)
        
        # 测量
        qc.measure(range(num_qubits), range(num_qubits))
        
        # 在模拟器上执行电路
        simulator = Aer.get_backend('qasm_simulator')
        qc_compiled = transpile(qc, simulator)
        job = simulator.run(qc_compiled, shots=1024)
        result = job.result()
        counts = result.get_counts(qc)
        
        # 使用测量结果概率分布作为额外的熵源
        probability_string = ""
        total_shots = sum(counts.values())
        
        # 按照比特字符串排序，确保结果确定性
        for bitstring in sorted(counts.keys()):
            # 将每个结果的概率转换为二进制表示的小数（取后8位）
            prob = counts[bitstring] / total_shots
            prob_bin = format(int(prob * 256), '08b')
            probability_string += prob_bin
        
        # 将概率字符串与原始哈希组合
        combined = sha256_hash + probability_string
        
        # 再次应用SHA-256
        final_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        # 截断到所需大小
        return final_hash[:output_size]

class Block:
    """区块链中的区块类"""
    
    def __init__(
        self, 
        index: int, 
        timestamp: float, 
        data: Any, 
        previous_hash: str, 
        quantum_signature: Optional[str] = None
    ):
        """
        初始化新的区块
        
        Args:
            index: 区块索引
            timestamp: 时间戳
            data: 区块中存储的数据
            previous_hash: 前一个区块的哈希
            quantum_signature: 可选，区块的量子签名
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.quantum_signature = quantum_signature or self._generate_quantum_signature()
        self.hash = self._calculate_hash()
        
    def _generate_quantum_signature(self) -> str:
        """生成区块的量子签名"""
        # 使用量子随机数生成器创建随机签名
        return QuantumRandom.generate_random_bits(128)
    
    def _calculate_hash(self) -> str:
        """计算区块的哈希值，包括量子增强"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "quantum_signature": self.quantum_signature
        }, sort_keys=True)
        
        # 使用我们的量子哈希函数
        return QuantumHash.quantum_hash(block_string)
    
    def to_dict(self) -> Dict:
        """将区块转换为字典"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "quantum_signature": self.quantum_signature,
            "hash": self.hash
        }

class QuantumBlockchain:
    """量子增强型区块链类"""
    
    def __init__(self):
        """初始化一个新的区块链，创建创世区块"""
        self.chain: List[Block] = []
        self._create_genesis_block()
        
    def _create_genesis_block(self) -> None:
        """创建并添加创世区块"""
        # 创世区块的特殊量子签名
        genesis_quantum_signature = QuantumRandom.generate_random_bits(256)
        quantum_sig_hex = QuantumRandom.bitstring_to_hex(genesis_quantum_signature)
        
        # 创建创世区块
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            data={"message": "量子区块链的创世区块", "quantum_state": quantum_sig_hex},
            previous_hash="0" * 64,  # 创世区块没有前一个哈希
            quantum_signature=genesis_quantum_signature
        )
        
        self.chain.append(genesis_block)
        print(f"创世区块已创建! 哈希: {genesis_block.hash}")
        
    @property
    def last_block(self) -> Block:
        """获取最后一个区块"""
        return self.chain[-1]
    
    def add_block(self, data: Any) -> Block:
        """
        向区块链添加新区块
        
        Args:
            data: 要存储在区块中的数据
            
        Returns:
            新创建的区块
        """
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=data,
            previous_hash=self.last_block.hash
        )
        
        self.chain.append(new_block)
        return new_block
    
    def is_chain_valid(self) -> bool:
        """验证区块链的完整性"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # 检查当前区块的哈希是否正确
            if current_block.hash != current_block._calculate_hash():
                print(f"区块 {i} 的哈希无效")
                return False
            
            # 检查区块链接是否正确
            if current_block.previous_hash != previous_block.hash:
                print(f"区块 {i} 与前一个区块的链接无效")
                return False
        
        return True
    
    def get_chain_data(self) -> List[Dict]:
        """获取整个区块链的数据"""
        return [block.to_dict() for block in self.chain]

def main():
    """主函数，展示量子区块链的创建和使用"""
    print("正在初始化量子区块链...")
    
    # 创建区块链实例
    quantum_blockchain = QuantumBlockchain()
    
    # 显示创世区块的详细信息
    genesis_block = quantum_blockchain.chain[0]
    print("\n创世区块信息:")
    print(f"索引: {genesis_block.index}")
    print(f"时间戳: {dt.datetime.fromtimestamp(genesis_block.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据: {genesis_block.data}")
    print(f"前一个哈希: {genesis_block.previous_hash}")
    print(f"量子签名: {genesis_block.quantum_signature[:20]}... (已截断)")
    print(f"哈希: {genesis_block.hash}")
    
    print("\n区块链已成功初始化!")

if __name__ == "__main__":
    main() 