        line_chart_action.triggered.connect(self.chart.show_price_chart)
        view_menu.addAction(line_chart_action)
        
        candle_chart_action = QAction("Candlestick Chart", self)
        candle_chart_action.triggered.connect(self.chart.show_candlestick_chart)
        view_menu.addAction(candle_chart_action)
        
        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")
        
        refresh_stats_action = QAction("Refresh Statistics", self)
        refresh_stats_action.triggered.connect(self.refresh_stats)
        tools_menu.addAction(refresh_stats_action)
        
        clean_data_action = QAction("Clean Old Data", self)
        clean_data_action.triggered.connect(self.clean_old_data)
        tools_menu.addAction(clean_data_action)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Start action
        start_action = QAction("Start Scanner", self)
        start_action.triggered.connect(self.start_scanner)
        toolbar.addAction(start_action)
        
        # Stop action
        stop_action = QAction("Stop Scanner", self)
        stop_action.triggered.connect(self.stop_scanner)
        toolbar.addAction(stop_action)
        
        # Separator
        toolbar.addSeparator()
        
        # Chart type actions
        line_chart_action = QAction("Line Chart", self)
        line_chart_action.triggered.connect(self.chart.show_price_chart)
        toolbar.addAction(line_chart_action)
        
        candle_chart_action = QAction("Candlestick Chart", self)
        candle_chart_action.triggered.connect(self.chart.show_candlestick_chart)
        toolbar.addAction(candle_chart_action)
        
        # Separator
        toolbar.addSeparator()
        
        # Export action
        export_action = QAction("Export Trades", self)
        export_action.triggered.connect(self.export_trades)
        toolbar.addAction(export_action)
    
    def export_trades(self):
        """Export trades to CSV file"""
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/export/trades_{timestamp}.csv"
            
            if self.storage.export_trades_csv(filepath):
                QMessageBox.information(self, "Export Successful", 
                                      f"Trades exported to {filepath}")
            else:
                QMessageBox.warning(self, "Export Failed", 
                                  "Failed to export trades to CSV")
                
        except Exception as e:
            self.logger.error(f"Error exporting trades: {str(e)}")
            QMessageBox.critical(self, "Export Error", str(e))
    
    def backup_database(self):
        """Backup database to file"""
        try:
            if self.storage.backup_database():
                QMessageBox.information(self, "Backup Successful", 
                                      "Database backed up successfully")
            else:
                QMessageBox.warning(self, "Backup Failed", 
                                  "Failed to backup database")
                
        except Exception as e:
            self.logger.error(f"Error backing up database: {str(e)}")
            QMessageBox.critical(self, "Backup Error", str(e))
    
    def clean_old_data(self):
        """Clean old data from database"""
        try:
            days, ok = QInputDialog.getInt(self, "Clean Old Data", 
                                       "Remove data older than (days):", 30, 1, 365)
            if ok:
                if self.storage.clean_old_data(days):
                    QMessageBox.information(self, "Clean Successful", 
                                          f"Data older than {days} days removed")
                else:
                    QMessageBox.warning(self, "Clean Failed", 
                                      "Failed to clean old data")
                    
        except Exception as e:
            self.logger.error(f"Error cleaning old data: {str(e)}")
            QMessageBox.critical(self, "Clean Error", str(e))
    
    def refresh_stats(self):
        """Refresh statistics panel"""
        try:
            self.stats_panel.update_stats()
            self.statusBar().showMessage("Statistics refreshed")
            
        except Exception as e:
            self.logger.error(f"Error refreshing stats: {str(e)}")
            self.statusBar().showMessage(f"Error refreshing stats: {str(e)}")
    def create_menu(self):
        """Create menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        export_action = QAction("Export Trades", self)
        export_action.triggered.connect(self.export_trades)
        file_menu.addAction(export_action)
        
        backup_action = QAction("Backup Database", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        
        line_chart_action = QAction("Line Chart", self)
        line_chart_action.triggered.                self.top_table.setItem(row, 2, QTableWidgetItem(str(stats.get('num_trades', 0))))
                self.top_table.setItem(row, 3, QTableWidgetItem(f"{stats.get('avg_profit', 0):.2f}%"))
                self.top_table.setItem(row, 4, QTableWidgetItem(f"{stats.get('max_profit', 0):.2f}%"))
            
            # Update daily stats
            daily_stats = self.storage.get_daily_stats(days=14)
            self.daily_table.setRowCount(len(daily_stats))
            
            for row, (date, stats) in enumerate(daily_stats.items()):
                self.daily_table.setItem(row, 0, QTableWidgetItem(date))
                self.daily_table.setItem(row, 1, QTableWidgetItem(f"{stats.get('profit', 0):.2f}%"))
                self.daily_table.setItem(row, 2, QTableWidgetItem(str(stats.get('trades', 0))))
                self.daily_table.setItem(row, 3, QTableWidgetItem(str(stats.get('orders', 0))))
                self.daily_table.setItem(row, 4, QTableWidgetItem(f"{stats.get('avg_profit', 0):.2f}%"))
            
        except Exception as e:
            logging.error(f"Error updating stats: {str(e)}")
    
    def export_data(self):
        """Export trade data to CSV"""
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"data/export/trades_{timestamp}.csv"
            
            if self.storage.export_trades_csv(filepath):
                QMessageBox.information(self, "Export Successful", 
                                      f"Trades exported to {filepath}")
            else:
                QMessageBox.warning(self, "Export Failed", 
                                  "Failed to export trades to CSV")
                
        except Exception as e:
            logging.error(f"Error exporting data: {str(e)}")
            QMessageBox.critical(self, "Export Error", str(e))class StatsPanel(QWidget):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        
        # Create layout
        main_layout = QVBoxLayout()
        
        # Performance summary
        summary_group = QGroupBox("Performance Summary")
        summary_layout = QGridLayout()
        
        self.total_trades_label = QLabel("0")
        self.total_profit_label = QLabel("0.00%")
        self.avg_profit_label = QLabel("0.00%")
        self.win_rate_label = QLabel("0.0%")
        
        summary_layout.addWidget(QLabel("Total Trades:"), 0, 0)
        summary_layout.addWidget(self.total_trades_label, 0, 1)
        summary_layout.addWidget(QLabel("Total Profit:"), 0, 2)
        summary_layout.addWidget(self.total_profit_label, 0, 3)
        summary_layout.addWidget(QLabel("Avg. Profit:"), 1, 0)
        summary_layout.addWidget(self.avg_profit_label, 1, 1)
        summary_layout.addWidget(QLabel("Win Rate:"), 1, 2)
        summary_layout.addWidget(self.win_rate_label, 1, 3)
        
        summary_group.setLayout(summary_layout)
        main_layout.addWidget(summary_group)
        
        # Top performers
        top_group = QGroupBox("Top Performing Pairs")
        top_layout = QVBoxLayout()
        
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(5)
        self.top_table.setHorizontalHeaderLabels([
            "Symbol", "Total Profit", "Trades", "Avg. Profit", "Max Profit"
        ])
        self.top_table.horizontalHeader().setStretchLastSection(True)
        self.top_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.top_table.verticalHeader().setVisible(False)
        
        top_layout.addWidget(self.top_table)
        top_group.setLayout(top_layout)
        main_layout.addWidget(top_group)
        
        # Daily stats
        daily_group = QGroupBox("Daily Performance")
        daily_layout = QVBoxLayout()
        
        self.daily_table = QTableWidget()
        self.daily_table.setColumnCount(5)
        self.daily_table.setHorizontalHeaderLabels([
            "Date", "Profit", "Trades", "Orders", "Avg. Profit"
        ])
        self.daily_table.horizontalHeader().setStretchLastSection(True)
        self.daily_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.daily_table.verticalHeader().setVisible(False)
        
        daily_layout.addWidget(self.daily_table)
        daily_group.setLayout(daily_layout)
        main_layout.addWidget(daily_group)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_data)
        self.refresh_button = QPushButton("Refresh Stats")
        self.refresh_button.clicked.connect(self.update_stats)
        
        controls_layout.addWidget(self.export_button)
        controls_layout.addWidget(self.refresh_button)
        main_layout.addLayout(controls_layout)
        
        self.setLayout(main_layout)
        
        # Initialize stats
        self.update_stats()
    
    def update_stats(self):
        """Update all statistics displays"""
        try:
            # Get all trades
            trades = self.storage.get_trades(limit=1000)
            
            # Calculate overall stats
            total_trades = len(trades)
            profitable_trades = sum(1 for trade in trades if trade.get('profit', 0) > 0)
            
            if total_trades > 0:
                win_rate = (profitable_trades / total_trades) * 100
            else:
                win_rate = 0.0
            
            # Get profit stats
            profit_stats = self.storage.get_profit_stats()
            total_profit = sum(stats.get('total_profit', 0) for stats in profit_stats.values())
            
            if total_trades > 0:
                avg_profit = total_profit / total_trades
            else:
                avg_profit = 0.0
            
            # Update summary labels
            self.total_trades_label.setText(str(total_trades))
            self.total_profit_label.setText(f"{total_profit:.2f}%")
            self.avg_profit_label.setText(f"{avg_profit:.2f}%")
            self.win_rate_label.setText(f"{win_rate:.1f}%")
            
            # Update top performers
            symbol_performance = self.storage.get_symbol_performance(top_n=10)
            self.top_table.setRowCount(len(symbol_performance))
            
            for row, (symbol, stats) in enumerate(symbol_performance.items()):
                self.top_table.setItem(row, 0, QTableWidgetItem(symbol))
                self.top_table.setItem(row, 1, QTableWidgetItem(f"{stats.get('total_profit', 0):.2f}%"))
                self.top_table.setItem(row, 2, QTableWidgetItem(str(stats.get('num_trades',        self.control_panel.start_signal.connect(self.start_scanner)
        self.control_panel.stop_signal.connect(self.stop_scanner)
        self.control_panel.settings_signal.connect(self.apply_settings)
        
        control_tab.setLayout(control_layout)
        tabs.addTab(control_tab, "Controls")
        
        # Add tabs to splitter
        splitter.addWidget(tabs)
        
        # Set splitter sizes
        splitter.setSizes([400, 400])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Set layout
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Create menu and toolbar
        self.create_menu()
        self.create_toolbar()
    
    def create_menu(self):
        """Create menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        
        line_chart_action = QAction("Line Chart", self)
        line_chart_action.triggered.connect(self.chart.show_price_chart)
        view_menu.addAction(line_chart_action)
        
        candle_chart_action = QAction("Candlestick Chart", self)
        candle_chart_action.triggered.connect(self.chart.show_candlestick_chart)
        view_menu.addAction(candle_chart_action)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        # Start action
        start_action = QAction("Start Scanner", self)
        start_action.triggered.connect(self.start_scanner)
        toolbar.addAction(start_action)
        
        # Stop action
        stop_action = QAction("Stop Scanner", self)
        stop_action.triggered.connect(self.stop_scanner)
        toolbar.addAction(stop_action)
        
        # Separator
        toolbar.addSeparator()
        
        # Chart type actions
        line_chart_action = QAction("Line Chart", self)
        line_chart_action.triggered.connect(self.chart.show_price_chart)
        toolbar.addAction(line_chart_action)
        
        candle_chart_action = QAction("Candlestick Chart", self)
        candle_chart_action.triggered.connect(self.chart.show_candlestick_chart)
        toolbar.addAction(candle_chart_action)
    
    def update_data(self):
        """Update data in tables and charts"""
        if not self.is_running:
            return
            
        try:
            # Update volatility table
            volatile_pairs = self.scanner.scan_market()
            self.volatility_table.update_data(volatile_pairs)
            
            # Update orders table
            self.orders_table.update_data(self.order_manager.active_orders)
            
            # Update trade history table
            trades = self.storage.get_trades(limit=100)
            self.history_table.update_data(trades)
            
            # Update alerts panel
            self.alerts_panel.update_alerts()
            
            # Save volatility data for stats
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
            self.statusBar().showMessage(f"Last update: {time.strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.logger.error(f"Error updating data: {str(e)}")
            self.statusBar().showMessage(f"Error: {str(e)}")
    
    def start_scanner(self):
        """Start scanner"""
        self.is_running = True
        self.statusBar().showMessage("Scanner running")
        self.control_panel.start_button.setEnabled(False)
        self.control_panel.stop_button.setEnabled(True)
    
    def stop_scanner(self):
        """Stop scanner"""
        self.is_running = False
        self.statusBar().showMessage("Scanner stopped")
        self.control_panel.start_button.setEnabled(True)
        self.control_panel.stop_button.setEnabled(False)
    
    def apply_settings(self, new_settings):
        """Apply new settings"""
        # Update scanner settings
        self.scanner.min_volatility = new_settings['scanner']['min_volatility']
        self.scanner.window_size = new_settings['scanner']['window_size']
        
        # Update order manager settings
        self.order_manager.discount_percentage = new_settings['order']['discount_percentage']
        
        # Update other settings
        self.settings.update(new_settings)
        
        # Save settings to storage
        self.storage.save_setting('scanner', new_settings['scanner'])
        self.storage.save_setting('order', new_settings['order'])
        self.storage.save_setting('exchange', new_settings['exchange'])
        
        self.statusBar().showMessage("Settings applied")
    
    def on_order_filled(self, data):
        """Handle order filled alert"""
        # Refresh chart and data
        self.update_data()
        
        # Highlight the order in the table
        order_id = data.get('order_id')
        if order_id:
            # Find order in table
            for row in range(self.orders_table.rowCount()):
                if self.orders_table.item(row, 0).text() == order_id:
                    # Highlight row
                    for col in range(self.orders_table.columnCount()):
                        item = self.orders_table.item(row, col)
                        item.setBackground(Qt.green)
    
    def on_high_volatility(self, data):
        """Handle high volatility alert"""
        # Switch to volatility tab
        tabs = self.findChild(QTabWidget)
        if tabs:
            tabs.setCurrentIndex(0)  # Volatility tab
        
        # Refresh data
        self.update_data()            # Format timestamp
            timestamp = item.get('timestamp', 0)
            dt = QDateTime.fromMSecsSinceEpoch(timestamp)
            time_str = dt.toString('yyyy-MM-dd hh:mm:ss')
            self.setItem(row, 4, QTableWidgetItem(time_str))

class OrdersTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "ID", "Symbol", "Type", "Amount", "Price", "Status", "Time"
        ])
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
    
    def update_data(self, data):
        """Update table with orders data"""
        self.setRowCount(len(data))
        
        for row, (order_id, item) in enumerate(data.items()):
            self.setItem(row, 0, QTableWidgetItem(order_id))
            self.setItem(row, 1, QTableWidgetItem(item.get('symbol', '')))
            self.setItem(row, 2, QTableWidgetItem(item.get('type', '')))
            self.setItem(row, 3, QTableWidgetItem(f"{item.get('amount', 0):.8f}"))
            self.setItem(row, 4, QTableWidgetItem(f"{item.get('price', 0):.8f}"))
            self.setItem(row, 5, QTableWidgetItem(item.get('status', '')))
            
            # Format timestamp
            timestamp = item.get('timestamp', 0)
            dt = QDateTime.fromSecsSinceEpoch(int(timestamp))
            time_str = dt.toString('yyyy-MM-dd hh:mm:ss')
            self.setItem(row, 6, QTableWidgetItem(time_str))

class TradeHistoryTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "Order ID", "Symbol", "Side", "Amount", "Price", "Timestamp", "Profit"
        ])
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
    
    def update_data(self, data):
        """Update table with trade history data"""
        self.setRowCount(len(data))
        
        for row, item in enumerate(data):
            self.setItem(row, 0, QTableWidgetItem(item.get('order_id', '')))
            self.setItem(row, 1, QTableWidgetItem(item.get('symbol', '')))
            self.setItem(row, 2, QTableWidgetItem(item.get('side', '')))
            self.setItem(row, 3, QTableWidgetItem(f"{item.get('amount', 0):.8f}"))
            self.setItem(row, 4, QTableWidgetItem(f"{item.get('price', 0):.8f}"))
            
            # Format timestamp
            timestamp = item.get('timestamp', 0)
            dt = QDateTime.fromSecsSinceEpoch(int(timestamp / 1000))
            time_str = dt.toString('yyyy-MM-dd hh:mm:ss')
            self.setItem(row, 5, QTableWidgetItem(time_str))
            
            # Format profit
            profit = item.get('profit')
            if profit is not None:
                self.setItem(row, 6, QTableWidgetItem(f"{profit:.2f}%"))
            else:
                self.setItem(row, 6, QTableWidgetItem(""))

class ControlPanel(QWidget):
    start_signal = pyqtSignal()
    stop_signal = pyqtSignal()
    settings_signal = pyqtSignal(dict)
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Scanner")
        self.stop_button = QPushButton("Stop Scanner")
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        # Settings
        settings_layout = QVBoxLayout()
        
        # Scanner settings
        scanner_layout = QHBoxLayout()
        scanner_layout.addWidget(QLabel("Min Volatility:"))
        self.volatility_spin = QDoubleSpinBox()
        self.volatility_spin.setRange(0.1, 100.0)
        self.volatility_spin.setValue(settings['scanner'].get('min_volatility', 5.0))
        scanner_layout.addWidget(self.volatility_spin)
        
        scanner_layout.addWidget(QLabel("Window Size:"))
        self.window_spin = QSpinBox()
        self.window_spin.setRange(1, 1440)
        self.window_spin.setValue(settings['scanner'].get('window_size', 60))
        scanner_layout.addWidget(self.window_spin)
        
        settings_layout.addLayout(scanner_layout)
        
        # Order settings
        order_layout = QHBoxLayout()
        order_layout.addWidget(QLabel("Discount %:"))
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(1.0, 50.0)
        self.discount_spin.setValue(settings['order'].get('discount_percentage', 15.0))
        order_layout.addWidget(self.discount_spin)
        
        order_layout.addWidget(QLabel("Max Position:"))
        self.max_position_spin = QDoubleSpinBox()
        self.max_position_spin.setRange(10.0, 10000.0)
        self.max_position_spin.setValue(settings['order'].get('max_position_size', 100.0))
        order_layout.addWidget(self.max_position_spin)
        
        settings_layout.addLayout(order_layout)
        
        # Exchange settings
        exchange_layout = QHBoxLayout()
        exchange_layout.addWidget(QLabel("Exchange:"))
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems(["binance", "kraken", "coinbase"])
        exchange_layout.addWidget(self.exchange_combo)
        
        exchange_layout.addWidget(QLabel("Sandbox:"))
        self.sandbox_check = QCheckBox()
        self.sandbox_check.setChecked(True)
        exchange_layout.addWidget(self.sandbox_check)
        
        settings_layout.addLayout(exchange_layout)
        
        # Apply settings button
        self.apply_button = QPushButton("Apply Settings")
        settings_layout.addWidget(self.apply_button)
        
        layout.addLayout(settings_layout)
        self.setLayout(layout)
        
        # Connect signals
        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)
        self.apply_button.clicked.connect(self.on_apply_settings)
    
    def on_start(self):
        """Handle start button click"""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.start_signal.emit()
        self.logger.info("Scanner started")
    
    def on_stop(self):
        """Handle stop button click"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stop_signal.emit()
        self.logger.info("Scanner stopped")
    
    def on_apply_settings(self):
        """Apply settings"""
        settings = {
            'scanner': {
                'min_volatility': self.volatility_spin.value(),
                'window_size': self.window_spin.value(),
            },
            'order': {
                'discount_percentage': self.discount_spin.value(),
                'max_position_size': self.max_position_spin.value(),
            },
            'exchange': {
                'name': self.exchange_combo.currentText(),
                'sandbox': self.sandbox_check.isChecked(),
            }
        }
        
        self.settings_signal.emit(settings)
        self.logger.info("Settings applied")

class AlertsPanel(QWidget):
    def __init__(self, alert_manager, parent=None):
        super().__init__(parent)
        self.alert_manager = alert_manager
        
        # Initialize layout
        layout = QVBoxLayout()
        
        # Alerts list
        self.alerts_text = QTextEdit()
        self.alerts_text.setReadOnly(True)
        layout.addWidget(self.alerts_text)
        
        # Control panel
        control_layout = QHBoxLayout()
        self.clear_button = QPushButton("Clear Alerts")
        self.clear_button.clicked.connect(self.clear_alerts)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("All Alerts")
        self.filter_combo.addItem("Order Placed")
        self.filter_combo.addItem("Order Filled")
        self.filter_combo.addItem("High Volatility")
        self.filter_combo.addItem("Errors")
        self.filter_combo.currentTextChanged.connect(self.filter_alerts)
        
        control_layout.addWidget(QLabel("Filter:"))
        control_layout.addWidget(self.filter_combo)
        control_layout.addWidget(self.clear_button)
        layout.addLayout(control_layout)
        
        self.setLayout(layout)
        
        # Initialize with current alerts
        self.update_alerts()
    
    def update_alerts(self):
        """Update alerts panel with latest alerts"""
        filter_text = self.filter_combo.currentText()
        
        if filter_text == "All Alerts":
            alerts = self.alert_manager.get_recent_alerts(20)
        elif filter_text == "Order Placed":
            alerts = self.alert_manager.get_recent_alerts(20, "order_placed")
        elif filter_text == "Order Filled":
            alerts = self.alert_manager.get_recent_alerts(20, "order_filled")
        elif filter_text == "High Volatility":
            alerts = self.alert_manager.get_recent_alerts(20, "high_volatility")
        elif filter_text == "Errors":
            alerts = self.alert_manager.get_recent_alerts(20, "error")
        else:
            alerts = self.alert_manager.get_recent_alerts(20)
        
        # Format alerts
        text = ""
        for alert in alerts:
            # Format timestamp
            timestamp = alert.get('timestamp', 0)
            dt = QDateTime.fromSecsSinceEpoch(int(timestamp))
            time_str = dt.toString('yyyy-MM-dd hh:mm:ss')
            
            # Get alert type and data
            alert_type = alert.get('type', '').replace('_', ' ').title()
            data = alert.get('data', {})
            
            # Format message
            message = self.alert_manager._format_alert_message(alert.get('type', ''), data)
            
            # Add to text
            text += f"[{time_str}] {alert_type}: {message}\n\n"
        
        self.alerts_text.setText(text)
    
    def clear_alerts(self):
        """Clear alerts text"""
        self.alerts_text.clear()
    
    def filter_alerts(self, filter_text):
        """Filter alerts by type"""
        self.update_alerts()

class Dashboard(QMainWindow):
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
        self.setWindowTitle("OrderTools Trading Bot")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Create splitter for chart and data
        splitter = QSplitter(Qt.Vertical)
        
        # Add chart area
        chart_widget = QWidget()
        chart_layout = QVBoxLayout()
        
        self.chart = ChartWidget()
        chart_layout.addWidget(self.chart)
        
        chart_widget.setLayout(chart_layout)
        splitter.addWidget(chart_widget)
        
        # Create tabs for data
        tabs = QTabWidget()
        
        # Volatility tab
        volatility_tab = QWidget()
        volatility_layout = QVBoxLayout()
        
        self.volatility_table = VolatilityTable()
        volatility_layout.addWidget(self.volatility_table)
        
        volatility_tab.setLayout(volatility_layout)
        tabs.addTab(volatility_tab, "Volatility Scanner")
        
        # Orders tab
        orders_tab = QWidget()
        orders_layout = QVBoxLayout()
        
        self.orders_table = OrdersTable()
        orders_layout.addWidget(self.orders_table)
        
        orders_tab.setLayout(orders_layout)
        tabs.addTab(orders_tab, "Active Orders")
        
        # Trade history tab
        history_tab = QWidget()
        history_layout = QVBoxLayout()
        
        self.history_table = TradeHistoryTable()
        history_layout.addWidget(self.history_table)
        
        history_tab.setLayout(history_layout)
        tabs.addTab(history_tab, "Trade History")
        
        # Statistics tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout()
        
        self.stats_panel = StatsPanel(self.storage)
        stats_layout.addWidget(self.stats_panel)
        
        stats_tab.setLayout(stats_layout)
        tabs.addTab(stats_tab, "Statistics")
        
        # Alerts tab
        alerts_tab = QWidget()
        alerts_layout = QVBoxLayout()
        
        self.alerts_panel = AlertsPanel(self.alert_manager)
        alerts_layout.addWidget(self.alerts_panel)
        
        alerts_tab.setLayout(alerts_layout)
        tabs.addTab(alerts_tab, "Alerts")
        
        # Control tab
        control_tab = QWidget()
        control_layout = QVBoxLayout()
        
        self.control_panel = ControlPanel(self.settings)
        control_layout.addWidget(self.control_panel)
        
        # Connect signals
        self.control_panel.start_signalfrom PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QTabWidget,
    QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QGridLayout,
    QGroupBox, QStatusBar, QAction, QToolBar, QTextEdit, QSplitter,
    QTableView, QHeaderView, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSortFilterProxyModel, QDateTime
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
import logging
import time
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
from .charts import ChartWidget

class VolatilityTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Symbol", "Volatility", "Price", "Volume", "Time"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)
    
    def update_data(self, data):
        """Update table with new data"""
        self.setRowCount(len(data))
        
        for row, item in enumerate(data):
            self.setItem(row, 0, QTableWidgetItem(item['symbol']))
            self.setItem(row, 1, QTableWidgetItem(f"{item['volatility']:.2f}%"))
            self.setItem(row, 2, QTableWidgetItem(f"{item['last_price']:.8f}"))
            self.setItem(row, 3, QTableWidgetItem(f"{item['volume']:.2f}"))
            
            # Format timestamp
            timestamp = item.get('timestamp', 0)
            dt = QDateTime.fromMSecsSinceEpoch(timestamp)
            time_str = dt.toString('yyyy-MM-dd hh:mm:ss')