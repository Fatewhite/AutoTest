"""
TXT转EXCEL插件
作者: CEM
版本: 1.0.0
功能: 提供TXT文件转EXCEL文件的功能
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import sys
import re
import json
import os
import pandas as pd
from datetime import datetime
from collections import deque


class TxtToExcelPlugin(BasePlugin):
    """TXT转EXCEL工具插件"""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.name = "TXT转EXCEL工具"
        self.version = "1.0.0"
        self.author = "CEM"
        self.description = "将TXT文件转换为EXCEL文件，支持自定义正则表达式匹配"
        #self.hotkey = "Ctrl+T"
        self.icon = "📊"

        self.dialog = None

    def initialize(self):
        """初始化插件"""
        print(f"插件 {self.name} 初始化")

        # 创建默认配置文件目录
        self.plugin_config_dir = os.path.join(os.path.dirname(__file__), "configs")
        os.makedirs(self.plugin_config_dir, exist_ok=True)

        # 插件配置文件
        self.config_file = os.path.join(self.plugin_config_dir, "txt_to_excel_config.json")

        # 默认正则表达式选项
        self.timestamp_regex_options = [
            (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3}', "默认: YYYY-MM-DD HH:MM:SS:mmm"),
            (r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', "YYYY/MM/DD HH:MM:SS"),
            (r'\d{8} \d{6}', "YYYYMMDD HHMMSS"),
            (r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}', "DD-MM-YYYY HH:MM:SS"),
            (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', "YYYY-MM-DDTHH:MM:SS"),
        ]

        self.param_value_regex_options = [
            (r'\*\*(\w+(?:\([^)]+\))?)\s*:\s*([^\s*]+)', "默认: **参数名: 值"),
            (r'([a-z,A-Z]+(?:\([^\)]\))?)\s*:\s*(-?\d)+\s*', "参数名: 值 (仅数字)"),
            (r'(\w+)\s*[:=]\s*([^\s]+)', "参数名:值 或 参数名=值"),
            (r'\[(\w+)\]\s*:\s*([^\s]+)', "[参数名]: 值"),
            (r'(\w+)\s*->\s*([^\s]+)', "参数名 -> 值"),
            (r'(\w+)\s+=\s+([^\s]+)', "参数名 = 值"),
        ]

        # 加载配置
        self.load_config()

    def load_config(self):
        """加载插件配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    return self.config
        except Exception as e:
            print(f"加载插件配置失败: {e}")
        return {}

    def save_config(self):
        """保存插件配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存插件配置失败: {e}")

    def on_enable(self):
        """插件启用"""
        print(f"插件 {self.name} 已启用")

        # 在主窗口日志中显示消息
        if hasattr(self.main_window, 'append_log_to_all'):
            self.main_window.append_log_to_all(f"插件 '{self.name}' 已启用", "blue")

    def on_disable(self):
        """插件禁用"""
        print(f"插件 {self.name} 已禁用")

        # 关闭对话框
        if self.dialog and self.dialog.isVisible():
            self.dialog.close()

        # 在主窗口日志中显示消息
        if hasattr(self.main_window, 'append_log_to_all'):
            self.main_window.append_log_to_all(f"插件 '{self.name}' 已禁用", "orange")

    def on_receive_data(self, data: str):
        """接收数据处理"""
        # 如果启用了自动检测TXT数据，可以在这里处理
        pass

    def on_send_data(self, data: str):
        """发送数据处理"""
        pass


    def create_ui(self):
        """创建插件UI"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 插件标题
        title_label = QLabel("📊 TXT转EXCEL工具")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 8px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 插件描述
        desc_label = QLabel(self.description)
        desc_label.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
            padding: 5px;
        """)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #bdc3c7;")
        layout.addWidget(line)

        # 功能说明
        features_label = QLabel("""
        <b>主要功能：</b>
        1. 支持自定义正则表达式匹配数据
        2. 支持多种时间戳格式
        3. 支持预览数据
        4. 自动检测文件编码
        5. 批量转换支持
        """)
        features_label.setStyleSheet("""
            font-size: 11px;
            color: #34495e;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 6px;
            border: 1px solid #dee2e6;
        """)
        features_label.setWordWrap(True)
        layout.addWidget(features_label)

        # 快速操作按钮
        quick_btn = QPushButton("🚀 打开TXT转EXCEL工具")
        quick_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c5a7a;
            }
        """)
        quick_btn.clicked.connect(self.open_txt_to_excel_tool)
        layout.addWidget(quick_btn)

        # 最近转换记录
        recent_group = QGroupBox("最近转换记录")
        recent_layout = QVBoxLayout(recent_group)

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(120)
        self.recent_list.itemDoubleClicked.connect(self.on_recent_item_double_clicked)
        recent_layout.addWidget(self.recent_list)

        layout.addWidget(recent_group)

        # 加载最近记录
        self.load_recent_records()

        # 添加占位空间
        layout.addStretch()

        return widget
        


    def get_menu_actions(self):
        """获取菜单动作"""
        actions = []

        # 打开TXT转EXCEL工具
        action = QAction("📊 打开TXT转EXCEL工具", self.main_window)
        #action.setShortcut(QKeySequence("Ctrl+T"))
        action.triggered.connect(self.open_txt_to_excel_tool)
        actions.append(action)

        # 打开转换记录
        action2 = QAction("📋 查看转换记录", self.main_window)
        action2.triggered.connect(self.show_conversion_history)
        actions.append(action2)

        # 批量转换
        action3 = QAction("🔧 批量转换工具", self.main_window)
        action3.triggered.connect(self.open_batch_conversion)
        actions.append(action3)

        return actions

    def open_txt_to_excel_tool(self):
        """打开TXT转EXCEL工具"""
        if not self.dialog:
            self.dialog = TxtToExcelDialog(self.main_window)

        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def open_batch_conversion(self):
        """打开批量转换工具"""
        QMessageBox.information(self.main_window, "批量转换",
                                "批量转换功能开发中...")

    def show_conversion_history(self):
        """显示转换历史"""
        QMessageBox.information(self.main_window, "转换历史",
                                "最近转换记录功能开发中...")

    def load_recent_records(self):
        """加载最近转换记录"""
        # 这里可以加载保存的转换记录
        self.recent_list.clear()

        # 示例记录
        records = [
            "data_log_20260203.txt → data_log_20260203.xlsx",
            "test_data.txt → test_data.xlsx",
            "sensor_log.txt → sensor_log.xlsx"
        ]

        for record in records:
            item = QListWidgetItem(record)
            self.recent_list.addItem(item)

    def on_recent_item_double_clicked(self, item):
        """最近记录项双击事件"""
        QMessageBox.information(self.main_window, "转换记录",
                                f"打开转换记录: {item.text()}")

    def cleanup(self):
        """清理插件资源"""
        print(f"插件 {self.name} 清理完成")

        # 关闭对话框
        if self.dialog:
            self.dialog.close()
            self.dialog = None

