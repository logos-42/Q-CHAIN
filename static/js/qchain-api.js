/**
 * Q-CHAIN 统一API客户端
 * 使用方式:
 *   const api = new QChainAPI();
 *   const result = await api.query('get_blockchain');
 *   const block = await api.query('pqec_mine', {data: 'test', difficulty: 3});
 */

class QChainAPI {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    async query(action, params = {}) {
        const response = await fetch('/api/v1/query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                action: action,
                params: params,
                version: '1.0'
            })
        });
        
        const result = await response.json();
        
        if (result.code !== 0) {
            throw new Error(result.message);
        }
        
        return result.data;
    }

    // ===== 区块链操作 =====
    async getBlockchain() {
        return this.query('get_blockchain');
    }

    async getBlocks() {
        return this.query('get_blocks');
    }

    async getBlock(index) {
        return this.query('get_block', {index});
    }

    async getLatestBlock() {
        return this.query('get_latest_block');
    }

    async addBlock(data, proof = '') {
        return this.query('add_block', {data, proof});
    }

    async validateChain() {
        return this.query('validate_chain');
    }

    // ===== PQEC操作 =====
    async pqecMine(data, difficulty = 3) {
        return this.query('pqec_mine', {data, difficulty});
    }

    async pqecVerify(proof, difficulty = 3) {
        return this.query('pqec_verify', {proof, difficulty});
    }

    async pqecStatus() {
        return this.query('pqec_status');
    }

    async pqecStats() {
        return this.query('pqec_stats');
    }

    async pqecCodes() {
        return this.query('pqec_codes');
    }

    async pqecSimulateError(codeType, errorProb) {
        return this.query('pqec_simulate_error', {
            code_type: codeType,
            error_probability: errorProb
        });
    }

    // ===== 量子操作 =====
    async quantumSignature(bits = 256) {
        return this.query('quantum_generate_signature', {bits});
    }

    async quantumHash(data, size = 64) {
        return this.query('quantum_hash', {data, size});
    }

    async quantumRandom(bits = 64) {
        return this.query('quantum_random', {bits});
    }

    // ===== 交易操作 =====
    async getTransactions() {
        return this.query('get_transactions');
    }

    // ===== 搜索 =====
    async search(query) {
        return this.query('search', {query});
    }
}

// 全局实例
const api = new QChainAPI();
