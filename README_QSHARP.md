# 量子区块链 Q# 重新实现项目

## 项目概述

这是一个使用 Q# 量子编程语言重新实现的量子区块链系统，通过子智能体并发执行的方式高效完成项目开发。

## 项目架构

### 1. Q# 量子核心模块 (`QuantumAlgorithms.qs`)
- **量子随机数生成器** - 使用量子叠加态生成真随机数
- **量子哈希函数** - 基于量子行走和量子傅里叶变换
- **BB84 量子密钥分发** - 实现量子安全通信
- **Grover 搜索算法** - 用于量子挖矿加速
- **量子纠缠态生成** - Bell态、GHZ态、W态、Cluster态
- **量子签名算法** - 基于量子特性的不可伪造签名

### 2. 区块链逻辑层 (`Models/`, `Services/`)
- **Block 模型** - 区块数据结构，包含量子特性字段
- **Transaction 模型** - 交易数据结构，支持多种交易类型
- **BlockchainService** - 区块链核心业务逻辑
- **IBlockchainService** - 服务接口定义

### 3. Web API 层 (`WebApi/`, `Controllers/`)
- **BlockchainController** - 区块链核心API
- **BlockController** - 区块管理API
- **TransactionController** - 交易管理API
- **QuantumController** - 量子功能API

### 4. 前端界面 (`Frontend/`)
- **React + Ant Design** - 现代化Web界面
- **区块链浏览器** - 可视化区块链数据
- **交易管理** - 创建和查看交易
- **量子功能演示** - 量子算法可视化

## 技术栈

### 后端技术
- **.NET 8.0** - 主要开发框架
- **ASP.NET Core Web API** - RESTful API服务
- **Q#** - 量子算法实现
- **Entity Framework Core** - 数据访问层（可选）
- **Microsoft.Quantum.Sdk** - Q#开发工具包

### 前端技术
- **React 18** - 前端框架
- **Ant Design** - UI组件库
- **React Router** - 路由管理
- **Axios** - HTTP客户端
- **Tailwind CSS** - CSS框架

### 开发工具
- **Visual Studio 2022** - 主要开发环境
- **Node.js** - 前端开发环境
- **Docker** - 容器化部署

## 项目特色

### 量子特性
1. **真随机数生成** - 利用量子叠加态的不可预测性
2. **量子哈希函数** - 结合经典哈希和量子测量
3. **量子签名** - 基于量子不可克隆定理
4. **量子挖矿** - Grover算法提供二次加速
5. **量子密钥分发** - BB84协议确保通信安全

### 区块链特性
1. **完整的区块链结构** - 区块链、交易、挖矿
2. **Merkle树** - 量子增强的Merkle根计算
3. **共识机制** - 工作量证明（PoW）
4. **代币系统** - 创世区块包含代币信息

### 现代化架构
1. **微服务架构** - 前后端分离
2. **RESTful API** - 标准化的API接口
3. **响应式设计** - 支持移动端访问
4. **实时更新** - WebSocket支持（可选）

## 快速开始

