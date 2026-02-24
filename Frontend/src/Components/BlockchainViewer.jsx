import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Button, 
  Input, 
  Space, 
  Tag, 
  Tooltip, 
  message,
  Spin,
  Card,
  Row,
  Col,
  Statistic,
  Modal,
  Descriptions
} from 'antd';
import { 
  SearchOutlined, 
  EyeOutlined, 
  ReloadOutlined,
  CopyOutlined,
  LinkOutlined
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import blockApi from '../Services/api';

const { Search } = Input;

function BlockchainViewer({ onRefresh }) {
  const [blocks, setBlocks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [searching, setSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedBlock, setSelectedBlock] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  // 获取区块列表
  const fetchBlocks = async () => {
    try {
      setLoading(true);
      const response = await blockApi.getBlockchain();
      setBlocks(response.data);
    } catch (error) {
      console.error('获取区块列表失败:', error);
      message.error('获取区块列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 搜索区块
  const handleSearch = async (value) => {
    if (!value.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setSearching(true);
      const response = await blockApi.searchBlocks(value);
      setSearchResults(response.data.blocks);
    } catch (error) {
      console.error('搜索失败:', error);
      message.error('搜索失败');
    } finally {
      setSearching(false);
    }
  };

  // 复制到剪贴板
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      message.success('已复制到剪贴板');
    });
  };

  // 格式化时间
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN');
  };

  // 格式化大小
  const formatSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 获取区块状态标签
  const getBlockStatusTag = (block) => {
    if (block.index === 0) {
      return <Tag color="gold">创世区块</Tag>;
    } else if (block.data.transactions.length > 0) {
      return <Tag color="green">已确认</Tag>;
    } else {
      return <Tag color="blue">空区块</Tag>;
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '高度',
      dataIndex: 'index',
      key: 'index',
      width: 80,
      sorter: (a, b) => a.index - b.index,
      render: (index) => (
        <Link to={`/blocks/${index}`} style={{ fontWeight: 'bold' }}>
          #{index}
        </Link>
      ),
    },
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (timestamp) => formatTime(timestamp),
      sorter: (a, b) => new Date(a.timestamp) - new Date(b.timestamp),
    },
    {
      title: '交易数',
      dataIndex: 'data',
      key: 'transactionCount',
      width: 100,
      render: (data) => (
        <Tag color="blue">{data.transactions.length}</Tag>
      ),
      sorter: (a, b) => a.data.transactions.length - b.data.transactions.length,
    },
    {
      title: '大小',
      dataIndex: 'blockSize',
      key: 'size',
      width: 100,
      render: (size) => formatSize(size),
      sorter: (a, b) => a.blockSize - b.blockSize,
    },
    {
      title: '状态',
      key: 'status',
      width: 100,
      render: (_, record) => getBlockStatusTag(record),
    },
    {
      title: '区块哈希',
      dataIndex: 'hash',
      key: 'hash',
      width: 200,
      ellipsis: {
        showTitle: false,
      },
      render: (hash) => (
        <Tooltip placement="topLeft" title={hash}>
          <Space>
            <span>{hash.substring(0, 12)}...</span>
            <Button 
              type="text" 
              size="small" 
              icon={<CopyOutlined />}
              onClick={() => copyToClipboard(hash)}
            />
          </Space>
        </Tooltip>
      ),
    },
    {
      title: '前一区块哈希',
      dataIndex: 'previousHash',
      key: 'previousHash',
      width: 200,
      ellipsis: {
        showTitle: false,
      },
      render: (previousHash) => (
        <Tooltip placement="topLeft" title={previousHash}>
          <Space>
            <span>{previousHash.substring(0, 12)}...</span>
            <Button 
              type="text" 
              size="small" 
              icon={<LinkOutlined />}
            />
          </Space>
        </Tooltip>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button
          type="primary"
          icon={<EyeOutlined />}
          onClick={() => {
            setSelectedBlock(record);
            setModalVisible(true);
          }}
        >
          详情
        </Button>
      ),
    },
  ];

  useEffect(() => {
    fetchBlocks();
    // 每10秒刷新一次
    const interval = setInterval(fetchBlocks, 10000);
    return () => clearInterval(interval);
  }, []);

  // 如果有搜索结果，显示搜索结果，否则显示所有区块
  const displayData = searchResults.length > 0 ? searchResults : blocks;

  return (
    <div>
      {/* 搜索区域 */}
      <Card style={{ marginBottom: '16px' }}>
        <Row gutter={[16, 16]}>
          <Col span={16}>
            <Search
              placeholder="搜索区块高度、哈希或量子签名..."
              enterButton="搜索"
              size="large"
              loading={searching}
              onSearch={handleSearch}
              onChange={(e) => setSearchText(e.target.value)}
              value={searchText}
            />
          </Col>
          <Col span={8}>
            <Space>
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                onClick={fetchBlocks}
                loading={loading}
              >
                刷新
              </Button>
              <Button onClick={() => { setSearchText(''); setSearchResults([]); }}>
                清除搜索
              </Button>
            </Space>
          </Col>
        </Row>
        
        {searchResults.length > 0 && (
          <div style={{ marginTop: '16px' }}>
            <Tag color="blue">
              搜索结果: {searchResults.length} 个区块
            </Tag>
            <Button 
              type="link" 
              size="small"
              onClick={() => { setSearchText(''); setSearchResults([]); }}
            >
              查看所有区块
            </Button>
          </div>
        )}
      </Card>

      {/* 统计信息 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总区块数"
              value={blocks.length}
              prefix={<span>📦</span>}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="总交易数"
              value={blocks.reduce((sum, block) => sum + block.data.transactions.length, 0)}
              prefix={<span>💳</span>}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="最新高度"
              value={blocks.length > 0 ? blocks[blocks.length - 1].index : 0}
              prefix={<span>🔝</span>}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="数据大小"
              value={formatSize(blocks.reduce((sum, block) => sum + block.blockSize, 0))}
              prefix={<span>💾</span>}
            />
          </Card>
        </Col>
      </Row>

      {/* 区块列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={displayData}
          rowKey="index"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个区块`,
            pageSizeOptions: ['10', '20', '50', '100']
          }}
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 区块详情模态框 */}
      <Modal
        title={`区块详情 - #${selectedBlock?.index}`}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedBlock && (
          <Descriptions bordered column={2}>
            <Descriptions.Item label="区块高度" span={1}>
              <strong>#{selectedBlock.index}</strong>
            </Descriptions.Item>
            <Descriptions.Item label="时间戳" span={1}>
              {formatTime(selectedBlock.timestamp)}
            </Descriptions.Item>
            <Descriptions.Item label="交易数量" span={1}>
              <Tag color="green">{selectedBlock.data.transactions.length}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="区块大小" span={1}>
              {formatSize(selectedBlock.blockSize)}
            </Descriptions.Item>
            <Descriptions.Item label="区块哈希" span={2}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <code style={{ fontSize: '12px' }}>{selectedBlock.hash}</code>
                <Button 
                  type="text" 
                  icon={<CopyOutlined />}
                  onClick={() => copyToClipboard(selectedBlock.hash)}
                />
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="前一区块哈希" span={2}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <code style={{ fontSize: '12px' }}>{selectedBlock.previousHash}</code>
                <Button 
                  type="text" 
                  icon={<CopyOutlined />}
                  onClick={() => copyToClipboard(selectedBlock.previousHash)}
                />
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="量子签名" span={2}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <code style={{ fontSize: '12px' }}>{selectedBlock.quantumSignature}</code>
                <Button 
                  type="text" 
                  icon={<CopyOutlined />}
                  onClick={() => copyToClipboard(selectedBlock.quantumSignature)}
                />
              </div>
            </Descriptions.Item>
            <Descriptions.Item label="随机数(Nonce)" span={1}>
              {selectedBlock.nonce}
            </Descriptions.Item>
            <Descriptions.Item label="Merkle根" span={1}>
              {selectedBlock.merkleRoot.substring(0, 20)}...
            </Descriptions.Item>
            <Descriptions.Item label="区块消息" span={2}>
              {selectedBlock.data.message}
            </Descriptions.Item>
            <Descriptions.Item label="量子密钥" span={2}>
              <code style={{ fontSize: '12px' }}>{selectedBlock.data.quantumKey}</code>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
}

export default BlockchainViewer;