import { useState, useEffect } from 'react'
import { Row, Col, Card, Statistic, Table, Tag, Typography } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { apiService, ArbitrageOpportunity } from '../services/api'
import type { ColumnsType } from 'antd/es/table'

const { Title } = Typography

export default function Dashboard() {
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 10000) // Refresh every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const result = await apiService.getArbitrageOpportunities({ limit: 20 })
      setOpportunities(result.data || [])
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  const columns: ColumnsType<ArbitrageOpportunity> = [
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (text: string) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: 'Buy From',
      dataIndex: 'buy_exchange',
      key: 'buy_exchange',
      render: (text: string) => <Tag color="green">{text.toUpperCase()}</Tag>,
    },
    {
      title: 'Sell To',
      dataIndex: 'sell_exchange',
      key: 'sell_exchange',
      render: (text: string) => <Tag color="red">{text.toUpperCase()}</Tag>,
    },
    {
      title: 'Buy Price',
      dataIndex: 'buy_price',
      key: 'buy_price',
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: 'Sell Price',
      dataIndex: 'sell_price',
      key: 'sell_price',
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: 'Spread %',
      dataIndex: 'spread_pct',
      key: 'spread_pct',
      render: (pct: number) => (
        <span style={{ color: pct > 0 ? '#3f8600' : '#cf1322' }}>
          {pct > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />} {pct.toFixed(2)}%
        </span>
      ),
      sorter: (a, b) => a.spread_pct - b.spread_pct,
      defaultSortOrder: 'descend',
    },
    {
      title: 'Est. Profit %',
      dataIndex: 'estimated_profit',
      key: 'estimated_profit',
      render: (profit: number) => (
        <Tag color={profit > 0.5 ? 'success' : 'warning'}>
          {profit.toFixed(2)}%
        </Tag>
      ),
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence_score',
      key: 'confidence_score',
      render: (score: number) => (
        <span>{(score * 100).toFixed(0)}%</span>
      ),
    },
  ]

  const topOpportunities = opportunities.slice(0, 3)
  const avgProfit = opportunities.length > 0
    ? opportunities.reduce((sum, opp) => sum + opp.estimated_profit, 0) / opportunities.length
    : 0

  return (
    <div>
      <Title level={2}>Dashboard</Title>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Total Opportunities"
              value={opportunities.length}
              prefix={<ThunderboltOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Avg. Estimated Profit"
              value={avgProfit}
              precision={2}
              suffix="%"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Top Opportunity"
              value={topOpportunities[0]?.estimated_profit || 0}
              precision={2}
              suffix="%"
              prefix={<ArrowUpOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Top Arbitrage Opportunities" style={{ marginTop: 24 }}>
        <Table
          columns={columns}
          dataSource={opportunities}
          rowKey={(record) => `${record.symbol}-${record.buy_exchange}-${record.sell_exchange}-${record.timestamp}`}
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  )
}
