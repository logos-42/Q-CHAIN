import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { 
  Layout, 
  Menu, 
  Card, 
  Statistic, 
  Row, 
  Col, 
  Spin, 
  message,
  theme,
  ConfigProvider
} from 'antd';
import {
  DashboardOutlined,
  BlockOutlined,
  TransactionOutlined,
  ApiOutlined,
  PlusOutlined,
  ReloadOutlined
} from '@ant-design/icons';

// 导入组件
import BlockchainViewer from './Components/BlockchainViewer';
import BlockDetail from './Components/BlockDetail';
import TransactionList from './Components/TransactionList';
import QuantumVisualizer from './Components/QuantumVisualizer';
import AddBlock from './Components/AddBlock';

// 导入API服务
import api from './Services/api';

const { Header, Sider, Content } = Layout;

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedKey, setSelectedKey] = useState('dashboard');

  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 获取统计数据
  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await api.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('获取统计数据失败:', error);
      message.error('获取统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    // 每30秒刷新一次统计数据
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '仪表板',
      path: '/'
    },
    {
      key: 'blocks',
      icon: <BlockOutlined />,
      label: '区块链浏览器',
      path: '/blocks'
    },
    {
      key: 'transactions',
      icon: <TransactionOutlined />,
      label: '交易管理',
      path: '/transactions'
    },
    {
      key: 'quantum',
      icon: <ApiOutlined />,
      label: '量子功能',
      path: '/quantum'
    },
    {
      key: 'add-block',
      icon: <PlusOutlined />,
      label: '添加区块',
      path: '/add-block'
    }
  ];

  const handleMenuClick = (e) => {
    setSelectedKey(e.key);
  };

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
      }}
    >
      <Router>
        <Layout style={{ minHeight: '100vh' }}>
          <Sider 
            collapsible 
            collapsed={collapsed} 
            onCollapse={(value) => setCollapsed(value)}
            theme="dark"
          >
            <div style={{ 
              height: 64, 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              color: 'white',
              fontSize: '18px',
              fontWeight: 'bold'
            }}>
              {collapsed ? 'QBC' : '量子区块链'}
            </div>
            <Menu
              theme="dark"
              selectedKeys={[selectedKey]}
              mode="inline"
              items={menuItems.map(item => ({
                key: item.key,
                icon: item.icon,
                label: item.label,
                onClick: () => setSelectedKey(item.key)
              }))}
            />
          </Sider>
          
          <Layout>
            <Header style={{ 
              padding: '0 16px', 
              background: colorBgContainer,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              borderBottom: '1px solid #f0f0f0'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>
                  量子区块链浏览器
                </h1>
                <span style={{ 
                  background: '#f0f0f0', 
                  padding: '4px 8px', 
                  borderRadius: '4px',
                  fontSize: '12px',
                  color: '#666'
                }}>
                  Q# + .NET 8.0 + React
                </span>
              </div>
              
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={fetchStats}
                  style={{
                    padding: '8px 16px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '6px',
                    background: 'white',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <ReloadOutlined />
                  刷新
                </button>
              </div>
            </Header>

            <Content style={{ 
              margin: '16px',
              padding: 24,
              minHeight: 280,
              background: colorBgContainer,
              borderRadius: borderRadiusLG 
            }}>
              {loading && (
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center', 
                  height: '100px' 
                }}>
                  <Spin size="large" />
                </div>
              )}

              {/* 统计卡片 */}
              {stats && !loading && (
                <div style={{ marginBottom: '24px' }}>
                  <Row gutter={[16, 16]}>
                    <Col xs={24} sm={12} md={6}>
                      <Card>
                        <Statistic
                          title="区块总数"
                          value={stats.blockCount}
                          prefix={<BlockOutlined />}
                          valueStyle={{ color: '#1890ff' }}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <Card>
                        <Statistic
                          title="总交易数"
                          value={stats.totalTransactions}
                          prefix={<TransactionOutlined />}
                          valueStyle={{ color: '#52c41a' }}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <Card>
                        <Statistic
                          title="区块链状态"
                          value={stats.isValid ? '正常' : '异常'}
                          prefix={<DashboardOutlined />}
                          valueStyle={{ color: stats.isValid ? '#52c41a' : '#ff4d4f' }}
                        />
                      </Card>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <Card>
                        <Statistic
                          title="数据大小"
                          value={Math.round(stats.totalSize / 1024 / 1024)}
                          suffix="MB"
                          prefix={<ApiOutlined />}
                          valueStyle={{ color: '#722ed1' }}
                        />
                      </Card>
                    </Col>
                  </Row>
                </div>
              )}

              {/* 路由内容 */}
              <Routes>
                <Route 
                  path="/" 
                  element={<Navigate to="/blocks" replace />} 
                />
                <Route 
                  path="/blocks" 
                  element={<BlockchainViewer onRefresh={fetchStats} />} 
                />
                <Route 
                  path="/blocks/:index" 
                  element={<BlockDetail />} 
                />
                <Route 
                  path="/transactions" 
                  element={<TransactionList />} 
                />
                <Route 
                  path="/quantum" 
                  element={<QuantumVisualizer />} 
                />
                <Route 
                  path="/add-block" 
                  element={<AddBlock onRefresh={fetchStats} />} 
                />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Router>
    </ConfigProvider>
  );
}

export default App;