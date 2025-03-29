#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
实际私有区块链实现
这个程序实现了一个真实的区块链，包括创世区块的创建和代币发行功能
"""

import hashlib
import json
import time
import datetime as dt
import os
import random
import binascii
from typing import Dict, List, Any, Optional, Tuple, Set
import socket
import threading
import argparse
from collections import defaultdict

class CryptoUtils:
    """加密实用工具类"""
    
    @staticmethod
    def generate_random_bits(num_bits: int = 256) -> str:
        """
        生成随机比特串
        
        Args:
            num_bits: 要生成的随机比特数量
            
        Returns:
            一个随机的二进制字符串
        """
        # 使用操作系统的加密安全随机数生成器
        random_bytes = os.urandom(num_bits // 8)
        
        # 转换为二进制字符串
        result_bits = ""
        for byte in random_bytes:
            result_bits += format(byte, '08b')
            
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
    
    @staticmethod
    def secure_hash(data: str, output_size: int = 64) -> str:
        """
        对输入数据应用安全哈希函数
        
        Args:
            data: 要哈希的数据
            output_size: 输出哈希的字符数（十六进制）
            
        Returns:
            哈希字符串（十六进制）
        """
        # 首先使用SHA-256
        sha256_hash = hashlib.sha256(data.encode()).hexdigest()
        
        # 使用哈希结果生成额外的随机性
        salt = os.urandom(16)  # 使用真正的随机盐
        salted_data = sha256_hash.encode() + salt
        
        # 再次应用SHA-256
        final_hash = hashlib.sha256(salted_data).hexdigest()
        
        # 截断到所需大小
        return final_hash[:output_size]

class KeyPair:
    """密钥对类，用于区块链中的签名和验证"""
    
    def __init__(self, private_key=None):
        """
        初始化密钥对
        
        Args:
            private_key: 可选的私钥（十六进制字符串），若为None则生成新密钥
        """
        if private_key:
            self.private_key = private_key
        else:
            # 生成新的私钥
            random_bits = CryptoUtils.generate_random_bits(256)
            self.private_key = CryptoUtils.bitstring_to_hex(random_bits)
            
        # 从私钥生成"公钥"（实际实现应使用椭圆曲线密码学）
        self.public_key = hashlib.sha256(self.private_key.encode()).hexdigest()
    
    def sign(self, data: str) -> str:
        """
        对数据进行签名
        
        Args:
            data: 要签名的数据
            
        Returns:
            签名（十六进制字符串）
        """
        message = data + self.private_key
        return hashlib.sha256(message.encode()).hexdigest()
    
    def verify(self, data: str, signature: str) -> bool:
        """
        验证签名
        
        Args:
            data: 原始数据
            signature: 签名
            
        Returns:
            验证是否通过
        """
        return self.sign(data) == signature

class Token:
    """代币类，用于管理代币相关操作"""
    
    def __init__(self, name: str, symbol: str, decimals: int = 18, total_supply: int = 100000000000):
        """
        初始化代币
        
        Args:
            name: 代币名称
            symbol: 代币符号
            decimals: 代币精度（小数位数）
            total_supply: 代币总供应量
        """
        self.name = name
        self.symbol = symbol
        self.decimals = decimals
        self.total_supply = total_supply
        self.balances = defaultdict(int)  # 地址 -> 余额的映射
        self.allowed = defaultdict(lambda: defaultdict(int))  # 地址 -> (地址 -> 授权金额)的映射
    
    def initial_distribution(self, creator_address: str):
        """
        初始代币分配给创建者
        
        Args:
            creator_address: 创建者地址
        """
        self.balances[creator_address] = self.total_supply
    
    def balance_of(self, owner: str) -> int:
        """
        查询地址余额
        
        Args:
            owner: 地址
            
        Returns:
            余额
        """
        return self.balances[owner]
    
    def transfer(self, sender: str, recipient: str, amount: int) -> bool:
        """
        转移代币
        
        Args:
            sender: 发送者地址
            recipient: 接收者地址
            amount: 转移数量
            
        Returns:
            是否成功
        """
        if self.balances[sender] < amount:
            return False
        
        self.balances[sender] -= amount
        self.balances[recipient] += amount
        return True
    
    def approve(self, owner: str, spender: str, amount: int) -> bool:
        """
        授权代币给其他地址使用
        
        Args:
            owner: 所有者地址
            spender: 被授权地址
            amount: 授权数量
            
        Returns:
            是否成功
        """
        self.allowed[owner][spender] = amount
        return True
    
    def allowance(self, owner: str, spender: str) -> int:
        """
        查询授权额度
        
        Args:
            owner: 所有者地址
            spender: 被授权地址
            
        Returns:
            授权额度
        """
        return self.allowed[owner][spender]
    
    def transfer_from(self, spender: str, owner: str, recipient: str, amount: int) -> bool:
        """
        从授权中转移代币
        
        Args:
            spender: 被授权地址（执行转账的地址）
            owner: 所有者地址
            recipient: 接收者地址
            amount: 转移数量
            
        Returns:
            是否成功
        """
        if self.balances[owner] < amount or self.allowed[owner][spender] < amount:
            return False
        
        self.balances[owner] -= amount
        self.balances[recipient] += amount
        self.allowed[owner][spender] -= amount
        return True
    
    def to_dict(self) -> Dict:
        """
        将代币信息转换为字典
        
        Returns:
            代币信息字典
        """
        return {
            "name": self.name,
            "symbol": self.symbol,
            "decimals": self.decimals,
            "total_supply": self.total_supply,
            "balances": dict(self.balances),
            "allowed": {k: dict(v) for k, v in self.allowed.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Token':
        """
        从字典创建代币对象
        
        Args:
            data: 代币信息字典
            
        Returns:
            代币对象
        """
        token = cls(
            name=data["name"],
            symbol=data["symbol"],
            decimals=data["decimals"],
            total_supply=data["total_supply"]
        )
        token.balances = defaultdict(int, data["balances"])
        token.allowed = defaultdict(lambda: defaultdict(int))
        for owner, spenders in data["allowed"].items():
            for spender, amount in spenders.items():
                token.allowed[owner][spender] = amount
        return token

class Block:
    """区块链中的区块类"""
    
    def __init__(
        self, 
        index: int, 
        timestamp: float, 
        data: Any, 
        previous_hash: str, 
        signature: Optional[str] = None,
        difficulty: int = 4,
        nonce: int = 0
    ):
        """
        初始化新的区块
        
        Args:
            index: 区块索引
            timestamp: 时间戳
            data: 区块中存储的数据
            previous_hash: 前一个区块的哈希
            signature: 可选，区块的签名
            difficulty: 挖矿难度（哈希前导零的个数）
            nonce: 工作量证明的随机数
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = nonce
        self.signature = signature or CryptoUtils.generate_random_bits(128)
        self.hash = self._calculate_hash()
        
    def _calculate_hash(self) -> str:
        """计算区块的哈希值"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "signature": self.signature,
            "nonce": self.nonce
        }, sort_keys=True)
        
        # 使用安全哈希函数
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        """
        挖掘区块（工作量证明）
        
        Args:
            difficulty: 挖矿难度（哈希前导零的个数）
        """
        target = '0' * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self._calculate_hash()
            
        print(f"区块已挖出！哈希: {self.hash}, Nonce: {self.nonce}")
    
    def to_dict(self) -> Dict:
        """将区块转换为字典"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "signature": self.signature,
            "nonce": self.nonce,
            "hash": self.hash
        }

