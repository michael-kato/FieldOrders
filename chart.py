import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QCandlestickSeries, QCandlestickSet, QDateTimeAxis, QValueAxis
from PyQt5.QtCore import Qt, QDateTime, QPoint, QPointF, pyqtSlot
from PyQt5.QtGui import QPainter

class ChartWidget(QWidget):
    def __init__(self, parent=None):
        """
        Chart widget for displaying price and volatility data
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Initialize layout
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        # Initialize chart
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTitle("Price Chart")
        self.chart.legend().setVisible(True)
        
        # Initialize chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.layout.addWidget(self.chart_view)
        
        # Initialize axes
        self.time_axis = QDateTimeAxis()
        self.time_axis.setFormat("hh:mm:ss")
        self.time_axis.setTitleText("Time")
        
        self.price_axis = QValueAxis()
        self.price_axis.setTitleText("Price")
        
        self.chart.addAxis(self.time_axis, Qt.AlignBottom)
        self.chart.addAxis(self.price_axis, Qt.AlignLeft)
        
        # Initialize series
        self.price_series = QLineSeries()
        self.price_series.setName("Price")
        
        self.volatility_series = QLineSeries()
        self.volatility_series.setName("Volatility %")
        
        self.candle_series = QCandlestickSeries()
        self.candle_series.setName("OHLC")
        self.candle_series.setIncreasingColor(Qt.green)
        self.candle_series.setDecreasingColor(Qt.red)
        
        # Add initial series
        self.chart.addSeries(self.price_series)
        self.price_series.attachAxis(self.time_axis)
        self.price_series.attachAxis(self.price_axis)
    
    def set_chart_title(self, title: str) -> None:
        """Set chart title"""
        self.chart.setTitle(title)
    
    def update_price_data(self, timestamps: List[int], 
                         prices: List[float]) -> None:
        """
        Update price line chart
        
        Args:
            timestamps: List of Unix timestamps (ms)
            prices: List of prices
        """
        try:
            # Clear existing data
            self.price_series.clear()
            
            # Add data points
            for ts, price in zip(timestamps, prices):
                dt = QDateTime()
                dt.setSecsSinceEpoch(int(ts / 1000))  # Convert ms to s
                self.price_series.append(dt.toMSecsSinceEpoch(), price)
            
            # Adjust axes
            if prices:
                min_price = min(prices) * 0.99
                max_price = max(prices) * 1.01
                self.price_axis.setRange(min_price, max_price)
            
            if timestamps:
                min_dt = QDateTime()
                min_dt.setSecsSinceEpoch(int(min(timestamps) / 1000))
                
                max_dt = QDateTime()
                max_dt.setSecsSinceEpoch(int(max(timestamps) / 1000))
                
                self.time_axis.setRange(min_dt, max_dt)
            
        except Exception as e:
            self.logger.error(f"Error updating price data: {str(e)}")
    
    def update_candlestick_data(self, ohlc_data: List[Dict]) -> None:
        """
        Update candlestick chart
        
        Args:
            ohlc_data: List of dictionaries with timestamp, open, high, low, close
        """
        try:
            # Clear existing series
            self.chart.removeSeries(self.candle_series)
            self.candle_series = QCandlestickSeries()
            self.candle_series.setName("OHLC")
            self.candle_series.setIncreasingColor(Qt.green)
            self.candle_series.setDecreasingColor(Qt.red)
            
            # Add data
            timestamps = []
            lows = []
            highs = []
            
            for candle in ohlc_data:
                timestamp = candle['timestamp']
                dt = QDateTime()
                dt.setSecsSinceEpoch(int(timestamp / 1000))
                
                candle_set = QCandlestickSet(
                    candle['open'],
                    candle['high'],
                    candle['low'],
                    candle['close'],
                    dt.toMSecsSinceEpoch()
                )
                
                self.candle_series.append(candle_set)
                timestamps.append(timestamp)
                lows.append(candle['low'])
                highs.append(candle['high'])
            
            # Add series to chart
            self.chart.addSeries(self.candle_series)
            self.candle_series.attachAxis(self.time_axis)
            self.candle_series.attachAxis(self.price_axis)
            
            # Adjust axes
            if lows and highs:
                min_price = min(lows) * 0.99
                max_price = max(highs) * 1.01
                self.price_axis.setRange(min_price, max_price)
            
            if timestamps:
                min_dt = QDateTime()
                min_dt.setSecsSinceEpoch(int(min(timestamps) / 1000))
                
                max_dt = QDateTime()
                max_dt.setSecsSinceEpoch(int(max(timestamps) / 1000))
                
                self.time_axis.setRange(min_dt, max_dt)
            
        except Exception as e:
            self.logger.error(f"Error updating candlestick data: {str(e)}")
    
    def update_volatility_data(self, timestamps: List[int], 
                             volatility: List[float]) -> None:
        """
        Update volatility line chart
        
        Args:
            timestamps: List of Unix timestamps (ms)
            volatility: List of volatility percentages
        """
        try:
            # Clear existing volatility series
            if self.volatility_series in self.chart.series():
                self.chart.removeSeries(self.volatility_series)
            
            self.volatility_series = QLineSeries()
            self.volatility_series.setName("Volatility %")
            
            # Add data points
            for ts, vol in zip(timestamps, volatility):
                dt = QDateTime()
                dt.setSecsSinceEpoch(int(ts / 1000))
                self.volatility_series.append(dt.toMSecsSinceEpoch(), vol)
            
            # Add to chart
            self.chart.addSeries(self.volatility_series)
            self.volatility_series.attachAxis(self.time_axis)
            
            # Create secondary axis for volatility
            self.volatility_axis = QValueAxis()
            self.volatility_axis.setTitleText("Volatility %")
            
            if volatility:
                min_vol = min(volatility) * 0.9
                max_vol = max(volatility) * 1.1
                self.volatility_axis.setRange(min_vol, max_vol)
            
            self.chart.addAxis(self.volatility_axis, Qt.AlignRight)
            self.volatility_series.attachAxis(self.volatility_axis)
            
        except Exception as e:
            self.logger.error(f"Error updating volatility data: {str(e)}")
    
    def show_price_chart(self) -> None:
        """Show price line chart only"""
        # Remove other series
        if self.candle_series in self.chart.series():
            self.chart.removeSeries(self.candle_series)
        
        # Ensure price series is added
        if self.price_series not in self.chart.series():
            self.chart.addSeries(self.price_series)
            self.price_series.attachAxis(self.time_axis)
            self.price_series.attachAxis(self.price_axis)
    
    def show_candlestick_chart(self) -> None:
        """Show candlestick chart only"""
        # Remove price line series
        if self.price_series in self.chart.series():
            self.chart.removeSeries(self.price_series)
        
        # Ensure candle series is added
        if self.candle_series not in self.chart.series():
            self.chart.addSeries(self.candle_series)
            self.candle_series.attachAxis(self.time_axis)
            self.candle_series.attachAxis(self.price_axis)