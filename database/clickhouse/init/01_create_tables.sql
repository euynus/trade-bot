-- Create database
CREATE DATABASE IF NOT EXISTS trading;

-- Use trading database
USE trading;

-- Table: prices
-- Stores real-time price data from all exchanges
CREATE TABLE IF NOT EXISTS prices (
    timestamp DateTime64(3) CODEC(Delta, ZSTD),
    exchange LowCardinality(String),
    exchange_type Enum8('CEX' = 1, 'DEX' = 2),
    symbol LowCardinality(String),
    base_currency LowCardinality(String),
    quote_currency LowCardinality(String),
    price Decimal(18, 8) CODEC(ZSTD),
    bid Nullable(Decimal(18, 8)) CODEC(ZSTD),
    ask Nullable(Decimal(18, 8)) CODEC(ZSTD),
    volume_24h Nullable(Decimal(18, 8)) CODEC(ZSTD),
    INDEX idx_timestamp timestamp TYPE minmax GRANULARITY 3,
    INDEX idx_symbol symbol TYPE bloom_filter GRANULARITY 1,
    INDEX idx_exchange exchange TYPE bloom_filter GRANULARITY 1
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (symbol, exchange, timestamp)
TTL timestamp + INTERVAL 90 DAY
SETTINGS index_granularity = 8192;

-- Table: spreads
-- Stores calculated price spreads between exchanges
CREATE TABLE IF NOT EXISTS spreads (
    timestamp DateTime64(3) CODEC(Delta, ZSTD),
    symbol LowCardinality(String),
    exchange_a LowCardinality(String),
    exchange_b LowCardinality(String),
    price_a Decimal(18, 8) CODEC(ZSTD),
    price_b Decimal(18, 8) CODEC(ZSTD),
    spread_abs Decimal(18, 8) CODEC(ZSTD),
    spread_pct Decimal(10, 6) CODEC(ZSTD),
    spread_type Enum8('CEX-CEX' = 1, 'CEX-DEX' = 2, 'DEX-DEX' = 3),
    INDEX idx_timestamp timestamp TYPE minmax GRANULARITY 3,
    INDEX idx_symbol symbol TYPE bloom_filter GRANULARITY 1,
    INDEX idx_spread_pct spread_pct TYPE minmax GRANULARITY 3
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (symbol, timestamp)
TTL timestamp + INTERVAL 90 DAY
SETTINGS index_granularity = 8192;

-- Table: funding_rates
-- Stores funding rate data for perpetual contracts
CREATE TABLE IF NOT EXISTS funding_rates (
    timestamp DateTime64(3) CODEC(Delta, ZSTD),
    exchange LowCardinality(String),
    symbol LowCardinality(String),
    funding_rate Decimal(10, 8) CODEC(ZSTD),
    predicted_rate Nullable(Decimal(10, 8)) CODEC(ZSTD),
    next_funding_time Nullable(DateTime) CODEC(ZSTD),
    mark_price Nullable(Decimal(18, 8)) CODEC(ZSTD),
    index_price Nullable(Decimal(18, 8)) CODEC(ZSTD),
    INDEX idx_timestamp timestamp TYPE minmax GRANULARITY 3,
    INDEX idx_symbol symbol TYPE bloom_filter GRANULARITY 1,
    INDEX idx_exchange exchange TYPE bloom_filter GRANULARITY 1
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (exchange, symbol, timestamp)
TTL timestamp + INTERVAL 90 DAY
SETTINGS index_granularity = 8192;

-- Table: arbitrage_opportunities
-- Stores detected arbitrage opportunities
CREATE TABLE IF NOT EXISTS arbitrage_opportunities (
    timestamp DateTime64(3) CODEC(Delta, ZSTD),
    symbol LowCardinality(String),
    buy_exchange LowCardinality(String),
    sell_exchange LowCardinality(String),
    buy_price Decimal(18, 8) CODEC(ZSTD),
    sell_price Decimal(18, 8) CODEC(ZSTD),
    spread_pct Decimal(10, 6) CODEC(ZSTD),
    estimated_profit Decimal(10, 6) CODEC(ZSTD),
    volume_available Nullable(Decimal(18, 8)) CODEC(ZSTD),
    confidence_score Float32 CODEC(ZSTD),
    INDEX idx_timestamp timestamp TYPE minmax GRANULARITY 3,
    INDEX idx_symbol symbol TYPE bloom_filter GRANULARITY 1,
    INDEX idx_spread_pct spread_pct TYPE minmax GRANULARITY 3
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, spread_pct DESC)
TTL timestamp + INTERVAL 30 DAY
SETTINGS index_granularity = 8192;
