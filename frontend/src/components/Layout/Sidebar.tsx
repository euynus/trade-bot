import { useState } from 'react'
import { Layout, Menu } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  LineChartOutlined,
  DollarOutlined,
  ThunderboltOutlined,
  HistoryOutlined,
} from '@ant-design/icons'

const { Sider } = Layout

export default function AppSidebar() {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/spreads',
      icon: <LineChartOutlined />,
      label: 'Price Spreads',
    },
    {
      key: '/funding-rates',
      icon: <DollarOutlined />,
      label: 'Funding Rates',
    },
    {
      key: '/arbitrage',
      icon: <ThunderboltOutlined />,
      label: 'Arbitrage',
    },
    {
      key: '/historical',
      icon: <HistoryOutlined />,
      label: 'Historical Data',
    },
  ]

  return (
    <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
      <div className="logo">Trade Bot</div>
      <Menu
        theme="dark"
        selectedKeys={[location.pathname]}
        mode="inline"
        items={menuItems}
        onClick={({ key }) => navigate(key)}
      />
    </Sider>
  )
}
