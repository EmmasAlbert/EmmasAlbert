import React, { useState } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import {
  Layout as AntLayout,
  Menu,
  Avatar,
  Dropdown,
  Badge,
  Space,
} from 'antd';
import {
  DashboardOutlined,
  VideoCameraOutlined,
  FileTextOutlined,
  BarChartOutlined,
  BookOutlined,
  TrophyOutlined,
  UserOutlined,
  BellOutlined,
  LogoutOutlined,
} from '@ant-design/icons';

const { Header, Sider, Content } = AntLayout;

const Layout: React.FC = () => {
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '首页',
    },
    {
      key: '/realtime',
      icon: <VideoCameraOutlined />,
      label: '实时训练',
    },
    {
      key: '/video-analysis',
      icon: <FileTextOutlined />,
      label: '视频分析',
    },
    {
      key: '/records',
      icon: <FileTextOutlined />,
      label: '训练记录',
    },
    {
      key: '/analysis',
      icon: <BarChartOutlined />,
      label: '数据分析',
    },
    {
      key: '/courses',
      icon: <BookOutlined />,
      label: '课程学习',
    },
    {
      key: '/achievements',
      icon: <TrophyOutlined />,
      label: '成就系统',
    },
  ];

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: () => navigate('/login'),
    },
  ];

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        theme="dark"
      >
        <div
          style={{
            height: 64,
            margin: 16,
            background: 'rgba(255, 255, 255, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: collapsed ? 18 : 20,
            fontWeight: 'bold',
            color: '#fff',
          }}
        >
          {collapsed ? '🏀' : '🏀 篮球训练'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          defaultSelectedKeys={['/']}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>

      <AntLayout>
        <Header
          style={{
            padding: '0 24px',
            background: '#fff',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div style={{ fontSize: 18, fontWeight: 500 }}>
            篮球训练辅助系统
          </div>

          <Space size="large">
            <Badge count={5}>
              <BellOutlined style={{ fontSize: 20, cursor: 'pointer' }} />
            </Badge>

            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Space style={{ cursor: 'pointer' }}>
                <Avatar src="/avatar.png" icon={<UserOutlined />} />
                <span>学生账号</span>
              </Space>
            </Dropdown>
          </Space>
        </Header>

        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;
