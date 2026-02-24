#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子区块链Web应用后端
提供区块链API接口和Web前端
"""

from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
import json
import time
import os

# 导入量子区块链实现
from quantum_blockchain import QuantumBlockchain, QuantumRandom, QuantumHash, Block

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域请求支持

# 全局区块链实例
blockchain = None

# 数据文件路径
BLOCKCHAIN_FILE = "quantum_blockchain.json"


# 初始化或加载区块链
def initialize_blockchain():
    global blockchain

    # 如果存在保存的区块链，则加载它
    if os.path.exists(BLOCKCHAIN_FILE):
        try:
            with open(BLOCKCHAIN_FILE, "r", encoding="utf-8") as f:
                blockchain_data = json.load(f)

            # 创建新的区块链实例
            blockchain = QuantumBlockchain()

            # 清除默认的创世区块
            blockchain.chain = []

            # 从文件加载区块链
            for block_data in blockchain_data:
                block = Block(
                    index=block_data["index"],
                    timestamp=block_data["timestamp"],
                    data=block_data["data"],
                    previous_hash=block_data["previous_hash"],
                    quantum_signature=block_data.get("quantum_signature", None),
                )
                block.hash = block_data["hash"]
                blockchain.chain.append(block)

            print(f"已加载保存的区块链，共{len(blockchain.chain)}个区块")
        except Exception as e:
            print(f"加载区块链出错: {e}")
            blockchain = QuantumBlockchain()  # 出错时创建新区块链
    else:
        # 创建新的区块链实例
        blockchain = QuantumBlockchain()

        # 修改创世区块以包含更多相关信息
        genesis_block = blockchain.chain[0]
        genesis_block.data = {
            "message": "量子区块链创世区块",
            "transactions": [
                {
                    "type": "coinbase",
                    "recipient": "创世地址",
                    "amount": 50,
                    "timestamp": time.time(),
                },
                {
                    "type": "message",
                    "content": "量子区块链创世区块",
                    "timestamp": time.time(),
                },
            ],
            "merkle_root": QuantumHash.quantum_hash(json.dumps({"genesis": "block"})),
            "quantum_signature": QuantumRandom.generate_random_bits(64),
            "nonce": int(QuantumRandom.generate_random_bits(32), 2),
            "quantum_key": QuantumRandom.generate_random_bits(4),
            "token": {
                "name": "量子币",
                "symbol": "QTC",
                "total_supply": 21000000,
                "decimals": 8,
                "creator": "量子创世地址",
            },
        }

        # 重新计算哈希
        genesis_block.hash = genesis_block._calculate_hash()

        # 保存区块链
        save_blockchain()

        print("已创建新的区块链并初始化创世区块")

    return blockchain


# 保存区块链到文件
def save_blockchain():
    blockchain_data = []

    for block in blockchain.chain:
        block_data = {
            "index": block.index,
            "timestamp": block.timestamp,
            "data": block.data,
            "previous_hash": block.previous_hash,
            "hash": block.hash,
            "quantum_signature": block.quantum_signature,
        }
        blockchain_data.append(block_data)

    with open(BLOCKCHAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(blockchain_data, f, ensure_ascii=False, indent=2)

    print(f"区块链已保存到 {BLOCKCHAIN_FILE}")


# 网页路由
@app.route("/")
def index():
    """首页"""
    return render_template("index.html")


@app.route("/blocks")
def blocks_page():
    """区块链页面"""
    return render_template("blocks.html")


@app.route("/transactions")
def transactions_page():
    """交易页面"""
    return render_template("transactions.html")


@app.route("/add-block")
def add_block_page():
    """添加区块页面"""
    return render_template("add_block.html")


@app.route("/pqec")
def pqec_page():
    """PQEC共识机制页面"""
    return render_template("pqec.html")


# PQEC API路由
@app.route("/api/pqec/status", methods=["GET"])
def pqec_status():
    """获取PQEC共识状态"""
    return jsonify(
        {
            "difficulty": 4,
            "target_time": 30,
            "block_reward": 50,
            "chain_status": "活跃",
            "algorithm": "Dilithium-Kyber",
            "quantum_bits": 256,
        }
    )


@app.route("/api/pqec/stats", methods=["GET"])
def pqec_stats():
    """获取PQEC统计信息"""
    return jsonify(
        {
            "total_blocks": len(blockchain.chain),
            "success_rate": 100,
            "avg_mining_time": 0,
            "hash_rate": 0,
            "valid_proofs": len(blockchain.chain),
        }
    )


@app.route("/api/pqec/mine", methods=["POST"])
def pqec_mine():
    """PQEC挖矿"""
    data = request.get_json()

    try:
        proof = data.get("proof", "")
        block_data = data.get("data", "量子区块")

        # 创建新区块
        last_block = blockchain.chain[-1]

        new_block_data = {
            "message": block_data,
            "transactions": [
                {"type": "coinbase", "amount": 50, "timestamp": time.time()}
            ],
            "merkle_root": QuantumHash.quantum_hash(json.dumps({"data": block_data})),
            "quantum_signature": QuantumRandom.generate_random_bits(64),
            "nonce": int(QuantumRandom.generate_random_bits(32), 2),
            "quantum_key": QuantumRandom.generate_random_bits(4),
            "quantum_proof": proof,
        }

        new_block = Block(
            index=last_block.index + 1,
            timestamp=time.time(),
            data=new_block_data,
            previous_hash=last_block.hash,
            quantum_signature=new_block_data["quantum_signature"],
        )

        new_block.hash = new_block._calculate_hash()
        blockchain.chain.append(new_block)
        save_blockchain()

        return jsonify(
            {
                "success": True,
                "block_index": new_block.index,
                "proof": proof,
                "hash": new_block.hash,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pqec/verify", methods=["POST"])
def pqec_verify():
    """验证PQEC证明"""
    data = request.get_json()
    proof = data.get("proof", "")
    algorithm = data.get("algorithm", "dilithium")

    # 简单验证逻辑
    is_valid = len(proof) >= 64 and proof.startswith("0x")

    return jsonify({"valid": is_valid, "algorithm": algorithm, "verify_time": 5})


# API路由
@app.route("/api/blockchain", methods=["GET"])
def get_blockchain():
    """获取完整区块链"""
    chain_data = []

    for block in blockchain.chain:
        chain_data.append(
            {
                "index": block.index,
                "timestamp": block.timestamp,
                "timestamp_human": time.ctime(block.timestamp),
                "data": block.data,
                "previous_hash": block.previous_hash,
                "hash": block.hash,
                "quantum_signature": block.quantum_signature,
            }
        )

    return jsonify({"chain": chain_data, "length": len(chain_data)})


@app.route("/api/blocks", methods=["GET"])
def get_blocks():
    """获取所有区块的简要信息"""
    blocks_data = []

    for block in blockchain.chain:
        tx_count = (
            len(block.data.get("transactions", []))
            if isinstance(block.data, dict)
            else 0
        )

        blocks_data.append(
            {
                "index": block.index,
                "timestamp": block.timestamp,
                "timestamp_human": time.ctime(block.timestamp),
                "hash": block.hash,
                "tx_count": tx_count,
            }
        )

    return jsonify(blocks_data)


@app.route("/api/block/<int:index>", methods=["GET"])
def get_block(index):
    """获取特定区块的详细信息"""
    if index < 0 or index >= len(blockchain.chain):
        return jsonify({"error": "区块不存在"}), 404

    block = blockchain.chain[index]

    block_data = {
        "index": block.index,
        "timestamp": block.timestamp,
        "timestamp_human": time.ctime(block.timestamp),
        "data": block.data,
        "previous_hash": block.previous_hash,
        "hash": block.hash,
        "quantum_signature": block.quantum_signature,
    }

    return jsonify(block_data)


@app.route("/api/block/latest", methods=["GET"])
def get_latest_block():
    """获取最新区块"""
    block = blockchain.chain[-1]

    block_data = {
        "index": block.index,
        "timestamp": block.timestamp,
        "timestamp_human": time.ctime(block.timestamp),
        "data": block.data,
        "previous_hash": block.previous_hash,
        "hash": block.hash,
        "quantum_signature": block.quantum_signature,
    }

    return jsonify(block_data)


@app.route("/api/blocks/add", methods=["POST"])
def add_block():
    """添加新区块"""
    try:
        data = request.get_json()

        # 验证请求数据
        if not data or not isinstance(data, dict):
            return jsonify({"error": "无效的区块数据"}), 400

        # 创建交易列表
        transactions = data.get("transactions", [])
        if not transactions:
            # 如果没有提供交易，创建一个默认消息交易
            transactions = [
                {
                    "type": "message",
                    "content": data.get("message", "新区块"),
                    "timestamp": time.time(),
                }
            ]

        # 获取最后一个区块
        last_block = blockchain.chain[-1]

        # 准备区块数据
        block_data = {
            "message": data.get("message", "新区块"),
            "transactions": transactions,
            "merkle_root": QuantumHash.quantum_hash(json.dumps(transactions)),
            "quantum_signature": QuantumRandom.generate_random_bits(64),
            "nonce": int(QuantumRandom.generate_random_bits(32), 2),
            "quantum_key": QuantumRandom.generate_random_bits(4),
        }

        # 创建新区块
        new_block = Block(
            index=last_block.index + 1,
            timestamp=time.time(),
            data=block_data,
            previous_hash=last_block.hash,
            quantum_signature=block_data["quantum_signature"],
        )

        # 计算哈希
        new_block.hash = new_block._calculate_hash()

        # 添加到区块链
        blockchain.chain.append(new_block)

        # 保存区块链到文件
        save_blockchain()

        return jsonify(
            {
                "message": "区块添加成功",
                "block": {
                    "index": new_block.index,
                    "timestamp": new_block.timestamp,
                    "timestamp_human": time.ctime(new_block.timestamp),
                    "hash": new_block.hash,
                },
            }
        )
    except Exception as e:
        return jsonify({"error": f"添加区块失败: {str(e)}"}), 500


@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    """获取所有交易"""
    all_transactions = []

    for block in blockchain.chain:
        if isinstance(block.data, dict) and "transactions" in block.data:
            for tx in block.data["transactions"]:
                # 添加区块信息到交易
                tx_with_block = tx.copy()
                tx_with_block["block_index"] = block.index
                tx_with_block["block_hash"] = block.hash
                tx_with_block["timestamp_human"] = time.ctime(tx.get("timestamp", 0))

                all_transactions.append(tx_with_block)

    return jsonify(all_transactions)


@app.route("/api/search", methods=["GET"])
def search():
    """搜索区块链"""
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "请提供搜索关键词"}), 400

    results = {"blocks": [], "transactions": []}

    # 搜索区块
    for block in blockchain.chain:
        # 按区块哈希或索引搜索
        if str(block.index) == query or block.hash.startswith(query):
            results["blocks"].append(
                {
                    "index": block.index,
                    "timestamp": block.timestamp,
                    "timestamp_human": time.ctime(block.timestamp),
                    "hash": block.hash,
                }
            )

    # 搜索交易
    for block in blockchain.chain:
        if isinstance(block.data, dict) and "transactions" in block.data:
            for tx in block.data["transactions"]:
                # 检查交易是否包含查询字符串
                tx_str = json.dumps(tx, ensure_ascii=False)
                if query.lower() in tx_str.lower():
                    tx_result = tx.copy()
                    tx_result["block_index"] = block.index
                    tx_result["block_hash"] = block.hash
                    tx_result["timestamp_human"] = time.ctime(tx.get("timestamp", 0))
                    results["transactions"].append(tx_result)

    return jsonify(results)


# 初始化区块链
initialize_blockchain()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=9000)
