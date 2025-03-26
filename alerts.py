import logging
import time
from typing import Dict, List, Callable, Any, Optional
import os
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal

class AlertEvent:
    ORDER_PLACED = "order_placed"
    ORDER_FILLED = "order_filled"
    SELL_ORDER_PLACED = "sell_order_placed"
    SELL_ORDER_FILLED = "sell_order_filled"
    HIGH_VOLATILITY = "high_volatility"
    ERROR = "error"

class AlertManager(QObject):
    alert_signal = pyqtSignal(str, dict)
    
    def __init__(self, enable_notifications: bool = True):
        """
        Alert manager for the trading bot
        
        Args:
            enable_notifications: Enable system notifications
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.enable_notifications = enable_notifications
        self.callbacks = {}
        self.alert_history = []
        
        # Connect signal
        self.alert_signal.connect(self.on_alert)
        
        # Setup tray icon if notifications enabled
        self.tray_icon = None
        if enable_notifications:
            pass#self.setup_tray_icon()
    
    def setup_tray_icon(self):
        """Setup system tray icon for notifications"""
        # This would typically use an actual icon file
        # For now we'll just create an empty icon
        # self.tray_icon = QSystemTrayIcon(QIcon("icons/ordertools.png"))
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setToolTip("OrderTools Trading Bot")
        
        # Create menu
        menu = QMenu()
        show_action = QAction("Show", menu)
        quit_action = QAction("Quit", menu)
        menu.addAction(show_action)
        menu.addAction(quit_action)
        self.tray_icon.setContextMenu(menu)
        
        # Show icon
        self.tray_icon.show()

    
    def register_callback(self, event_type: str, callback: Callable) -> bool:
        """
        Register callback for alert type
        
        Args:
            event_type: Event type (use AlertEvent constants)
            callback: Callback function that takes event data dict
            
        Returns:
            Success status
        """
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
            
        self.callbacks[event_type].append(callback)
        return True
    
    def trigger_alert(self, event_type: str, data: Dict) -> None:
        """
        Trigger alert
        
        Args:
            event_type: Event type
            data: Event data
        """
        # Emit signal (thread-safe)
        self.alert_signal.emit(event_type, data)
    
    def on_alert(self, event_type: str, data: Dict) -> None:
        """
        Handle alert (called from main thread via signal)
        
        Args:
            event_type: Event type
            data: Event data
        """
        # Log alert
        self.logger.info(f"Alert: {event_type} - {data}")
        
        # Add to history
        self.alert_history.append({
            'type': event_type,
            'data': data,
            'timestamp': time.time()
        })
        
        # Limit history size
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
        
        # Show notification if enabled
        if self.enable_notifications and self.tray_icon:
            title = f"OrderTools: {event_type.replace('_', ' ').title()}"
            message = self._format_alert_message(event_type, data)
            self.show_notification(title, message)
        
        # Call registered callbacks
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {str(e)}")
    
    def _format_alert_message(self, event_type: str, data: Dict) -> str:
        """Format alert message for notification"""
        if event_type == AlertEvent.ORDER_PLACED:
            return f"Buy field deployed for {data.get('symbol', 'unknown')} at {data.get('price', 0)}"
        elif event_type == AlertEvent.ORDER_FILLED:
            return f"Buy field activated for {data.get('symbol', 'unknown')} at {data.get('price', 0)}"
        elif event_type == AlertEvent.SELL_ORDER_PLACED:
            return f"Sell field deployed for {data.get('symbol', 'unknown')} at {data.get('price', 0)}"
        elif event_type == AlertEvent.SELL_ORDER_FILLED:
            return f"Sell field activated for {data.get('symbol', 'unknown')} at {data.get('price', 0)}"
        elif event_type == AlertEvent.HIGH_VOLATILITY:
            return f"High volatility detected for {data.get('symbol', 'unknown')}: {data.get('volatility', 0)}%"
        elif event_type == AlertEvent.ERROR:
            return f"Error: {data.get('message', 'Unknown error')}"
        else:
            return str(data)
            
    def show_notification(self, title: str, message: str) -> bool:
        """
        Show system notification
        
        Args:
            title: Notification title
            message: Notification message
            
        Returns:
            Success status
        """
        if not self.enable_notifications or not self.tray_icon:
            return False
            
        try:
            self.tray_icon.showMessage(title, message)
            return True
        except Exception as e:
            self.logger.error(f"Error showing notification: {str(e)}")
            return False
    
    def get_recent_alerts(self, limit: int = 10, 
                         event_type: Optional[str] = None) -> List[Dict]:
        """
        Get recent alerts
        
        Args:
            limit: Maximum number of alerts to return
            event_type: Filter by event type
            
        Returns:
            List of alert dictionaries
        """
        if event_type:
            filtered = [alert for alert in self.alert_history if alert['type'] == event_type]
            return filtered[-limit:]
        else:
            return self.alert_history[-limit:]