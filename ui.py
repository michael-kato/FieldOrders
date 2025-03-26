import sys
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QSpinBox, QDoubleSpinBox,
    QGroupBox, QHeaderView, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QDateTime
from PyQt5.QtGui import QColor, QPalette, QFont

# Color scheme
COLOR_BG_DARK = "#121212"
COLOR_BG_MEDIUM = "#1E1E1E"
COLOR_TEXT = "#E0E0E0"
COLOR_ACCENT = "#00B0FF"
COLOR_SUCCESS = "#00E676"
COLOR_WARNING = "#FFEA00"
COLOR_DANGER = "#FF1744"
COLOR_BUY_FIELD = "#00C853"
COLOR_SELL_FIELD = "#2979FF"

class SimplifiedStyle:
    """Apply simplified styling to the application"""
    
    @staticmethod
    def apply_style(app):
        """Apply dark style to application"""
        app.setStyle("Fusion")
        
        # Create dark palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(COLOR_BG_DARK))
        palette.setColor(QPalette.WindowText, QColor(COLOR_TEXT))
        palette.setColor(QPalette.Base, QColor(COLOR_BG_MEDIUM))
        palette.setColor(QPalette.AlternateBase, QColor(COLOR_BG_MEDIUM))
        palette.setColor(QPalette.Text, QColor(COLOR_TEXT))
        palette.setColor(QPalette.Button, QColor(COLOR_BG_MEDIUM))
        palette.setColor(QPalette.ButtonText, QColor(COLOR_TEXT))
        palette.setColor(QPalette.Highlight, QColor(COLOR_ACCENT))
        palette.setColor(QPalette.HighlightedText, QColor(COLOR_BG_DARK))
        
        app.setPalette(palette)
        
        # Set stylesheet
        app.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {COLOR_BG_DARK};
                color: {COLOR_TEXT};
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            
            QPushButton {{
                background-color: {COLOR_BG_MEDIUM};
                color: {COLOR_TEXT};
                border: 1px solid {COLOR_ACCENT};
                border-radius: 4px;
                padding: 5px 15px;
            }}
            
            QPushButton:hover {{
                background-color: {COLOR_ACCENT};
                color: {COLOR_BG_DARK};
            }}
            
            QTableView {{
                gridline-color: {COLOR_ACCENT};
                border: 1px solid {COLOR_ACCENT};
            }}
            
            QHeaderView::section {{
                background-color: {COLOR_BG_MEDIUM};
                color: {COLOR_ACCENT};
                border: none;
                padding: 4px;
            }}
            
            QGroupBox {{
                border: 1px solid {COLOR_ACCENT};
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {COLOR_ACCENT};
            }}
            
            QSpinBox, QDoubleSpinBox {{
                background-color: {COLOR_BG_MEDIUM};
                color: {COLOR_TEXT};
                border: 1px solid {COLOR_ACCENT};
                border-radius: 4px;
                padding: 2px 5px;
            }}
        """)

class VolatilityList(QTableWidget):
    """Table showing volatility scan results"""
    
    item_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Symbol", "Volatility", "Price"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        
        # Connect selection changed
        self.itemSelectionChanged.connect(self.on_selection_changed)
    
    def update_data(self, data, active_symbols=None):
        """Update table with volatility scan results"""
        self.setSortingEnabled(False)
        self.setRowCount(len(data))
        
        for row, item in enumerate(data):
            symbol_item = QTableWidgetItem(item['symbol'])
            
            # Color symbols with active orders
            if active_symbols and item['symbol'] in active_symbols:
                symbol_item.setBackground(QColor(COLOR_SUCCESS))
                symbol_item.setForeground(QColor(COLOR_BG_DARK))
            
            self.setItem(row, 0, symbol_item)
            
            # Volatility with coloring
            volatility_value = item['volatility']
            volatility_item = QTableWidgetItem(f"{volatility_value:.2f}%")
            
            # Apply color based on volatility
            if volatility_value >= 15.0:
                volatility_item.setBackground(QColor(COLOR_DANGER))
            elif volatility_value >= 8.0:
                volatility_item.setBackground(QColor(COLOR_WARNING))
            
            self.setItem(row, 1, volatility_item)
            
            # Price with precision
            self.setItem(row, 2, QTableWidgetItem(f"{item['last_price']:.8f}"))
        
        self.setSortingEnabled(True)
        # Sort by volatility by default
        self.sortItems(1, Qt.DescendingOrder)
    
    def on_selection_changed(self):
        """Handle selection change"""
        selected_items = self.selectedItems()
        if selected_items:
            symbol = self.item(selected_items[0].row(), 0).text()
            self.item_selected.emit(symbol)

class ActiveOrdersList(QTableWidget):
    """Table showing active orders for selected symbol"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Type", "Price", "Amount", "Status"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
    
    def update_data(self, orders, symbol):
        """Update table with orders for selected symbol"""
        # Filter orders for the selected symbol
        filtered_orders = []
        for order_id, order in orders.items():
            if order.get('symbol') == symbol:
                filtered_orders.append(order)
        
        self.setSortingEnabled(False)
        self.setRowCount(len(filtered_orders))
        
        for row, order in enumerate(filtered_orders):
            # Field type with color coding
            field_type = order.get('field_type', '')
            field_type_item = QTableWidgetItem(field_type.upper())
            
            if field_type == 'buy':
                field_type_item.setBackground(QColor(COLOR_BUY_FIELD))
                field_type_item.setForeground(QColor(COLOR_BG_DARK))
            elif field_type == 'sell':
                field_type_item.setBackground(QColor(COLOR_SELL_FIELD))
                field_type_item.setForeground(QColor(COLOR_BG_DARK))
            
            self.setItem(row, 0, field_type_item)
            
            # Price, amount
            self.setItem(row, 1, QTableWidgetItem(f"{order.get('price', 0):.8f}"))
            self.setItem(row, 2, QTableWidgetItem(f"{order.get('amount', 0):.8f}"))
            
            # Status
            status = order.get('status', '')
            status_item = QTableWidgetItem(status.upper())
            
            if status == 'closed':
                status_item.setBackground(QColor(COLOR_SUCCESS))
                status_item.setText("ACTIVATED")
            elif status == 'open':
                status_item.setBackground(QColor(COLOR_WARNING))
                status_item.setText("ARMED")
            
            self.setItem(row, 3, status_item)
        
        self.setSortingEnabled(True)

