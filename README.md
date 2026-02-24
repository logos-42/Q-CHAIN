# 量子区块链项目 (Q-CHAIN)

## 项目愿景

创建一个**抗量子的区块链系统**，使用**Proof of Quantum Error Correction (PQEC)** 作为共识机制。

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           用户层 (Web界面)                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│   │  index.html │  │ blocks.html │  │ pqec.html   │  │  其他页面 │  │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘  │
└──────────┼─────────────────┼─────────────────┼────────────────┼───────┘
           │                 │                 │                │
           ▼                 ▼                 ▼                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        API 层 (Flask + ASP.NET Core)                    │
│   ┌─────────────────────────┐    ┌─────────────────────────────────┐   │
│   │   Flask (Python)        │    │   WebApi (C# ASP.NET Core)      │   │
│   │   - /api/blockchain     │    │   - /api/block                  │   │
│   │   - /api/pqec/*         │    │   - /api/transaction           │   │
│   │   - /api/quantum/*      │    │   - SignalR Hubs               │   │
│   └───────────┬─────────────┘    └──────────────┬────────────────┘   │
└──────────────┼──────────────────────────────────┼─────────────────────┘
               │                                  │
               ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        核心层 (Q# 量子计算)                             │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    QuantumAlgorithms.qs                        │  │
│   │  ┌──────────────┐ ┌─────────────┐ ┌────────────┐ ┌─────────┐  │  │
│   │  │ QRNG         │ │ 量子哈希    │ │ BB84 QKD   │ │ Grover  │  │  │
│   │  │ (随机数)     │ │ (Hash)      │ │ (密钥分发) │ │ (挖矿)  │  │  │
│   │  └──────────────┘ └─────────────┘ └────────────┘ └─────────┘  │  │
│   └─────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 技术栈说明

### 为什么使用 Python?

| 用途 | 原因 |
|------|------|
| **Web服务 (Flask)** | 快速原型开发、丰富的库生态 |
| **量子模拟集成** | `qsharp` Python包可调用Q#模块 |
| **数据处理** | JSON序列化、区块链数据管理 |
| **传统API** | 快速构建RESTful接口 |

**示例**: `app.py` 提供HTTP API，`pqec_app.py` 提供PQEC专用接口

---

### 为什么使用 C# (.NET)?

| 用途 | 原因 |
|------|------|
| **WebApi** | 企业级API框架，高性能 |
| **SignalR** | 实时通信（区块链更新推送） |
| **项目结构** | 完善的MVC/三层架构 |

**示例**: `Controllers/` 处理API请求，`Services/` 包含业务逻辑

---

### 为什么使用 Q#?

| 用途 | 原因 |
|------|------|
| **量子算法** | 微软官方量子编程语言 |
| **量子模拟** | 内置多种量子模拟器 |
| **算法库** | 丰富的量子门、操作、测量支持 |

**示例**: `QuantumAlgorithms.qs` 包含所有量子算法

---

## 项目模块结构

```
D:\AI\量子区块链\
│
├── quantum_blockchain_qsharp/     ← 新的Q#项目 (PQEC)
│   ├── src/
│   │   ├── QuantumRandom.qs       # 量子随机数生成
│   │   ├── QuantumHash.qs        # 量子哈希函数
│   │   ├── QuantumErrorCorrection.qs  # 量子纠错码
│   │   ├── QuantumProof.qs       # PQEC协议
│   │   └── PQECBlockchain.qs    # 区块链共识
│   └── host/
│       ├── app.py                # Flask Web服务
│       └── pqec_app.py           # PQEC专用API
│
├── QuantumAlgorithms.qs          ← 原有Q#核心算法
│   ├── 量子随机数 (QRNG)
│   ├── 量子哈希 (Quantum Hash)
│   ├── BB84量子密钥分发
│   ├── Grover搜索 (量子挖矿)
│   ├── 量子纠缠态生成
│   └── 量子签名
│
├── Controllers/                  ← C# API控制器
├── Services/                     ← C# 业务逻辑
├── Models/                       ← C# 数据模型
├── WebApi/                       ← C# ASP.NET Core
│
├── app.py                        ← Python Flask Web服务
├── qsharp_integration.py         ← Python调用Q#桥接
│
└── templates/                    ← HTML前端页面
    ├── index.html
    ├── blocks.html
    └── pqec.html                ← PQEC挖矿界面
```

---

## PQEC 共识机制 (核心创新)

### 什么是 Proof of Quantum Error Correction?

```
┌────────────────────────────────────────────────────────────┐
│                    PQEC 工作流程                           │
├────────────────────────────────────────────────────────────┤
│ 1. 编码                                                  │
│    原始数据 → Shor码/表面码 → 9个物理量子比特           │
│                                                             │
│ 2. 错误注入 (模拟噪声)                                    │
│    随机Bit翻转 / 相位错误 / 去极化                        │
│                                                             │
│ 3. 纠错                                                  │
│    测量症状 → 定位错误 → 纠正                            │
│                                                             │
│ 4. 验证                                                  │
│    检查纠错是否成功 + 难度验证                           │
└────────────────────────────────────────────────────────────┘
```

### 为什么选择 PQEC?

| 特性 | 说明 |
|------|------|
| **量子优势** | 真正的量子计算任务，非经典可模拟 |
| **验证快速** | 验证比生成快（只需检查结果） |
| **抗攻击** | 经典计算机难以完成量子纠错任务 |
| **可调难度** | 通过码距和错误率调整 |

---

## 快速开始

### 1. 运行 Python Web服务

```bash
cd quantum_blockchain_qsharp/host
pip install -r requirements.txt
python app.py
# 访问 http://127.0.0.1:9000
```

### 2. 运行 PQEC 专用API

```bash
python pqec_app.py
# 访问 http://127.0.0.1:9001/pqec
```

### 3. 测试 Q# 模块

```bash
cd quantum_blockchain_qsharp
dotnet run
```

---

## API 端点

### Python Flask API

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/blockchain` | GET | 获取完整区块链 |
| `/api/blocks/add` | POST | 添加区块 |
| `/api/pqec/mine` | POST | PQEC挖矿 |
| `/api/pqec/verify` | POST | 验证PQEC Proof |
| `/api/pqec/simulate-error` | POST | 量子纠错模拟 |

### C# WebApi

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/block` | GET, POST | 区块管理 |
| `/api/transaction` | GET, POST | 交易管理 |
| `/blockchain` | GET | SignalR Hub |

---

## 依赖项

### Python
```
flask
flask-cors
qsharp
numpy
```

### .NET
```
.NET 6.0+
Microsoft.Quantum.SDK
```

### Q#
```
Microsoft.Quantum.Standard
```

---

## 常见问题

**Q: 为什么有Python又有C#?**
A: Python用于快速原型和量子集成，C#用于企业级API。两者可以独立运行。

**Q: Q#能做什么?**
A: 实现量子算法（随机数、哈希、纠错），在量子模拟器上运行。

**Q: PQEC和传统POW的区别?**
A: PQEC使用量子纠错任务作为工作量证明，需要真正的量子计算能力。

---

## 项目贡献者

- 量子算法: Q# 实现
- Web层: Python Flask + C# ASP.NET Core
- 前端: HTML/JavaScript
