import { useState, useEffect } from 'react'
import { Card, Table, Select, Button, Space, Tag, Typography, InputNumber } from 'antd'
import { ReloadOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { apiService, ArbitrageOpportunity } from '../services/api'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'

const { Title } = Typography

export default function ArbitrageOpportunities() {
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([])
  const [symbols, setSymbols] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    symbol: undefined as string | undefined,
    min_spread_pct: 0.5,
  })

  useEffect(() => {
    fetchSymbols()
    fetchOpportunities()
    const interval = setInterval(fetchOpportunities, 10000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    fetchOpportunities()
  }, [filters])

  const fetchSymbols = async () => {
    try {
      const result = await apiService.getSymbols()
      setSymbols(result.data || [])
    } catch (error) {
      console.error('Failed to fetch symbols:', error)
    }
  }

  const fetchOpportunities = async () => {
    try {
      setLoading(true)
      const result = await apiService.getArbitrageOpportunities({
        ...filters,
        limit: 100,
      })
      setOpportunities(result.data || [])
    } catch (error) {
      console.error('Failed to fetch opportunities:', error)
    } finally {
      setLoading(false)
    }
  }

  const columns: ColumnsType<ArbitrageOpportunity> = [
    {
      title: 'Time',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (time: string) => dayjs(time).format('HH:mm:ss'),
      width: 100,
    },
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
      title: 'Buy Price',
      dataIndex: 'buy_price',
      key: 'buy_price',
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: 'Sell To',
      dataIndex: 'sell_exchange',
      key: 'sell_exchange',
      render: (text: string) => <Tag color="red">{text.toUpperCase()}</Tag>,
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
        <Tag color={pct > 2 ? 'red' : pct > 1 ? 'orange' : 'green'}>
          {pct.toFixed(2)}%
        </Tag>
      ),
      sorter: (a, b) => a.spread_pct - b.spread_pct,
    },
    {
      title: 'Est. Profit %',
      dataIndex: 'estimated_profit',
      key: 'estimated_profit',
      render: (profit: number) => (
        <Tag color={profit > 1 ? 'success' : 'warning'}>
          <ThunderboltOutlined /> {profit.toFixed(2)}%
        </Tag>
      ),
      sorter: (a, b) => a.estimated_profit - b.estimated_profit,
      defaultSortOrder: 'descend',
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence_score',
      key: 'confidence_score',
      render: (score: number) => (
        <span>{(score * 100).toFixed(0)}%</span>
      ),
    },
    {
      title: 'Volume',
      dataIndex: 'volume_available',
      key: 'volume_available',
      render: (volume: number | undefined) =>
        volume ? volume.toFixed(4) : '-',
    },
  ]

  return (
    <div>
      <Title level={2}>Arbitrage Opportunities</Title>

      <Card style={{ marginBottom: 24 }}>
        <Space wrap>
          <Select
            style={{ width: 200 }}
            placeholder="Select Symbol"
            allowClear
            value={filters.symbol}
            onChange={(value) => setFilters({ ...filters, symbol: value })}
          >
            {symbols.map((symbol) => (
              <Select.Option key={symbol} value={symbol}>
                {symbol}
              </Select.Option>
            ))}
          </Select>

          <Space>
            <span>Min Spread %:</span>
            <InputNumber
              style={{ width: 120 }}
              min={0}
              max={10}
              step={0.1}
              value={filters.min_spread_pct}
              onChange={(value) => setFilters({ ...filters, min_spread_pct: value || 0.5 })}
            />
          </Space>

          <Button icon={<ReloadOutlined />} onClick={fetchOpportunities}>
            Refresh
          </Button>
        </Space>
      </Card>

      <Card title={`${opportunities.length} Opportunities Found`}>
        <Table
          columns={columns}
          dataSource={opportunities}
          rowKey={(record) => `${record.symbol}-${record.buy_exchange}-${record.sell_exchange}-${record.timestamp}`}
          loading={loading}
          pagination={{ pageSize: 20 }}
        />
      </Card>
    </div>
  )
}
