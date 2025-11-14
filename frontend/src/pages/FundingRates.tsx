import { useState, useEffect } from 'react'
import { Card, Table, Select, Button, Space, Tag, Typography } from 'antd'
import { ReloadOutlined } from '@ant-design/icons'
import { apiService, FundingRateData } from '../services/api'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'

const { Title } = Typography

export default function FundingRates() {
  const [fundingRates, setFundingRates] = useState<FundingRateData[]>([])
  const [symbols, setSymbols] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedSymbol, setSelectedSymbol] = useState<string | undefined>()

  useEffect(() => {
    fetchSymbols()
    fetchFundingRates()
  }, [])

  useEffect(() => {
    fetchFundingRates()
  }, [selectedSymbol])

  const fetchSymbols = async () => {
    try {
      const result = await apiService.getSymbols()
      setSymbols(result.data || [])
    } catch (error) {
      console.error('Failed to fetch symbols:', error)
    }
  }

  const fetchFundingRates = async () => {
    try {
      setLoading(true)
      const result = await apiService.getFundingRates({
        symbol: selectedSymbol,
        limit: 1000,
      })
      setFundingRates(result.data || [])
    } catch (error) {
      console.error('Failed to fetch funding rates:', error)
    } finally {
      setLoading(false)
    }
  }

  const columns: ColumnsType<FundingRateData> = [
    {
      title: 'Time',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
      width: 180,
    },
    {
      title: 'Exchange',
      dataIndex: 'exchange',
      key: 'exchange',
      render: (text: string) => <Tag color="blue">{text.toUpperCase()}</Tag>,
    },
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: 'Funding Rate',
      dataIndex: 'funding_rate',
      key: 'funding_rate',
      render: (rate: number) => (
        <Tag color={rate > 0.01 ? 'red' : rate < -0.01 ? 'green' : 'default'}>
          {(rate * 100).toFixed(4)}%
        </Tag>
      ),
      sorter: (a, b) => a.funding_rate - b.funding_rate,
    },
    {
      title: 'Predicted Rate',
      dataIndex: 'predicted_rate',
      key: 'predicted_rate',
      render: (rate: number | undefined) =>
        rate !== undefined ? `${(rate * 100).toFixed(4)}%` : '-',
    },
    {
      title: 'Next Funding Time',
      dataIndex: 'next_funding_time',
      key: 'next_funding_time',
      render: (time: string | undefined) =>
        time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-',
    },
    {
      title: 'Mark Price',
      dataIndex: 'mark_price',
      key: 'mark_price',
      render: (price: number | undefined) =>
        price ? `$${price.toFixed(2)}` : '-',
    },
  ]

  return (
    <div>
      <Title level={2}>Funding Rates</Title>

      <Card style={{ marginBottom: 24 }}>
        <Space>
          <Select
            style={{ width: 200 }}
            placeholder="Select Symbol"
            allowClear
            value={selectedSymbol}
            onChange={setSelectedSymbol}
          >
            {symbols.map((symbol) => (
              <Select.Option key={symbol} value={symbol}>
                {symbol}
              </Select.Option>
            ))}
          </Select>

          <Button icon={<ReloadOutlined />} onClick={fetchFundingRates}>
            Refresh
          </Button>
        </Space>
      </Card>

      <Card>
        <Table
          columns={columns}
          dataSource={fundingRates}
          rowKey={(record) => `${record.timestamp}-${record.exchange}-${record.symbol}`}
          loading={loading}
          pagination={{ pageSize: 20 }}
        />
      </Card>
    </div>
  )
}
