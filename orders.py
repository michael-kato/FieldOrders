import logging
from typing import Dict, List, Optional, Tuple
import time

class OrderManager:
    def __init__(self, connector, discount_percentage: float = 15.0, 
                 profit_tiers: List[float] = [5.0, 10.0, 15.0],
                 tier_percentages: List[float] = [0.5, 0.3, 0.2]):
        """
        Manages order placement and tracking
        
        Args:
            connector: ExchangeConnector instance
            discount_percentage: Target discount for buy orders (%)
            profit_tiers: List of profit percentages for sell orders
            tier_percentages: Percentage of position to sell at each tier
        """
        self.logger = logging.getLogger(__name__)
        self.connector = connector
        self.discount_percentage = discount_percentage
        self.profit_tiers = profit_tiers
        self.tier_percentages = tier_percentages
        self.active_orders = {}
        
    def place_fat_finger_buy(self, symbol: str, base_price: float, 
                             position_size: float) -> Dict:
        """
        Place a "fat finger" buy order at discounted price
        
        Args:
            symbol: Trading pair symbol
            base_price: Current market price
            position_size: Amount to buy in quote currency
            
        Returns:
            Order details or empty dict on failure
        """
        try:
            # Calculate discounted price
            buy_price = base_price * (1 - (self.discount_percentage / 100))
            
            # Calculate amount to buy (units of base currency)
            amount = position_size / buy_price
            
            self.logger.info(f"Placing fat finger buy order for {symbol} at {buy_price} " 
                             f"({self.discount_percentage}% below market)")
            
            # Place buy order
            order = self.connector.place_limit_buy(symbol, amount, buy_price)
            
            if order and 'id' in order:
                # Store order details
                self.active_orders[order['id']] = {
                    'type': 'buy',
                    'symbol': symbol,
                    'amount': amount,
                    'price': buy_price,
                    'base_price': base_price,
                    'timestamp': time.time()
                }
                return order
            else:
                self.logger.error(f"Failed to place buy order for {symbol}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error placing buy order for {symbol}: {str(e)}")
            return {}
            
    def setup_tiered_sells(self, buy_order_id: str) -> List[Dict]:
        """
        Set up tiered sell orders once a buy order is filled
        
        Args:
            buy_order_id: ID of the filled buy order
            
        Returns:
            List of sell order details
        """
        try:
            # Check if buy order exists and is filled
            if buy_order_id not in self.active_orders:
                self.logger.error(f"Buy order {buy_order_id} not found")
                return []
                
            buy_order = self.active_orders[buy_order_id]
            symbol = buy_order['symbol']
            buy_price = buy_order['price']
            total_amount = buy_order['amount']
            
            # Get latest order status from exchange
            order_status = self.connector.get_order_status(buy_order_id, symbol)
            
            # If order is not filled, return empty list
            if order_status.get('status') != 'closed':
                self.logger.info(f"Buy order {buy_order_id} not yet filled")
                return []
                
            sell_orders = []
            
            # Place tiered sell orders
            for i, (profit, percentage) in enumerate(zip(self.profit_tiers, self.tier_percentages)):
                # Calculate sell price and amount
                sell_price = buy_price * (1 + (profit / 100))
                sell_amount = total_amount * percentage
                
                self.logger.info(f"Placing tier {i+1} sell order for {symbol} at {sell_price} "
                                 f"({profit}% profit, {percentage*100}% of position)")
                
                # Place sell order
                sell_order = self.connector.place_limit_sell(symbol, sell_amount, sell_price)
                
                if sell_order and 'id' in sell_order:
                    # Store order details
                    self.active_orders[sell_order['id']] = {
                        'type': 'sell',
                        'symbol': symbol,
                        'amount': sell_amount,
                        'price': sell_price,
                        'buy_price': buy_price,
                        'profit_percentage': profit,
                        'tier': i+1,
                        'related_buy': buy_order_id,
                        'timestamp': time.time()
                    }
                    
                    sell_orders.append(sell_order)
                else:
                    self.logger.error(f"Failed to place sell order for {symbol}")
            
            return sell_orders
            
        except Exception as e:
            self.logger.error(f"Error setting up sell orders: {str(e)}")
            return []
            
    def check_order_status(self, order_id: str) -> Dict:
        """
        Check status of an order
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Updated order status
        """
        try:
            if order_id not in self.active_orders:
                self.logger.error(f"Order {order_id} not found")
                return {}
                
            order = self.active_orders[order_id]
            symbol = order['symbol']
            
            # Get latest status from exchange
            status = self.connector.get_order_status(order_id, symbol)
            
            # Update local record
            if status:
                self.active_orders[order_id].update({
                    'status': status.get('status', 'unknown'),
                    'filled': status.get('filled', 0),
                    'last_update': time.time()
                })
                
            return status
            
        except Exception as e:
            self.logger.error(f"Error checking order status: {str(e)}")
            return {}