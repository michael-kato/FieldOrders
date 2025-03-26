import ccxt
import logging
from typing import Dict, List, Any, Optional

class ExchangeConnector:
    def __init__(self, exchange_id: str, api_key: str = "", api_secret: str = "", sandbox: bool = True):
        """
        Initialize connection to a cryptocurrency exchange
        
        Args:
            exchange_id: Name of the exchange (e.g., 'binance')
            api_key: API key for authentication
            api_secret: API secret for authentication
            sandbox: Whether to use sandbox/testnet mode
        """
        self.logger = logging.getLogger(__name__)
        self.exchange_id = exchange_id
        self.sandbox = sandbox
        
        # Initialize exchange
        try:
            exchange_class = getattr(ccxt, exchange_id)
            self.exchange = exchange_class({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
            })
            
            if sandbox:
                self.exchange.set_sandbox_mode(True)
                self.logger.info(f"Connected to {exchange_id} in SANDBOX mode")
            else:
                self.logger.info(f"Connected to {exchange_id} in PRODUCTION mode")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize {exchange_id}: {str(e)}")
            raise
            
    def get_markets(self) -> Dict:
        """Get all available markets"""
        try:
            return self.exchange.load_markets()
        except Exception as e:
            self.logger.error(f"Failed to load markets: {str(e)}")
            return {}
            
    def get_ticker(self, symbol: str) -> Dict:
        """Get current ticker data for a symbol"""
        try:
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            self.logger.error(f"Failed to fetch ticker for {symbol}: {str(e)}")
            return {}
            
    def get_ohlcv(self, symbol: str, timeframe: str = '1m', limit: int = 100) -> List:
        """Get OHLCV candle data"""
        try:
            return self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        except Exception as e:
            self.logger.error(f"Failed to fetch OHLCV for {symbol}: {str(e)}")
            return []
            
    def place_limit_buy(self, symbol: str, amount: float, price: float) -> Dict:
        """Place a limit buy order"""
        try:
            return self.exchange.create_limit_buy_order(symbol, amount, price)
        except Exception as e:
            self.logger.error(f"Failed to place buy order for {symbol}: {str(e)}")
            return {}
            
    def place_limit_sell(self, symbol: str, amount: float, price: float) -> Dict:
        """Place a limit sell order"""
        try:
            return self.exchange.create_limit_sell_order(symbol, amount, price)
        except Exception as e:
            self.logger.error(f"Failed to place sell order for {symbol}: {str(e)}")
            return {}
            
    def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """Get status of an order"""
        try:
            return self.exchange.fetch_order(order_id, symbol)
        except Exception as e:
            self.logger.error(f"Failed to get order status for {order_id}: {str(e)}")
            return {}
            
    def cancel_order(self, order_id: str, symbol: str) -> Dict:
        """Cancel an order"""
        try:
            return self.exchange.cancel_order(order_id, symbol)
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {str(e)}")
            return {}
            
    def get_balance(self) -> Dict:
        """Get account balances"""
        try:
            return self.exchange.fetch_balance()
        except Exception as e:
            self.logger.error(f"Failed to fetch balance: {str(e)}")
            return {}