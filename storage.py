import sqlite3
import json
import os
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

class Storage:
    def __init__(self, db_path: str = "data/ordertools.db"):
        """
        Persistent storage for trade history and settings
        
        Args:
            db_path: Path to SQLite database file
        """
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create orders table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                status TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                metadata TEXT
            )
            ''')
            
            # Create trades table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL,
                timestamp INTEGER NOT NULL,
                profit REAL,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
            ''')
            
            # Create settings table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            ''')
            
            # Create volatility history table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS volatility_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                volatility REAL NOT NULL,
                price REAL NOT NULL,
                timestamp INTEGER NOT NULL
            )
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def save_order(self, order_id: str, order_data: Dict) -> bool:
        """
        Save order to database
        
        Args:
            order_id: Order ID
            order_data: Order data dictionary
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extract basic fields
            symbol = order_data.get('symbol', '')
            order_type = order_data.get('type', '')
            amount = order_data.get('amount', 0.0)
            price = order_data.get('price', 0.0)
            status = order_data.get('status', 'unknown')
            timestamp = order_data.get('timestamp', 0)
            
            # Store remaining data as JSON
            metadata = json.dumps({k: v for k, v in order_data.items() 
                                if k not in ['symbol', 'type', 'amount', 'price', 'status', 'timestamp']})
            
            cursor.execute('''
            INSERT OR REPLACE INTO orders 
            (id, symbol, type, amount, price, status, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (order_id, symbol, order_type, amount, price, status, timestamp, metadata))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Order {order_id} saved to database")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving order to database: {str(e)}")
            return False
    
    def save_trade(self, trade_data: Dict) -> bool:
        """
        Save executed trade to database
        
        Args:
            trade_data: Trade data dictionary
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            order_id = trade_data.get('order_id', '')
            symbol = trade_data.get('symbol', '')
            side = trade_data.get('side', '')
            amount = trade_data.get('amount', 0.0)
            price = trade_data.get('price', 0.0)
            timestamp = trade_data.get('timestamp', 0)
            profit = trade_data.get('profit', None)
            
            cursor.execute('''
            INSERT INTO trades 
            (order_id, symbol, side, amount, price, timestamp, profit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (order_id, symbol, side, amount, price, timestamp, profit))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Trade for order {order_id} saved to database")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving trade to database: {str(e)}")
            return False
    
    def save_volatility(self, volatility_data: Dict) -> bool:
        """
        Save volatility data to database
        
        Args:
            volatility_data: Volatility data dictionary with symbol, volatility, price, timestamp
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            symbol = volatility_data.get('symbol', '')
            volatility = volatility_data.get('volatility', 0.0)
            price = volatility_data.get('price', 0.0)
            timestamp = volatility_data.get('timestamp', int(time.time() * 1000))
            
            cursor.execute('''
            INSERT INTO volatility_history 
            (symbol, volatility, price, timestamp)
            VALUES (?, ?, ?, ?)
            ''', (symbol, volatility, price, timestamp))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving volatility data: {str(e)}")
            return False
    
    def get_orders(self, status: Optional[str] = None, 
                   symbol: Optional[str] = None, 
                   limit: int = 100) -> List[Dict]:
        """
        Get orders from database with optional filtering
        
        Args:
            status: Filter by order status
            symbol: Filter by symbol
            limit: Maximum number of orders to return
            
        Returns:
            List of order dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM orders"
            params = []
            
            # Add filters
            if status or symbol:
                query += " WHERE"
                
                if status:
                    query += " status = ?"
                    params.append(status)
                    
                    if symbol:
                        query += " AND"
                
                if symbol:
                    query += " symbol = ?"
                    params.append(symbol)
            
            # Add limit and order by
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            orders = []
            for row in rows:
                order_dict = dict(row)
                
                # Parse metadata JSON
                if 'metadata' in order_dict and order_dict['metadata']:
                    metadata = json.loads(order_dict['metadata'])
                    del order_dict['metadata']
                    order_dict.update(metadata)
                
                orders.append(order_dict)
            
            conn.close()
            return orders
            
        except Exception as e:
            self.logger.error(f"Error getting orders from database: {str(e)}")
            return []
    
    def get_trades(self, symbol: Optional[str] = None, 
                   order_id: Optional[str] = None, 
                   limit: int = 100) -> List[Dict]:
        """
        Get trades from database with optional filtering
        
        Args:
            symbol: Filter by symbol
            order_id: Filter by order ID
            limit: Maximum number of trades to return
            
        Returns:
            List of trade dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM trades"
            params = []
            
            # Add filters
            if symbol or order_id:
                query += " WHERE"
                
                if symbol:
                    query += " symbol = ?"
                    params.append(symbol)
                    
                    if order_id:
                        query += " AND"
                
                if order_id:
                    query += " order_id = ?"
                    params.append(order_id)
            
            # Add limit and order by
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            trades = [dict(row) for row in rows]
            conn.close()
            
            return trades
            
        except Exception as e:
            self.logger.error(f"Error getting trades from database: {str(e)}")
            return []
    
    def get_volatility_history(self, symbol: Optional[str] = None,
                             period: Optional[int] = None,
                             limit: int = 100) -> List[Dict]:
        """
        Get volatility history from database
        
        Args:
            symbol: Filter by symbol
            period: Time period in hours (e.g., 24 for last day)
            limit: Maximum number of records to return
            
        Returns:
            List of volatility history dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM volatility_history"
            params = []
            
            # Add filters
            filters_added = False
            
            if symbol:
                query += " WHERE symbol = ?"
                params.append(symbol)
                filters_added = True
            
            if period:
                # Calculate timestamp for period start
                period_start = int((datetime.now() - timedelta(hours=period)).timestamp() * 1000)
                
                if filters_added:
                    query += " AND"
                else:
                    query += " WHERE"
                    filters_added = True
                
                query += " timestamp >= ?"
                params.append(period_start)
            
            # Add limit and order by
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            volatility_data = [dict(row) for row in rows]
            conn.close()
            
            return volatility_data
            
        except Exception as e:
            self.logger.error(f"Error getting volatility history: {str(e)}")
            return []
    
    def save_setting(self, key: str, value: Any) -> bool:
        """
        Save setting to database
        
        Args:
            key: Setting key
            value: Setting value (will be JSON serialized)
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
            ''', (key, json.dumps(value)))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving setting: {str(e)}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get setting from database
        
        Args:
            key: Setting key
            default: Default value if setting not found
            
        Returns:
            Setting value (JSON deserialized)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return json.loads(row[0])
            else:
                return default
                
        except Exception as e:
            self.logger.error(f"Error getting setting: {str(e)}")
            return default
    
    def get_profit_stats(self, 
                        symbol: Optional[str] = None, 
                        start_time: Optional[int] = None, 
                        end_time: Optional[int] = None) -> Dict:
        """
        Get profit statistics
        
        Args:
            symbol: Filter by symbol
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            
        Returns:
            Dictionary with profit statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT SUM(profit) as total_profit, AVG(profit) as avg_profit, " \
                   "COUNT(*) as total_trades, symbol FROM trades WHERE profit IS NOT NULL"
            params = []
            
            # Add filters
            if symbol or start_time or end_time:
                if symbol:
                    query += " AND symbol = ?"
                    params.append(symbol)
                
                if start_time:
                    query += " AND timestamp >= ?"
                    params.append(start_time)
                
                if end_time:
                    query += " AND timestamp <= ?"
                    params.append(end_time)
            
            # Add group by
            query += " GROUP BY symbol"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            stats = {}
            for row in rows:
                total_profit, avg_profit, total_trades, symbol = row
                stats[symbol] = {
                    'total_profit': total_profit,
                    'avg_profit': avg_profit,
                    'total_trades': total_trades
                }
            
            conn.close()
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting profit statistics: {str(e)}")
            return {}
    
    def get_daily_stats(self, days: int = 7) -> Dict:
        """
        Get daily trading statistics
        
        Args:
            days: Number of days to include
            
        Returns:
            Dictionary with daily statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate timestamp for days ago
            days_ago = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            # Get daily profit
            cursor.execute('''
            SELECT 
                date(datetime(timestamp/1000, 'unixepoch')) as trade_date,
                SUM(profit) as daily_profit,
                COUNT(*) as num_trades,
                AVG(profit) as avg_profit
            FROM trades
            WHERE timestamp >= ? AND profit IS NOT NULL
            GROUP BY trade_date
            ORDER BY trade_date DESC
            ''', (days_ago,))
            
            daily_stats = {}
            for row in cursor.fetchall():
                trade_date, daily_profit, num_trades, avg_profit = row
                daily_stats[trade_date] = {
                    'profit': daily_profit,
                    'trades': num_trades,
                    'avg_profit': avg_profit
                }
            
            # Get daily order counts
            cursor.execute('''
            SELECT 
                date(datetime(timestamp/1000, 'unixepoch')) as order_date,
                COUNT(*) as num_orders,
                COUNT(CASE WHEN type = 'buy' THEN 1 END) as buy_orders,
                COUNT(CASE WHEN type = 'sell' THEN 1 END) as sell_orders
            FROM orders
            WHERE timestamp >= ?
            GROUP BY order_date
            ORDER BY order_date DESC
            ''', (days_ago,))
            
            for row in cursor.fetchall():
                order_date, num_orders, buy_orders, sell_orders = row
                if order_date in daily_stats:
                    daily_stats[order_date].update({
                        'orders': num_orders,
                        'buy_orders': buy_orders,
                        'sell_orders': sell_orders
                    })
                else:
                    daily_stats[order_date] = {
                        'profit': 0,
                        'trades': 0,
                        'avg_profit': 0,
                        'orders': num_orders,
                        'buy_orders': buy_orders,
                        'sell_orders': sell_orders
                    }
            
            conn.close()
            return daily_stats
            
        except Exception as e:
            self.logger.error(f"Error getting daily statistics: {str(e)}")
            return {}
    
    def get_symbol_performance(self, top_n: int = 5) -> Dict:
        """
        Get performance statistics by symbol
        
        Args:
            top_n: Number of top performers to return
            
        Returns:
            Dictionary with symbol performance statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get profit by symbol
            cursor.execute('''
            SELECT 
                symbol,
                SUM(profit) as total_profit,
                COUNT(*) as num_trades,
                AVG(profit) as avg_profit,
                MIN(profit) as min_profit,
                MAX(profit) as max_profit
            FROM trades
            WHERE profit IS NOT NULL
            GROUP BY symbol
            ORDER BY total_profit DESC
            LIMIT ?
            ''', (top_n,))
            
            symbol_stats = {}
            for row in cursor.fetchall():
                symbol, total_profit, num_trades, avg_profit, min_profit, max_profit = row
                symbol_stats[symbol] = {
                    'total_profit': total_profit,
                    'num_trades': num_trades,
                    'avg_profit': avg_profit,
                    'min_profit': min_profit,
                    'max_profit': max_profit
                }
            
            conn.close()
            return symbol_stats
            
        except Exception as e:
            self.logger.error(f"Error getting symbol performance: {str(e)}")
            return {}
    
    def get_volatility_stats(self, symbol: Optional[str] = None, 
                           period: int = 24) -> Dict:
        """
        Get volatility statistics
        
        Args:
            symbol: Filter by symbol
            period: Time period in hours
            
        Returns:
            Dictionary with volatility statistics
        """
        try:
            volatility_data = self.get_volatility_history(symbol, period)
            
            if not volatility_data:
                return {}
            
            # Group by symbol
            by_symbol = {}
            for data in volatility_data:
                sym = data['symbol']
                if sym not in by_symbol:
                    by_symbol[sym] = []
                by_symbol[sym].append(data['volatility'])
            
            # Calculate statistics
            stats = {}
            for sym, values in by_symbol.items():
                stats[sym] = {
                    'avg_volatility': sum(values) / len(values),
                    'max_volatility': max(values),
                    'min_volatility': min(values),
                    'num_samples': len(values)
                }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting volatility statistics: {str(e)}")
            return {}
    
    def export_trades_csv(self, filepath: str, 
                         start_time: Optional[int] = None,
                         end_time: Optional[int] = None) -> bool:
        """
        Export trades to CSV file
        
        Args:
            filepath: Path to save CSV file
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM trades"
            params = []
            
            # Add filters
            if start_time or end_time:
                query += " WHERE"
                
                if start_time:
                    query += " timestamp >= ?"
                    params.append(start_time)
                    
                    if end_time:
                        query += " AND"
                
                if end_time:
                    query += " timestamp <= ?"
                    params.append(end_time)
            
            # Order by timestamp
            query += " ORDER BY timestamp"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Write to CSV
            with open(filepath, 'w') as csv_file:
                # Write header
                csv_file.write(','.join(column_names) + '\n')
                
                # Write rows
                for row in rows:
                    csv_file.write(','.join([str(item) for item in row]) + '\n')
            
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting trades to CSV: {str(e)}")
            return False
    
    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """
        Backup database to file
        
        Args:
            backup_path: Path to save backup file
            
        Returns:
            Success status
        """
        try:
            if backup_path is None:
                # Generate backup filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = os.path.join(os.path.dirname(self.db_path), 'backups')
                os.makedirs(backup_dir, exist_ok=True)
                backup_path = os.path.join(backup_dir, f"ordertools_backup_{timestamp}.db")
            
            # Create backup
            source = sqlite3.connect(self.db_path)
            destination = sqlite3.connect(backup_path)
            
            source.backup(destination)
            
            source.close()
            destination.close()
            
            self.logger.info(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error backing up database: {str(e)}")
            return False
            
    def clean_old_data(self, days: int = 30) -> bool:
        """
        Remove old data from database
        
        Args:
            days: Age of data to remove in days
            
        Returns:
            Success status
        """
        try:
            # Calculate timestamp for days ago
            days_ago = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old volatility data
            cursor.execute("DELETE FROM volatility_history WHERE timestamp < ?", (days_ago,))
            volatility_count = cursor.rowcount
            
            # We don't delete orders and trades as they're important for record keeping
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Removed {volatility_count} old volatility records")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cleaning old data: {str(e)}")
            return False