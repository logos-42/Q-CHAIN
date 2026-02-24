#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一API量子区块链服务
All-in-One API Server for Quantum Blockchain

统一入口: POST /api/v1/query
响应格式: {code, message, data, timestamp, version}
"""

import json
import time
import hashlib
import random
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder="../../templates", static_folder="../../static")
CORS(app)

API_VERSION = "1.0"


def success_response(data, message="success"):
    """统一成功响应"""
    return {
        "code": 0,
        "message": message,
        "data": data,
        "timestamp": int(time.time()),
        "version": API_VERSION,
    }


def error_response(code, message, data=None):
    """统一错误响应"""
    return {
        "code": code,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time()),
        "version": API_VERSION,
    }


class QuantumBlockchain:
    """量子区块链核心"""

    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_genesis_block()

    def _quantum_signature(self, bits=256):
        """生成量子签名"""
        return "".join(random.choice("0123456789abcdef") for _ in range(bits // 4))

    def _quantum_hash(self, data):
        """量子哈希"""
        classic = hashlib.sha256(str(data).encode()).hexdigest()
        quantum_part = self._quantum_signature(64)
        return hashlib.sha256((classic + quantum_part).encode()).hexdigest()

    def create_genesis_block(self):
        """创建创世区块"""
        genesis = {
            "index": 0,
            "timestamp": str(time.time()),
            "data": {"message": "Genesis Block - Q-CHAIN", "token": "QTC"},
            "previous_hash": "0" * 64,
            "quantum_signature": self._quantum_signature(256),
            "quantum_proof": "",
            "hash": self._quantum_hash({"genesis": 0}),
        }
        self.chain.append(genesis)
        return genesis

    def add_block(self, data, quantum_proof=""):
        """添加区块"""
        prev = self.chain[-1]
        new_block = {
            "index": len(self.chain),
            "timestamp": str(time.time()),
            "data": data,
            "previous_hash": prev["hash"],
            "quantum_signature": self._quantum_signature(256),
            "quantum_proof": quantum_proof,
            "hash": self._quantum_hash(
                {
                    "index": len(self.chain),
                    "data": data,
                    "previous_hash": prev["hash"],
                    "proof": quantum_proof,
                }
            ),
        }
        self.chain.append(new_block)
        return new_block

    def is_valid(self):
        """验证区块链"""
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr["previous_hash"] != prev["hash"]:
                return False
        return True


class PQECConsensus:
    """PQEC共识引擎"""

    def __init__(self):
        self.total_proofs = 0
        self.successful_proofs = 0
        self.total_time = 0.0
        self.difficulty = 3

    def mine(self, data, difficulty=3):
        """PQEC挖矿"""
        start_time = time.time()

        code_types = ["Shor", "Surface", "BitFlip"]
        code_type = random.choice(code_types)

        proof = self._generate_pqec_proof(data, difficulty)

        elapsed = time.time() - start_time
        self.total_proofs += 1
        self.successful_proofs += 1
        self.total_time += elapsed

        return {
            "proof": proof,
            "code_type": code_type,
            "difficulty": difficulty,
            "mining_time": elapsed,
        }

    def _generate_pqec_proof(self, data, difficulty):
        """生成PQEC证明"""
        base = f"{data}:{time.time()}:{random.random()}"
        proof_data = hashlib.sha256(base.encode()).hexdigest()

        error_correction = f"EC:{difficulty}:"
        for _ in range(difficulty * 4):
            error_correction += self._simulate_error_correction()

        return f"{proof_data}:{error_correction}"

    def _simulate_error_correction(self):
        """模拟纠错"""
        operations = ["encode", "syndrome", "correct", "verify"]
        return random.choice(operations) + random.choice(["0", "1"])

    def verify(self, proof, difficulty):
        """验证PQEC证明"""
        parts = proof.split(":")
        if len(parts) < 3:
            return False

        expected_prefix = "EC:" + str(difficulty) + ":"
        return expected_prefix in proof

    def get_stats(self):
        """获取统计"""
        avg_time = self.total_time / self.total_proofs if self.total_proofs > 0 else 0
        rate = (
            self.successful_proofs / self.total_proofs if self.total_proofs > 0 else 0
        )
        return {
            "total_blocks": len(blockchain.chain),
            "total_proofs": self.total_proofs,
            "success_rate": round(rate, 4),
            "avg_mining_time": round(avg_time, 4),
            "difficulty": self.difficulty,
            "error_correction_codes": ["Shor", "Surface", "BitFlip", "PhaseFlip"],
        }


blockchain = QuantumBlockchain()
pqec = PQECConsensus()


# ==================== 统一API入口 ====================


@app.route("/api/v1/query", methods=["GET", "POST"])
def unified_api():
    """统一API入口"""

    if request.method == "GET":
        action = request.args.get("action", "")
        params_json = request.args.get("params", "{}")
    else:
        data = request.get_json() or {}
        action = data.get("action", "")
        params_json = data.get("params", {})

    if isinstance(params_json, str):
        try:
            params = json.loads(params_json)
        except:
            params = {}
    else:
        params = params_json

    try:
        result = handle_action(action, params)
        return jsonify(result)
    except Exception as e:
        return jsonify(error_response(3, str(e)))


def handle_action(action, params):
    """处理所有Action"""

    # ===== 区块链操作 =====
    if action == "get_blockchain":
        return success_response(
            {
                "chain": blockchain.chain,
                "length": len(blockchain.chain),
                "qec_enabled": True,
            }
        )

    elif action == "get_blocks":
        blocks = [
            {
                "index": b["index"],
                "timestamp": b["timestamp"],
                "hash": b["hash"][:16] + "...",
                "data": b["data"],
            }
            for b in blockchain.chain
        ]
        return success_response({"blocks": blocks, "count": len(blocks)})

    elif action == "get_block":
        index = params.get("index", 0)
        if 0 <= index < len(blockchain.chain):
            return success_response(blockchain.chain[index])
        return error_response(2, "Block not found")

    elif action == "get_latest_block":
        return success_response(blockchain.chain[-1])

    elif action == "add_block":
        data = params.get("data", {})
        proof = params.get("proof", "")
        block = blockchain.add_block(data, proof)
        return success_response({"block": block}, "Block added")

    elif action == "validate_chain":
        is_valid = blockchain.is_valid()
        return success_response({"valid": is_valid})

    # ===== 交易操作 =====
    elif action == "get_transactions":
        transactions = []
        for b in blockchain.chain:
            if isinstance(b["data"], dict):
                transactions.append(
                    {
                        "block_index": b["index"],
                        "timestamp": b["timestamp"],
                        "data": b["data"],
                    }
                )
        return success_response(
            {"transactions": transactions, "count": len(transactions)}
        )

    # ===== PQEC操作 =====
    elif action == "pqec_mine":
        data = params.get("data", "transaction data")
        difficulty = params.get("difficulty", 3)
        result = pqec.mine(data, difficulty)

        new_block = blockchain.add_block(
            {"transaction": data, "proof": result["proof"]}, result["proof"]
        )

        return success_response(
            {
                "block": new_block,
                "proof": result["proof"],
                "code_type": result["code_type"],
                "mining_time": round(result["mining_time"], 4),
                "difficulty": result["difficulty"],
            }
        )

    elif action == "pqec_verify":
        proof = params.get("proof", "")
        difficulty = params.get("difficulty", 3)
        is_valid = pqec.verify(proof, difficulty)
        return success_response({"valid": is_valid})

    elif action == "pqec_status":
        return success_response(
            {
                "difficulty": pqec.difficulty,
                "total_blocks": len(blockchain.chain),
                "qec_enabled": True,
                "consensus": "PQEC",
            }
        )

    elif action == "pqec_stats":
        return success_response(pqec.get_stats())

    elif action == "pqec_codes":
        return success_response(
            {
                "codes": [
                    {"name": "Shor", "qubits": 9, "description": "Shor量子纠错码"},
                    {"name": "Surface", "qubits": 17, "description": "表面码"},
                    {"name": "BitFlip", "qubits": 3, "description": "位翻转码"},
                    {"name": "PhaseFlip", "qubits": 3, "description": "相位翻转码"},
                ]
            }
        )

    elif action == "pqec_simulate_error":
        code_type = params.get("code_type", "Shor")
        error_prob = params.get("error_probability", 0.1)

        qubits = {"Shor": 9, "Surface": 17, "BitFlip": 3, "PhaseFlip": 3}
        num_qubits = qubits.get(code_type, 3)

        original_state = "".join(random.choice("01") for _ in range(num_qubits))

        errors = int(num_qubits * error_prob)
        error_positions = random.sample(range(num_qubits), min(errors, num_qubits))

        error_state = list(original_state)
        for pos in error_positions:
            error_state[pos] = "1" if error_state[pos] == "0" else "0"
        error_state = "".join(error_state)

        corrected_state = original_state

        return success_response(
            {
                "code_type": code_type,
                "num_qubits": num_qubits,
                "original_state": original_state,
                "error_applied": error_state,
                "corrected_state": corrected_state,
                "error_corrected": True,
                "error_probability": error_prob,
            }
        )

    # ===== 量子操作 =====
    elif action == "quantum_generate_signature":
        bits = params.get("bits", 256)
        signature = blockchain._quantum_signature(bits)
        return success_response({"signature": signature, "bits": bits})

    elif action == "quantum_hash":
        data = params.get("data", "")
        size = params.get("size", 64)
        hash_result = blockchain._quantum_hash(data)
        return success_response({"hash": hash_result[: size // 4], "data": data})

    elif action == "quantum_random":
        bits = params.get("bits", 64)
        random_bits = "".join(random.choice("01") for _ in range(bits))
        return success_response(
            {"bits": random_bits, "hex": hex(int(random_bits, 2))[2:]}
        )

    # ===== 搜索 =====
    elif action == "search":
        query = params.get("query", "")
        results = {"blocks": [], "transactions": []}

        for b in blockchain.chain:
            if str(b["index"]) == query or query in str(b["hash"]):
                results["blocks"].append({"index": b["index"], "hash": b["hash"]})
            if isinstance(b["data"], dict):
                for v in b["data"].values():
                    if query.lower() in str(v).lower():
                        results["transactions"].append(
                            {"block_index": b["index"], "data": b["data"]}
                        )
                        break

        return success_response(results)

    # ===== 默认 =====
    else:
        return error_response(1, f"Unknown action: {action}")


# ==================== 页面路由 ====================


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/blocks")
def blocks_page():
    return render_template("blocks.html")


@app.route("/transactions")
def transactions_page():
    return render_template("transactions.html")


@app.route("/add-block")
def add_block_page():
    return render_template("add_block.html")


@app.route("/pqec")
def pqec_page():
    return render_template("pqec.html")


if __name__ == "__main__":
    print("=" * 60)
    print("  Q-CHAIN 统一API服务器")
    print("  统一入口: POST /api/v1/query")
    print("  版本: " + API_VERSION)
    print("=" * 60)
    print("\n可用Action:")
    print("  区块链: get_blockchain, get_blocks, add_block, validate_chain")
    print("  PQEC:   pqec_mine, pqec_verify, pqec_stats, pqec_simulate_error")
    print("  量子:   quantum_generate_signature, quantum_hash, quantum_random")
    print("  搜索:   search")
    print("\n启动服务: http://127.0.0.1:9000")
    print("=" * 60)

    app.run(host="0.0.0.0", port=9000, debug=True)
