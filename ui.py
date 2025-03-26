"""
OrderTools - Tactical Field Deployment System
A sci-fi themed UI for crypto trading with the concept of deploying "fields" of orders
"""

import sys
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget, 
    QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QGroupBox, 
    QStatusBar, QAction, QToolBar, QTextEdit, QSplitter, QMessageBox, 
    QInputDialog, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QDateTime, QSize
from PyQt5.QtGui import QColor, QPalette, QFont

from chart import ChartWidget


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


class SciFiStyle:
    """Apply sci-fi styling to the application"""
    
    @staticmethod
    def apply_style(app):
        """Apply dark sci-fi style to application"""
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
            
            QTabWidget::pane {{
                border: 1px solid {COLOR_ACCENT};
            }}
            
            QTabBar::tab {{
                background-color: {COLOR_BG_MEDIUM};
                color: {COLOR_TEXT};
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 12px;
            }}
            
            QTabBar::tab:selected {{
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
        """)


class VolatilityTable(QTableWidget):
    """Table showing volatility scan results"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Symbol", "Volatility", "Price", "Volume", "Time"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
    
    def update_data(self, data):
        """Update table with volatility scan results"""
        self.setSortingEnabled(False)
        self.setRowCount(len(data))
        
        for row, item in enumerate(data):
            self.setItem(row, 0, QTableWidgetItem(item['symbol']))
            
            # Volatility with coloring
            volatility_value = item['volatility']
            volatility_item = QTableWidgetItem(f"{volatility_value:.2f}%")
            
            # Apply color based on volatility
            if volatility_value >= 15.0:
                volatility_item.setBackground(QColor(COLOR_DANGER))
            elif volatility_value >= 8.0:
                volatility_item.setBackground(QColor(COLOR_WARNING))
            elif volatility_value >= 5.0:
                volatility_item.setBackground(QColor(COLOR_SUCCESS))
            
            self.setItem(row, 1, volatility_item)
            
            # Price with precision
            self.setItem(row, 2, QTableWidgetItem(f"{item['last_price']:.8f}"))
            
            # Volume
            self.setItem(row, 3, QTableWidgetItem(f"{item['volume']:.2f}"))
            
            # Format timestamp
            timestamp = item.get('timestamp', 0)
            dt = QDateTime.fromMSecsSinceEpoch(timestamp)
            time_str = dt.toString('HH:mm:ss')
            self.setItem(row, 4, QTableWidgetItem(time_str))
        
        self.setSortingEnabled(True)
        # Sort by volatility by default
        self.sortItems(1, Qt.DescendingOrder)


class FieldsTable(QTableWidget):
    """Table showing deployed order fields"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels([
            "ID", "Symbol", "Field Type", "Amount", "Price", "Status"
        ])
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
    
    def update_data(self, data):
        """Update table with fields data"""
        self.setSortingEnabled(False)
        self.setRowCount(len(data))
        
        for row, (order_id, item) in enumerate(data.items()):
            self.setItem(row, 0, QTableWidgetItem(order_id[:8] + "..."))
            self.setItem(row, 1, QTableWidgetItem(item.get('symbol', '')))
            
            # Field type with color coding
            field_type = item.get('field_type', '')
            field_type_item = QTableWidgetItem(field_type.upper())
            
            if field_type == 'buy':
                field_type_item.setBackground(QColor(COLOR_BUY_FIELD))
                field_type_item.setForeground(QColor(COLOR_BG_DARK))
            elif field_type == 'sell':
                field_type_item.setBackground(QColor(COLOR_SELL_FIELD))
                field_type_item.setForeground(QColor(COLOR_BG_DARK))
            
            self.setItem(row, 2, field_type_item)
            
            # Amount, price, status
            self.setItem(row, 3, QTableWidgetItem(f"{item.get('amount', 0):.8f}"))
            self.setItem(row, 4, QTableWidgetItem(f"{item.get('price', 0):.8f}"))
            
            # Status with color coding
            status = item.get('status', '')
            status_item = QTableWidgetItem(status.upper())
            
            if status == 'closed':
                status_item.setBackground(QColor(COLOR_SUCCESS))
                status_item.setText("ACTIVATED")
            elif status == 'open':
                status_item.setBackground(QColor(COLOR_WARNING))
                status_item.setText("ARMED")
            
            self.setItem(row, 5, status_item)
        
        self.setSortingEnabled(True)


class ActivationsTable(QTableWidget):
    """Table showing field activations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            "Symbol", "Field Type", "Amount", "Price", "Time"
        ])
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
    
    def update_data(self, data):
        """Update table with field activations"""
        self.setSortingEnabled(False)
        self.setRowCount(len(data))
        
        for row, item in enumerate(data):
            self.setItem(row, 0, QTableWidgetItem(item.get('symbol', '')))
            
            # Field type with color coding
            field_type = item.get('field_type', '')
            field_type_item = QTableWidgetItem(field_type.upper() + " FIELD")
            
            if field_type == 'buy':
                field_type_item.setBackground(QColor(COLOR_BUY_FIELD))
                field_type_item.setForeground(QColor(COLOR_BG_DARK))
            elif field_type == 'sell':
                field_type_item.setBackground(QColor(COLOR_SELL_FIELD))
                field_type_item.setForeground(QColor(COLOR_BG_DARK))
            
            self.setItem(row, 1, field_type_item)
            
            # Amount, price
            self.setItem(row, 2, QTableWidgetItem(f"{item.get('amount', 0):.8f}"))
            self.setItem(row, 3, QTableWidgetItem(f"{item.get('price', 0):.8f}"))
            
            # Format timestamp
            timestamp = item.get('timestamp', 0)
            dt = QDateTime.fromSecsSinceEpoch(int(timestamp / 1000))
            time_str = dt.toString('yyyy-MM-dd HH:mm:ss')
            self.setItem(row, 4, QTableWidgetItem(time_str))
        
        self.setSortingEnabled(True)
        # Sort by time (descending)
        self.sortItems(4, Qt.DescendingOrder)


