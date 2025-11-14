-- Use trading database
USE trading;

-- Materialized view: latest_prices
-- Quick access to the latest price for each symbol and exchange
CREATE MATERIALIZED VIEW IF NOT EXISTS latest_prices_mv
ENGINE = ReplacingMergeTree()
ORDER BY (symbol, exchange)
AS SELECT
    symbol,
    exchange,
    exchange_type,
    argMax(price, timestamp) as latest_price,
    argMax(bid, timestamp) as latest_bid,
    argMax(ask, timestamp) as latest_ask,
    argMax(volume_24h, timestamp) as latest_volume_24h,
    max(timestamp) as latest_timestamp
FROM prices
GROUP BY symbol, exchange, exchange_type;

-- View: hourly_price_aggregates
-- Aggregated price data by hour for better query performance
CREATE VIEW IF NOT EXISTS hourly_price_aggregates AS
SELECT
    toStartOfHour(timestamp) as hour,
    exchange,
    exchange_type,
    symbol,
    avg(price) as avg_price,
    min(price) as min_price,
    max(price) as max_price,
    argMin(price, timestamp) as open_price,
    argMax(price, timestamp) as close_price,
    sum(volume_24h) as total_volume
FROM prices
GROUP BY hour, exchange, exchange_type, symbol;

-- View: daily_spread_stats
-- Daily statistics for spreads
CREATE VIEW IF NOT EXISTS daily_spread_stats AS
SELECT
    toDate(timestamp) as date,
    symbol,
    spread_type,
    avg(spread_pct) as avg_spread_pct,
    min(spread_pct) as min_spread_pct,
    max(spread_pct) as max_spread_pct,
    stddevPop(spread_pct) as stddev_spread_pct,
    count() as count
FROM spreads
GROUP BY date, symbol, spread_type;

-- View: top_arbitrage_opportunities
-- Most profitable arbitrage opportunities in the last hour
CREATE VIEW IF NOT EXISTS top_arbitrage_opportunities AS
SELECT
    timestamp,
    symbol,
    buy_exchange,
    sell_exchange,
    buy_price,
    sell_price,
    spread_pct,
    estimated_profit,
    volume_available,
    confidence_score
FROM arbitrage_opportunities
WHERE timestamp >= now() - INTERVAL 1 HOUR
ORDER BY estimated_profit DESC
LIMIT 100;