### 环境要求
- .NET 8.0 SDK
- Node.js 18+
- Visual Studio 2022 (推荐)
- Q# 开发工具包

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd 量子区块链
```

2. **后端设置**
```bash
cd WebApi
dotnet restore
dotnet build
dotnet run
```

3. **前端设置**
```bash
cd Frontend
npm install
npm run dev
```

4. **访问应用**
- API服务: http://localhost:5000
- 前端界面: http://localhost:5173

## API 接口

### 区块链API
- `GET /api/blockchain` - 获取完整区块链
- `GET /api/blockchain/stats` - 获取统计信息
- `GET /api/blockchain/validate` - 验证区块链

### 区块API
- `GET /api/block/latest` - 获取最新区块
- `GET /api/block/{index}` - 根据索引获取区块
- `GET /api/block/range` - 获取区块范围
- `GET /api/block/search` - 搜索区块

### 交易API
- `GET /api/transaction` - 获取所有交易
- `POST /api/transaction` - 创建新交易
- `GET /api/transaction/address/{address}` - 获取地址交易历史

### 量子功能API
- `GET /api/quantum/random` - 生成量子随机数
- `POST /api/quantum/hash` - 生成量子哈希
- `POST /api/quantum/sign` - 生成量子签名
- `GET /api/quantum/qkd` - 量子密钥分发
- `POST /api/quantum/mine` - 量子挖矿

## 项目结构

```
量子区块链/
├── QuantumAlgorithms.qs              # Q#量子算法核心
├── Models/                           # 数据模型
│   ├── Block.cs                     # 区块模型
│   ├── Transaction.cs               # 交易模型
│   └── TokenInfo.cs                 # 代币信息
├── Services/                        # 业务逻辑层
│   ├── BlockchainService.cs         # 区块链服务
│   └── IBlockchainService.cs        # 服务接口
├── Controllers/                     # Web API控制器
│   ├── BlockchainController.cs      # 区块链API
│   ├── BlockController.cs           # 区块API
│   ├── TransactionController.cs     # 交易API
│   └── QuantumController.cs         # 量子功能API
├── WebApi/                          # ASP.NET Core Web API
│   ├── Program.cs                   # 应用启动配置
│   └── appsettings.json             # 配置文件
├── Frontend/                        # React前端
│   ├── src/
│   │   ├── App.jsx                  # 主应用组件
│   │   ├── main.jsx                 # 应用入口
│   │   ├── Components/              # 组件目录
│   │   │   ├── BlockchainViewer.jsx # 区块链浏览器
│   │   │   ├── TransactionList.jsx  # 交易列表
│   │   │   ├── QuantumVisualizer.jsx # 量子可视化
│   │   │   └── AddBlock.jsx         # 添加区块
│   │   └── Services/                # API服务
│   │       └── api.js               # API客户端
│   ├── package.json                 # 前端依赖
│   └── vite.config.js               # Vite配置
├── Tests/                           # 测试项目
│   ├── UnitTests/                   # 单元测试
│   ├── IntegrationTests/            # 集成测试
│   └── EndToEndTests/               # 端到端测试
└── README.md                        # 项目文档
```

## 开发指南

### Q# 量子算法开发
1. 使用 Visual Studio 2022 打开解决方案
2. 在 `QuantumAlgorithms.qs` 中编写量子算法
3. 使用 Q# 模拟器测试量子算法
4. 通过 C# 主程序调用量子操作

### 区块链功能开发
1. 在 `Models/` 中定义数据结构
2. 在 `Services/` 中实现业务逻辑
3. 在 `Controllers/` 中暴露API接口
4. 编写单元测试确保代码质量

### 前端界面开发
1. 使用 React 组件化开发
2. 集成 Ant Design 组件库
3. 通过 API 与后端交互
4. 实现响应式设计

## 测试

### 单元测试
```bash
cd Tests/UnitTests
dotnet test
```

### 集成测试
```bash
cd Tests/IntegrationTests
dotnet test
```

### 端到端测试
```bash
cd Tests/EndToEndTests
dotnet test
```

## 部署

### Docker 部署
```bash
# 构建镜像
docker build -t quantum-blockchain .

# 运行容器
docker run -p 5000:80 quantum-blockchain
```

### Azure 部署
1. 将项目推送到 Azure DevOps 或 GitHub
2. 配置 Azure App Service
3. 设置 CI/CD 管道
4. 自动部署到云端

## 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目维护者: [你的名字]
- 邮箱: [你的邮箱]
- 项目链接: [https://github.com/yourusername/quantum-blockchain](https://github.com/yourusername/quantum-blockchain)

## 致谢

- Microsoft Quantum Development Kit
- .NET Foundation
- React 社区
- Ant Design 团队

---

**注意**: 这是一个教育和研究项目，用于展示量子计算在区块链技术中的应用潜力。实际生产环境使用前需要进行充分的安全评估和性能测试。