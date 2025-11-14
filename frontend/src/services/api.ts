import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export interface PriceData {
  timestamp: string
  exchange: string
  symbol: string
  price: number
  bid?: number
  ask?: number
  volume_24h?: number
}

export interface SpreadData {
  timestamp: string
  symbol: string
  exchange_a: string
  exchange_b: string
  price_a: number
  price_b: number
  spread_abs: number
  spread_pct: number
  spread_type: string
}

export interface FundingRateData {
  timestamp: string
  exchange: string
  symbol: string
  funding_rate: number
  predicted_rate?: number
  next_funding_time?: string
  mark_price?: number
  index_price?: number
}

export interface ArbitrageOpportunity {
  timestamp: string
  symbol: string
  buy_exchange: string
  sell_exchange: string
  buy_price: number
  sell_price: number
  spread_pct: number
  estimated_profit: number
  volume_available?: number
  confidence_score: number
}

// API methods
export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Prices
  getLatestPrices: (symbol?: string) =>
    api.get<any, { data: PriceData[] }>('/prices/latest', {
      params: { symbol },
    }),

  getPrices: (params?: {
    symbol?: string
    exchange?: string
    start_time?: string
    end_time?: string
    limit?: number
  }) => api.get<any, { data: PriceData[] }>('/prices', { params }),

  // Spreads
  getSpreads: (params?: {
    symbol?: string
    spread_type?: string
    start_time?: string
    end_time?: string
    min_spread_pct?: number
    limit?: number
  }) => api.get<any, { data: SpreadData[] }>('/spreads', { params }),

  // Funding rates
  getFundingRates: (params?: {
    symbol?: string
    exchange?: string
    start_time?: string
    end_time?: string
    limit?: number
  }) => api.get<any, { data: FundingRateData[] }>('/funding-rates', { params }),

  // Arbitrage
  getArbitrageOpportunities: (params?: {
    symbol?: string
    min_spread_pct?: number
    limit?: number
  }) => api.get<any, { data: ArbitrageOpportunity[] }>('/arbitrage-opportunities', { params }),

  // Statistics
  getStatistics: (symbol: string, hours: number = 24) =>
    api.get(`/statistics/summary`, {
      params: { symbol, hours },
    }),

  // Metadata
  getExchanges: () => api.get<any, { data: { exchange: string; type: string }[] }>('/exchanges'),
  getSymbols: () => api.get<any, { data: string[] }>('/symbols'),
}

export default api
