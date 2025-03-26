# Exchange settings
EXCHANGES = {
    'binance': {
        'sandbox': True,
        'api_key': '',  # Fill in for live testing
        'api_secret': '',  # Fill in for live testing
    }
}

# Scanner settings
SCANNER_SETTINGS = {
    'min_volatility': 5.0,  # Minimum volatility percentage
    'window_size': 60,  # Lookback period in minutes
    'scan_interval': 300,  # Seconds between scans
    'symbols': [],  # Empty list means scan all available
}

# Order settings
ORDER_SETTINGS = {
    'discount_percentage': 15.0,  # Target discount for buy orders
    'profit_tiers': [5.0, 10.0, 15.0],  # Profit percentages for sell orders
    'tier_percentages': [0.5, 0.3, 0.2],  # Percentage of position to sell at each tier
    'max_position_size': 100.0,  # Maximum position size in USD
}

# Risk settings
RISK_SETTINGS = {
    'max_concurrent_positions': 5,  # Maximum number of concurrent positions
    'max_daily_trades': 20,  # Maximum number of trades per day
    'max_daily_loss': 100.0,  # Maximum daily loss in USD
}

# GUI settings
GUI_SETTINGS = {
    'update_interval': 1000,  # Milliseconds
    'chart_timeframe': '1m',
    'chart_candles': 100,
}