class AlertConsole(QTextEdit):
    """Console for displaying system alerts"""
    
    def __init__(self, alert_manager, parent=None):
        super().__init__(parent)
        self.alert_manager = alert_manager
        self.setReadOnly(True)
        
        # Set monospace font for console-like appearance
        font = QFont("Consolas, Courier New")
        font.setPointSize(9)
        self.setFont(font)
    
    def update_alerts(self):
        """Update with recent alerts"""
        alerts = self.alert_manager.get_recent_alerts(20)
        
        # Format alerts
        console_text = ""
        for alert in alerts:
            # Format timestamp
            timestamp = alert.get('timestamp', 0)
            dt = QDateTime.fromSecsSinceEpoch(int(timestamp))
            time_str = dt.toString('HH:mm:ss')
            
            # Get message
            alert_type = alert.get('type', '').replace('_', ' ').upper()
            data = alert.get('data', {})
            message = self.alert_manager._format_alert_message(alert.get('type', ''), data)
            
            # Add colored message based on type
            if "buy field" in message.lower():
                console_text += f'<span style="color:{COLOR_BUY_FIELD};">[{time_str}] {message}</span><br>'
            elif "sell field" in message.lower():
                console_text += f'<span style="color:{COLOR_SELL_FIELD};">[{time_str}] {message}</span><br>'
            elif "volatility" in message.lower():
                console_text += f'<span style="color:{COLOR_WARNING};">[{time_str}] {message}</span><br>'
            elif "error" in message.lower():
                console_text += f'<span style="color:{COLOR_DANGER};">[{time_str}] {message}</span><br>'
            else:
                console_text += f'<span style="color:{COLOR_TEXT};">[{time_str}] {message}</span><br>'
        
        self.setHtml(console_text)
        
        # Scroll to bottom
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class ControlPanel(QWidget):
    """Panel for controlling field deployment"""
    
    deploy_signal = pyqtSignal()
    retract_signal = pyqtSignal()
    settings_signal = pyqtSignal(dict)
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        
        # Create layout
        layout = QVBoxLayout()
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.deploy_button = QPushButton("DEPLOY FIELD ARRAY")
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
        """)
        
        self.retract_button = QPushButton("RETRACT FIELD ARRAY")
        self.retract_button.setMinimumHeight(40)
        self.retract_button.setEnabled(False)
        self.retract_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_BG_MEDIUM};
                color: {COLOR_DANGER};
                border: 2px solid {COLOR_DANGER};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_DANGER};
                color: {COLOR_BG_DARK};
            }}
            QPushButton:disabled {{
                color: #666666;
                border: 2px solid #666666;
            }}
        """)
        
        button_layout.addWidget(self.deploy_button)
        button_layout.addWidget(self.retract_button)
        layout.addLayout(button_layout)
        
        # Scanner settings
        scanner_group = QGroupBox("Scanner Settings")
        scanner_layout = QGridLayout()
        
        scanner_layout.addWidget(QLabel("Volatility Threshold (%):"), 0, 0)
        self.volatility_spin = QDoubleSpinBox()
        self.volatility_spin.setRange(0.1, 100.0)
        self.volatility_spin.setValue(settings['scanner'].get('min_volatility', 5.0))
        scanner_layout.addWidget(self.volatility_spin, 0, 1)
        
        scanner_layout.addWidget(QLabel("Scan Window (minutes):"), 1, 0)
        self.window_spin = QSpinBox()
        self.window_spin.setRange(1, 1440)
        self.window_spin.setValue(settings['scanner'].get('window_size', 60))
        scanner_layout.addWidget(self.window_spin, 1, 1)
        
        scanner_layout.addWidget(QLabel("Scan Interval (sec):"), 2, 0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 3600)
        self.interval_spin.setValue(settings['scanner'].get('scan_interval', 300))
        scanner_layout.addWidget(self.interval_spin, 2, 1)
        
        scanner_group.setLayout(scanner_layout)
        layout.addWidget(scanner_group)
        
        # Field settings
        field_group = QGroupBox("Field Configuration")
        field_layout = QGridLayout()
        
        field_layout.addWidget(QLabel("Buy Field Discount (%):"), 0, 0)
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(1.0, 50.0)
        self.discount_spin.setValue(settings['order'].get('discount_percentage', 15.0))
        field_layout.addWidget(self.discount_spin, 0, 1)
        
        field_layout.addWidget(QLabel("Max Field Size (USD):"), 1, 0)
        self.max_size_spin = QDoubleSpinBox()
        self.max_size_spin.setRange(10.0, 10000.0)
        self.max_size_spin.setValue(settings['order'].get('max_position_size', 100.0))
        field_layout.addWidget(self.max_size_spin, 1, 1)
        
        # Profit tiers
        field_layout.addWidget(QLabel("Sell Field Tiers (%):"), 2, 0)
        
        tier_layout = QHBoxLayout()
        
        self.tier1_spin = QDoubleSpinBox()
        self.tier1_spin.setRange(0.1, 100.0)
        self.tier1_spin.setValue(settings['order'].get('profit_tiers', [5.0, 10.0, 15.0])[0])
        tier_layout.addWidget(QLabel("Tier 1:"))
        tier_layout.addWidget(self.tier1_spin)
        
        self.tier2_spin = QDoubleSpinBox()
        self.tier2_spin.setRange(0.1, 100.0)
        self.tier2_spin.setValue(settings['order'].get('profit_tiers', [5.0, 10.0, 15.0])[1])
        tier_layout.addWidget(QLabel("Tier 2:"))
        tier_layout.addWidget(self.tier2_spin)
        
        self.tier3_spin = QDoubleSpinBox()
        self.tier3_spin.setRange(0.1, 100.0)
        self.tier3_spin.setValue(settings['order'].get('profit_tiers', [5.0, 10.0, 15.0])[2])
        tier_layout.addWidget(QLabel("Tier 3:"))
        tier_layout.addWidget(self.tier3_spin)
        
        field_layout.addLayout(tier_layout, 2, 1)
        
        # Apply button
        self.apply_button = QPushButton("APPLY CONFIGURATION")
        field_layout.addWidget(self.apply_button, 3, 0, 1, 2)
        
        field_group.setLayout(field_layout)
        layout.addWidget(field_group)
        
        # Set main layout
        self.setLayout(layout)
        
        # Connect signals
        self.deploy_button.clicked.connect(self.on_deploy)
        self.retract_button.clicked.connect(self.on_retract)
        self.apply_button.clicked.connect(self.on_apply_settings)
    
    def on_deploy(self):
        """Handle deploy button click"""
        self.deploy_button.setEnabled(False)
        self.retract_button.setEnabled(True)
        self.deploy_signal.emit()
    
    def on_retract(self):
        """Handle retract button click"""
        self.deploy_button.setEnabled(True)
        self.retract_button.setEnabled(False)
        self.retract_signal.emit()
    
    def on_apply_settings(self):
        """Apply settings"""
        # Get profit tiers
        profit_tiers = [
            self.tier1_spin.value(),
            self.tier2_spin.value(),
            self.tier3_spin.value()
        ]
        
        settings = {
            'scanner': {
                'min_volatility': self.volatility_spin.value(),
                'window_size': self.window_spin.value(),
                'scan_interval': self.interval_spin.value()
            },
            'order': {
                'discount_percentage': self.discount_spin.value(),
                'max_position_size': self.max_size_spin.value(),
                'profit_tiers': profit_tiers,
                'tier_percentages': [0.5, 0.3, 0.2]  # Default
            },
            'exchange': self.settings['exchange']  # Keep existing exchange settings
        }
        
        self.settings_signal.emit(settings)


