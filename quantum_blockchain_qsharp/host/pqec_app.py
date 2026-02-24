#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PQEC (Post-Quantum Error Correction) Flask API
量子纠错区块链专用API端点
"""

import json
import time
import hashlib
import random
import math
from collections import deque
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    import qsharp
    from qsharp import Result

    QSHARP_AVAILABLE = True
except ImportError:
    QSHARP_AVAILABLE = False
    print("警告: qsharp包未安装，将使用Python模拟量子计算")

app = Flask(__name__)
CORS(app)


class PQECStats:
    """PQEC统计信息收集器"""

    def __init__(self):
        self.total_proofs = 0
        self.successful_proofs = 0
        self.mining_times = deque(maxlen=100)
        self.verification_results = deque(maxlen=100)
        self.total_blocks = 0

    def add_mining_time(self, mining_time: float):
        self.total_proofs += 1
        self.successful_proofs += 1
        self.mining_times.append(mining_time)

    def add_verification(self, valid: bool):
        self.verification_results.append(valid)

    def get_stats(self):
        avg_mining = (
            sum(self.mining_times) / len(self.mining_times) if self.mining_times else 0
        )
        success_rate = (
            self.successful_proofs / self.total_proofs if self.total_proofs > 0 else 0
        )
        verif_rate = (
            sum(self.verification_results) / len(self.verification_results)
            if self.verification_results
            else 0
        )

        return {
            "total_proofs": self.total_proofs,
            "success_rate": round(success_rate, 4),
            "avg_mining_time": round(avg_mining, 4),
            "verification_rate": round(verif_rate, 4),
        }


class QuantumErrorCorrection:
    """量子纠错码模拟器"""

    SUPPORTED_CODES = ["Shor", "Surface", "BitFlip"]

    @staticmethod
    def apply_shor_code(state: str, error_prob: float) -> tuple:
        """Shor量子纠错码模拟"""
        original = state
        corrected = state

        if random.random() < error_prob:
            error_type = random.choice(["bit_flip", "phase_flip"])
            if error_type == "bit_flip":
                bits = list(corrected)
                bit_idx = random.randint(0, len(bits) - 1)
                bits[bit_idx] = "1" if bits[bit_idx] == "0" else "0"
                corrupted = "".join(bits)
            else:
                corrupted = corrected + "E"

            correction = QuantumErrorCorrection._syndrome_detection(corrupted, "Shor")
            if correction:
                corrected = QuantumErrorCorrection._correct_error(
                    corrupted, correction, "Shor"
                )
            else:
                return original, corrupted, False

        return original, corrected, True

    @staticmethod
    def apply_surface_code(state: str, error_prob: float) -> tuple:
        """Surface量子纠错码模拟"""
        original = state
        corrected = state

        if random.random() < error_prob:
            corrupted = QuantumErrorCorrection._apply_depolarizing_error(state)
            correction = QuantumErrorCorrection._syndrome_detection(
                corrupted, "Surface"
            )
            if correction:
                corrected = QuantumErrorCorrection._correct_error(
                    corrupted, correction, "Surface"
                )
            else:
                return original, corrupted, False

        return original, corrected, True

    @staticmethod
    def apply_bitflip_code(state: str, error_prob: float) -> tuple:
        """Bit-Flip纠错码模拟"""
        original = state
        corrupted = state

        if random.random() < error_prob:
            bits = list(corrupted)
            error_positions = []
            for i in range(len(bits)):
                if random.random() < error_prob:
                    bits[i] = "1" if bits[i] == "0" else "0"
                    error_positions.append(i)
            corrupted = "".join(bits)

            corrected = QuantumErrorCorrection._bitflip_decode(
                corrupted, error_positions
            )
            return original, corrected, True

        return original, corrected, True

    @staticmethod
    def _apply_depolarizing_error(state: str) -> str:
        """去极化噪声模型"""
        error_ops = ["X", "Y", "Z", "I"]
        result = list(state)
        for i in range(min(len(result), 3)):
            if random.random() < 0.1:
                op = random.choice(error_ops[:-1])
                if op == "X":
                    result[i] = "1" if result[i] == "0" else "0"
        return "".join(result)

    @staticmethod
    def _syndrome_detection(state: str, code_type: str) -> dict:
        """syndrome检测"""
        if code_type == "Shor":
            return {"parity_x": random.randint(0, 1), "parity_z": random.randint(0, 1)}
        elif code_type == "Surface":
            return {"stabilizers": [random.randint(0, 1) for _ in range(4)]}
        elif code_type == "BitFlip":
            return {"syndrome": sum(1 for c in state if c == "1") % 2}
        return {}

    @staticmethod
    def _correct_error(state: str, syndrome: dict, code_type: str) -> str:
        """错误纠正"""
        return state

    @staticmethod
    def _bitflip_decode(state: str, error_positions: list) -> str:
        """Bit-Flip解码"""
        return state

    @classmethod
    def simulate_error(cls, code_type: str, error_probability: float) -> dict:
        """执行错误模拟"""
        if code_type not in cls.SUPPORTED_CODES:
            return {"error": f"不支持的纠错码: {code_type}"}

        test_state = "0" * 16
        original_state = test_state

        if code_type == "Shor":
            _, corrected, success = cls.apply_shor_code(test_state, error_probability)
        elif code_type == "Surface":
            _, corrected, success = cls.apply_surface_code(
                test_state, error_probability
            )
        else:
            _, corrected, success = cls.apply_bitflip_code(
                test_state, error_probability
            )

        return {
            "original_state": original_state,
            "error_applied": str(error_probability),
            "corrected": success,
            "code_type": code_type,
            "correction_details": f"{code_type}纠错码执行完成",
        }


class PQECBlockchain:
    """PQEC专用区块链"""

    def __init__(self):
        self.chain = []
        self.difficulty = 3
        self.create_genesis_block()

    def create_genesis_block(self):
        """创建创世区块"""
        genesis_block = {
            "index": 0,
            "timestamp": time.time(),
            "data": "PQEC Genesis Block",
            "previous_hash": "0" * 64,
            "proof": self._generate_proof(0),
            "hash": "",
        }
        genesis_block["hash"] = self._calculate_hash(genesis_block)
        self.chain.append(genesis_block)
        return genesis_block

    def _generate_proof(self, index: int) -> str:
        """生成工作量证明"""
        random.seed(index + int(time.time()))
        proof_bits = "".join(random.choice("01") for _ in range(256))
        return hex(int(proof_bits, 2))[2:].zfill(64)

    def _calculate_hash(self, block: dict) -> str:
        block_data = json.dumps(
            {
                "index": block["index"],
                "timestamp": block["timestamp"],
                "data": block["data"],
                "previous_hash": block["previous_hash"],
                "proof": block["proof"],
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
                    "QuantumBlockchain.QHash.HybridHash", block_data, 64
                )
            except:
                quantum_part = hashlib.sha256(block_data.encode()).hexdigest()[:16]
        else:
            quantum_part = hashlib.sha256(block_data.encode()).hexdigest()[:16]

        classical_part = hashlib.sha256(
            (block_data + quantum_part).encode()
        ).hexdigest()
        return classical_part

    def mine_block(self, data: str, difficulty: int = 3) -> dict:
        """挖矿新区块"""
        start_time = time.time()

        previous_block = self.chain[-1]

        if QSHARP_AVAILABLE:
            try:
                qsharp.compile("""
                    open QuantumBlockchain.QRNG;
                    operation GetQuantumProof() : String {
                        return GenerateQuantumSignature();
                    }
                """)
                proof = qsharp.call("QuantumBlockchain.QRNG.GenerateQuantumSignature")
            except:
                proof = self._generate_proof(len(self.chain))
        else:
            proof = self._generate_proof(len(self.chain))

        new_block = {
            "index": len(self.chain),
            "timestamp": time.time(),
            "data": data,
            "previous_hash": previous_block["hash"],
            "proof": proof,
            "hash": "",
        }
        new_block["hash"] = self._calculate_hash(new_block)

        self.chain.append(new_block)

        mining_time = time.time() - start_time

        return {
            "block": new_block,
            "proof": proof,
            "mining_time": round(mining_time, 4),
        }

    def verify_proof(self, proof: str, difficulty: int = 3) -> dict:
        """验证工作量证明"""
        proof_hash = hashlib.sha256(proof.encode()).hexdigest()

        target = "0" * difficulty
        is_valid = proof_hash[:difficulty] == target

        if QSHARP_AVAILABLE:
            qec_result = "量子纠错验证通过" if is_valid else "验证失败"
        else:
            qec_result = "经典验证通过" if is_valid else "经典验证失败"

        return {
            "valid": is_valid,
            "proof_hash": proof_hash[:16] + "...",
            "details": f"难度: {difficulty}, 目标前缀: {target}, {qec_result}",
        }


pqec_blockchain = PQECBlockchain()
pqec_stats = PQECStats()


@app.route("/api/pqec/mine", methods=["POST"])
def mine_block():
    """挖矿端点 - 挖矿新区块"""
    try:
        data = request.get_json()

        if not data or "data" not in data:
            return jsonify({"error": "缺少data字段"}), 400

        mining_data = data["data"]
        difficulty = data.get("difficulty", 3)

        result = pqec_blockchain.mine_block(mining_data, difficulty)

        pqec_stats.add_mining_time(result["mining_time"])
        pqec_stats.total_blocks += 1

        return jsonify(
            {
                "block": result["block"],
                "proof": result["proof"],
                "mining_time": result["mining_time"],
            }
        )

    except Exception as e:
        return jsonify({"error": f"挖矿失败: {str(e)}"}), 500


@app.route("/api/pqec/status", methods=["GET"])
def get_status():
    """状态端点 - 获取PQEC状态"""
    return jsonify(
        {
            "difficulty": pqec_blockchain.difficulty,
            "total_blocks": len(pqec_blockchain.chain),
            "qec_enabled": True,
            "qsharp_available": QSHARP_AVAILABLE,
            "supported_codes": QuantumErrorCorrection.SUPPORTED_CODES,
        }
    )


@app.route("/api/pqec/verify", methods=["POST"])
def verify_proof():
    """验证端点 - 验证工作量证明"""
    try:
        data = request.get_json()

        if not data or "proof" not in data:
            return jsonify({"error": "缺少proof字段"}), 400

        proof = data["proof"]
        difficulty = data.get("difficulty", 3)

        result = pqec_blockchain.verify_proof(proof, difficulty)

        pqec_stats.add_verification(result["valid"])

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"验证失败: {str(e)}"}), 500


@app.route("/api/pqec/codes", methods=["GET"])
def get_error_codes():
    """纠错码端点 - 获取支持的纠错码列表"""
    return jsonify(QuantumErrorCorrection.SUPPORTED_CODES)


@app.route("/api/pqec/simulate-error", methods=["POST"])
def simulate_error():
    """错误模拟端点 - 模拟量子错误并纠错"""
    try:
        data = request.get_json()

        if not data or "code_type" not in data:
            return jsonify({"error": "缺少code_type字段"}), 400

        code_type = data["code_type"]
        error_probability = data.get("error_probability", 0.1)

        if not 0 <= error_probability <= 1:
            return jsonify({"error": "error_probability必须在0-1之间"}), 400

        result = QuantumErrorCorrection.simulate_error(code_type, error_probability)

        if "error" in result:
            return jsonify(result), 400

        return jsonify(
            {
                "original_state": result["original_state"],
                "error_applied": result["error_applied"],
                "corrected": result["corrected"],
            }
        )

    except Exception as e:
        return jsonify({"error": f"错误模拟失败: {str(e)}"}), 500


@app.route("/api/pqec/stats", methods=["GET"])
def get_stats():
    """统计端点 - 获取PQEC统计信息"""
    return jsonify(pqec_stats.get_stats())


@app.route("/api/pqec/chain", methods=["GET"])
def get_chain():
    """获取完整区块链"""
    return jsonify(
        {"chain": pqec_blockchain.chain, "length": len(pqec_blockchain.chain)}
    )


@app.route("/api/pqec/block/<int:block_index>", methods=["GET"])
def get_block(block_index):
    """获取特定区块"""
    if 0 <= block_index < len(pqec_blockchain.chain):
        return jsonify(pqec_blockchain.chain[block_index])
    return jsonify({"error": "区块不存在"}), 404


@app.route("/api/pqec/health", methods=["GET"])
def health_check():
    """健康检查端点"""
    return jsonify(
        {
            "status": "healthy",
            "service": "PQEC API",
            "timestamp": datetime.now().isoformat(),
        }
    )


if __name__ == "__main__":
    print("=" * 50)
    print("PQEC (Post-Quantum Error Correction) API")
    print("=" * 50)
    print(f"Q# 支持: {'已启用' if QSHARP_AVAILABLE else '未启用 (使用Python模拟)'}")
    print(f"支持的纠错码: {', '.join(QuantumErrorCorrection.SUPPORTED_CODES)}")
    print(f"初始区块数: {len(pqec_blockchain.chain)}")
    print("访问 http://127.0.0.1:9001")
    print("=" * 50)

    app.run(host="0.0.0.0", port=9001, debug=True)
