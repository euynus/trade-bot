import { useState, useEffect } from 'react'
import { Card, Table, Select, DatePicker, Button, Space, Tag, Typography } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { apiService, SpreadData } from '../services/api'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'

const { Title } = Typography
const { RangePicker } = DatePicker

export default function SpreadMonitor() {
  const [spreads, setSpreads] = useState<SpreadData[]>([])
  const [symbols, setSymbols] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    symbol: undefined as string | undefined,
    spread_type: undefined as string | undefined,
  })

  useEffect(() => {
    fetchSymbols()
    fetchSpreads()
  }, [])

  useEffect(() => {
    fetchSpreads()
  }, [filters])

  const fetchSymbols = async () => {
    try {
      const result = await apiService.getSymbols()
      setSymbols(result.data || [])
    } catch (error) {
      console.error('Failed to fetch symbols:', error)
    }
  }

  const fetchSpreads = async () => {
    try {
      setLoading(true)
      const result = await apiService.getSpreads({
        ...filters,
        limit: 1000,
      })
      setSpreads(result.data || [])
    } catch (error) {
      console.error('Failed to fetch spreads:', error)
    } finally {
      setLoading(false)
    }
  }

  const columns: ColumnsType<SpreadData> = [
    {
      title: 'Time',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
      width: 180,
    },
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (text: string) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: 'Exchange A',
      dataIndex: 'exchange_a',
      key: 'exchange_a',
      render: (text: string) => text.toUpperCase(),
    },
    {
      title: 'Price A',
      dataIndex: 'price_a',
      key: 'price_a',
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: 'Exchange B',
      dataIndex: 'exchange_b',
      key: 'exchange_b',
      render: (text: string) => text.toUpperCase(),
    },
    {
      title: 'Price B',
      dataIndex: 'price_b',
      key: 'price_b',
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: 'Spread %',
      dataIndex: 'spread_pct',
      key: 'spread_pct',
      render: (pct: number) => (
        <Tag color={Math.abs(pct) > 1 ? 'red' : Math.abs(pct) > 0.5 ? 'orange' : 'green'}>
          {pct.toFixed(2)}%
        </Tag>
      ),
      sorter: (a, b) => Math.abs(a.spread_pct) - Math.abs(b.spread_pct),
    },
    {
      title: 'Type',
      dataIndex: 'spread_type',
      key: 'spread_type',
      render: (type: string) => <Tag>{type}</Tag>,
    },
  ]

  return (
    <div>
      <Title level={2}>Price Spread Monitor</Title>

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

          <Select
            style={{ width: 200 }}
            placeholder="Spread Type"
            allowClear
            value={filters.spread_type}
            onChange={(value) => setFilters({ ...filters, spread_type: value })}
          >
            <Select.Option value="CEX-CEX">CEX-CEX</Select.Option>
            <Select.Option value="CEX-DEX">CEX-DEX</Select.Option>
            <Select.Option value="DEX-DEX">DEX-DEX</Select.Option>
          </Select>

          <Button icon={<ReloadOutlined />} onClick={fetchSpreads}>
            Refresh
          </Button>
        </Space>
      </Card>

      <Card>
        <Table
          columns={columns}
          dataSource={spreads}
          rowKey={(record) => `${record.timestamp}-${record.exchange_a}-${record.exchange_b}-${record.symbol}`}
          loading={loading}
          pagination={{ pageSize: 20 }}
        />
      </Card>
    </div>
  )
}
