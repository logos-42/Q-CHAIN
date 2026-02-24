# 量子区块链 Q# 项目

基于Microsoft Q#量子编程语言重新实现的量子区块链项目。

## 项目结构

```
quantum_blockchain_qsharp/
├── src/
│   ├── QuantumRandom.qs    # 量子随机数生成器
│   ├── QuantumHash.qs      # 量子哈希函数
│   └── Blockchain.qs       # 区块链核心逻辑
├── host/
│   ├── app.py              # Flask Web服务器
│   └── requirements.txt    # Python依赖
├── qsharp.json             # Q#项目配置
├── QuantumBlockchain.csproj
└── README.md
```

## 技术栈

- **Q#** - 量子计算核心 (Microsoft Quantum SDK)
- **Python** - 主机层 + Flask Web服务
- **qsharp** - Q#与Python集成

## 快速开始

### 1. 安装依赖

```bash
# 安装.NET SDK和QDK
# 访问 https://docs.microsoft.com/quantum/install-guide/

# 安装Python依赖
cd host
pip install -r requirements.txt
```

### 2. 运行Q#模块测试

```bash
cd quantum_blockchain_qsharp
dotnet run
```

### 3. 启动Web服务

```bash
cd host
python app.py
```

访问 http://127.0.0.1:9000

## Q#模块说明

### QuantumRandom.qs

- `GenerateRandomBits(nBits)` - 生成量子随机比特
- `BitStringToHex(bits)` - 比特转十六进制
- `GenerateQuantumSignature()` - 生成量子签名

### QuantumHash.qs

- `QuantumHashCircuit(data)` - 量子哈希电路
- `HybridHash(data, outputSize)` - 混合哈希函数

### Blockchain.qs

- `CreateGenesisBlock()` - 创建创世区块
- `AddBlock(chain, data)` - 添加新区块
- `IsChainValid(chain)` - 验证区块链

## API端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/blockchain` | GET | 获取完整区块链 |
| `/api/blocks` | GET | 获取所有区块 |
| `/api/block/<index>` | GET | 获取特定区块 |
| `/api/block/latest` | GET | 获取最新区块 |
| `/api/blocks/add` | POST | 添加新区块 |
| `/api/transactions` | GET | 获取交易列表 |
| `/api/validate` | GET | 验证区块链 |

## 量子计算特性

1. **量子随机数生成** - 使用H门创建叠加态
2. **量子哈希** - 量子电路 + 经典哈希混合
3. **量子签名** - 256位量子签名

## 许可证

MIT
