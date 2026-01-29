# frontend-desktop/main.py
"""
Chemical Equipment Parameter Visualizer - Desktop Application

A PyQt5 desktop application that provides the same functionality
as the React web app, connected to the same Django backend.

Features:
- CSV file upload with drag-and-drop
- Data table with sorting
- Charts using Matplotlib
- Summary statistics display
- Upload history management
- PDF report generation
- User authentication
"""

import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QFileDialog, QTableWidget,
    QTableWidgetItem, QMessageBox, QLineEdit, QFormLayout, QDialog,
    QHeaderView, QGroupBox, QGridLayout, QScrollArea, QFrame,
    QSplitter, QProgressBar, QStatusBar, QMenuBar, QMenu, QAction,
    QComboBox, QSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QDragEnterEvent, QDropEvent

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from api_client import APIClient


# ====================== Worker Thread for API Calls ======================

class APIWorker(QThread):
    """
    Worker thread for making API calls without blocking the UI.
    
    Emits signals when operations complete or fail.
    """
    
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# ====================== Custom Widgets ======================

class DragDropArea(QFrame):
    """
    Custom widget for drag-and-drop file upload.
    
    Accepts CSV files dropped onto it and emits a signal
    with the file path.
    """
    
    file_dropped = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(200)
        self.setStyleSheet("""
            DragDropArea {
                border: 3px dashed #3498db;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
            DragDropArea:hover {
                background-color: #e3f2fd;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel("📁")
        icon_label.setFont(QFont("Arial", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        
        text_label = QLabel("Drag & Drop CSV file here\nor click to browse")
        text_label.setFont(QFont("Arial", 14))
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("color: #666;")
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                DragDropArea {
                    border: 3px dashed #2ecc71;
                    border-radius: 10px;
                    background-color: #e8f5e9;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            DragDropArea {
                border: 3px dashed #3498db;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("""
            DragDropArea {
                border: 3px dashed #3498db;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
        """)
        
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.endswith('.csv'):
                self.file_dropped.emit(file_path)
                return
        
        QMessageBox.warning(self, "Invalid File", "Please drop a CSV file.")
    
    def mousePressEvent(self, event):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.file_dropped.emit(file_path)


class StatCard(QFrame):
    """
    A styled card widget for displaying statistics.
    """
    
    def __init__(self, title: str, value: str, color: str = "#3498db", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            StatCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {color}, stop:1 {self._darken_color(color)});
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        self.setMinimumSize(150, 100)
        
        layout = QVBoxLayout(self)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        title_label.setAlignment(Qt.AlignCenter)
        
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.value_label.setStyleSheet("color: white;")
        self.value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
    
    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color for gradient effect"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darker = tuple(max(0, c - 30) for c in rgb)
        return f"#{darker[0]:02x}{darker[1]:02x}{darker[2]:02x}"
    
    def update_value(self, value: str):
        self.value_label.setText(value)


# ====================== Tab Widgets ======================

class UploadTab(QWidget):
    """
    Tab for uploading CSV files.
    
    Features:
    - Drag-and-drop file upload
    - File selection dialog
    - Upload progress indication
    - File info display
    """
    
    upload_complete = pyqtSignal(dict)
    
    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.selected_file: Optional[str] = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📤 Upload Equipment Data")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Upload a CSV file containing equipment parameters")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #666;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Drag and drop area
        self.drop_area = DragDropArea()
        self.drop_area.file_dropped.connect(self.on_file_selected)
        layout.addWidget(self.drop_area)
        
        layout.addSpacing(10)
        
        # Selected file info
        self.file_info_label = QLabel("")
        self.file_info_label.setFont(QFont("Arial", 11))
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.file_info_label.setStyleSheet("""
            background-color: #e8f5e9;
            padding: 10px;
            border-radius: 5px;
        """)
        self.file_info_label.hide()
        layout.addWidget(self.file_info_label)
        
        layout.addSpacing(10)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Upload button
        self.upload_btn = QPushButton("🚀 Upload & Analyze")
        self.upload_btn.setFont(QFont("Arial", 14))
        self.upload_btn.setMinimumHeight(50)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 30px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.upload_btn.setEnabled(False)
        self.upload_btn.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_btn)
        
        layout.addSpacing(20)
        
        # Instructions
        instructions = QGroupBox("Required CSV Format")
        instructions_layout = QVBoxLayout(instructions)
        format_label = QLabel("Equipment Name, Type, Flowrate, Pressure, Temperature")
        format_label.setFont(QFont("Courier New", 11))
        format_label.setStyleSheet("""
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
        """)
        instructions_layout.addWidget(format_label)
        layout.addWidget(instructions)
        
        layout.addStretch()
    
    def on_file_selected(self, file_path: str):
        """Handle file selection"""
        self.selected_file = file_path
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / 1024  # KB
        
        self.file_info_label.setText(f"📄 {file_name} ({file_size:.1f} KB)")
        self.file_info_label.show()
        self.upload_btn.setEnabled(True)
    
    def upload_file(self):
        """Upload the selected file"""
        if not self.selected_file:
            return
        
        self.upload_btn.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Create worker thread
        self.worker = APIWorker(self.api_client.upload_csv, self.selected_file)
        self.worker.finished.connect(self.on_upload_success)
        self.worker.error.connect(self.on_upload_error)
        self.worker.start()
    
    def on_upload_success(self, result: dict):
        """Handle successful upload"""
        self.progress_bar.hide()
        self.upload_btn.setEnabled(True)
        self.file_info_label.hide()
        self.selected_file = None
        
        QMessageBox.information(
            self,
            "Upload Successful",
            f"File uploaded and processed successfully!\n"
            f"Records: {result['dataset']['record_count']}"
        )
        
        self.upload_complete.emit(result['dataset'])
    
    def on_upload_error(self, error_msg: str):
        """Handle upload error"""
        self.progress_bar.hide()
        self.upload_btn.setEnabled(True)
        
        QMessageBox.critical(self, "Upload Failed", error_msg)


class SummaryTab(QWidget):
    """
    Tab for displaying dataset summary statistics.
    
    Shows:
    - Key metric cards
    - Statistics table
    - Type distribution
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_dataset: Optional[dict] = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        self.title = QLabel("📊 Dataset Summary")
        self.title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(self.title)
        
        # Stats cards grid
        cards_layout = QHBoxLayout()
        
        self.count_card = StatCard("Total Equipment", "0", "#3498db")
        self.flow_card = StatCard("Avg Flowrate", "0", "#2ecc71")
        self.pressure_card = StatCard("Avg Pressure", "0", "#f39c12")
        self.temp_card = StatCard("Avg Temperature", "0°", "#9b59b6")
        
        cards_layout.addWidget(self.count_card)
        cards_layout.addWidget(self.flow_card)
        cards_layout.addWidget(self.pressure_card)
        cards_layout.addWidget(self.temp_card)
        
        layout.addLayout(cards_layout)
        layout.addSpacing(20)
        
        # Statistics table
        stats_group = QGroupBox("📈 Parameter Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(5)
        self.stats_table.setHorizontalHeaderLabels([
            "Parameter", "Minimum", "Average", "Maximum", "Std Deviation"
        ])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.stats_table.setRowCount(3)
        self.stats_table.setMaximumHeight(150)
        stats_layout.addWidget(self.stats_table)
        
        layout.addWidget(stats_group)
        
        # Type distribution
        type_group = QGroupBox("🏭 Equipment Type Distribution")
        self.type_layout = QHBoxLayout(type_group)
        layout.addWidget(type_group)
        
        layout.addStretch()
    
    def update_data(self, dataset: dict):
        """Update display with new dataset"""
        self.current_dataset = dataset
        summary = dataset.get('summary_parsed', {})
        
        # Update title
        self.title.setText(f"📊 Dataset Summary: {dataset.get('name', 'Unknown')}")
        
        # Update cards
        self.count_card.update_value(str(summary.get('total_count', 0)))
        self.flow_card.update_value(str(summary.get('averages', {}).get('flowrate', 0)))
        self.pressure_card.update_value(str(summary.get('averages', {}).get('pressure', 0)))
        self.temp_card.update_value(f"{summary.get('averages', {}).get('temperature', 0)}°")
        
        # Update statistics table
        averages = summary.get('averages', {})
        minimums = summary.get('minimums', {})
        maximums = summary.get('maximums', {})
        std_devs = summary.get('std_deviations', {})
        
        params = ['flowrate', 'pressure', 'temperature']
        for i, param in enumerate(params):
            self.stats_table.setItem(i, 0, QTableWidgetItem(param.capitalize()))
            self.stats_table.setItem(i, 1, QTableWidgetItem(str(minimums.get(param, ''))))
            self.stats_table.setItem(i, 2, QTableWidgetItem(str(averages.get(param, ''))))
            self.stats_table.setItem(i, 3, QTableWidgetItem(str(maximums.get(param, ''))))
            self.stats_table.setItem(i, 4, QTableWidgetItem(str(std_devs.get(param, ''))))
        
        # Update type distribution
        # Clear existing items
        while self.type_layout.count():
            item = self.type_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        type_dist = summary.get('type_distribution', {})
        for eq_type, count in type_dist.items():
            type_widget = QLabel(f"{eq_type}: {count}")
            type_widget.setStyleSheet("""
                background-color: #ecf0f1;
                padding: 10px 20px;
                border-radius: 20px;
                font-weight: bold;
            """)
            self.type_layout.addWidget(type_widget)
        
        self.type_layout.addStretch()


class DataTableTab(QWidget):
    """
    Tab for displaying equipment data in a table.
    
    Features:
    - Sortable columns
    - Search/filter functionality
    - Colored type badges
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_data: List[dict] = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and search bar
        header_layout = QHBoxLayout()
        
        title = QLabel("📋 Equipment Data Table")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by name or type...")
        self.search_input.setMinimumWidth(300)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 15px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.textChanged.connect(self.filter_data)
        header_layout.addWidget(self.search_input)
        
        layout.addLayout(header_layout)
        layout.addSpacing(10)
        
        # Record count label
        self.count_label = QLabel("Showing 0 records")
        self.count_label.setStyleSheet("color: #666;")
        layout.addWidget(self.count_label)
        
        # Data table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        layout.addWidget(self.table)
    
    def update_data(self, data: List[dict]):
        """Update table with new data"""
        self.current_data = data
        self.display_data(data)
    
    def display_data(self, data: List[dict]):
        """Display data in the table"""
        self.table.setRowCount(len(data))
        self.count_label.setText(f"Showing {len(data)} of {len(self.current_data)} records")
        
        type_colors = {
            'Pump': '#3498db',
            'Compressor': '#e74c3c',
            'Valve': '#2ecc71',
            'HeatExchanger': '#f39c12',
            'Reactor': '#9b59b6',
            'Condenser': '#1abc9c'
        }
        
        for i, item in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(item.get('Equipment Name', ''))))
            
            type_item = QTableWidgetItem(str(item.get('Type', '')))
            color = type_colors.get(item.get('Type', ''), '#95a5a6')
            type_item.setBackground(QColor(color))
            type_item.setForeground(QColor('white'))
            self.table.setItem(i, 1, type_item)
            
            self.table.setItem(i, 2, QTableWidgetItem(str(item.get('Flowrate', ''))))
            self.table.setItem(i, 3, QTableWidgetItem(str(item.get('Pressure', ''))))
            self.table.setItem(i, 4, QTableWidgetItem(f"{item.get('Temperature', '')}°"))
    
    def filter_data(self, search_term: str):
        """Filter table data based on search term"""
        if not search_term:
            self.display_data(self.current_data)
            return
        
        term = search_term.lower()
        filtered = [
            item for item in self.current_data
            if term in str(item.get('Equipment Name', '')).lower()
            or term in str(item.get('Type', '')).lower()
        ]
        self.display_data(filtered)


class ChartsTab(QWidget):
    """
    Tab for displaying charts using Matplotlib.
    
    Includes:
    - Pie chart for type distribution
    - Bar chart for parameter averages
    - Line chart for trends
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📈 Data Visualization")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)
        
        # Scroll area for charts
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        charts_widget = QWidget()
        self.charts_layout = QVBoxLayout(charts_widget)
        
        # Create figure for charts
        self.figure = Figure(figsize=(12, 10), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        self.charts_layout.addWidget(self.toolbar)
        self.charts_layout.addWidget(self.canvas)
        
        scroll.setWidget(charts_widget)
        layout.addWidget(scroll)
    
    def update_data(self, dataset: dict):
        """Update charts with new data"""
        self.figure.clear()
        
        summary = dataset.get('summary_parsed', {})
        raw_data = dataset.get('raw_data_parsed', [])
        
        if not summary or not raw_data:
            return
        
        # Create 2x2 grid of subplots
        gs = self.figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # ===== Pie Chart - Type Distribution =====
        ax1 = self.figure.add_subplot(gs[0, 0])
        type_dist = summary.get('type_distribution', {})
        if type_dist:
            colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
            ax1.pie(
                type_dist.values(),
                labels=type_dist.keys(),
                autopct='%1.1f%%',
                colors=colors[:len(type_dist)],
                explode=[0.02] * len(type_dist)
            )
            ax1.set_title('Equipment Type Distribution', fontweight='bold')
        
        # ===== Bar Chart - Averages =====
        ax2 = self.figure.add_subplot(gs[0, 1])
        averages = summary.get('averages', {})
        params = ['Flowrate', 'Pressure', 'Temperature']
        values = [averages.get(p.lower(), 0) for p in params]
        colors = ['#3498db', '#e74c3c', '#f39c12']
        bars = ax2.bar(params, values, color=colors)
        ax2.set_title('Average Parameter Values', fontweight='bold')
        ax2.set_ylabel('Value')
        
        # Add value labels on bars
        for bar, val in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{val:.1f}', ha='center', va='bottom')
        
        # ===== Line Chart - Trends =====
        ax3 = self.figure.add_subplot(gs[1, :])
        if raw_data:
            names = [item['Equipment Name'] for item in raw_data]
            flowrates = [item['Flowrate'] for item in raw_data]
            pressures = [item['Pressure'] for item in raw_data]
            temps = [item['Temperature'] for item in raw_data]
            
            x = range(len(names))
            ax3.plot(x, flowrates, 'o-', label='Flowrate', color='#3498db', linewidth=2)
            ax3.plot(x, pressures, 's-', label='Pressure', color='#e74c3c', linewidth=2)
            ax3.plot(x, temps, '^-', label='Temperature', color='#f39c12', linewidth=2)
            
            ax3.set_xticks(x)
            ax3.set_xticklabels(names, rotation=45, ha='right')
            ax3.set_title('Parameter Trends Across Equipment', fontweight='bold')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()


# frontend-desktop/main.py (continued)

class HistoryTab(QWidget):
    """
    Tab for displaying upload history.
    
    Shows last 5 datasets with summary info.
    Allows selecting a dataset to view details.
    """
    
    dataset_selected = pyqtSignal(dict)
    
    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and refresh button
        header_layout = QHBoxLayout()
        
        title = QLabel("🕐 Upload History (Last 5 Datasets)")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_history)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        
        # History list
        self.history_list = QVBoxLayout()
        layout.addLayout(self.history_list)
        
        layout.addStretch()
    
    def load_history(self):
        """Load history from API"""
        # Clear existing items
        while self.history_list.count():
            item = self.history_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        try:
            datasets = self.api_client.get_history()
            
            if not datasets:
                no_data = QLabel("📭 No datasets uploaded yet.\nUpload a CSV file to get started!")
                no_data.setAlignment(Qt.AlignCenter)
                no_data.setStyleSheet("color: #666; font-size: 14px;")
                self.history_list.addWidget(no_data)
                return
            
            for dataset in datasets:
                item = self.create_history_item(dataset)
                self.history_list.addWidget(item)
                
        except Exception as e:
            error_label = QLabel(f"Error loading history: {str(e)}")
            error_label.setStyleSheet("color: #e74c3c;")
            self.history_list.addWidget(error_label)
    
    def create_history_item(self, dataset: dict) -> QFrame:
        """Create a history item widget"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 10px;
            }
            QFrame:hover {
                background-color: #e3f2fd;
                border: 2px solid #3498db;
            }
        """)
        frame.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(frame)
        
        # Info section
        info_layout = QVBoxLayout()
        
        name_label = QLabel(f"📄 {dataset.get('name', 'Unknown')}")
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addWidget(name_label)
        
        date_str = dataset.get('uploaded_at', '')
        if date_str:
            date_label = QLabel(f"Uploaded: {date_str[:19].replace('T', ' ')}")
            date_label.setStyleSheet("color: #666;")
            info_layout.addWidget(date_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Stats section
        summary = dataset.get('summary_parsed', {})
        
        records_label = QLabel(f"Records: {dataset.get('record_count', 0)}")
        records_label.setStyleSheet("background: #3498db; color: white; padding: 5px 15px; border-radius: 15px;")
        layout.addWidget(records_label)
        
        if summary:
            types_count = len(summary.get('type_distribution', {}))
            types_label = QLabel(f"Types: {types_count}")
            types_label.setStyleSheet("background: #2ecc71; color: white; padding: 5px 15px; border-radius: 15px;")
            layout.addWidget(types_label)
        
        # View button
        view_btn = QPushButton("👁️ View")
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        view_btn.clicked.connect(lambda: self.select_dataset(dataset.get('id')))
        layout.addWidget(view_btn)
        
        return frame
    
    def select_dataset(self, dataset_id: int):
        """Load and emit selected dataset"""
        try:
            full_dataset = self.api_client.get_dataset(dataset_id)
            self.dataset_selected.emit(full_dataset)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dataset: {str(e)}")


# ====================== Login Dialog ======================

class LoginDialog(QDialog):
    """
    Login/Register dialog window.
    """
    
    def __init__(self, api_client: APIClient, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("🔐 Login")
        self.setFixedSize(400, 350)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🔐 Login to Continue")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Form
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        
        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e74c3c;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("Login")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 30px;
                border: none;
                border-radius: 5px;
            }
        """)
        self.login_btn.clicked.connect(self.do_login)
        btn_layout.addWidget(self.login_btn)
        
        self.register_btn = QPushButton("Register")
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px 30px;
                border: none;
                border-radius: 5px;
            }
        """)
        self.register_btn.clicked.connect(self.do_register)
        btn_layout.addWidget(self.register_btn)
        
        layout.addLayout(btn_layout)
        
        # Skip button
        skip_btn = QPushButton("Skip (Continue as Guest)")
        skip_btn.setStyleSheet("color: #666; border: none;")
        skip_btn.clicked.connect(self.accept)
        layout.addWidget(skip_btn)
    
    def do_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            self.error_label.setText("Please fill in all fields")
            return
        
        try:
            result = self.api_client.login(username, password)
            self.user = result.get('user')
            self.accept()
        except Exception as e:
            self.error_label.setText(str(e))
    
    def do_register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            self.error_label.setText("Please fill in all fields")
            return
        
        try:
            result = self.api_client.register(username, password)
            self.user = result.get('user')
            self.accept()
        except Exception as e:
            self.error_label.setText(str(e))


# ====================== Main Window ======================

class MainWindow(QMainWindow):
    """
    Main application window.
    
    Contains:
    - Menu bar with actions
    - Tab widget with all tabs
    - Status bar
    """
    
    def __init__(self):
        super().__init__()
        self.api_client = APIClient()
        self.current_dataset: Optional[dict] = None
        self.user: Optional[dict] = None
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        self.setWindowTitle("⚗️ Chemical Equipment Visualizer")
        self.setMinimumSize(1200, 800)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QTabWidget::pane {
                border: none;
                background-color: white;
                border-radius: 10px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 12px 25px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #bdc3c7;
            }
        """)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.upload_tab = UploadTab(self.api_client)
        self.upload_tab.upload_complete.connect(self.on_upload_complete)
        
        self.summary_tab = SummaryTab()
        self.table_tab = DataTableTab()
        self.charts_tab = ChartsTab()
        
        self.history_tab = HistoryTab(self.api_client)
        self.history_tab.dataset_selected.connect(self.on_dataset_selected)
        
        # Add tabs
        self.tabs.addTab(self.upload_tab, "📤 Upload")
        self.tabs.addTab(self.summary_tab, "📊 Summary")
        self.tabs.addTab(self.table_tab, "📋 Data Table")
        self.tabs.addTab(self.charts_tab, "📈 Charts")
        self.tabs.addTab(self.history_tab, "🕐 History")
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        upload_action = QAction("Upload CSV", self)
        upload_action.setShortcut("Ctrl+O")
        upload_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        file_menu.addAction(upload_action)
        
        download_pdf_action = QAction("Download PDF Report", self)
        download_pdf_action.setShortcut("Ctrl+P")
        download_pdf_action.triggered.connect(self.download_pdf)
        file_menu.addAction(download_pdf_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        refresh_action = QAction("Refresh Data", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)
        
        # Account menu
        account_menu = menubar.addMenu("Account")
        
        login_action = QAction("Login", self)
        login_action.triggered.connect(self.show_login)
        account_menu.addAction(login_action)
        
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.do_logout)
        account_menu.addAction(logout_action)
    
    def load_initial_data(self):
        """Load latest dataset on startup"""
        try:
            dataset = self.api_client.get_latest_dataset()
            if dataset:
                self.on_dataset_selected(dataset)
            self.history_tab.load_history()
        except Exception:
            pass
    
    def on_upload_complete(self, dataset: dict):
        """Handle successful upload"""
        self.on_dataset_selected(dataset)
        self.tabs.setCurrentIndex(1)  # Switch to summary tab
        self.history_tab.load_history()
    
    def on_dataset_selected(self, dataset: dict):
        """Update all tabs with selected dataset"""
        self.current_dataset = dataset
        self.summary_tab.update_data(dataset)
        self.table_tab.update_data(dataset.get('raw_data_parsed', []))
        self.charts_tab.update_data(dataset)
        self.statusBar().showMessage(f"Loaded: {dataset.get('name', 'Unknown')}")
    
    def download_pdf(self):
        """Download PDF report for current dataset"""
        if not self.current_dataset:
            QMessageBox.warning(self, "No Data", "Please load a dataset first.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            f"report_{self.current_dataset.get('name', 'data')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            try:
                self.api_client.download_pdf(self.current_dataset['id'], file_path)
                QMessageBox.information(self, "Success", f"PDF saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to download PDF: {str(e)}")
    
    def refresh_data(self):
        """Refresh current data"""
        self.load_initial_data()
        self.statusBar().showMessage("Data refreshed")
    
    def show_login(self):
        """Show login dialog"""
        dialog = LoginDialog(self.api_client, self)
        if dialog.exec_() == QDialog.Accepted and dialog.user:
            self.user = dialog.user
            self.statusBar().showMessage(f"Logged in as: {self.user.get('username')}")
    
    def do_logout(self):
        """Logout user"""
        self.api_client.logout()
        self.user = None
        self.statusBar().showMessage("Logged out")


# ====================== Application Entry Point ======================

def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    
    # Set application info
    app.setApplicationName("Chemical Equipment Visualizer")
    app.setOrganizationName("ChemViz")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()