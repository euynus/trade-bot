import { Layout, Space, Typography } from 'antd'
import { DashboardOutlined } from '@ant-design/icons'

const { Header } = Layout
const { Title } = Typography

export default function AppHeader() {
  return (
    <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', alignItems: 'center' }}>
      <Space>
        <DashboardOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
        <Title level={4} style={{ margin: 0 }}>
          CEX/DEX Spread Monitor
        </Title>
      </Space>
    </Header>
  )
}
