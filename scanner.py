import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Tuple

class VolatilityScanner:
    def __init__(self, connector, min_volatility: float = 5.0, window_size: int = 60):
        """
        Scanner to detect volatile pairs
        
        Args:
            connector: ExchangeConnector instance
            min_volatility: Minimum volatility percentage to trigger detection
            window_size: Lookback period in minutes for volatility calculation
        """
        self.logger = logging.getLogger(__name__)
        self.connector = connector
        self.min_volatility = min_volatility
        self.window_size = window_size
        
    def calculate_volatility(self, symbol: str) -> float:
        """Calculate volatility percentage for a symbol"""
        try:
            # Get OHLCV data
            ohlcv = self.connector.get_ohlcv(symbol, '1m', limit=self.window_size)
            if not ohlcv:
                return 0.0
                
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Calculate volatility (high-low range as percentage of price)
            df['volatility'] = ((df['high'] - df['low']) / df['low']) * 100
            
            # Return average volatility
            return df['volatility'].mean()
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility for {symbol}: {str(e)}")
            return 0.0
            
    def scan_market(self, symbols: List[str] = None) -> List[Dict]:
        """
        Scan market for volatile pairs
        
        Args:
            symbols: List of symbols to scan, if None scans all available
            
        Returns:
            List of dictionaries with volatile symbols and their data
        """
        volatile_pairs = []
        
        try:
            # If no symbols provided, get all
            if symbols is None or len(symbols) == 0:
                markets = self.connector.get_markets()
                symbols = list(markets.keys())
                
            # Calculate volatility for each symbol
            for symbol in symbols:
                volatility = self.calculate_volatility(symbol)
                
                if volatility >= self.min_volatility:
                    ticker = self.connector.get_ticker(symbol)
                    
                    volatile_pairs.append({
                        'symbol': symbol,
                        'volatility': volatility,
                        'last_price': ticker.get('last', 0),
                        'volume': ticker.get('quoteVolume', 0),
                        'timestamp': ticker.get('timestamp', 0)
                    })
                    
                    self.logger.info(f"Detected volatile pair: {symbol} with {volatility:.2f}% volatility")
            
            # Sort by volatility (highest first)
            return sorted(volatile_pairs, key=lambda x: x['volatility'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error scanning market: {str(e)}")
            return []