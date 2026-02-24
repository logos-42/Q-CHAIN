#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子区块链 Q# 版本 - Python主机层
使用qsharp包调用Q#量子计算模块
"""

import json
import time
import hashlib
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

try:
    import qsharp
    from qsharp import Result

    QSHARP_AVAILABLE = True
except ImportError:
    QSHARP_AVAILABLE = False
    print("警告: qsharp包未安装，将使用Python模拟量子计算")

app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)


class QuantumBlockchain:
    """量子区块链实现 - Python主机层"""

    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        """创建创世区块"""
        if QSHARP_AVAILABLE:
            try:
                qsharp.compile("""
                    open QuantumBlockchain.QRNG;
                    open QuantumBlockchain.QHash;
                    
                    operation GetGenesisSignature() : String {
                        return GenerateQuantumSignature();
                    }
                """)
                signature = qsharp.call(
                    "QuantumBlockchain.QRNG.GenerateQuantumSignature"
                )
            except:
                signature = self._python_quantum_signature(256)
        else:
            signature = self._python_quantum_signature(256)

        genesis_block = {
            "index": 0,
            "timestamp": str(time.time()),
            "data": {"message": "量子区块链创世区块", "token": "QTC"},
            "previous_hash": "0" * 64,
            "quantum_signature": signature,
            "hash": self.calculate_hash(
                0, time.time(), {"message": "Genesis"}, "0" * 64, signature
            ),
        }
        self.chain.append(genesis_block)
        return genesis_block

    def _python_quantum_signature(self, num_bits):
        """Python模拟量子随机签名（当Q#不可用时）"""
        import random

        bits = "".join(random.choice("01") for _ in range(num_bits))
        return hex(int(bits, 2))[2:].zfill(num_bits // 4)

    def calculate_hash(self, index, timestamp, data, previous_hash, signature):
        """计算区块哈希"""
        block_string = json.dumps(
            {
                "index": index,
                "timestamp": timestamp,
                "data": data,
                "previous_hash": previous_hash,
                "quantum_signature": signature,
            },
            sort_keys=True,
        )

        if QSHARP_AVAILABLE:
            try:
                qsharp.compile("""
                    open QuantumBlockchain.QHash;
                    
                    operation GetHybridHash(data : String) : String {
                        return HybridHash(data, 64);
                    }
                """)
                quantum_part = qsharp.call(
                    "QuantumBlockchain.QHash.HybridHash", block_string, 64
                )
            except:
                quantum_part = hashlib.sha256(block_string.encode()).hexdigest()[:16]
        else:
            quantum_part = hashlib.sha256(block_string.encode()).hexdigest()[:16]

        classical_part = hashlib.sha256(
            (block_string + quantum_part).encode()
        ).hexdigest()
        return classical_part

    def add_block(self, data):
        """添加新区块"""
        previous_block = self.chain[-1]

        if QSHARP_AVAILABLE:
            try:
                signature = qsharp.call(
                    "QuantumBlockchain.QRNG.GenerateQuantumSignature"
                )
            except:
                signature = self._python_quantum_signature(256)
        else:
            signature = self._python_quantum_signature(256)

        new_block = {
            "index": len(self.chain),
            "timestamp": str(time.time()),
            "data": data,
            "previous_hash": previous_block["hash"],
            "quantum_signature": signature,
            "hash": self.calculate_hash(
                len(self.chain), time.time(), data, previous_block["hash"], signature
            ),
        }

        if self.is_valid(new_block, previous_block):
            self.chain.append(new_block)
            return new_block
        return None

    def is_valid(self, new_block, previous_block):
        """验证新区块"""
        if new_block["previous_hash"] != previous_block["hash"]:
            return False

        expected_hash = self.calculate_hash(
            new_block["index"],
            float(new_block["timestamp"]),
            new_block["data"],
            new_block["previous_hash"],
            new_block["quantum_signature"],
        )
        return new_block["hash"] == expected_hash

    def is_chain_valid(self):
        """验证整条链"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if not self.is_valid(current_block, previous_block):
                return False
        return True

    def get_chain_data(self):
        """获取链数据"""
        return self.chain


blockchain = QuantumBlockchain()


@app.route("/")
def index():
    """首页"""
    return render_template("index.html")


@app.route("/blocks")
def blocks_page():
    """区块列表页"""
    return render_template("blocks.html")


@app.route("/transactions")
def transactions_page():
    """交易列表页"""
    return render_template("transactions.html")


@app.route("/add-block")
def add_block_page():
    """添加区块页"""
    return render_template("add_block.html")


@app.route("/api/blockchain", methods=["GET"])
def get_blockchain():
    """获取完整区块链"""
    return jsonify(
        {
            "chain": blockchain.get_chain_data(),
            "length": len(blockchain.chain),
            "qsharp_available": QSHARP_AVAILABLE,
        }
    )


@app.route("/api/blocks", methods=["GET"])
def get_blocks():
    """获取所有区块概要"""
    blocks = []
    for block in blockchain.chain:
        blocks.append(
            {
                "index": block["index"],
                "timestamp": block["timestamp"],
                "hash": block["hash"][:16] + "...",
                "quantum_signature": block["quantum_signature"][:16] + "...",
                "data": block["data"],
            }
        )
    return jsonify(blocks)


@app.route("/api/block/<int:block_index>", methods=["GET"])
def get_block(block_index):
    """获取特定区块"""
    if 0 <= block_index < len(blockchain.chain):
        return jsonify(blockchain.chain[block_index])
    return jsonify({"error": "Block not found"}), 404


@app.route("/api/block/latest", methods=["GET"])
def get_latest_block():
    """获取最新区块"""
    return jsonify(blockchain.chain[-1])


@app.route("/api/blocks/add", methods=["POST"])
def add_block():
    """添加新区块"""
    data = request.get_json()

    if not data or "data" not in data:
        return jsonify({"error": "Invalid data"}), 400

    new_block = blockchain.add_block(data["data"])

    if new_block:
        return jsonify({"message": "Block added successfully", "block": new_block}), 201
    return jsonify({"error": "Failed to add block"}), 400


@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    """获取所有交易"""
    transactions = []
    for block in blockchain.chain:
        if isinstance(block["data"], dict):
            transactions.append(
                {
                    "block_index": block["index"],
                    "timestamp": block["timestamp"],
                    "data": block["data"],
                }
            )
    return jsonify(transactions)


@app.route("/api/search", methods=["GET"])
def search():
    """搜索区块和交易"""
    query = request.args.get("q", "")
    results = {"blocks": [], "transactions": []}

    for block in blockchain.chain:
        if str(block["index"]) == query or query in str(block["hash"]):
            results["blocks"].append({"index": block["index"], "hash": block["hash"]})

        if isinstance(block["data"], dict):
            for key, value in block["data"].items():
                if query.lower() in str(value).lower():
                    results["transactions"].append(
                        {"block_index": block["index"], "data": block["data"]}
                    )

    return jsonify(results)


@app.route("/api/validate", methods=["GET"])
def validate_chain():
    """验证区块链"""
    is_valid = blockchain.is_chain_valid()
    return jsonify(
        {
            "valid": is_valid,
            "message": "Blockchain is valid" if is_valid else "Blockchain is invalid",
        }
    )


if __name__ == "__main__":
    print("=" * 50)
    print("量子区块链 Q# 版本")
    print("=" * 50)
    print(f"Q# 支持: {'已启用' if QSHARP_AVAILABLE else '未启用 (使用Python模拟)'}")
    print(f"初始区块数: {len(blockchain.chain)}")
    print("访问 http://127.0.0.1:9000")
    print("=" * 50)

    app.run(host="0.0.0.0", port=9000, debug=True)
