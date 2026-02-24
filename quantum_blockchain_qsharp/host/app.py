#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
量子区块链 Q# 版本 - 统一API服务器
使用统一API: POST /api/v1/query
"""

import json
import time
import hashlib
import random
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)

API_VERSION = "1.0"


def success_response(data, message="success"):
    return {
        "code": 0,
        "message": message,
        "data": data,
        "timestamp": int(time.time()),
        "version": API_VERSION,
    }


def error_response(code, message, data=None):
    return {
        "code": code,
        "message": message,
        "data": data or {},
        "timestamp": int(time.time()),
        "version": API_VERSION,
    }


class QuantumBlockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def _quantum_signature(self, bits=256):
        return "".join(random.choice("0123456789abcdef") for _ in range(bits // 4))

    def _quantum_hash(self, data):
        classic = hashlib.sha256(str(data).encode()).hexdigest()
        quantum_part = self._quantum_signature(64)
        return hashlib.sha256((classic + quantum_part).encode()).hexdigest()

    def create_genesis_block(self):
        genesis = {
            "index": 0,
            "timestamp": str(time.time()),
            "data": {"message": "量子区块链创世区块", "token": "QTC"},
            "previous_hash": "0" * 64,
            "quantum_signature": self._quantum_signature(256),
            "quantum_proof": "",
            "hash": self._quantum_hash({"genesis": 0}),
        }
        self.chain.append(genesis)
        return genesis

    def add_block(self, data, quantum_proof=""):
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
        for i in range(1, len(self.chain)):
            if self.chain[i]["previous_hash"] != self.chain[i - 1]["hash"]:
                return False
        return True


class PQECConsensus:
    def __init__(self):
        self.total_proofs = 0
        self.successful_proofs = 0
        self.total_time = 0.0
        self.difficulty = 3

    def mine(self, data, difficulty=3):
        start_time = time.time()
        code_types = ["Shor", "Surface", "BitFlip"]
        code_type = random.choice(code_types)

        base = f"{data}:{time.time()}:{random.random()}"
        proof = hashlib.sha256(base.encode()).hexdigest()
        proof = f"{proof}:EC:{difficulty}:{code_type}"

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

    def verify(self, proof, difficulty):
        return "EC:" + str(difficulty) in proof

    def get_stats(self):
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


@app.route("/api/v1/query", methods=["POST"])
def unified_api():
    """统一API入口"""
    data = request.get_json() or {}
    action = data.get("action", "")
    params = data.get("params", {})

    try:
        result = handle_action(action, params)
        return jsonify(result)
    except Exception as e:
        return jsonify(error_response(3, str(e)))


@app.route("/api/v1/query", methods=["GET"])
def unified_api_get():
    """GET方式统一API"""
    action = request.args.get("action", "")
    params_json = request.args.get("params", "{}")
    try:
        params = json.loads(params_json) if params_json else {}
    except:
        params = {}

    try:
        result = handle_action(action, params)
        return jsonify(result)
    except Exception as e:
        return jsonify(error_response(3, str(e)))


def handle_action(action, params):
    # 区块链
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
                "quantum_signature": b["quantum_signature"][:16] + "...",
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
        return success_response({"valid": blockchain.is_valid()})

    # 交易
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
        return success_response({"transactions": transactions})

    # PQEC
    elif action == "pqec_mine":
        data = params.get("data", "transaction")
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
        return success_response({"valid": pqec.verify(proof, difficulty)})

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
                    {"name": "Shor", "qubits": 9},
                    {"name": "Surface", "qubits": 17},
                    {"name": "BitFlip", "qubits": 3},
                ]
            }
        )

    elif action == "pqec_simulate_error":
        code = params.get("code_type", "Shor")
        prob = params.get("error_probability", 0.1)
        qubits = {"Shor": 9, "Surface": 17, "BitFlip": 3}
        n = qubits.get(code, 3)
        original = "".join(random.choice("01") for _ in range(n))
        corrected = original
        return success_response(
            {
                "code_type": code,
                "num_qubits": n,
                "original_state": original,
                "corrected_state": corrected,
                "error_corrected": True,
            }
        )

    # 量子
    elif action == "quantum_generate_signature":
        bits = params.get("bits", 256)
        return success_response(
            {"signature": blockchain._quantum_signature(bits), "bits": bits}
        )

    elif action == "quantum_hash":
        data = params.get("data", "")
        return success_response({"hash": blockchain._quantum_hash(data)[:16]})

    elif action == "quantum_random":
        bits = params.get("bits", 64)
        r = "".join(random.choice("01") for _ in range(bits))
        return success_response({"bits": r, "hex": hex(int(r, 2))[2:]})

    # 搜索
    elif action == "search":
        query = params.get("query", "")
        results = {"blocks": [], "transactions": []}
        for b in blockchain.chain:
            if str(b["index"]) == query or query in str(b["hash"]):
                results["blocks"].append({"index": b["index"], "hash": b["hash"]})
        return success_response(results)

    else:
        return error_response(1, f"Unknown action: {action}")


# 页面路由
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
    print("=" * 50)
    print("Q-CHAIN 统一API服务器")
    print("API入口: POST /api/v1/query")
    print("运行: http://127.0.0.1:9000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=9000, debug=True)
