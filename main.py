import sys
import time
import logging
import argparse
import threading
from PyQt5.QtWidgets import QApplication

from settings import EXCHANGES, SCANNER_SETTINGS, ORDER_SETTINGS, GUI_SETTINGS
from exchange import ExchangeConnector
from scanner import VolatilityScanner
from orders import OrderManager
from logger import setup_logger
from storage import Storage
from alerts import AlertManager, AlertEvent
from ui import SimplifiedDashboard

def parse_args():
    parser = argparse.ArgumentParser(description='OrderTools Trading Bot')
    parser.add_argument('--exchange', type=str, default='mexc', help='Exchange to use')
    parser.add_argument('--sandbox', action='store_true', help='Use sandbox mode')
    parser.add_argument('--headless', action='store_true', help='Run without GUI')
    parser.add_argument('--simulate', action='store_true', help='Run in simulation mode')
    parser.add_argument('--db-path', type=str, default='data/ordertools.db', help='Database path')
    return parser.parse_args()

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Setup logger
    logger = setup_logger()
    logger.info("Starting OrderTools Trading Bot")
    
    try:
        # Initialize storage
        storage = Storage(args.db_path)
        logger.info(f"Storage initialized with database at {args.db_path}")
        
        # Initialize alert manager
        alert_manager = AlertManager()
        logger.info("Alert manager initialized")
        
        # Initialize exchange connector
        exchange_settings = EXCHANGES.get(args.exchange, {})
        
        if args.simulate:
            # Use simulation mode
            from simulation import Simulator
            simulator = Simulator()
            connector = simulator  # We'll need to adapt the simulator to match connector interface
            logger.info("Running in simulation mode")
        else:
            # Use real exchange
            connector = ExchangeConnector(
                args.exchange,
                api_key=exchange_settings.get('api_key', ''),
                api_secret=exchange_settings.get('api_secret', ''),
                sandbox=args.sandbox if args.sandbox else exchange_settings.get('sandbox', True)
            )
        
        # Initialize scanner and order manager
        scanner = VolatilityScanner(
            connector,
            min_volatility=SCANNER_SETTINGS.get('min_volatility', 5.0),
            window_size=SCANNER_SETTINGS.get('window_size', 60)
        )
        
        order_manager = OrderManager(
            connector,
            discount_percentage=ORDER_SETTINGS.get('discount_percentage', 15.0),
            profit_tiers=ORDER_SETTINGS.get('profit_tiers', [5.0, 10.0, 15.0]),
            tier_percentages=ORDER_SETTINGS.get('tier_percentages', [0.5, 0.3, 0.2])
        )
        
        # Override methods to add storage and alerts
        original_place_buy_field = order_manager.place_buy_field
        original_deploy_sell_field = order_manager.deploy_sell_field
        
        def place_buy_field_extended(symbol, base_price, position_size):
            order = original_place_buy_field(symbol, base_price, position_size)
            
            if order and 'id' in order:
                # Save to storage
                storage.save_order(order['id'], order_manager.active_orders[order['id']])
                
                # Trigger alert
                alert_manager.trigger_alert(AlertEvent.ORDER_PLACED, {
                    'order_id': order['id'],
                    'symbol': symbol,
                    'price': base_price * (1 - (order_manager.discount_percentage / 100)),
                    'amount': position_size / (base_price * (1 - (order_manager.discount_percentage / 100))),
                    'field_type': 'buy'
                })
            
            return order
        
        def deploy_sell_field_extended(buy_order_id):
            sell_orders = original_deploy_sell_field(buy_order_id)
            
            for order in sell_orders:
                if 'id' in order:
                    # Save to storage
                    storage.save_order(order['id'], order_manager.active_orders[order['id']])
                    
                    # Trigger alert
                    alert_manager.trigger_alert(AlertEvent.SELL_ORDER_PLACED, {
                        'order_id': order['id'],
                        'symbol': order_manager.active_orders[order['id']]['symbol'],
                        'price': order_manager.active_orders[order['id']]['price'],
                        'amount': order_manager.active_orders[order['id']]['amount'],
                        'field_type': 'sell'
                    })
            
            return sell_orders
        
        # Replace methods
        order_manager.place_buy_field = place_buy_field_extended
        order_manager.deploy_sell_field = deploy_sell_field_extended
        
        # Add method to check for filled orders and trigger alerts
        def check_and_update_fields():
            """Check field status and trigger alerts for activated fields"""
            for order_id, order in list(order_manager.active_orders.items()):
                # Skip orders we know are already filled
                if order.get('status') == 'closed':
                    continue
                
                # Check current status
                status = order_manager.check_field_status(order_id)
                
                # If order is now filled
                if status and status.get('status') == 'closed':
                    # Update local status
                    order_manager.active_orders[order_id]['status'] = 'closed'
                    
                    # Save to storage
                    storage.save_order(order_id, order_manager.active_orders[order_id])
                    
                    # Record trade
                    trade_data = {
                        'order_id': order_id,
                        'symbol': order.get('symbol', ''),
                        'side': order.get('type', ''),
                        'amount': order.get('amount', 0),
                        'price': order.get('price', 0),
                        'timestamp': int(time.time() * 1000),
                        'field_type': order.get('field_type', '')
                    }
                    
                    storage.save_trade(trade_data)
                    
                    # Trigger alert
                    if order.get('type') == 'buy':
                        alert_manager.trigger_alert(AlertEvent.ORDER_FILLED, {
                            'order_id': order_id,
                            'symbol': order.get('symbol', ''),
                            'price': order.get('price', 0),
                            'amount': order.get('amount', 0),
                            'field_type': 'buy'
                        })
                        
                        # Setup sell field for filled buy orders
                        order_manager.deploy_sell_field(order_id)
                    else:
                        alert_manager.trigger_alert(AlertEvent.SELL_ORDER_FILLED, {
                            'order_id': order_id,
                            'symbol': order.get('symbol', ''),
                            'price': order.get('price', 0),
                            'amount': order.get('amount', 0),
                            'field_type': 'sell'
                        })
        
        # Add method to scanner to trigger volatility alerts
        original_scan_market = scanner.scan_market
        
        def scan_market_with_alerts(symbols=None):
            volatile_pairs = original_scan_market(symbols)
            
            # Trigger alerts for high volatility
            for pair in volatile_pairs:
                if pair['volatility'] >= SCANNER_SETTINGS.get('min_volatility', 5.0) * 2:  # 2x threshold
                    alert_manager.trigger_alert(AlertEvent.HIGH_VOLATILITY, {
                        'symbol': pair['symbol'],
                        'volatility': pair['volatility'],
                        'price': pair['last_price']
                    })
            
            return volatile_pairs
        
        scanner.scan_market = scan_market_with_alerts
        
        if args.headless:
            # CLI mode - run scanner loop
            logger.info("Running in CLI mode")
            
            while True:
                try:
                    # Scan for volatile pairs
                    volatile_pairs = scanner.scan_market(SCANNER_SETTINGS.get('symbols', []))
                    
                    if volatile_pairs:
                        logger.info(f"Found {len(volatile_pairs)} volatile pairs")
                        
                        # Process top pair
                        pair = volatile_pairs[0]
                        symbol = pair['symbol']
                        current_price = pair['last_price']
                        
                        # Deploy buy field
                        position_size = min(
                            ORDER_SETTINGS.get('max_position_size', 100.0),
                            pair['volume'] * 0.01  # 1% of volume for demonstration
                        )
                        
                        buy_order = order_manager.place_buy_field(
                            symbol, current_price, position_size
                        )
                        
                        if buy_order:
                            logger.info(f"Deployed buy field: {buy_order}")
                    
                    # Check for activated fields
                    check_and_update_fields()
                    
                    # Sleep before next scan
                    time.sleep(SCANNER_SETTINGS.get('scan_interval', 300))
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Error in scanner loop: {str(e)}")
                    alert_manager.trigger_alert(AlertEvent.ERROR, {
                        'message': str(e)
                    })
                    time.sleep(10)  # Short delay before retry
        
        else:
            # GUI mode - initialize and run GUI
            logger.info("Running in GUI mode")
            app = QApplication(sys.argv)
            
            # Create dashboard
            settings = {
                'scanner': SCANNER_SETTINGS,
                'order': ORDER_SETTINGS,
                'gui': GUI_SETTINGS,
                'exchange': exchange_settings
            }
            
            dashboard = SimplifiedDashboard(scanner, order_manager, settings, storage, alert_manager)
            dashboard.show()
            
            # Start background thread for checking filled orders
            def check_fields_background():
                while True:
                    try:
                        # Only check when scanner is running
                        if dashboard.is_running:
                            check_and_update_fields()
                        time.sleep(5)  # Check every 5 seconds
                    except Exception as e:
                        logger.error(f"Error checking fields: {str(e)}")
            
            order_thread = threading.Thread(target=check_fields_background, daemon=True)
            order_thread.start()
            
            sys.exit(app.exec_())
    
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        
        # Try to send alert if possible
        try:
            if 'alert_manager' in locals():
                alert_manager.trigger_alert(AlertEvent.ERROR, {
                    'message': f"Fatal error: {str(e)}"
                })
        except:
            pass
    
    logger.info("OrderTools Trading Bot stopped")

if __name__ == "__main__":
    main()