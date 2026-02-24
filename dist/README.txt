私有区块链节点使用说明
========================

本程序实现了一个简易的私有区块链节点，可以用于创建和管理自己的区块链网络。
多个节点可以互相连接，形成一个私有区块链网络。

快速启动：
1. Windows: 双击 start_node.bat
2. Linux/Mac: 在终端中执行 chmod +x start_node.sh 然后运行 ./start_node.sh

目录结构：
- PrivateBlockchain.exe: 主程序
- blockchain_data/: 区块链数据存储目录
- config/: 配置文件目录
  - node_config.json: 节点配置示例
- start_node.bat: Windows启动脚本
- start_node.sh: Linux/Mac启动脚本

命令行参数：
  --host HOST         主机地址 (默认: localhost，建议使用0.0.0.0接受所有连接)
  --port PORT         端口号 (默认: 5000)
  --difficulty DIFF   挖矿难度 (默认: 4)
  --token_name NAME   代币名称 (默认: MyToken)
  --token_symbol SYM  代币符号 (默认: MTK)
  --token_supply SUP  代币初始供应量 (默认: 100000000000)
  --auto_external     自动检测并使用外部IP地址
  --data_dir DIR      数据目录 (默认: blockchain_data)
  --config FILE       配置文件路径
  --connect NODE      启动时连接的节点地址，格式为host:port
  --demo              运行演示模式

示例：
PrivateBlockchain.exe --host 0.0.0.0 --port 5001 --token_name "MyChain" --token_symbol "MYC"
PrivateBlockchain.exe --connect 192.168.1.100:5000  # 连接到另一个节点

节点启动后，可以使用以下命令：
  add_block <data>           - 添加新区块
  show_chain                 - 显示整个区块链
  token_info                 - 显示代币信息
  balance <address>          - 查询地址余额
  transfer <to> <amount>     - 转移代币到指定地址
  mint <to> <amount>         - 铸造新代币（仅限创建者）
  all_balances               - 显示所有账户余额
  save                       - 保存区块链到文件
  load                       - 从文件加载区块链
  generate_keypair           - 生成新的密钥对
  connect <host:port>        - 连接到其他节点
  show_peers                 - 显示已连接的节点
  exit                       - 退出节点

连接多个节点创建网络：
1. 在第一台电脑上启动节点: PrivateBlockchain.exe --host 0.0.0.0 --port 5000 --auto_external
2. 记下第一个节点的IP地址和端口，如 192.168.1.100:5000
3. 在第二台电脑上启动节点并连接到第一个: PrivateBlockchain.exe --connect 192.168.1.100:5000
4. 现在两个节点已经连接成为一个网络，可以共享区块链数据

注意事项：
- 如果您的计算机有防火墙，需要允许程序通过端口（默认5000）进行通信
- 连接外部网络的节点需要公网IP或端口转发
- 区块链数据保存在blockchain_data目录中，请不要删除此目录
- 为了安全，请妥善保管您的私钥
使用方法：
节点启动：   PrivateBlockchain.exe --host 0.0.0.0 --port 5000 --auto_external
连接到其他节点：   PrivateBlockchain.exe --connect 192.168.1.100:5000
节点可以使用的命令：
add_block <data> - 添加新区块
show_chain - 显示整个区块链
connect <host:port> - 连接到其他节点
save - 保存区块链数据
load - 加载区块链数据