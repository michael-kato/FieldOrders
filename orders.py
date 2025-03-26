import logging
from typing import Dict, List, Optional, Tuple
import time
import uuid

class OrderManager:
    def __init__(self, connector, discount_percentage: float = 15.0, 
                 profit_tiers: List[float] = [5.0, 10.0, 15.0],
                 tier_percentages: List[float] = [0.5, 0.3, 0.2]):
        """
        Manages order fields for trading - orchestrates buy fields and sell fields
        
        Args:
            connector: ExchangeConnector instance
            discount_percentage: Target discount for buy field orders (%)
            profit_tiers: List of profit percentages for sell field orders
            tier_percentages: Percentage of position to sell at each tier
        """
        self.logger = logging.getLogger(__name__)
        self.connector = connector
        self.discount_percentage = discount_percentage
        self.profit_tiers = profit_tiers
        self.tier_percentages = tier_percentages
        self.active_orders = {}
        
        # Track buy and sell fields
        self.buy_field_orders = {}
        self.sell_field_orders = {}
        
    def place_buy_field(self, symbol: str, base_price: float, 
                       position_size: float) -> Dict:
        """
        Place a buy field order at discounted price
        
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
            
            self.logger.info(f"Deploying buy field for {symbol} at {buy_price} " 
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
                    'timestamp': time.time(),
                    'field_type': 'buy'
                }
                
                # Add to buy field tracking
                self.buy_field_orders[order['id']] = self.active_orders[order['id']]
                
                return order
            else:
                self.logger.error(f"Failed to deploy buy field for {symbol}")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error deploying buy field for {symbol}: {str(e)}")
            return {}
            
    def deploy_sell_field(self, buy_order_id: str) -> List[Dict]:
        """
        Deploy a sell field once a buy order is filled
        
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
                self.logger.info(f"Buy field {buy_order_id} not yet triggered")
                return []
                
            sell_orders = []
            
            # Deploy tiered sell field orders
            for i, (profit, percentage) in enumerate(zip(self.profit_tiers, self.tier_percentages)):
                # Calculate sell price and amount
                sell_price = buy_price * (1 + (profit / 100))
                sell_amount = total_amount * percentage
                
                self.logger.info(f"Deploying sell field tier {i+1} for {symbol} at {sell_price} "
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
                        'timestamp': time.time(),
                        'field_type': 'sell'
                    }
                    
                    # Add to sell field tracking
                    self.sell_field_orders[sell_order['id']] = self.active_orders[sell_order['id']]
                    
                    sell_orders.append(sell_order)
                else:
                    self.logger.error(f"Failed to deploy sell field for {symbol}")
            
            return sell_orders
            
        except Exception as e:
            self.logger.error(f"Error deploying sell field: {str(e)}")
            return []
            
    def check_field_status(self, order_id: str) -> Dict:
        """
        Check status of a field order
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Updated order status
        """
        try:
            if order_id not in self.active_orders:
                self.logger.error(f"Order {order_id} not found in field")
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
            self.logger.error(f"Error checking field status: {str(e)}")
            return {}
            
    def get_buy_field_orders(self) -> Dict:
        """Get all active buy field orders"""
        return self.buy_field_orders
        
    def get_sell_field_orders(self) -> Dict:
        """Get all active sell field orders"""
        return self.sell_field_orders
        
    def retract_field(self, order_id: str) -> Dict:
        """
        Retract (cancel) an order from the field
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            Cancellation result
        """
        try:
            if order_id not in self.active_orders:
                self.logger.error(f"Order {order_id} not found in field")
                return {}
                
            order = self.active_orders[order_id]
            symbol = order['symbol']
            
            # Cancel order
            result = self.connector.cancel_order(order_id, symbol)
            
            # Update status if successful
            if result:
                self.active_orders[order_id]['status'] = 'canceled'
                
                # Remove from appropriate field tracking
                field_type = order.get('field_type')
                if field_type == 'buy':
                    if order_id in self.buy_field_orders:
                        del self.buy_field_orders[order_id]
                elif field_type == 'sell':
                    if order_id in self.sell_field_orders:
                        del self.sell_field_orders[order_id]
                        
            return result
            
        except Exception as e:
            self.logger.error(f"Error retracting field order: {str(e)}")
            return {}