# FieldOrders trading tools

A crypto trading tool that autonomously identifies volatile pairs, places strategic buy orders at discount prices, and manages profitable exits through tiered sell orders.

## Features

- **Real-time Scanning**: Monitor exchanges for volatile cryptocurrency pairs
- **"Fat Finger" Buy Strategy**: Place discounted buy orders to capture sudden price drops
- **Automated Sell Orders**: Set up tiered sell orders for profit taking
- **User-friendly GUI**: Clean interface with charts, tables, and control panel
- **Comprehensive Alerts**: Get notifications for important events
- **Persistent Storage**: Track trades, orders, and performance metrics
- **Detailed Analytics**: View statistics and export data for analysis
- **Simulation Mode**: Test strategies without risking real capital

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/FieldOrders.git
   cd FieldOrders
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure your API keys:
   - Open `config/settings.py`
   - Add your exchange API keys in the `EXCHANGES` section

## Usage

### GUI Mode (Default)

Run the application with a graphical user interface:

```
python main.py
```

### Simulation Mode

Test strategies without using real exchange accounts:

```
python main.py --simulate
```

### CLI Mode

Run in command line mode without GUI:

```
python main.py --headless
```

### Use Specific Exchange

```
python main.py --exchange kraken
```

### Database Maintenance

Backup the database:

```
python main.py --backup
```

Clean old data:

```
python main.py --clean 30  # Remove data older than 30 days
```

Export trades to CSV:

```
python main.py --export trades_export.csv
```

## Project Structure

```
ordertools/
├── config/          # Configuration settings
├── core/            # Core trading logic
├── exchange/        # Exchange connectivity
├── gui/             # User interface components
├── utils/           # Utility functions & data storage
├── data/            # Database and exports
│   ├── backups/     # Database backups
│   └── export/      # Exported data files
├── logs/            # Application logs
├── main.py          # Application entry point
└── requirements.txt # Dependencies
```

## Dashboard Tabs

- **Volatility Scanner**: View volatile pairs in real-time
- **Active Orders**: Monitor current buy/sell orders
- **Trade History**: Review completed trades
- **Statistics**: Analyze performance metrics
- **Alerts**: Track important events
- **Controls**: Configure scanner and order parameters

## Trading Strategy

The bot implements a "fat finger" trading strategy:

1. **Scan**: Continuously scan for volatile cryptocurrency pairs
2. **Buy**: Place limit buy orders at heavily discounted prices (e.g., 15% below market)
3. **Sell**: When buy orders fill, automatically place tiered sell orders:
   - 50% of position at +5% profit
   - 30% of position at +10% profit
   - 20% of position at +15% profit

## Risk Management

- Set maximum position sizes in settings
- Configure maximum concurrent positions
- Implement daily loss limits

## Configuration

Edit `config/settings.py` to customize:

- Exchange settings (API keys, sandbox mode)
- Scanner parameters (volatility threshold, scan interval)
- Order parameters (discount percentage, profit tiers)
- Risk management settings (max positions, daily limits)
- GUI settings (update interval, chart options)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

Trading cryptocurrencies involves significant risk. This software is for educational and personal use only. Always use caution and never trade with funds you cannot afford to lose.
