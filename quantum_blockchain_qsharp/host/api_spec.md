# 统一API v1 规范

## 请求格式

```json
POST /api/v1/query
Content-Type: application/json

{
  "action": "action_name",
  "params": {
    "key": "value"
  },
  "version": "1.0"
}
```

或 GET 方式：

```
GET /api/v1/query?action=action_name&params={"key": "value"}
```

## 响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": {
    // 实际数据
  },
  "timestamp": 1704067200,
  "version": "1.0"
}
```

## 状态码

| code | 含义 |
|------|------|
| 0 | 成功 |
| 1 | 参数错误 |
| 2 | 资源不存在 |
| 3 | 服务器错误 |
| 4 | 未授权 |

---

## Action 列表

### 区块链操作

| action | 说明 | params |
|--------|------|--------|
| `get_blockchain` | 获取完整区块链 | - |
| `get_blocks` | 获取所有区块 | - |
| `get_block` | 获取单个区块 | `{index: int}` |
| `get_latest_block` | 获取最新区块 | - |
| `add_block` | 添加区块 | `{data: object}` |
| `validate_chain` | 验证区块链 | - |

### 交易操作

| action | 说明 | params |
|--------|------|--------|
| `get_transactions` | 获取所有交易 | - |
| `get_transaction` | 获取交易 | `{hash: string}` |

### PQEC共识操作

| action | 说明 | params |
|--------|------|--------|
| `pqec_mine` | PQEC挖矿 | `{data: string, difficulty: int}` |
| `pqec_verify` | 验证Proof | `{proof: string, difficulty: int}` |
| `pqec_status` | 获取状态 | - |
| `pqec_stats` | 获取统计 | - |
| `pqec_codes` | 支持的纠错码 | - |
| `pqec_simulate_error` | 模拟错误 | `{code_type: string, error_probability: float}` |

### 量子操作

| action | 说明 | params |
|--------|------|--------|
| `quantum_generate_signature` | 生成量子签名 | `{bits: int}` |
| `quantum_hash` | 量子哈希 | `{data: string, size: int}` |
| `quantum_random` | 量子随机数 | `{bits: int}` |

### 搜索操作

| action | 说明 | params |
|--------|------|--------|
| `search` | 搜索 | `{query: string}` |

---

## 响应数据结构

### get_blockchain

```json
{
  "chain": [
    {
      "index": 0,
      "timestamp": "1704067200.123",
      "data": {"message": "Genesis"},
      "previous_hash": "0000...0000",
      "quantum_signature": "a1b2c3...",
      "quantum_proof": "pqec_proof_data",
      "hash": "abc123..."
    }
  ],
  "length": 1,
  "qec_enabled": true
}
```

### pqec_mine

```json
{
  "block": {
    "index": 1,
    "hash": "...",
    "quantum_proof": "..."
  },
  "proof": "pqec_proof_string",
  "mining_time": 2.35,
  "difficulty": 3
}
```

### pqec_stats

```json
{
  "total_blocks": 10,
  "total_proofs": 10,
  "success_rate": 1.0,
  "avg_mining_time": 2.5,
  "difficulty": 3,
  "error_correction_codes": ["Shor", "Surface", "BitFlip"]
}
```