class Blockchain:
    """实际区块链类"""
    
    def __init__(self, difficulty: int = 4, token_name: str = "MyToken", token_symbol: str = "MTK", token_supply: int = 100000000000):
        """
        初始化一个新的区块链，创建创世区块
        
        Args:
            difficulty: 挖矿难度
            token_name: 代币名称
            token_symbol: 代币符号
            token_supply: 代币总供应量
        """
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions = []
        self.nodes = set()  # 存储网络中的其他节点
        
        # 创建代币
        self.token = Token(name=token_name, symbol=token_symbol, total_supply=token_supply)
        
        self._create_genesis_block()
        
    def _create_genesis_block(self) -> None:
        """创建并添加创世区块，同时初始分配代币"""
        # 创世区块的特殊签名
        genesis_signature = CryptoUtils.generate_random_bits(256)
        sig_hex = CryptoUtils.bitstring_to_hex(genesis_signature)
        
        # 创建密钥对（作为创始人地址）
        creator_key_pair = KeyPair()
        creator_address = creator_key_pair.public_key
        
        # 初始分配代币给创始人
        self.token.initial_distribution(creator_address)
        
        # 创建创世区块
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            data={
                "message": "创世区块",
                "timestamp": dt.datetime.now().isoformat(),
                "creator": "Blockchain创建者",
                "creator_address": creator_address,
                "signature_key": sig_hex,
                "token_info": {
                    "name": self.token.name,
                    "symbol": self.token.symbol,
                    "total_supply": self.token.total_supply,
                    "initial_holder": creator_address
                }
            },
            previous_hash="0" * 64,  # 创世区块没有前一个哈希
            signature=genesis_signature
        )
        
        # 对创世区块进行挖矿
        genesis_block.mine_block(self.difficulty)
        
        self.chain.append(genesis_block)
        print(f"创世区块已创建! 哈希: {genesis_block.hash}")
        print(f"创世区块中初始分配的 {self.token.total_supply} {self.token.symbol} 代币给地址: {creator_address[:16]}...")
        
    @property
    def last_block(self) -> Block:
        """获取最后一个区块"""
        return self.chain[-1]
    
    def add_block(self, data: Any, key_pair: Optional[KeyPair] = None) -> Block:
        """
        向区块链添加新区块
        
        Args:
            data: 要存储在区块中的数据
            key_pair: 可选的密钥对，用于对区块进行签名
            
        Returns:
            新创建的区块
        """
        # 如果提供了密钥对，对数据进行签名
        signature = None
        if key_pair:
            data_str = json.dumps(data, sort_keys=True)
            signature = key_pair.sign(data_str)
            # 在数据中添加公钥和签名信息
            if isinstance(data, dict):
                data["public_key"] = key_pair.public_key
                data["signature"] = signature
        
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=data,
            previous_hash=self.last_block.hash,
            signature=signature
        )
        
        # 对新区块进行挖矿
        new_block.mine_block(self.difficulty)
        
        self.chain.append(new_block)
        return new_block
    
    def transfer_token(self, sender_key: KeyPair, recipient_address: str, amount: int) -> Dict:
        """
        转移代币
        
        Args:
            sender_key: 发送者密钥对
            recipient_address: 接收者地址
            amount: 转移数量
            
        Returns:
            交易结果
        """
        sender_address = sender_key.public_key
        
        # 检查余额
        if self.token.balances[sender_address] < amount:
            return {
                "success": False,
                "message": f"余额不足。当前余额: {self.token.balances[sender_address]}, 请求转账: {amount}"
            }
        
        # 执行转账
        success = self.token.transfer(sender_address, recipient_address, amount)
        
        if not success:
            return {
                "success": False,
                "message": "转账失败，可能是余额不足或其他错误"
            }
        
        # 创建交易记录
        transaction = {
            "type": "token_transfer",
            "sender": sender_address,
            "recipient": recipient_address,
            "amount": amount,
            "token": self.token.symbol,
            "timestamp": time.time()
        }
        
        # 对交易进行签名
        transaction_string = json.dumps(transaction, sort_keys=True)
        signature = sender_key.sign(transaction_string)
        transaction["signature"] = signature
        
        # 添加交易到区块链
        self.add_block(transaction, sender_key)
        
        return {
            "success": True,
            "message": f"成功转移 {amount} {self.token.symbol} 从 {sender_address[:10]}... 到 {recipient_address[:10]}...",
            "transaction": transaction
        }
    
    def get_token_balance(self, address: str) -> int:
        """
        获取地址的代币余额
        
        Args:
            address: 地址
            
        Returns:
            代币余额
        """
        return self.token.balance_of(address)
    
    def mint_tokens(self, admin_key: KeyPair, recipient_address: str, amount: int) -> Dict:
        """
        铸造新代币（仅限管理员）
        
        Args:
            admin_key: 管理员密钥对
            recipient_address: 接收者地址
            amount: 铸造数量
            
        Returns:
            铸造结果
        """
        # 检查创世区块中的创建者地址
        creator_address = self.chain[0].data.get("creator_address")
        admin_address = admin_key.public_key
        
        # 只有创建者才能铸造新代币
        if creator_address != admin_address:
            return {
                "success": False,
                "message": "只有区块链创建者才能铸造新代币"
            }
        
        # 增加总供应量
        self.token.total_supply += amount
        
        # 分配新代币
        self.token.balances[recipient_address] += amount
        
        # 创建铸造记录
        mint_record = {
            "type": "token_mint",
            "minter": admin_address,
            "recipient": recipient_address,
            "amount": amount,
            "token": self.token.symbol,
            "new_total_supply": self.token.total_supply,
            "timestamp": time.time()
        }
        
        # 对铸造记录进行签名
        mint_string = json.dumps(mint_record, sort_keys=True)
        signature = admin_key.sign(mint_string)
        mint_record["signature"] = signature
        
        # 添加铸造记录到区块链
        self.add_block(mint_record, admin_key)
        
        return {
            "success": True,
            "message": f"成功铸造 {amount} {self.token.symbol} 给地址 {recipient_address[:10]}...",
            "transaction": mint_record
        }
    
    def add_transaction(self, sender: str, recipient: str, amount: float, key_pair: KeyPair) -> int:
        """
        添加交易到待处理列表
        
        Args:
            sender: 发送者地址
            recipient: 接收者地址
            amount: 交易金额
            key_pair: 发送者的密钥对，用于签署交易
            
        Returns:
            该交易将被添加的区块索引
        """
        transaction = {
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
            "timestamp": time.time()
        }
        
        # 对交易进行签名
        transaction_string = json.dumps(transaction, sort_keys=True)
        signature = key_pair.sign(transaction_string)
        transaction["signature"] = signature
        transaction["public_key"] = key_pair.public_key
        
        self.pending_transactions.append(transaction)
        return self.last_block.index + 1
    
    def mine_pending_transactions(self, miner_address: str) -> Block:
        """
        挖掘包含所有待处理交易的新区块
        
        Args:
            miner_address: 接收挖矿奖励的地址
            
        Returns:
            新挖出的区块
        """
        # 创建挖矿奖励交易
        reward_transaction = {
            "sender": "0",  # 系统地址
            "recipient": miner_address,
            "amount": 1.0,  # 挖矿奖励
            "timestamp": time.time(),
            "type": "reward"
        }
        
        # 添加挖矿奖励到交易列表
        transactions = self.pending_transactions + [reward_transaction]
        
        # 创建新区块
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data={"transactions": transactions},
            previous_hash=self.last_block.hash
        )
        
        # 对新区块进行挖矿
        new_block.mine_block(self.difficulty)
        
        # 添加区块到链上
        self.chain.append(new_block)
        
        # 清空待处理交易列表
        self.pending_transactions = []
        
        return new_block
    
    def register_node(self, address: str) -> None:
        """
        将新节点添加到节点列表
        
        Args:
            address: 节点地址（如 'http://192.168.0.5:5000'）
        """
        self.nodes.add(address)
    
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
            
            # 验证工作量证明
            if current_block.hash[:self.difficulty] != '0' * self.difficulty:
                print(f"区块 {i} 未满足工作量证明要求")
                return False
        
        return True
    
    def resolve_conflicts(self, chains: List[List[Dict]]) -> bool:
        """
        实现共识算法，使用最长链规则
        
        Args:
            chains: 从其他节点获取的区块链数据列表
            
        Returns:
            如果当前链被替换则返回True，否则返回False
        """
        new_chain = None
        max_length = len(self.chain)
        
        # 查找所有节点中最长的有效链
        for chain_data in chains:
            length = len(chain_data)
            
            if length > max_length:
                # 验证链的有效性
                chain = []
                for block_data in chain_data:
                    block = Block(
                        index=block_data["index"],
                        timestamp=block_data["timestamp"],
                        data=block_data["data"],
                        previous_hash=block_data["previous_hash"],
                        signature=block_data["signature"],
                        nonce=block_data["nonce"]
                    )
                    block.hash = block_data["hash"]
                    chain.append(block)
                
                # 检查这个链是否有效
                valid = True
                for i in range(1, len(chain)):
                    if chain[i].previous_hash != chain[i-1].hash:
                        valid = False
                        break
                    if chain[i].hash != chain[i]._calculate_hash():
                        valid = False
                        break
                    if chain[i].hash[:self.difficulty] != '0' * self.difficulty:
                        valid = False
                        break
                
                if valid:
                    max_length = length
                    new_chain = chain
        
        # 如果找到了更长的有效链，则替换当前链
        if new_chain:
            self.chain = new_chain
            return True
        
        return False
    
    def get_chain_data(self) -> List[Dict]:
        """获取整个区块链的数据"""
        return [block.to_dict() for block in self.chain]
    
    def get_token_info(self) -> Dict:
        """
        获取代币信息
        
        Returns:
            代币信息字典
        """
        return {
            "name": self.token.name,
            "symbol": self.token.symbol,
            "total_supply": self.token.total_supply,
            "decimals": self.token.decimals,
            "creator": self.chain[0].data.get("creator_address", "未知")
        }
    
    def get_all_balances(self) -> Dict[str, int]:
        """
        获取所有账户余额
        
        Returns:
            地址到余额的映射
        """
        return dict(self.token.balances)
    
    def save_to_file(self, filename: str = "blockchain.json") -> None:
        """
        将区块链保存到文件
        
        Args:
            filename: 保存的文件名
        """
        data = {
            "chain": self.get_chain_data(),
            "token": self.token.to_dict()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"区块链已保存到文件: {filename}")
    
    @classmethod
    def load_from_file(cls, filename: str = "blockchain.json", difficulty: int = 4) -> 'Blockchain':
        """
        从文件加载区块链
        
        Args:
            filename: 加载的文件名
            difficulty: 新区块链的挖矿难度
            
        Returns:
            加载的区块链对象
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            chain_data = data["chain"]
            token_data = data["token"]
            
            # 创建空的区块链
            blockchain = cls(
                difficulty=difficulty,
                token_name=token_data["name"],
                token_symbol=token_data["symbol"],
                token_supply=token_data["total_supply"]
            )
            
            # 清空初始化时自动创建的链和代币
            blockchain.chain = []
            
            # 加载代币
            blockchain.token = Token.from_dict(token_data)
            
            # 加载区块链
            for block_data in chain_data:
                block = Block(
                    index=block_data["index"],
                    timestamp=block_data["timestamp"],
                    data=block_data["data"],
                    previous_hash=block_data["previous_hash"],
                    signature=block_data["signature"],
                    nonce=block_data["nonce"]
                )
                block.hash = block_data["hash"]
                blockchain.chain.append(block)
                
            print(f"从文件加载了 {len(blockchain.chain)} 个区块和代币 {blockchain.token.name} ({blockchain.token.symbol})")
            return blockchain
            
        except FileNotFoundError:
            print(f"文件 {filename} 不存在, 创建新的区块链")
            return cls(difficulty=difficulty)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"加载文件时出错: {e}")
            return cls(difficulty=difficulty)

# 简单的命令行节点服务器
class BlockchainNode:
    """区块链网络节点"""
    
    def __init__(self, host: str = 'localhost', port: int = 5000, token_name: str = "MyToken", token_symbol: str = "MTK"):
        """
        初始化区块链节点
        
        Args:
            host: 主机地址
            port: 端口号
            token_name: 代币名称
            token_symbol: 代币符号
        """
        self.blockchain = Blockchain(difficulty=4, token_name=token_name, token_symbol=token_symbol)
        self.host = host
        self.port = port
        self.peers = set()  # 对等节点列表
        self.key_pair = KeyPair()  # 创建节点密钥对
        
    def start(self):
        """启动节点服务器"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        
        print(f"区块链节点已启动，监听地址: {self.host}:{self.port}")
        print(f"节点公钥: {self.key_pair.public_key}")
        
        # 显示代币信息
        token_info = self.blockchain.get_token_info()
        print(f"代币信息: {token_info['name']} ({token_info['symbol']})")
        print(f"总供应量: {token_info['total_supply']}")
        
        # 创建一个线程处理命令行输入
        command_thread = threading.Thread(target=self._handle_commands)
        command_thread.daemon = True
        command_thread.start()
        
        try:
            while True:
                client, address = server.accept()
                client_thread = threading.Thread(target=self._handle_client, args=(client, address))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("节点关闭")
            server.close()
    
    def _handle_client(self, client, address):
        """处理客户端连接"""
        # 实现节点通信的逻辑
        pass
    
    def _handle_commands(self):
        """处理命令行命令"""
        print("\n可用命令:")
        print("  add_block <data>           - 添加新区块")
        print("  show_chain                 - 显示整个区块链")
        print("  token_info                 - 显示代币信息")
        print("  balance <address>          - 查询地址余额")
        print("  transfer <to> <amount>     - 转移代币到指定地址")
        print("  mint <to> <amount>         - 铸造新代币（仅限创建者）")
        print("  all_balances               - 显示所有账户余额")
        print("  save                       - 保存区块链到文件")
        print("  load                       - 从文件加载区块链")
        print("  generate_keypair           - 生成新的密钥对")
        print("  exit                       - 退出节点")
        
        while True:
            command = input("\n输入命令> ")
            parts = command.split(' ')
            cmd = parts[0].lower()
            
            if cmd == "add_block" and len(parts) > 1:
                data = ' '.join(parts[1:])
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    data = {"message": data}
                
                block = self.blockchain.add_block(data, self.key_pair)
                print(f"已添加新区块，哈希: {block.hash}")
                
            elif cmd == "show_chain":
                chain_data = self.blockchain.get_chain_data()
                print(json.dumps(chain_data, indent=2))
                
            elif cmd == "token_info":
                token_info = self.blockchain.get_token_info()
                print(f"代币名称: {token_info['name']}")
                print(f"代币符号: {token_info['symbol']}")
                print(f"总供应量: {token_info['total_supply']}")
                print(f"精度: {token_info['decimals']}")
                print(f"创建者: {token_info['creator']}")
                
            elif cmd == "balance":
                if len(parts) < 2:
                    address = self.key_pair.public_key
                    print(f"使用当前节点地址: {address[:16]}...")
                else:
                    address = parts[1]
                
                balance = self.blockchain.get_token_balance(address)
                print(f"地址 {address[:16]}... 的余额: {balance} {self.blockchain.token.symbol}")
                
            elif cmd == "transfer" and len(parts) >= 3:
                to_address = parts[1]
                try:
                    amount = int(parts[2])
                    if amount <= 0:
                        print("金额必须大于0")
                        continue
                except ValueError:
                    print("金额必须是整数")
                    continue
                
                result = self.blockchain.transfer_token(self.key_pair, to_address, amount)
                if result["success"]:
                    print(result["message"])
                else:
                    print(f"转账失败: {result['message']}")
                
            elif cmd == "mint" and len(parts) >= 3:
                to_address = parts[1]
                try:
                    amount = int(parts[2])
                    if amount <= 0:
                        print("金额必须大于0")
                        continue
                except ValueError:
                    print("金额必须是整数")
                    continue
                
                result = self.blockchain.mint_tokens(self.key_pair, to_address, amount)
                if result["success"]:
                    print(result["message"])
                else:
                    print(f"铸造失败: {result['message']}")
                
            elif cmd == "all_balances":
                balances = self.blockchain.get_all_balances()
                if not balances:
                    print("没有账户余额记录")
                else:
                    print(f"账户余额 ({self.blockchain.token.symbol}):")
                    for address, balance in balances.items():
                        print(f"  {address[:16]}...: {balance}")
                
            elif cmd == "save":
                self.blockchain.save_to_file()
                
            elif cmd == "load":
                self.blockchain = Blockchain.load_from_file()
                
            elif cmd == "generate_keypair":
                new_keypair = KeyPair()
                print(f"已生成新的密钥对:")
                print(f"私钥: {new_keypair.private_key}")
                print(f"公钥 (地址): {new_keypair.public_key}")
                
            elif cmd == "exit":
                print("节点关闭")
                break
                
            else:
                print("未知命令或格式错误")