class FieldConfigPanel(QWidget):
    """Panel for configuring and placing field orders"""
    
    deploy_buy_field = pyqtSignal(str, float, dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_symbol = ""
        self.current_price = 0.0
        
        # Create layout
        layout = QVBoxLayout()
        
        # Buy field config
        buy_group = QGroupBox("Buy Field Configuration")
        buy_layout = QGridLayout()
        
        buy_layout.addWidget(QLabel("Number of Orders:"), 0, 0)
        self.buy_orders_spin = QSpinBox()
        self.buy_orders_spin.setRange(1, 10)
        self.buy_orders_spin.setValue(3)
        buy_layout.addWidget(self.buy_orders_spin, 0, 1)
        
        buy_layout.addWidget(QLabel("Start Discount (%):"), 1, 0)
        self.buy_start_spin = QDoubleSpinBox()
        self.buy_start_spin.setRange(0.1, 30.0)
        self.buy_start_spin.setValue(5.0)
        buy_layout.addWidget(self.buy_start_spin, 1, 1)
        
        buy_layout.addWidget(QLabel("End Discount (%):"), 2, 0)
        self.buy_end_spin = QDoubleSpinBox()
        self.buy_end_spin.setRange(0.1, 50.0)
        self.buy_end_spin.setValue(15.0)
        buy_layout.addWidget(self.buy_end_spin, 2, 1)
        
        buy_layout.addWidget(QLabel("Position Size (USD):"), 3, 0)
        self.position_size_spin = QDoubleSpinBox()
        self.position_size_spin.setRange(10.0, 1000.0)
        self.position_size_spin.setValue(100.0)
        buy_layout.addWidget(self.position_size_spin, 3, 1)
        
        buy_group.setLayout(buy_layout)
        layout.addWidget(buy_group)
        
        # Sell field config
        sell_group = QGroupBox("Sell Field Configuration (Auto)")
        sell_layout = QGridLayout()
        
        sell_layout.addWidget(QLabel("Number of Orders:"), 0, 0)
        self.sell_orders_spin = QSpinBox()
        self.sell_orders_spin.setRange(1, 10)
        self.sell_orders_spin.setValue(3)
        sell_layout.addWidget(self.sell_orders_spin, 0, 1)
        
        sell_layout.addWidget(QLabel("Start Profit (%):"), 1, 0)
        self.sell_start_spin = QDoubleSpinBox()
        self.sell_start_spin.setRange(0.1, 30.0)
        self.sell_start_spin.setValue(5.0)
        sell_layout.addWidget(self.sell_start_spin, 1, 1)
        
        sell_layout.addWidget(QLabel("End Profit (%):"), 2, 0)
        self.sell_end_spin = QDoubleSpinBox()
        self.sell_end_spin.setRange(0.1, 100.0)
        self.sell_end_spin.setValue(15.0)
        sell_layout.addWidget(self.sell_end_spin, 2, 1)
        
        sell_group.setLayout(sell_layout)
        layout.addWidget(sell_group)
        
        # Deploy button
        self.deploy_button = QPushButton("DEPLOY FIELD")
        self.deploy_button.setEnabled(False)
        self.deploy_button.setMinimumHeight(40)
        self.deploy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BG_MEDIUM};
                color: {COLOR_BUY_FIELD};
                border: 2px solid {COLOR_BUY_FIELD};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BUY_FIELD};
                color: {COLOR_BG_DARK};
            }}
            QPushButton:disabled {{
                color: #666666;
                border: 2px solid #666666;
            }}
        """)
        layout.addWidget(self.deploy_button)
        
        # Add stretch
        layout.addStretch()
        
        # Set main layout
        self.setLayout(layout)
        
        # Connect signals
        self.deploy_button.clicked.connect(self.on_deploy_field)
    
    def set_selected_symbol(self, symbol, price):
        """Set selected symbol and enable/disable deploy button"""
        self.selected_symbol = symbol
        self.current_price = price
        self.deploy_button.setEnabled(bool(symbol))
    
    def on_deploy_field(self):
        """Handle deploy button click"""
        if not self.selected_symbol:
            return
        
        # Get field configuration
        config = {
            'buy_orders': self.buy_orders_spin.value(),
            'buy_start': self.buy_start_spin.value(),
            'buy_end': self.buy_end_spin.value(),
            'sell_orders': self.sell_orders_spin.value(),
            'sell_start': self.sell_start_spin.value(),
            'sell_end': self.sell_end_spin.value()
        }
        
        # Emit signal with symbol, position size, and config
        self.deploy_buy_field.emit(self.selected_symbol, self.position_size_spin.value(), config)

class SimplifiedDashboard(QMainWindow):
    """Main application window with simplified UI"""
    
    def __init__(self, scanner, order_manager, settings, storage=None, alert_manager=None):
        super().__init__()
        self.scanner = scanner
        self.order_manager = order_manager
        self.settings = settings
        self.storage = storage
        self.alert_manager = alert_manager
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.selected_symbol = ""
        self.selected_price = 0.0
        
        self.init_ui()
        
        # Setup timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(settings.get('gui', {}).get('update_interval', 1000))
    
    def init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("FieldOrders - Simplified UI")
        self.setGeometry(100, 100, 900, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left side: Volatility list (1/3 width)
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Volatile Pairs"))
        
        self.volatility_list = VolatilityList()
        self.volatility_list.item_selected.connect(self.on_symbol_selected)
        left_layout.addWidget(self.volatility_list)
        
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        
        # Center: Active orders for selected pair (1/3 width)
        center_layout = QVBoxLayout()
        center_layout.addWidget(QLabel("Active Orders"))
        
        self.orders_list = ActiveOrdersList()
        center_layout.addWidget(self.orders_list)
        
        center_widget = QWidget()
        center_widget.setLayout(center_layout)
        
        # Right side: Field configuration panel (1/3 width)
        self.config_panel = FieldConfigPanel()
        self.config_panel.deploy_buy_field.connect(self.on_deploy_buy_field)
        
        # Add widgets to main layout with equal width
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(center_widget, 1)
        main_layout.addWidget(self.config_panel, 1)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Start/Stop button in status bar
        self.statusBar().showMessage("Scanner Ready")
        
        self.scan_button = QPushButton("START SCANNER")
        self.scan_button.clicked.connect(self.toggle_scanner)
        self.statusBar().addPermanentWidget(self.scan_button)
    
    def toggle_scanner(self):
        """Toggle scanner on/off"""
        self.is_running = not self.is_running
        
        if self.is_running:
            self.scan_button.setText("STOP SCANNER")
            self.statusBar().showMessage("Scanner Running")
        else:
            self.scan_button.setText("START SCANNER")
            self.statusBar().showMessage("Scanner Stopped")
    
    def update_data(self):
        """Update data in all components"""
        if not self.is_running:
            return
            
        try:
            # Get all active orders
            all_orders = {}
            all_orders.update(self.order_manager.get_buy_field_orders())
            all_orders.update(self.order_manager.get_sell_field_orders())
            
            # Get active symbols
            active_symbols = set(order.get('symbol', '') for order in all_orders.values())
            
            # Update volatility list
            volatile_pairs = self.scanner.scan_market()
            self.volatility_list.update_data(volatile_pairs, active_symbols)
            
            # Update orders list for selected symbol
            if self.selected_symbol:
                self.orders_list.update_data(all_orders, self.selected_symbol)
            
            # Update status bar
            self.statusBar().showMessage(f"Scanner Running | Last Update: {time.strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.logger.error(f"Error updating data: {str(e)}")
            self.statusBar().showMessage(f"Error: {str(e)}")
    
    def on_symbol_selected(self, symbol):
        """Handle symbol selection"""
        self.selected_symbol = symbol
        
        # Find price for selected symbol
        volatile_pairs = self.scanner.scan_market()
        for pair in volatile_pairs:
            if pair['symbol'] == symbol:
                self.selected_price = pair['last_price']
                break
        
        # Update orders list
        all_orders = {}
        all_orders.update(self.order_manager.get_buy_field_orders())
        all_orders.update(self.order_manager.get_sell_field_orders())
        self.orders_list.update_data(all_orders, symbol)
        
        # Update field panel
        self.config_panel.set_selected_symbol(symbol, self.selected_price)
    
    def on_deploy_buy_field(self, symbol, position_size, config):
        """Handle deploy buy field signal"""
        if not symbol:
            return
        
        try:
            # Calculate price spread for buy orders
            buy_orders = config['buy_orders']
            buy_start = config['buy_start']
            buy_end = config['buy_end']
            
            # Save sell field config for when buy orders are filled
            sell_config = {
                'orders': config['sell_orders'],
                'start': config['sell_start'],
                'end': config['sell_end']
            }
            
            # Deploy multiple buy field orders
            if buy_orders > 1:
                # Calculate price steps
                buy_step = (buy_end - buy_start) / (buy_orders - 1) if buy_orders > 1 else 0
                order_size = position_size / buy_orders
                
                orders_placed = 0
                for i in range(buy_orders):
                    discount = buy_start + (i * buy_step)
                    buy_price = self.selected_price * (1 - (discount / 100))
                    
                    order = self.order_manager.place_buy_field(symbol, self.selected_price, order_size)
                    
                    if order and 'id' in order:
                        # Store sell field config for this order
                        if self.storage:
                            self.storage.save_setting(f"sell_config_{order['id']}", sell_config)
                        
                        orders_placed += 1
                
                self.statusBar().showMessage(f"Deployed {orders_placed} buy orders for {symbol}")
            else:
                # Single buy field order
                buy_price = self.selected_price * (1 - (buy_start / 100))
                order = self.order_manager.place_buy_field(symbol, self.selected_price, position_size)
                
                if order and 'id' in order:
                    # Store sell field config for this order
                    if self.storage:
                        self.storage.save_setting(f"sell_config_{order['id']}", sell_config)
                    
                    self.statusBar().showMessage(f"Deployed buy field for {symbol} at {buy_price:.8f}")
                else:
                    self.statusBar().showMessage(f"Failed to deploy buy field for {symbol}")
            
            # Refresh data
            self.update_data()
            
        except Exception as e:
            self.logger.error(f"Error deploying buy field: {str(e)}")
            self.statusBar().showMessage(f"Error: {str(e)}")
    
    def deploy_multi_sell_field(self, buy_order_id):
        """Deploy multiple sell field orders based on configuration"""
        try:
            # Get order details
            buy_order = self.order_manager.active_orders.get(buy_order_id)
            if not buy_order:
                return []
            
            # Get sell field configuration for this order
            sell_config = None
            if self.storage:
                sell_config = self.storage.get_setting(f"sell_config_{buy_order_id}")
            
            if not sell_config:
                # Use default sell field configuration
                sell_config = {
                    'orders': 3,
                    'start': 5.0,
                    'end': 15.0
                }
            
            # Calculate custom profit tiers
            orders = sell_config['orders']
            start = sell_config['start']
            end = sell_config['end']
            
            # Generate profit tiers
            if orders > 1:
                step = (end - start) / (orders - 1)
                profit_tiers = [start + (i * step) for i in range(orders)]
            else:
                profit_tiers = [start]
            
            # Generate percentages (equal distribution)
            tier_percentages = [1.0 / orders] * orders
            
            # Save original tiers
            original_tiers = self.order_manager.profit_tiers
            original_percentages = self.order_manager.tier_percentages
            
            # Set custom tiers
            self.order_manager.profit_tiers = profit_tiers
            self.order_manager.tier_percentages = tier_percentages
            
            # Deploy sell field
            sell_orders = self.order_manager.deploy_sell_field(buy_order_id)
            
            # Restore original tiers
            self.order_manager.profit_tiers = original_tiers
            self.order_manager.tier_percentages = original_percentages
            
            return sell_orders
            
        except Exception as e:
            self.logger.error(f"Error deploying multi sell field: {str(e)}")
            return []