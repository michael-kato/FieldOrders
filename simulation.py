import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
import time
import random

class Simulator:
    def __init__(self, symbols: List[str] = None, initial_prices: Dict = None):
        """
        Simulation engine for testing without real exchange
        
        Args:
            symbols: List of symbols to simulate
            initial_prices: Dictionary of initial prices for symbols
        """
        self.logger = logging.getLogger(__name__)
        self.symbols = symbols or ["BTC/USDT", "ETH/USDT", "XRP/USDT", "LTC/USDT", "ADA/USDT"]
        self.prices = initial_prices or {}
        self.orders = {}
        self.next_order_id = 1000
        self.last_update = time.time()
        
        # Initialize prices if not provided
        if not self.prices:
            self._initialize_prices()
    
    def _initialize_prices(self):
        """Initialize random prices for symbols"""
        base_prices = {
            "BTC/USDT": 40000.0,
            "ETH/USDT": 2000.0,
            "XRP/USDT": 0.5,
            "LTC/USDT": 150.0,
            "ADA/USDT": 1.0
        }
        
        for symbol in self.symbols:
            if symbol in base_prices:
                self.prices[symbol] = base_prices[symbol]
            else:
                # Random price between 0.1 and 1000
                self.prices[symbol] = random.uniform(0.1, 1000.0)
    
    def update_prices(self, volatility: float = 5.0):
        """
        Update simulated prices
        
        Args:
            volatility: Volatility percentage
        """
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now
        
        # Update each price with random movement
        for symbol in self.symbols:
            if symbol in self.prices:
                # Calculate price change based on volatility
                change_percent = random.uniform(-volatility, volatility) * (elapsed / 60.0)
                
                # Apply change
                self.prices[symbol] *= (1 + (change_percent / 100.0))
                
                # Check for fat finger events
                if random.random() < 0.01:  # 1% chance
                    # Simulate fat finger with large price drop
                    drop_percent = random.uniform(10.0, 30.0)
                    self.prices[symbol] *= (1 - (drop_percent / 100.0))
                    self.logger.info(f"Simulated fat finger for {symbol}: {drop_percent:.2f}% drop")
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        Get simulated ticker
        
        Args:
            symbol: Symbol to get ticker for
            
        Returns:
            Simulated ticker data
        """
        if symbol not in self.prices:
            return {}
            
        price = self.prices[symbol]
        
        return {
            'symbol': symbol,
            'last': price,
            'bid': price * 0.999,
            'ask': price * 1.001,
            'high': price * 1.02,
            'low': price * 0.98,
            'volume': random.uniform(10000, 1000000),
            'quoteVolume': price * random.uniform(10, 1000),
            'timestamp': int(time.time() * 1000)
        }
    
    def get_markets(self) -> Dict:
        """Get all available markets"""
        markets = {}
        for symbol in self.symbols:
            markets[symbol] = {
                'symbol': symbol,
                'base': symbol.split('/')[0],
                'quote': symbol.split('/')[1],
                'active': True
            }
        return markets
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1m', limit: int = 100) -> List:
        """
        Get simulated OHLCV data
        
        Args:
            symbol: Symbol to get data for
            timeframe: Timeframe (not used in simulation)
            limit: Number of candles
            
        Returns:
            List of OHLCV candles
        """
        if symbol not in self.prices:
            return []
            
        # Get current price
        current_price = self.prices[symbol]
        
        # Generate random candles
        candles = []
        now = int(time.time() * 1000)
        
        for i in range(limit):
            # Calculate candle time
            candle_time = now - ((limit - i - 1) * 60 * 1000)  # 1m candles
            
            # Generate random price movement (more volatile for older candles)
            volatility = 5.0 * (1 + ((limit - i) / limit))
            open_price = current_price * (1 + random.uniform(-volatility, volatility) / 100)
            close_price = current_price * (1 + random.uniform(-volatility, volatility) / 100)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, volatility/2) / 100)
            low_price = min(open_price, close_price) * (1 - random.uniform(0, volatility/2) / 100)
            volume = random.uniform(1, 100) * current_price
            
            candles.append([candle_time, open_price, high_price, low_price, close_price, volume])
        
        return candles
    
    def place_limit_buy(self, symbol: str, amount: float, price: float) -> Dict:
        """Place simulated limit buy order"""
        return self.place_order(symbol, 'buy', amount, price)
    
    def place_limit_sell(self, symbol: str, amount: float, price: float) -> Dict:
        """Place simulated limit sell order"""
        return self.place_order(symbol, 'sell', amount, price)
    
    def place_order(self, symbol: str, side: str, amount: float, price: float) -> Dict:
        """
        Place simulated order
        
        Args:
            symbol: Symbol to trade
            side: 'buy' or 'sell'
            amount: Amount to trade
            price: Order price
            
        Returns:
            Simulated order details
        """
        # Generate order ID
        order_id = str(self.next_order_id)
        self.next_order_id += 1
        
        # Create order
        order = {
            'id': order_id,
            'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': price,
            'status': 'open',
            'filled': 0.0,
            'remaining': amount,
            'timestamp': int(time.time() * 1000)
        }
        
        # Store order
        self.orders[order_id] = order
        
        self.logger.info(f"Placed simulated {side} order for {symbol}: {amount} @ {price}")
        
        return order
    
    def update_orders(self):
        """Update status of open orders"""
        for order_id, order in list(self.orders.items()):
            if order['status'] != 'open':
                continue
                
            symbol = order['symbol']
            price = order['price']
            current_price = self.prices.get(symbol, 0)
            
            # Check if order should be filled
            if (order['side'] == 'buy' and current_price <= price) or \
               (order['side'] == 'sell' and current_price >= price):
                
                # Fill order
                self.orders[order_id]['status'] = 'closed'
                self.orders[order_id]['filled'] = order['amount']
                self.orders[order_id]['remaining'] = 0.0
                
                self.logger.info(f"Filled simulated {order['side']} order for {symbol}")
    
    def get_order_status(self, order_id: str, symbol: str = None) -> Dict:
        """
        Get order details
        
        Args:
            order_id: Order ID
            symbol: Symbol (not used in simulation)
            
        Returns:
            Order details
        """
        return self.orders.get(order_id, {})
    
    def cancel_order(self, order_id: str, symbol: str = None) -> Dict:
        """
        Cancel an order
        
        Args:
            order_id: Order ID
            symbol: Symbol (not used in simulation)
            
        Returns:
            Canceled order details
        """
        if order_id in self.orders and self.orders[order_id]['status'] == 'open':
            self.orders[order_id]['status'] = 'canceled'
            self.logger.info(f"Canceled order {order_id}")
            return self.orders[order_id]
        return {}