def main():
    """主函数，展示区块链的创建和使用"""
    parser = argparse.ArgumentParser(description="区块链节点")
    parser.add_argument('--host', default='localhost', help='主机地址 (默认: localhost)')
    parser.add_argument('--port', default=5000, type=int, help='端口号 (默认: 5000)')
    parser.add_argument('--difficulty', default=4, type=int, help='挖矿难度 (默认: 4)')
    parser.add_argument('--token_name', default="MyToken", help='代币名称 (默认: MyToken)')
    parser.add_argument('--token_symbol', default="MTK", help='代币符号 (默认: MTK)')
    parser.add_argument('--token_supply', default=100000000000, type=int, help='代币初始供应量 (默认: 100000000000)')
    parser.add_argument('--demo', action='store_true', help='运行演示模式')
    
    args = parser.parse_args()
    
    if args.demo:
        print("========================================")
        print("   区块链创世区块与代币演示")
        print("========================================")
        
        # 创建区块链实例
        blockchain = Blockchain(
            difficulty=args.difficulty,
            token_name=args.token_name,
            token_symbol=args.token_symbol,
            token_supply=args.token_supply
        )
        
        # 显示创世区块的详细信息
        genesis_block = blockchain.chain[0]
        creator_address = genesis_block.data.get("creator_address")
        
        print("\n创世区块信息:")
        print(f"索引: {genesis_block.index}")
        print(f"时间戳: {dt.datetime.fromtimestamp(genesis_block.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"数据: {genesis_block.data}")
        print(f"前一个哈希: {genesis_block.previous_hash}")
        print(f"签名: {genesis_block.signature[:20]}... (已截断)")
        print(f"哈希: {genesis_block.hash}")
        
        # 显示代币信息
        token_info = blockchain.get_token_info()
        print(f"\n代币信息:")
        print(f"名称: {token_info['name']}")
        print(f"符号: {token_info['symbol']}")
        print(f"总供应量: {token_info['total_supply']}")
        print(f"创建者地址: {token_info['creator'][:16]}...")
        
        # 查询创建者余额
        creator_balance = blockchain.get_token_balance(creator_address)
        print(f"创建者余额: {creator_balance} {token_info['symbol']}")
        
        # 创建一个新的用户密钥对
        user_key_pair = KeyPair()
        user_address = user_key_pair.public_key
        print(f"\n新用户地址: {user_address[:16]}...")
        
        # 转移一些代币给新用户
        transfer_amount = 1000
        print(f"\n从创建者转移 {transfer_amount} {token_info['symbol']} 到新用户...")
        
        # 我们需要创建者的密钥对才能转移代币
        # 由于我们没有在创世块中保存创建者的私钥，这里我们为演示创建一个新的密钥对
        creator_key_pair = KeyPair()
        creator_key_pair.public_key = creator_address  # 覆盖公钥为创世块中的创建者地址
        
        # 为演示，修改代币余额以便我们可以进行转账
        blockchain.token.balances[creator_key_pair.public_key] = blockchain.token.total_supply
        
        # 执行转账
        transfer_result = blockchain.transfer_token(creator_key_pair, user_address, transfer_amount)
        if transfer_result["success"]:
            print(f"转账成功: {transfer_result['message']}")
        else:
            print(f"转账失败: {transfer_result['message']}")
        
        # 查询余额
        creator_balance = blockchain.get_token_balance(creator_address)
        user_balance = blockchain.get_token_balance(user_address)
        print(f"\n转账后余额:")
        print(f"创建者: {creator_balance} {token_info['symbol']}")
        print(f"新用户: {user_balance} {token_info['symbol']}")
        
        # 保存区块链到文件
        blockchain.save_to_file("blockchain_with_token.json")
        
        print("\n演示完成! 区块链已成功初始化并创建了代币。")
    else:
        # 启动节点服务器
        node = BlockchainNode(
            host=args.host, 
            port=args.port,
            token_name=args.token_name,
            token_symbol=args.token_symbol
        )
        node.start()

if __name__ == "__main__":
    main() 