# ==================== TXT转EXCEL对话框 ====================
class TxtToExcelDialog(QDialog):
    """TXT转EXCEL转换对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_window()
        self.init_ui()
        self.setup_default_values()

    def setup_window(self):
        """窗口设置"""
        self.setWindowTitle("TXT转EXCEL工具")
        self.setMinimumSize(900, 650)

    def setup_default_values(self):
        """设置默认正则表达式选项"""
        # 时间戳正则表达式选项
        self.timestamp_regex_options = [
            (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3}', "默认: YYYY-MM-DD HH:MM:SS:mmm"),
            (r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', "YYYY/MM/DD HH:MM:SS"),
            (r'\d{8} \d{6}', "YYYYMMDD HHMMSS"),
            (r'\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}', "DD-MM-YYYY HH:MM:SS"),
            (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', "YYYY-MM-DDTHH:MM:SS"),
        ]

        # 参数与值正则表达式选项
        self.param_value_regex_options = [
            (r'\*\*(\w+(?:\([^)]+\))?)\s*:\s*([^\s*]+)', "默认: **参数名: 值"),
            (r'([a-z,A-Z]+(?:\([^\)]\))?)\s*:\s*(-?\d)+\s*', "参数名: 值 (仅数字)"),
            (r'(\w+)\s*[:=]\s*([^\s]+)', "参数名:值 或 参数名=值"),
            (r'\[(\w+)\]\s*:\s*([^\s]+)', "[参数名]: 值"),
            (r'(\w+)\s*->\s*([^\s]+)', "参数名 -> 值"),
            (r'(\w+)\s+=\s+([^\s]+)', "参数名 = 值"),
        ]

    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout(file_group)
        file_layout.setSpacing(8)

        # TXT文件选择
        txt_layout = QHBoxLayout()
        txt_layout.addWidget(QLabel("TXT文件:"))
        self.txt_path_edit = QLineEdit()
        self.txt_path_edit.setReadOnly(True)
        self.txt_path_edit.setPlaceholderText("请选择要转换的TXT文件...")
        txt_layout.addWidget(self.txt_path_edit, 1)

        self.browse_txt_btn = QPushButton("📂 浏览...")
        self.browse_txt_btn.clicked.connect(self.browse_txt_file)
        self.browse_txt_btn.setStyleSheet("padding: 6px 12px;")
        txt_layout.addWidget(self.browse_txt_btn)

        file_layout.addLayout(txt_layout)

        # EXCEL文件输出路径
        excel_layout = QHBoxLayout()
        excel_layout.addWidget(QLabel("EXCEL输出路径:"))
        self.excel_path_edit = QLineEdit()
        self.excel_path_edit.setPlaceholderText("自动生成输出路径或手动选择...")
        excel_layout.addWidget(self.excel_path_edit, 1)

        self.browse_excel_btn = QPushButton("📂 浏览...")
        self.browse_excel_btn.clicked.connect(self.browse_excel_file)
        self.browse_excel_btn.setStyleSheet("padding: 6px 12px;")
        excel_layout.addWidget(self.browse_excel_btn)

        file_layout.addLayout(excel_layout)

        main_layout.addWidget(file_group)

        # 转换选项区域
        options_group = QGroupBox("转换选项")
        options_layout = QFormLayout(options_group)
        options_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        options_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        options_layout.setLabelAlignment(Qt.AlignRight)
        options_layout.setSpacing(10)

        # 时间戳匹配正则表达式
        timestamp_widget = QWidget()
        timestamp_layout = QVBoxLayout(timestamp_widget)
        timestamp_layout.setContentsMargins(0, 0, 0, 0)
        timestamp_layout.setSpacing(5)

        # 时间戳正则表达式输入行
        timestamp_input_layout = QHBoxLayout()
        self.timestamp_regex_edit = QLineEdit()
        self.timestamp_regex_edit.setText(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3}')
        self.timestamp_regex_edit.setPlaceholderText("输入时间戳匹配正则表达式...")
        timestamp_input_layout.addWidget(self.timestamp_regex_edit, 1)

        # 时间戳正则表达式选择按钮
        self.timestamp_preset_btn = QPushButton("📋 预设")
        self.timestamp_preset_btn.setToolTip("选择预设的时间戳正则表达式")
        self.timestamp_preset_btn.setStyleSheet("padding: 6px 12px;")
        self.timestamp_preset_btn.clicked.connect(self.show_timestamp_preset_menu)
        timestamp_input_layout.addWidget(self.timestamp_preset_btn)

        timestamp_layout.addLayout(timestamp_input_layout)

        # 添加说明标签
        self.timestamp_hint_label = QLabel("默认匹配格式: YYYY-MM-DD HH:MM:SS:mmm")
        self.timestamp_hint_label.setStyleSheet("color: #6c757d; font-size: 11px; font-style: italic;")
        timestamp_layout.addWidget(self.timestamp_hint_label)

        options_layout.addRow("时间戳匹配正则表达式(python):", timestamp_widget)

        # 参数与值匹配正则表达式
        param_widget = QWidget()
        param_layout = QVBoxLayout(param_widget)
        param_layout.setContentsMargins(0, 0, 0, 0)
        param_layout.setSpacing(5)

        # 参数正则表达式输入行
        param_input_layout = QHBoxLayout()
        self.param_value_regex_edit = QLineEdit()
        self.param_value_regex_edit.setText(r'\*\*(\w+(?:\([^)]+\))?)\s*:\s*([^\s*]+)')
        self.param_value_regex_edit.setPlaceholderText("输入参数与值匹配正则表达式...")
        param_input_layout.addWidget(self.param_value_regex_edit, 1)

        # 参数正则表达式选择按钮
        self.param_preset_btn = QPushButton("📋 预设")
        self.param_preset_btn.setToolTip("选择预设的参数匹配正则表达式")
        self.param_preset_btn.setStyleSheet("padding: 6px 12px;")
        self.param_preset_btn.clicked.connect(self.show_param_preset_menu)
        param_input_layout.addWidget(self.param_preset_btn)

        param_layout.addLayout(param_input_layout)

        # 添加说明标签
        self.param_hint_label = QLabel("默认匹配格式: **参数名: 值")
        self.param_hint_label.setStyleSheet("color: #6c757d; font-size: 11px; font-style: italic;")
        param_layout.addWidget(self.param_hint_label)

        options_layout.addRow("参数与值匹配正则表达式(python):", param_widget)

        # 编码选择
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems([
            "自动检测",
            "UTF-8",
            "GB2312",
            "GBK",
            "GB18030",
            "ASCII",
            "ISO-8859-1",
            "Windows-1252"
        ])
        options_layout.addRow("文件编码:", self.encoding_combo)

        # 表头选项
        self.header_checkbox = QCheckBox("第一行作为表头")
        self.header_checkbox.setChecked(True)
        options_layout.addRow("表头选项:", self.header_checkbox)

        # 预览选项
        self.preview_checkbox = QCheckBox("转换前预览数据")
        self.preview_checkbox.setChecked(True)
        options_layout.addRow("预览选项:", self.preview_checkbox)

        main_layout.addWidget(options_group)

        # 预览区域
        preview_group = QGroupBox("数据预览")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setShowGrid(True)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        self.preview_table.setStyleSheet("""
            QTableWidget {
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 3px;
            }
        """)
        preview_layout.addWidget(self.preview_table)

        main_layout.addWidget(preview_group, 1)

        # 状态和按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; font-style: italic; padding: 6px;")
        button_layout.addWidget(self.status_label, 1)

        self.preview_btn = QPushButton("👁 预览数据")
        self.preview_btn.clicked.connect(self.preview_data)
        self.preview_btn.setEnabled(False)
        self.preview_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        button_layout.addWidget(self.preview_btn)

        self.convert_btn = QPushButton("🚀 开始转换")
        self.convert_btn.clicked.connect(self.convert_file)
        self.convert_btn.setEnabled(False)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 8px 24px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        button_layout.addWidget(self.convert_btn)

        self.close_btn = QPushButton("✕ 关闭")
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        button_layout.addWidget(self.close_btn)

        main_layout.addLayout(button_layout)

        # 设置正则表达式输入框的文本改变信号
        self.timestamp_regex_edit.textChanged.connect(self.on_timestamp_regex_changed)
        self.param_value_regex_edit.textChanged.connect(self.on_param_regex_changed)

    def show_timestamp_preset_menu(self):
        """显示时间戳正则表达式预设菜单"""
        menu = QMenu(self)

        for regex_pattern, description in self.timestamp_regex_options:
            action = menu.addAction(description)
            action.triggered.connect(lambda checked, pattern=regex_pattern, desc=description:
                                     self.select_timestamp_preset(pattern, desc))

        # 在按钮下方显示菜单
        menu.exec(self.timestamp_preset_btn.mapToGlobal(
            QPoint(0, self.timestamp_preset_btn.height())))

    def show_param_preset_menu(self):
        """显示参数正则表达式预设菜单"""
        menu = QMenu(self)

        for regex_pattern, description in self.param_value_regex_options:
            action = menu.addAction(description)
            action.triggered.connect(lambda checked, pattern=regex_pattern, desc=description:
                                     self.select_param_preset(pattern, desc))

        # 在按钮下方显示菜单
        menu.exec(self.param_preset_btn.mapToGlobal(
            QPoint(0, self.param_preset_btn.height())))

    def select_timestamp_preset(self, pattern: str, description: str):
        """选择时间戳预设"""
        self.timestamp_regex_edit.setText(pattern)
        self.timestamp_hint_label.setText(description)

    def select_param_preset(self, pattern: str, description: str):
        """选择参数预设"""
        self.param_value_regex_edit.setText(pattern)
        self.param_hint_label.setText(description)

    def on_timestamp_regex_changed(self, text: str):
        """时间戳正则表达式改变事件"""
        # 更新提示文本
        if not text.strip():
            self.timestamp_hint_label.setText("请输入时间戳正则表达式")
        else:
            self.timestamp_hint_label.setText(f"当前: {text[:50]}{'...' if len(text) > 50 else ''}")

    def on_param_regex_changed(self, text: str):
        """参数正则表达式改变事件"""
        # 更新提示文本
        if not text.strip():
            self.param_hint_label.setText("请输入参数正则表达式")
        else:
            self.param_hint_label.setText(f"当前: {text[:50]}{'...' if len(text) > 50 else ''}")

    def browse_txt_file(self):
        """浏览TXT文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择TXT文件", "",
            "文本文件 (*.txt);;所有文件 (*)"
        )

        if file_path:
            self.txt_path_edit.setText(file_path)

            # 自动生成EXCEL输出路径
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            dir_name = os.path.dirname(file_path)
            excel_path = os.path.join(dir_name, f"{base_name}.xlsx")
            self.excel_path_edit.setText(excel_path)

            self.preview_btn.setEnabled(True)
            self.convert_btn.setEnabled(True)
            self.status_label.setText("已选择文件，点击预览查看数据")

    def browse_excel_file(self):
        """浏览EXCEL输出文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存EXCEL文件", "",
            "Excel文件 (*.xlsx);;所有文件 (*)"
        )

        if file_path:
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            self.excel_path_edit.setText(file_path)

    def detect_encoding(self, file_path):
        """检测文件编码"""
        encodings_to_try = [
            'utf-8',
            'gb2312',
            'gbk',
            'gb18030',
            'ascii',
            'iso-8859-1',
            'windows-1252'
        ]

        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read(1024)  # 读取前1024个字符测试
                return encoding
            except UnicodeDecodeError:
                continue

        return 'utf-8'  # 默认使用UTF-8

    def get_timestamp_regex(self):
        """获取时间戳正则表达式"""
        regex_text = self.timestamp_regex_edit.text().strip()
        if regex_text:
            return regex_text
        return r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3}'  # 默认值

    def get_param_value_regex(self):
        """获取参数与值正则表达式"""
        regex_text = self.param_value_regex_edit.text().strip()
        if regex_text:
            return regex_text
        return r'\*\*(\w+(?:\([^)]+\))?)\s*:\s*([^\s*]+)'  # 默认值

    def get_encoding(self):
        """获取编码"""
        index = self.encoding_combo.currentIndex()

        if index == 0:  # 自动检测
            return self.detect_encoding(self.txt_path_edit.text())
        else:
            return self.encoding_combo.currentText()

    def preview_data(self):
        """预览数据"""
        txt_path = self.txt_path_edit.text()
        if not txt_path or not os.path.exists(txt_path):
            QMessageBox.warning(self, "警告", "请先选择有效的TXT文件")
            return

        try:
            # 获取编码
            encoding = self.get_encoding()

            # 读取文件前100行用于预览
            with open(txt_path, 'r', encoding=encoding) as f:
                lines = []
                for i in range(100):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line.strip())

            if not lines:
                QMessageBox.warning(self, "警告", "文件为空或读取失败")
                return

            # 获取正则表达式
            timestamp_regex = self.get_timestamp_regex()
            param_value_regex = self.get_param_value_regex()

            # 解析数据
            data = []
            column_names = set()  # 收集所有参数名作为列名
            column_names.add("时间戳")  # 添加时间戳列

            for line in lines:
                if not line.strip():
                    continue

                # 定义为字典
                row_data = {"时间戳": ""}

                # 提取时间戳
                timestamp_match = re.search(timestamp_regex, line)
                if timestamp_match:
                    row_data["时间戳"] = timestamp_match.group(0)

                # 提取参数与值
                param_matches = re.findall(param_value_regex, line)
                if param_matches:
                    for param_name, param_value in param_matches:
                        row_data[param_name] = param_value
                        column_names.add(param_name)

                # 如果没有匹配到参数，则将整行作为原始数据
                if not param_matches:
                    row_data["原始数据"] = line
                    column_names.add("原始数据")

                data.append(row_data)

            # 确定列顺序
            columns = ["时间戳"] + ([col for col in column_names if col != "时间戳" and col != "原始数据"]) + (
                ["原始数据"] if "原始数据" in column_names else [])

            # 显示预览
            self.preview_table.setRowCount(min(90, len(data)))
            self.preview_table.setColumnCount(len(columns))

            # 设置表头
            self.preview_table.setHorizontalHeaderLabels(columns)

            # 填充数据
            for i, row_data in enumerate(data[:90]):
                for j, column_name in enumerate(columns):
                    value = row_data.get(column_name, "")
                    self.preview_table.setItem(i, j, QTableWidgetItem(str(value)))

            # 调整列宽
            self.preview_table.resizeColumnsToContents()

            # 更新状态
            self.status_label.setText(f"预览完成：{len(data)}行，{len(columns)}列")

        except Exception as e:
            QMessageBox.critical(self, "预览错误", f"预览数据时发生错误：\n{str(e)}")

    def convert_file(self):
        """转换文件"""
        txt_path = self.txt_path_edit.text()
        excel_path = self.excel_path_edit.text()

        if not txt_path or not os.path.exists(txt_path):
            QMessageBox.warning(self, "警告", "请先选择有效的TXT文件")
            return

        if not excel_path:
            QMessageBox.warning(self, "警告", "请指定EXCEL输出路径")
            return

        # 如果预览选项开启且未预览，先预览
        if self.preview_checkbox.isChecked() and self.preview_table.rowCount() == 0:
            self.preview_data()

        try:
            # 获取编码和正则表达式
            encoding = self.get_encoding()
            timestamp_regex = self.get_timestamp_regex()
            param_value_regex = self.get_param_value_regex()

            self.status_label.setText("正在读取TXT文件...")
            QApplication.processEvents()

            # 读取完整文件
            with open(txt_path, 'r', encoding=encoding) as f:
                lines = f.readlines()

            if not lines:
                QMessageBox.warning(self, "警告", "文件为空")
                return

            self.status_label.setText("正在解析数据...")
            QApplication.processEvents()

            # 解析数据
            data = []
            column_names = set()  # 收集所有参数名作为列名
            column_names.add("时间戳")  # 添加时间戳列

            for line_num, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                row_data = {"时间戳": ""}

                # 提取时间戳
                timestamp_match = re.search(timestamp_regex, line)
                if timestamp_match:
                    row_data["时间戳"] = timestamp_match.group(0)

                # 提取参数与值
                param_matches = re.findall(param_value_regex, line)
                if param_matches:
                    for param_name, param_value in param_matches:
                        # 尝试将值转换为数值
                        try:
                            if '.' in param_value:
                                row_data[param_name] = float(param_value)
                            else:
                                row_data[param_name] = int(param_value)
                        except ValueError:
                            row_data[param_name] = param_value
                        column_names.add(param_name)

                # 如果没有匹配到参数，则将整行作为原始数据
                if not param_matches:
                    row_data["原始数据"] = line
                    column_names.add("原始数据")

                data.append(row_data)

            # 确定列顺序
            columns = ["时间戳"] + ([col for col in column_names if col != "时间戳" and col != "原始数据"]) + (
                ["原始数据"] if "原始数据" in column_names else [])

            self.status_label.setText("正在创建Excel文件...")
            QApplication.processEvents()

            # 创建DataFrame
            rows_list = []
            for row_data in data:
                row = {col: row_data.get(col, "") for col in columns}
                rows_list.append(row)

            df = pd.DataFrame(rows_list)

            # 保存到EXCEL
            with pd.ExcelWriter(f'{excel_path}', engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name=f'数据', index=False)
                workbook = writer.book
                worksheet = writer.sheets[f'数据']

                # 根据单元格内容自动调整列宽
                for i, col in enumerate(df.columns):
                    column_width = max(len(str(col)), df[col].astype(str).map(len).max())
                    worksheet.set_column(i, i, column_width + 2)  # 设置第 i 列宽度
                # 冻结第一行
                worksheet.freeze_panes(1, 0)

            self.status_label.setText("转换完成！")

            # 询问是否打开文件
            reply = QMessageBox.question(
                self, "转换成功",
                f"文件转换完成！\n\n"
                f"原始文件：{os.path.basename(txt_path)}\n"
                f"输出文件：{os.path.basename(excel_path)}\n\n"
                f"是否打开转换后的文件？",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                try:
                    if sys.platform == 'win32':
                        os.startfile(excel_path)
                    elif sys.platform == 'darwin':  # macOS
                        os.system(f'open "{excel_path}"')
                    else:  # Linux
                        os.system(f'xdg-open "{excel_path}"')
                except:
                    pass

        except Exception as e:
            QMessageBox.critical(self, "转换错误", f"转换文件时发生错误：\n{str(e)}")
            self.status_label.setText("转换失败")