class TacticalDashboard(QMainWindow):
    """Main application window with sci-fi tactical UI"""
    
    def __init__(self, scanner, order_manager, settings, storage, alert_manager):
        super().__init__()
        self.scanner = scanner
        self.order_manager = order_manager
        self.settings = settings
        self.storage = storage
        self.alert_manager = alert_manager
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        
        self.init_ui()
        
        # Setup timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(settings['gui'].get('update_interval', 1000))
        
        # Register for alerts
        self.alert_manager.register_callback("order_filled", self.on_order_filled)
        self.alert_manager.register_callback("high_volatility", self.on_high_volatility)
    
    def init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("OrderTools - Tactical Field System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Create splitter for top/bottom sections
        splitter = QSplitter(Qt.Vertical)
        
        # Top section (chart & control panel)
        top_widget = QWidget()
        top_layout = QHBoxLayout()
        
        # Chart (2/3 width)
        self.chart = ChartWidget()
        
        # Control panel (1/3 width)
        self.control_panel = ControlPanel(self.settings)
        
        top_layout.addWidget(self.chart, 2)
        top_layout.addWidget(self.control_panel, 1)
        top_widget.setLayout(top_layout)
        
        # Bottom section (tabs)
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout()
        
        tabs = QTabWidget()
        
        # Volatility tab
        volatility_tab = QWidget()
        volatility_layout = QVBoxLayout()
        self.volatility_table = VolatilityTable()
        volatility_layout.addWidget(self.volatility_table)
        volatility_tab.setLayout(volatility_layout)
        tabs.addTab(volatility_tab, "TACTICAL SCANNER")
        
        # Fields tab
        fields_tab = QWidget()
        fields_layout = QVBoxLayout()
        self.fields_table = FieldsTable()
        fields_layout.addWidget(self.fields_table)
        fields_tab.setLayout(fields_layout)
        tabs.addTab(fields_tab, "ACTIVE FIELDS")
        
        # Activations tab
        activations_tab = QWidget()
        activations_layout = QVBoxLayout()
        self.activations_table = ActivationsTable()
        activations_layout.addWidget(self.activations_table)
        activations_tab.setLayout(activations_layout)
        tabs.addTab(activations_tab, "FIELD ACTIVATIONS")
        
        # Alerts console tab
        alerts_tab = QWidget()
        alerts_layout = QVBoxLayout()
        self.alerts_console = AlertConsole(self.alert_manager)
        
        # Add clear button
        clear_button = QPushButton("CLEAR CONSOLE")
        clear_button.clicked.connect(self.alerts_console.clear)
        
        alerts_layout.addWidget(self.alerts_console)
        alerts_layout.addWidget(clear_button)
        alerts_tab.setLayout(alerts_layout)
        tabs.addTab(alerts_tab, "COMMAND CONSOLE")
        
        bottom_layout.addWidget(tabs)
        bottom_widget.setLayout(bottom_layout)
        
        # Add to splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([350, 450])  # Proportions: ~40% top, ~60% bottom
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Status bar
        self.statusBar().showMessage("System Ready")
        
        # Create menu and toolbar
        self.create_menu()
        self.create_toolbar()
        
        # Connect signals
        self.control_panel.deploy_signal.connect(self.start_scanner)
        self.control_panel.retract_signal.connect(self.stop_scanner)
        self.control_panel.settings_signal.connect(self.apply_settings)
    
    def create_menu(self):
        """Create menu bar"""
        menu_bar = self.menuBar()
        
        # Tactical menu
        tactical_menu = menu_bar.addMenu("Tactical")
        
        deploy_action = QAction("Deploy Field Array", self)
        deploy_action.triggered.connect(self.start_scanner)
        tactical_menu.addAction(deploy_action)
        
        retract_action = QAction("Retract Field Array", self)
        retract_action.triggered.connect(self.stop_scanner)
        tactical_menu.addAction(retract_action)
        
        tactical_menu.addSeparator()
        
        export_action = QAction("Export Data", self)
        export_action.triggered.connect(self.export_field_data)
        tactical_menu.addAction(export_action)
        
        tactical_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        tactical_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        
        price_chart_action = QAction("Price Chart", self)
        price_chart_action.triggered.connect(self.chart.show_price_chart)
        view_menu.addAction(price_chart_action)
        
        candle_chart_action = QAction("Candlestick Chart", self)
        candle_chart_action.triggered.connect(self.chart.show_candlestick_chart)
        view_menu.addAction(candle_chart_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        manual_action = QAction("Field Manual", self)
        manual_action.triggered.connect(self.show_manual)
        help_menu.addAction(manual_action)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        deploy_action = QAction("DEPLOY FIELDS", self)
        deploy_action.triggered.connect(self.start_scanner)
        toolbar.addAction(deploy_action)
        
        retract_action = QAction("RETRACT FIELDS", self)
        retract_action.triggered.connect(self.stop_scanner)
        toolbar.addAction(retract_action)
        
        toolbar.addSeparator()
        
        price_chart_action = QAction("PRICE CHART", self)
        price_chart_action.triggered.connect(self.chart.show_price_chart)
        toolbar.addAction(price_chart_action)
        
        candle_chart_action = QAction("CANDLESTICK", self)
        candle_chart_action.triggered.connect(self.chart.show_candlestick_chart)
        toolbar.addAction(candle_chart_action)
    
    def update_data(self):
        """Update data in all components"""
        if not self.is_running:
            return
            
        try:
            # Update volatility table
            volatile_pairs = self.scanner.scan_market()
            self.volatility_table.update_data(volatile_pairs)
            
            # Update fields table
            all_fields = {}
            all_fields.update(self.order_manager.get_buy_field_orders())
            all_fields.update(self.order_manager.get_sell_field_orders())
            self.fields_table.update_data(all_fields)
            
            # Update activations table
            trades = self.storage.get_trades(limit=100)
            self.activations_table.update_data(trades)
            
            # Update alerts console
            self.alerts_console.update_alerts()
            
            # Save volatility data
            if volatile_pairs:
                for pair in volatile_pairs:
                    self.storage.save_volatility({
                        'symbol': pair['symbol'],
                        'volatility': pair['volatility'],
                        'price': pair['last_price'],
                        'timestamp': pair['timestamp']
                    })
            
            # Update chart if we have volatile pairs
            if volatile_pairs:
                # Select first pair for chart
                pair = volatile_pairs[0]
                symbol = pair['symbol']
                
                # Set chart title
                self.chart.set_chart_title(f"{symbol} - Volatility: {pair['volatility']:.2f}%")
                
                # Get OHLCV data for candlestick chart
                ohlcv = self.scanner.connector.get_ohlcv(symbol, '1m', 60)
                
                if ohlcv:
                    # Format data for chart
                    candles = []
                    timestamps = []
                    prices = []
                    volatility_data = []
                    vol_timestamps = []
                    
                    for i, candle in enumerate(ohlcv):
                        timestamp, open_price, high, low, close, volume = candle
                        
                        candles.append({
                            'timestamp': timestamp,
                            'open': open_price,
                            'high': high,
                            'low': low,
                            'close': close
                        })
                        
                        timestamps.append(timestamp)
                        prices.append(close)
                        
                        # Calculate volatility for each candle
                        if i > 0:
                            vol = ((high - low) / low) * 100
                            volatility_data.append(vol)
                            vol_timestamps.append(timestamp)
                    
                    # Update charts
                    self.chart.update_candlestick_data(candles)
                    self.chart.update_price_data(timestamps, prices)
                    
                    if volatility_data:
                        self.chart.update_volatility_data(vol_timestamps, volatility_data)
            
            # Update status bar
            self.statusBar().showMessage(f"Field Array Active | Last Update: {time.strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.logger.error(f"Error updating data: {str(e)}")
            self.statusBar().showMessage(f"Error: {str(e)}")
    
    def start_scanner(self):
        """Start scanner and deploy fields"""
        self.is_running = True
        self.statusBar().showMessage("Field Array Deployed")
    
    def stop_scanner(self):
        """Stop scanner and retract fields"""
        self.is_running = False
        self.statusBar().showMessage("Field Array Retracted")
    
    def apply_settings(self, new_settings):
        """Apply new field settings"""
        # Update scanner settings
        self.scanner.min_volatility = new_settings['scanner']['min_volatility']
        self.scanner.window_size = new_settings['scanner']['window_size']
        
        # Update order manager settings
        self.order_manager.discount_percentage = new_settings['order']['discount_percentage']
        self.order_manager.profit_tiers = new_settings['order']['profit_tiers']
        
        # Update other settings
        self.settings.update(new_settings)
        
        # Save settings to storage
        self.storage.save_setting('scanner', new_settings['scanner'])
        self.storage.save_setting('order', new_settings['order'])
        self.storage.save_setting('exchange', new_settings['exchange'])
        
        self.statusBar().showMessage("Field Configuration Updated")
    
    def on_order_filled(self, data):
        """Handle order filled alert"""
        # Refresh data
        self.update_data()
    
    def on_high_volatility(self, data):
        """Handle high volatility alert"""
        # Switch to volatility tab
        tabs = self.findChild(QTabWidget)
        if tabs:
            tabs.setCurrentIndex(0)  # Volatility tab
        
        # Refresh data
        self.update_data()
    
    def export_field_data(self):
        """Export field activation data to CSV file"""
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/export/field_activations_{timestamp}.csv"
            
            if self.storage.export_trades_csv(filepath):
                QMessageBox.information(self, "Export Successful", 
                                      f"Field activation data exported to {filepath}")
            else:
                QMessageBox.warning(self, "Export Failed", 
                                  "Failed to export field activation data")
                
        except Exception as e:
            self.logger.error(f"Error exporting field data: {str(e)}")
            QMessageBox.critical(self, "Export Error", str(e))
    
    def show_manual(self):
        """Show field manual dialog"""
        manual_text = """
        <h2>TACTICAL FIELD ARRAY MANUAL</h2>
        
        <h3>OVERVIEW</h3>
        <p>The Field Deployment System allows you to place strategic order fields across price territories. These fields act like landmines, waiting to be triggered by price movements.</p>
        
        <h3>FIELD TYPES</h3>
        <ul>
            <li><b>BUY FIELDS:</b> Deployed below market price to capture price drops</li>
            <li><b>SELL FIELDS:</b> Deployed after buy field activation to secure profits</li>
        </ul>
        
        <h3>OPERATIONS</h3>
        <ol>
            <li>Configure volatility threshold and field parameters</li>
            <li>Deploy field array using the DEPLOY button</li>
            <li>Monitor field activations in the console</li>
            <li>Retract fields when tactical objectives are complete</li>
        </ol>
        """
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Field Array Manual")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(manual_text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.exec_()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_running:
            reply = QMessageBox.question(self, 'Confirm Exit',
                "Field Array is active. Do you want to exit?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def run_tactical_interface(scanner, order_manager, settings, storage, alert_manager):
    """Run the tactical interface application"""
    app = QApplication(sys.argv)
    
    # Apply sci-fi styling
    SciFiStyle.apply_style(app)
    
    # Create and show main window
    main_window = TacticalDashboard(scanner, order_manager, settings, storage, alert_manager)
    main_window.show()
    
    # Run application
    sys.exit(app.exec_())
