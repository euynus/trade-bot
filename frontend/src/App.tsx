import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import AppHeader from './components/Layout/Header'
import AppSidebar from './components/Layout/Sidebar'
import Dashboard from './pages/Dashboard'
import SpreadMonitor from './pages/SpreadMonitor'
import FundingRates from './pages/FundingRates'
import ArbitrageOpportunities from './pages/ArbitrageOpportunities'
import HistoricalData from './pages/HistoricalData'
import './App.css'

const { Content } = Layout

function App() {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <AppSidebar />
      <Layout>
        <AppHeader />
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/spreads" element={<SpreadMonitor />} />
            <Route path="/funding-rates" element={<FundingRates />} />
            <Route path="/arbitrage" element={<ArbitrageOpportunities />} />
            <Route path="/historical" element={<HistoricalData />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

export default App
