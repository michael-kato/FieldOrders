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
        Persistent storage for field history and settings
        
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
                field_type TEXT NOT NULL,
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
                field_type TEXT NOT NULL,
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
            field_type = order_data.get('field_type', 'unknown')
            
            # Store remaining data as JSON
            metadata = json.dumps({k: v for k, v in order_data.items() 
                                if k not in ['symbol', 'type', 'amount', 'price', 
                                           'status', 'timestamp', 'field_type']})
            
            cursor.execute('''
            INSERT OR REPLACE INTO orders 
            (id, symbol, type, amount, price, status, timestamp, field_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (order_id, symbol, order_type, amount, price, status, timestamp, field_type, metadata))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Field order {order_id} saved to database")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving field activation: {str(e)}")
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
                   field_type: Optional[str] = None,
                   limit: int = 100) -> List[Dict]:
        """
        Get orders from database with optional filtering
        
        Args:
            status: Filter by order status
            symbol: Filter by symbol
            field_type: Filter by field type (buy/sell)
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
            filter_conditions = []
            
            if status:
                filter_conditions.append("status = ?")
                params.append(status)
            
            if symbol:
                filter_conditions.append("symbol = ?")
                params.append(symbol)
                
            if field_type:
                filter_conditions.append("field_type = ?")
                params.append(field_type)
            
            if filter_conditions:
                query += " WHERE " + " AND ".join(filter_conditions)
            
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
            self.logger.error(f"Error getting field orders from database: {str(e)}")
            return []
    
    def get_trades(self, symbol: Optional[str] = None, 
                   order_id: Optional[str] = None,
                   field_type: Optional[str] = None,
                   limit: int = 100) -> List[Dict]:
        """
        Get trades from database with optional filtering
        
        Args:
            symbol: Filter by symbol
            order_id: Filter by order ID
            field_type: Filter by field type (buy/sell)
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
            filter_conditions = []
            
            if symbol:
                filter_conditions.append("symbol = ?")
                params.append(symbol)
            
            if order_id:
                filter_conditions.append("order_id = ?")
                params.append(order_id)
                
            if field_type:
                filter_conditions.append("field_type = ?")
                params.append(field_type)
            
            if filter_conditions:
                query += " WHERE " + " AND ".join(filter_conditions)
            
            # Add limit and order by
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            trades = [dict(row) for row in rows]
            conn.close()
            
            return trades
            
        except Exception as e:
            self.logger.error(f"Error getting field activations from database: {str(e)}")
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
            filter_conditions = []
            
            if symbol:
                filter_conditions.append("symbol = ?")
                params.append(symbol)
            
            if period:
                # Calculate timestamp for period start
                period_start = int((datetime.now() - timedelta(hours=period)).timestamp() * 1000)
                filter_conditions.append("timestamp >= ?")
                params.append(period_start)
            
            if filter_conditions:
                query += " WHERE " + " AND ".join(filter_conditions)
            
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
    
    def export_trades_csv(self, filepath: str, 
                         start_time: Optional[int] = None,
                         end_time: Optional[int] = None) -> bool:
        """
        Export field activations to CSV file
        
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
            filter_conditions = []
            
            if start_time:
                filter_conditions.append("timestamp >= ?")
                params.append(start_time)
            
            if end_time:
                filter_conditions.append("timestamp <= ?")
                params.append(end_time)
            
            if filter_conditions:
                query += " WHERE " + " AND ".join(filter_conditions)
            
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
            self.logger.error(f"Error exporting field activations to CSV: {str(e)}")
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
            
    
    def save_trade(self, trade_data: Dict) -> bool:
        """
        Save executed trade to database
        
        Args:
            trade_data: Trade data dictionary
            
        Returns:
            Success status
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        order_id = trade_data.get('order_id', '')
        symbol = trade_data.get('symbol', '')
        side = trade_data.get('side', '')
        amount = trade_data.get('amount', 0.0)
        price = trade_data.get('price', 0.0)
        timestamp = trade_data.get('timestamp', 0)
        field_type = trade_data.get('field_type', 'unknown')
        
        cursor.execute('''
        INSERT INTO trades 
        (order_id, symbol, side, amount, price, timestamp, field_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, symbol, side, amount, price, timestamp, field_type))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Field activation for order {order_id} saved to database")