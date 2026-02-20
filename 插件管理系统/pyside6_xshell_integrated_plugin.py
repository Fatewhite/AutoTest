import sys
import re
import serial
import serial.tools.list_ports
import json
import os
import pandas as pd
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from PySide6.QtCore import QThread, Signal, Slot, Qt, QTimer, QSize, QPointF, QPoint, QObject
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit,
    QGroupBox, QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem, QCheckBox,
    QFrame, QGridLayout, QHeaderView, QProgressBar, QSplitter, QDialog,
    QScrollArea, QSizePolicy, QMenu, QInputDialog, QSpinBox, QRadioButton,
    QButtonGroup, QTabWidget, QFormLayout, QListWidget, QListWidgetItem, QColorDialog,
    QStackedWidget
)
from PySide6.QtGui import (
    QFont, QColor, QBrush, QTextCursor, QAction, QKeySequence, QIcon,
    QPainter, QPen, QPainterPath, QFontMetrics, QResizeEvent, QMouseEvent
)
import pyqtgraph as pg
from collections import deque
import importlib.util
import inspect
from pathlib import Path
import numpy as np


# ==================== 插件管理系统 ====================

@dataclass
class PluginInfo:
    """插件信息数据结构"""
    name: str
    version: str
    author: str
    description: str
    module_path: str
    enabled: bool = True
    #hotkey: str = ""
    icon: str = ""

class BasePlugin:
    """插件基类"""
    def __init__(self, main_window):
        self.main_window = main_window
        self.name = "未命名插件"
        self.version = "1.0.0"
        self.author = "未知作者"
        self.description = "无描述"
        #self.hotkey = ""
        self.icon = ""

    def initialize(self):
        """插件初始化"""
        pass

    def on_enable(self):
        """插件启用时调用"""
        pass

    def on_disable(self):
        """插件禁用时调用"""
        pass

    def on_receive_data(self, data: str):
        """接收到数据时调用"""
        pass

    def on_send_data(self, data: str):
        """发送数据时调用"""
        pass

    def create_ui(self):
        """创建插件UI"""
        return None

    def get_menu_actions(self):
        """获取菜单动作"""
        return []

    def cleanup(self):
        """清理插件资源"""
        pass

class PluginManager(QObject):
    """插件管理器"""

    plugin_loaded = Signal(str, str)  # 插件名, 状态
    plugin_error = Signal(str, str)  # 插件名, 错误信息

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.plugin_widgets: Dict[str, QWidget] = {}
        self.plugin_menu_actions: Dict[str, List[QAction]] = {}

        # 插件目录
        self.plugin_dir = Path("plugins")
        self.plugin_dir.mkdir(exist_ok=True)

        # 配置文件
        self.config_file = "plugins_config.json"
        self.load_config()

    def load_config(self):
        """加载插件配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 可以在这里加载插件启用状态等配置
                    return config
        except Exception as e:
            print(f"加载插件配置失败: {e}")
        return {}

    def save_config(self):
        """保存插件配置"""
        try:
            config = {
                'enabled_plugins': {
                    name: info.enabled
                    for name, info in self.plugin_info.items()
                }
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存插件配置失败: {e}")

    def discover_plugins(self):
        """发现插件"""
        plugin_files = []

        # 扫描插件目录
        if self.plugin_dir.exists():
            for file in self.plugin_dir.glob("*.py"):
                plugin_files.append(file)

        return plugin_files

    def load_plugin(self, plugin_path: Path) -> bool:
        """加载单个插件"""
        try:
            # 动态导入插件模块
            module_name = plugin_path.stem
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if spec is None:
                self.plugin_error.emit(plugin_path.name, "无法创建模块规范")
                return False

            module = importlib.util.module_from_spec(spec)

            from __main__ import SerialTool  # 导入主窗口类

            # 定义本地 BasePlugin 类（与主程序中相同的定义）
            class LocalBasePlugin:
                def __init__(self, main_window):
                    self.main_window = main_window
                    self.name = "未命名插件"
                    self.version = "1.0.0"
                    self.author = "未知作者"
                    self.description = "无描述"
                    #self.hotkey = ""
                    self.icon = ""

                def initialize(self):
                    pass

                def on_enable(self):
                    pass

                def on_disable(self):
                    pass

                def on_receive_data(self, data: str):
                    pass

                def on_send_data(self, data: str):
                    pass

                def create_ui(self):
                    return None

                def get_menu_actions(self):
                    return []

                def cleanup(self):
                    pass

            # 将 LocalBasePlugin 作为 BasePlugin 注入
            module.BasePlugin = LocalBasePlugin
            #module.BasePlugin = BasePlugin

            # 注入 Qt 核心模块
            module.Qt = Qt
            module.QThread = QThread
            module.Signal = Signal
            module.Slot = Slot

            # 注入 Qt Widgets
            module.QApplication = QApplication
            module.QWidget = QWidget
            module.QVBoxLayout = QVBoxLayout
            module.QHBoxLayout = QHBoxLayout
            module.QLabel = QLabel
            module.QPushButton = QPushButton
            module.QTextEdit = QTextEdit
            module.QLineEdit = QLineEdit
            module.QComboBox = QComboBox
            module.QTableWidget = QTableWidget
            module.QTableWidgetItem = QTableWidgetItem
            module.QHeaderView = QHeaderView
            module.QGroupBox = QGroupBox
            module.QMessageBox = QMessageBox
            module.QFileDialog = QFileDialog
            module.QCheckBox = QCheckBox
            module.QFrame = QFrame
            module.QGridLayout = QGridLayout
            module.QProgressBar = QProgressBar
            module.QSplitter = QSplitter
            module.QDialog = QDialog
            module.QScrollArea = QScrollArea
            module.QSizePolicy = QSizePolicy
            module.QMenu = QMenu
            module.QInputDialog = QInputDialog
            module.QSpinBox = QSpinBox
            module.QRadioButton = QRadioButton
            module.QButtonGroup = QButtonGroup
            module.QTabWidget = QTabWidget
            module.QFormLayout = QFormLayout
            module.QListWidget = QListWidget
            module.QListWidgetItem = QListWidgetItem
            module.QColorDialog = QColorDialog
            module.QStackedWidget = QStackedWidget

            # 注入 Qt Gui
            module.QFont = QFont
            module.QColor = QColor
            module.QBrush = QBrush
            module.QTextCursor = QTextCursor
            module.QAction = QAction
            module.QKeySequence = QKeySequence
            module.QIcon = QIcon
            module.QPainter = QPainter
            module.QPen = QPen
            module.QPainterPath = QPainterPath
            module.QFontMetrics = QFontMetrics
            module.QResizeEvent = QResizeEvent
            module.QMouseEvent = QMouseEvent

            # 注入其他常用模块
            module.sys = sys
            module.os = os
            module.json = json
            module.time = time
            module.datetime = datetime
            module.re = re

            # 执行模块代码
            spec.loader.exec_module(module)

            # 查找插件类
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                        hasattr(obj, '__bases__') and
                        LocalBasePlugin in obj.__bases__):
                    plugin_class = obj
                    break

            if plugin_class is None:
                self.plugin_error.emit(plugin_path.name, "未找到插件类")
                return False

            # 创建插件实例
            plugin_instance = plugin_class(self.main_window)

            # 验证插件基本信息
            if not plugin_instance.name or plugin_instance.name == "未命名插件":
                plugin_instance.name = module_name

            # 存储插件信息
            plugin_info = PluginInfo(
                name=plugin_instance.name,
                version=plugin_instance.version,
                author=plugin_instance.author,
                description=plugin_instance.description,
                module_path=str(plugin_path),
                enabled=True,
                #hotkey=plugin_instance.hotkey,
                icon=plugin_instance.icon
            )

            # 初始化插件
            plugin_instance.initialize()

            # 注册插件
            self.plugins[plugin_instance.name] = plugin_instance
            self.plugin_info[plugin_instance.name] = plugin_info

            # 创建插件UI
            widget = plugin_instance.create_ui()
            if widget:
                self.plugin_widgets[plugin_instance.name] = widget

            self.plugin_loaded.emit(plugin_instance.name, "加载成功")
            return True

        except Exception as e:
            error_msg = f"加载插件失败: {str(e)}"
            import traceback
            error_msg += f"\n详细错误:\n{traceback.format_exc()}"  # 添加详细错误信息
            self.plugin_error.emit(plugin_path.name, error_msg)
            return False

    def load_all_plugins(self):
        """加载所有插件"""
        plugin_files = self.discover_plugins()
        loaded_count = 0

        for plugin_file in plugin_files:
            if self.load_plugin(plugin_file):
                loaded_count += 1

        return loaded_count

    def enable_plugin(self, plugin_name: str):
        """启用插件"""
        if plugin_name in self.plugins and plugin_name in self.plugin_info:
            plugin = self.plugins[plugin_name]
            info = self.plugin_info[plugin_name]

            if not info.enabled:
                try:
                    plugin.on_enable()
                    info.enabled = True
                    self.save_config()
                    self.plugin_loaded.emit(plugin_name, "已启用")
                except Exception as e:
                    self.plugin_error.emit(plugin_name, f"启用失败: {str(e)}")

    def disable_plugin(self, plugin_name: str):
        """禁用插件"""
        if plugin_name in self.plugins and plugin_name in self.plugin_info:
            plugin = self.plugins[plugin_name]
            info = self.plugin_info[plugin_name]

            if info.enabled:
                try:
                    plugin.on_disable()
                    info.enabled = False
                    self.save_config()
                    self.plugin_loaded.emit(plugin_name, "已禁用")
                except Exception as e:
                    self.plugin_error.emit(plugin_name, f"禁用失败: {str(e)}")

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """获取插件实例"""
        return self.plugins.get(plugin_name)

    def get_plugin_widget(self, plugin_name: str) -> Optional[QWidget]:
        """获取插件UI组件"""
        return self.plugin_widgets.get(plugin_name)

    def broadcast_data_received(self, data: str):
        """广播接收到的数据给所有插件"""
        for plugin_name, plugin in self.plugins.items():
            if self.plugin_info[plugin_name].enabled:
                try:
                    plugin.on_receive_data(data)
                except Exception as e:
                    self.plugin_error.emit(plugin_name, f"处理接收数据失败: {str(e)}")

    def broadcast_data_sent(self, data: str):
        """广播发送的数据给所有插件"""
        for plugin_name, plugin in self.plugins.items():
            if self.plugin_info[plugin_name].enabled:
                try:
                    plugin.on_send_data(data)
                except Exception as e:
                    self.plugin_error.emit(plugin_name, f"处理发送数据失败: {str(e)}")

    def unload_plugin(self, plugin_name: str):
        """卸载插件"""
        if plugin_name in self.plugins:
            try:
                plugin = self.plugins[plugin_name]
                plugin.cleanup()

                # 清理UI组件
                if plugin_name in self.plugin_widgets:
                    widget = self.plugin_widgets[plugin_name]
                    widget.deleteLater()
                    del self.plugin_widgets[plugin_name]

                # 清理菜单动作
                if plugin_name in self.plugin_menu_actions:
                    del self.plugin_menu_actions[plugin_name]

                # 清理插件实例
                del self.plugins[plugin_name]
                del self.plugin_info[plugin_name]

                self.plugin_loaded.emit(plugin_name, "已卸载")

            except Exception as e:
                self.plugin_error.emit(plugin_name, f"卸载失败: {str(e)}")

    def cleanup(self):
        """清理所有插件"""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)

    def get_all_plugins_info(self) -> List[PluginInfo]:
        """获取所有插件信息"""
        return list(self.plugin_info.values())


# ==================== 插件管理对话框 ====================

# 主窗口插件管理UI设计
class PluginManagerDialog(QDialog):
    """插件管理对话框"""

    def __init__(self, plugin_manager: PluginManager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.setup_ui()
        self.load_plugins_list()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("插件管理")
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout(self)

        # 插件列表表格
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["插件名称", "版本", "作者", "描述", "状态", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)

        layout.addWidget(self.table)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.reload_btn = QPushButton("🔄 重新加载插件")
        self.reload_btn.clicked.connect(self.reload_plugins)

        self.open_dir_btn = QPushButton("📂 打开插件目录")
        self.open_dir_btn.clicked.connect(self.open_plugin_dir)

        self.create_plugin_btn = QPushButton("➕ 创建新插件")
        self.create_plugin_btn.clicked.connect(self.create_new_plugin)

        self.help_btn = QPushButton("❓ 插件开发帮助")
        self.help_btn.clicked.connect(self.show_help)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)

        button_layout.addWidget(self.reload_btn)
        button_layout.addWidget(self.open_dir_btn)
        button_layout.addWidget(self.create_plugin_btn)
        button_layout.addWidget(self.help_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

    def load_plugins_list(self):
        """加载插件列表"""
        self.table.setRowCount(0)

        plugins_info = self.plugin_manager.get_all_plugins_info()

        for info in plugins_info:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # 插件名称
            name_item = QTableWidgetItem(info.name)
            self.table.setItem(row, 0, name_item)

            # 版本
            version_item = QTableWidgetItem(info.version)
            self.table.setItem(row, 1, version_item)

            # 作者
            author_item = QTableWidgetItem(info.author)
            self.table.setItem(row, 2, author_item)

            # 描述
            desc_item = QTableWidgetItem(info.description)
            self.table.setItem(row, 3, desc_item)

            # 状态
            status_item = QTableWidgetItem("已启用" if info.enabled else "已禁用")
            status_item.setForeground(QColor("green" if info.enabled else "red"))
            self.table.setItem(row, 4, status_item)

            # 操作按钮
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.setContentsMargins(4, 2, 4, 2)

            enable_btn = QPushButton("启用" if not info.enabled else "禁用")
            enable_btn.setFixedWidth(60)
            enable_btn.clicked.connect(lambda checked, p=info.name: self.toggle_plugin(p))

            unload_btn = QPushButton("卸载")
            unload_btn.setFixedWidth(60)
            unload_btn.setStyleSheet("background-color: #dc3545; color: white;")
            unload_btn.clicked.connect(lambda checked, p=info.name: self.unload_plugin(p))

            config_btn = QPushButton("配置")
            config_btn.setFixedWidth(60)
            config_btn.clicked.connect(lambda checked, p=info.name: self.configure_plugin(p))

            button_layout.addWidget(enable_btn)
            button_layout.addWidget(unload_btn)
            button_layout.addWidget(config_btn)

            self.table.setCellWidget(row, 5, button_widget)

    def toggle_plugin(self, plugin_name: str):
        """切换插件启用状态"""
        info = self.plugin_manager.plugin_info.get(plugin_name)
        if info:
            if info.enabled:
                self.plugin_manager.disable_plugin(plugin_name)
            else:
                self.plugin_manager.enable_plugin(plugin_name)

            self.load_plugins_list()

    def unload_plugin(self, plugin_name: str):
        """卸载插件"""
        reply = QMessageBox.question(
            self, "确认卸载",
            f"确定要卸载插件 '{plugin_name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.plugin_manager.unload_plugin(plugin_name)
            self.load_plugins_list()

    def configure_plugin(self, plugin_name: str):
        """配置插件"""
        plugin = self.plugin_manager.get_plugin(plugin_name)
        if plugin:
            # 这里可以调用插件的配置对话框
            QMessageBox.information(
                self, "插件配置",
                f"插件 '{plugin_name}' 的配置功能\n\n"
                f"版本: {plugin.version}\n"
                f"作者: {plugin.author}\n"
                f"描述: {plugin.description}"
            )

    def reload_plugins(self):
        """重新加载所有插件"""
        # 先卸载所有插件
        for plugin_name in list(self.plugin_manager.plugins.keys()):
            self.plugin_manager.unload_plugin(plugin_name)

        # 重新加载
        loaded_count = self.plugin_manager.load_all_plugins()
        self.load_plugins_list()
        self.status_label.setText(f"已加载 {loaded_count} 个插件")

    def open_plugin_dir(self):
        """打开插件目录"""
        plugin_dir = self.plugin_manager.plugin_dir
        if not plugin_dir.exists():
            plugin_dir.mkdir(exist_ok=True)

        if sys.platform == "win32":
            os.startfile(str(plugin_dir))
        # elif sys.platform == "darwin":  # macOS
        #     os.system(f'open "{plugin_dir}"')
        # else:  # Linux
        #     os.system(f'xdg-open "{plugin_dir}"')

    def create_new_plugin(self):
        """创建新插件"""
        dialog = CreatePluginDialog(self)
        if dialog.exec():
            plugin_info = dialog.get_plugin_info()
            self.create_plugin_template(plugin_info)

    def create_plugin_template(self, plugin_info: dict):
        """创建插件模板文件"""
        plugin_name = plugin_info['name']
        plugin_file = self.plugin_manager.plugin_dir / f"{plugin_name}.py"

        template = f'''"""
{plugin_info['name']} - {plugin_info['description']}
作者: {plugin_info['author']}
版本: {plugin_info['version']}
"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class {plugin_info['name'].replace(' ', '').replace('-', '')}Plugin(BasePlugin):
    """{plugin_info['description']}"""

    def __init__(self, main_window):
        super().__init__(main_window)
        self.name = "{plugin_info['name']}"
        self.version = "{plugin_info['version']}"
        self.author = "{plugin_info['author']}"
        self.description = "{plugin_info['description']}"

    def initialize(self):
        """初始化插件"""
        print(f"插件 {{self.name}} 初始化")

    def on_enable(self):
        """插件启用"""
        print(f"插件 {{self.name}} 已启用")

    def on_disable(self):
        """插件禁用"""
        print(f"插件 {{self.name}} 已禁用")

    def on_receive_data(self, data: str):
        """接收数据处理"""
        # 在这里处理接收到的数据
        pass

    def on_send_data(self, data: str):
        """发送数据处理"""
        # 在这里处理发送的数据
        pass

    def create_ui(self):
        """创建插件UI"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("这是 {plugin_info['name']} 的UI界面"))
        return widget

    def get_menu_actions(self):
        """获取菜单动作"""
        actions = []

        # 示例：添加一个菜单动作
        action = QAction("插件动作", self.main_window)
        action.triggered.connect(self.on_plugin_action)
        actions.append(action)

        return actions

    def on_plugin_action(self):
        """插件动作处理"""
        QMessageBox.information(self.main_window, "插件动作", 
                               f"这是 {{self.name}} 插件的动作！")

    def cleanup(self):
        """清理插件资源"""
        print(f"插件 {{self.name}} 清理完成")
'''

        try:
            with open(plugin_file, 'w', encoding='utf-8') as f:
                f.write(template)

            self.status_label.setText(f"已创建插件模板: {plugin_file}")
            self.open_plugin_dir()

        except Exception as e:
            QMessageBox.critical(self, "创建失败", f"创建插件模板失败: {str(e)}")

    def show_help(self):
        """显示插件开发帮助"""
        help_text = """
        🚀 插件开发指南
        1. 插件放置在 'plugins' 目录下
        2. 每个插件是一个单独的 .py 文件
        3. 插件类必须继承 BasePlugin
        4. 插件必须实现以下方法：
           - initialize(): 初始化插件
           - on_enable(): 插件启用时调用
           - on_disable(): 插件禁用时调用
           - on_receive_data(data): 处理接收的数据
           - on_send_data(data): 处理发送的数据
        示例插件模板：
        
        class MyPlugin(BasePlugin):
            def __init__(self, main_window):
                super().__init__(main_window)
                self.name = "我的插件"
                self.version = "1.0.0"
                self.author = "开发者"
                self.description = "插件描述"
                
                --------------------------by CEM
        """
        QMessageBox.information(self, "插件开发帮助", help_text)


# ==================== 创建插件对话框 ====================

class CreatePluginDialog(QDialog):
    """创建新插件对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("创建新插件")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：数据统计插件")
        form_layout.addRow("插件名称:", self.name_edit)

        self.version_edit = QLineEdit()
        self.version_edit.setText("1.0.0")
        form_layout.addRow("版本:", self.version_edit)

        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("您的名字")
        form_layout.addRow("作者:", self.author_edit)

        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.setPlaceholderText("插件功能描述")
        form_layout.addRow("描述:", self.desc_edit)

        layout.addLayout(form_layout)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)

        self.create_btn = QPushButton("创建")
        self.create_btn.setStyleSheet("background-color: #28a745; color: white;")
        self.create_btn.clicked.connect(self.accept)

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.create_btn)

        layout.addLayout(button_layout)

    def get_plugin_info(self) -> dict:
        """获取插件信息"""
        return {
            'name': self.name_edit.text().strip(),
            'version': self.version_edit.text().strip(),
            'author': self.author_edit.text().strip(),
            'description': self.desc_edit.toPlainText().strip()
        }

# ==================== 波形数据管理 ====================
class WaveformData:
    """波形数据管理器"""

    def __init__(self, max_points=1000):
        self.max_points = max_points
        self.data = {}  # 参数名 -> 数据队列
        self.timestamps = deque(maxlen=max_points)
        self.start_time = datetime.now()

    def add_data_point(self, param_name: str, value: float, timestamp: datetime = None):
        """添加数据点"""
        if timestamp is None:
            timestamp = datetime.now()

        # 转换为相对时间（秒）
        rel_time = (timestamp - self.start_time).total_seconds()

        # 添加时间戳
        self.timestamps.append(rel_time)

        # 添加参数数据
        if param_name not in self.data:
            self.data[param_name] = deque(maxlen=self.max_points)

        self.data[param_name].append(value)

        # 确保所有数据队列长度一致
        while len(self.timestamps) > len(self.data[param_name]):
            self.data[param_name].appendleft(None)

        # 截断时间戳队列
        while len(self.timestamps) > self.max_points:
            self.timestamps.popleft()

    def get_data(self, param_name: str):
        """获取参数数据"""
        if param_name in self.data:
            # 过滤掉None值
            valid_indices = [i for i, v in enumerate(self.data[param_name]) if v is not None]
            if valid_indices:
                times = [self.timestamps[i] for i in valid_indices]
                values = [self.data[param_name][i] for i in valid_indices]
                return times, values
        return [], []

    def get_all_params(self):
        """获取所有参数名"""
        return list(self.data.keys())

    def clear(self):
        """清空数据"""
        self.data.clear()
        self.timestamps.clear()
        self.start_time = datetime.now()

    def remove_param(self, param_name: str):
        """移除参数"""
        if param_name in self.data:
            del self.data[param_name]


# ==================== 波形绘制窗口 ====================
class WaveformWindow(QDialog):
    """波形绘制窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.waveform_data = WaveformData(max_points=2000)  # 存储2000个数据点
        self.param_colors = {}  # 参数颜色映射
        self.curves = {}  # 参数名 -> 曲线对象
        self.setup_window()
        self.init_ui()
        self.setup_colors()
        self.setup_plot()

    def setup_window(self):
        """窗口设置"""
        self.setWindowTitle("波形图 - 实时绘制")
        self.resize(1200, 800)

    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # 控制面板
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(8)

        # 添加参数按钮
        self.add_param_btn = QPushButton("➕ 添加参数")
        self.add_param_btn.clicked.connect(self.add_parameter_dialog)
        control_layout.addWidget(self.add_param_btn)

        # 移除参数按钮
        self.remove_param_btn = QPushButton("🗑 移除参数")
        self.remove_param_btn.clicked.connect(self.remove_parameter)
        control_layout.addWidget(self.remove_param_btn)

        # 清空数据按钮
        self.clear_data_btn = QPushButton("🗑 清空数据")
        self.clear_data_btn.clicked.connect(self.clear_waveform_data)
        control_layout.addWidget(self.clear_data_btn)

        # 保存图像按钮
        self.save_image_btn = QPushButton("💾 保存图像")
        self.save_image_btn.clicked.connect(self.save_waveform_image)
        control_layout.addWidget(self.save_image_btn)

        # 保存数据按钮
        self.save_data_btn = QPushButton("📊 保存数据")
        self.save_data_btn.clicked.connect(self.save_waveform_data)
        control_layout.addWidget(self.save_data_btn)

        # 时间范围控制
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("时间范围(秒):"))
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["10", "30", "60", "120", "300", "600", "0(全部)"])
        self.time_range_combo.setCurrentText("30")
        self.time_range_combo.currentTextChanged.connect(self.update_time_range)
        time_layout.addWidget(self.time_range_combo)

        control_layout.addLayout(time_layout)
        control_layout.addStretch()

        # 关闭按钮
        self.close_btn = QPushButton("✕ 关闭")
        self.close_btn.setStyleSheet("background-color: #dc3545; color: white;")
        self.close_btn.clicked.connect(self.close)
        control_layout.addWidget(self.close_btn)

        main_layout.addWidget(control_panel)

        # 图表区域
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left', '参数值')
        self.plot_widget.setLabel('bottom', '时间', 's')
        self.plot_widget.addLegend()
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        main_layout.addWidget(self.plot_widget, 1)

        # 参数列表区域
        param_group = QGroupBox("参数列表")
        param_layout = QVBoxLayout(param_group)

        self.param_list = QListWidget()
        self.param_list.itemClicked.connect(self.on_param_item_clicked)
        param_layout.addWidget(self.param_list)

        main_layout.addWidget(param_group)

    def setup_colors(self):
        """设置颜色列表"""
        self.color_list = [
            '#FF0000',  # 红色
            '#00FF00',  # 绿色
            '#0000FF',  # 蓝色
            '#FF00FF',  # 紫色
            '#FFFF00',  # 黄色
            '#00FFFF',  # 青色
            '#FF8800',  # 橙色
            '#8800FF',  # 紫色
            '#008800',  # 深绿
            '#880000',  # 深红
        ]

    def setup_plot(self):
        """设置图表"""
        # 启用抗锯齿
        self.plot_widget.setAntialiasing(True)

    def get_color_for_param(self, param_name: str):
        """为参数分配颜色"""
        if param_name not in self.param_colors:
            # 使用循环颜色
            color_index = len(self.param_colors) % len(self.color_list)
            self.param_colors[param_name] = self.color_list[color_index]
        return self.param_colors[param_name]

    def add_parameter(self, param_name: str):
        """添加参数到波形图"""
        if not param_name:
            return

        if param_name in self.curves:
            QMessageBox.information(self, "提示", f"参数 '{param_name}' 已存在")
            return

        # 获取颜色
        color = self.get_color_for_param(param_name)

        # 创建曲线
        pen = pg.mkPen(color=color, width=2)
        curve = self.plot_widget.plot([], [], name=param_name, pen=pen)
        self.curves[param_name] = curve

        # 添加到列表
        item = QListWidgetItem(param_name)
        item.setForeground(QColor(color))
        self.param_list.addItem(item)

        # 如果数据中已有该参数的历史数据，立即更新曲线
        if param_name in self.waveform_data.data:
            times, values = self.waveform_data.get_data(param_name)
            if times and values:
                self.curves[param_name].setData(times, values)

    def add_parameter_dialog(self):
        """添加参数对话框"""
        param_name, ok = QInputDialog.getText(
            self, "添加参数", "请输入参数名:"
        )

        if ok and param_name:
            self.add_parameter(param_name.strip())

    def remove_parameter(self):
        """移除选中的参数"""
        current_item = self.param_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要移除的参数")
            return

        param_name = current_item.text()

        reply = QMessageBox.question(
            self, "确认移除",
            f"确定要移除参数 '{param_name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 从曲线中移除
            if param_name in self.curves:
                self.plot_widget.removeItem(self.curves[param_name])
                del self.curves[param_name]

            # 从数据中移除
            self.waveform_data.remove_param(param_name)

            # 从列表中移除
            self.param_list.takeItem(self.param_list.row(current_item))

            # 从颜色映射中移除
            if param_name in self.param_colors:
                del self.param_colors[param_name]

    def clear_waveform_data(self):
        """清空波形数据"""
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要清空所有波形数据吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.waveform_data.clear()
            for curve in self.curves.values():
                curve.setData([], [])

    def save_waveform_image(self):
        """保存波形图像"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存波形图像",
            f"waveform_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "PNG图像 (*.png);;JPEG图像 (*.jpg);;所有文件 (*)"
        )

        if file_path:
            try:
                # 使用pyqtgraph的导出功能
                exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
                exporter.export(file_path)
                QMessageBox.information(self, "保存成功", f"波形图像已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存图像失败:\n{str(e)}")

    def save_waveform_data(self):
        """保存波形数据到CSV"""
        if not self.waveform_data.data:
            QMessageBox.warning(self, "警告", "没有可保存的数据")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存波形数据",
            f"waveform_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV文件 (*.csv);;所有文件 (*)"
        )

        if file_path:
            try:
                # 收集所有时间戳
                all_times = list(self.waveform_data.timestamps)

                # 创建数据字典
                data_dict = {"时间(s)": all_times}

                # 添加每个参数的数据
                for param_name in self.waveform_data.data:
                    values = []
                    for i, time in enumerate(all_times):
                        if i < len(self.waveform_data.data[param_name]):
                            value = self.waveform_data.data[param_name][i]
                            values.append(value if value is not None else "")
                        else:
                            values.append("")
                    data_dict[param_name] = values

                # 创建DataFrame并保存
                df = pd.DataFrame(data_dict)
                df.to_csv(file_path, index=False, encoding='utf-8')

                QMessageBox.information(self, "保存成功", f"波形数据已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存数据失败:\n{str(e)}")

    def update_time_range(self, time_range_str: str):
        """更新时间范围"""
        if time_range_str == "0(全部)":
            self.plot_widget.enableAutoRange()
        else:
            try:
                time_range = float(time_range_str)
                # 获取当前X轴范围
                x_range = self.plot_widget.viewRange()[0]
                current_max = x_range[1]

                # 设置新的X轴范围
                self.plot_widget.setXRange(current_max - time_range, current_max)
            except ValueError:
                pass

    def on_param_item_clicked(self, item):
        """参数项点击事件"""
        param_name = item.text()

        # 可以在这里添加更多操作，比如显示/隐藏曲线等
        if param_name in self.curves:
            curve = self.curves[param_name]
            curve.setVisible(not curve.isVisible())

    def add_data_from_log(self, data_str: str):
        """从日志数据中添加数据点"""
        try:
            # 解析数据字符串，格式如: "参数名: 值"
            lines = data_str.split('\n')
            for line in lines:
                line = line.strip()
                if ':' in line:
                    # 尝试多种分隔符
                    if ':' in line:
                        parts = line.split(':', 1)
                    elif '=' in line:
                        parts = line.split('=', 1)
                    else:
                        continue

                    if len(parts) == 2:
                        param_name = parts[0].strip()
                        value_str = parts[1].strip()

                        # 尝试转换为数值
                        try:
                            value = float(value_str)

                            # 添加到波形数据
                            self.waveform_data.add_data_point(param_name, value)

                            # 如果参数尚未添加到图表，自动添加
                            if param_name not in self.curves:
                                self.add_parameter(param_name)

                            # 更新曲线数据
                            if param_name in self.curves:
                                times, values = self.waveform_data.get_data(param_name)
                                if times and values:
                                    self.curves[param_name].setData(times, values)

                        except ValueError:
                            continue
        except Exception as e:
            print(f"解析波形数据失败: {e}")

    def add_data_point(self, param_name: str, value: float):
        """添加单个数据点"""
        # 添加到波形数据
        self.waveform_data.add_data_point(param_name, value)

        # 如果参数尚未添加到图表，自动添加
        if param_name not in self.curves:
            self.add_parameter(param_name)

        # 更新曲线数据
        if param_name in self.curves:
            times, values = self.waveform_data.get_data(param_name)
            if times and values:
                self.curves[param_name].setData(times, values)

        # 自动调整时间范围
        time_range_str = self.time_range_combo.currentText()
        if time_range_str != "0(全部)":
            try:
                time_range = float(time_range_str)
                if self.waveform_data.timestamps:
                    current_time = self.waveform_data.timestamps[-1]
                    self.plot_widget.setXRange(current_time - time_range, current_time)
            except ValueError:
                pass

    def closeEvent(self, event):
        """关闭事件"""
        # 通知主窗口波形窗口已关闭
        if self.parent():
            self.parent().on_waveform_window_closed()
        event.accept()


# ==================== 批量命令发送线程 ====================
class BatchCommandSender(QThread):
    """批量命令发送线程"""
    progress_updated = Signal(int, str, int)  # 进度百分比, 当前命令, 当前循环
    current_command_highlight = Signal(int, bool)  # 行号, 是否高亮
    finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, commands: List[dict], loop_count: int, exec_mode: str, parent=None):
        """
        commands: 命令列表，每个元素为 {'command': str, 'delay_ms': int}
        loop_count: 循环次数，-1表示无限循环
        exec_mode: 'exec_first' 先执行后延时, 'delay_first' 先延时后执行
        """
        super().__init__(parent)
        self.commands = commands
        self.loop_count = loop_count
        self.exec_mode = exec_mode
        self.running = True
        self.is_stopping = False
        self.current_loop = 0
        self.current_command_index = 0

    def run(self):
        """线程主循环"""
        try:
            self.current_loop = 0

            while self.running and (self.loop_count == -1 or self.current_loop < self.loop_count):
                if self.is_stopping:
                    break

                for i, cmd_info in enumerate(self.commands):
                    if not self.running or self.is_stopping:
                        break

                    self.current_command_index = i
                    command = cmd_info['command']
                    delay_ms = cmd_info['delay_ms']

                    # 计算进度百分比
                    total_commands = len(self.commands)
                    if self.loop_count > 0:
                        total_items = self.loop_count * total_commands
                        current_item = (self.current_loop * total_commands) + i
                        progress = int((current_item / total_items) * 100) if total_items > 0 else 0
                    else:
                        progress = int((i / total_commands) * 100) if total_commands > 0 else 0

                    # 发送当前命令高亮信号（使用行号）
                    self.current_command_highlight.emit(i, True)

                    # 先延时后执行模式
                    if self.exec_mode == 'delay_first' and delay_ms > 0:
                        self.sleep_ms(delay_ms)
                        if not self.running or self.is_stopping:
                            self.current_command_highlight.emit(i, False)
                            break

                    # 发送命令
                    self.progress_updated.emit(progress, command, self.current_loop + 1)

                    # 先执行后延时模式
                    if self.exec_mode == 'exec_first' and delay_ms > 0:
                        self.sleep_ms(delay_ms)
                        if not self.running or self.is_stopping:
                            self.current_command_highlight.emit(i, False)
                            break

                    # 取消高亮
                    self.current_command_highlight.emit(i, False)

                    # 处理停止信号
                    QApplication.processEvents()

                self.current_loop += 1

                # 如果不是无限循环，更新循环计数
                if self.loop_count != -1:
                    self.progress_updated.emit(100, f"循环 {self.current_loop}/{self.loop_count} 完成", self.current_loop)

            if not self.is_stopping:
                self.progress_updated.emit(100, "批量命令发送完成", self.current_loop)

        except Exception as e:
            self.error_occurred.emit(f"批量发送错误: {str(e)}")
        finally:
            self.finished.emit()

    def sleep_ms(self, ms: int):
        """毫秒级休眠"""
        for _ in range(ms // 10):
            if not self.running or self.is_stopping:
                break
            self.msleep(10)

        remainder = ms % 10
        if remainder > 0:
            self.msleep(remainder)

    def stop(self):
        """停止发送"""
        self.is_stopping = True
        self.running = False
        self.wait(1000)


# ==================== 全屏日志窗口 ====================
class FullScreenLogWindow(QDialog):
    """全屏日志窗口（包含手动命令输入）"""
    command_sent = Signal(str)  # 发送命令信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_window()
        self.init_ui()
        self.setup_shortcuts()

    def setup_window(self):
        """窗口设置"""
        self.setWindowTitle("日志输出 - 全屏模式")
        self.resize(1200, 800)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint |
                            Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # ===== 中部：日志显示区域 =====
        log_group = QGroupBox("日志输出")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(8, 8, 8, 8)

        # 日志工具栏
        toolbar_layout = QHBoxLayout()

        self.clear_btn = QPushButton("🗑 清空")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_log)
        toolbar_layout.addWidget(self.clear_btn)

        self.save_btn = QPushButton("💾 保存")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.save_btn.clicked.connect(self.save_log)
        toolbar_layout.addWidget(self.save_btn)

        self.copy_btn = QPushButton("📋 复制")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_log)
        toolbar_layout.addWidget(self.copy_btn)

        # 搜索区域
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入搜索内容...")
        self.search_edit.setMaximumWidth(200)
        self.search_edit.returnPressed.connect(self.search_text)
        search_layout.addWidget(self.search_edit)

        self.search_btn = QPushButton("🔍 查找")
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.search_btn.clicked.connect(self.search_text)
        search_layout.addWidget(self.search_btn)

        toolbar_layout.addLayout(search_layout)
        toolbar_layout.addStretch()

        self.fullscreen_btn = QPushButton("📺 全屏")
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        toolbar_layout.addWidget(self.fullscreen_btn)

        self.close_btn = QPushButton("✕ 关闭")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        toolbar_layout.addWidget(self.close_btn)

        log_layout.addLayout(toolbar_layout)

        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 12))
        self.log_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f8f9fa;
                padding: 10px;
                font-family: Consolas;
            }
        """)
        log_layout.addWidget(self.log_text, 1)

        main_layout.addWidget(log_group, 1)

        # ===== 底部：状态栏 =====
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                border-top: 1px solid #dee2e6;
                padding: 5px;
                color: #6c757d;
                font-size: 12px;
            }
        """)
        main_layout.addWidget(self.status_label)

        # ===== 底部：命令输入区域 =====
        command_group = QGroupBox("命令输入")
        command_layout = QVBoxLayout(command_group)
        command_layout.setContentsMargins(8, 8, 8, 8)

        # 命令输入行
        input_layout = QHBoxLayout()

        self.command_edit = QLineEdit()
        self.command_edit.setPlaceholderText("输入指令后按Enter或点击发送...")
        self.command_edit.returnPressed.connect(self.send_command)
        self.command_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #007bff;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                font-family: Consolas;
            }
            QLineEdit:focus {
                border: 2px solid #0056b3;
            }
        """)

        self.send_btn = QPushButton("📤 发送")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.send_btn.clicked.connect(self.send_command)

        # 历史命令
        history_layout = QHBoxLayout()
        history_layout.addWidget(QLabel("历史命令:"))
        self.history_combo = QComboBox()
        self.history_combo.setMaximumWidth(300)
        self.history_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 1px solid #007bff;
            }
        """)
        self.history_combo.activated.connect(self.select_history_command)

        history_layout.addWidget(self.history_combo)

        input_layout.addWidget(self.command_edit, 1)
        input_layout.addWidget(self.send_btn)

        command_layout.addLayout(input_layout)
        command_layout.addLayout(history_layout)

        main_layout.addWidget(command_group)

    def setup_shortcuts(self):
        """设置快捷键"""
        # F11 全屏切换
        fullscreen_action = QAction(self)
        fullscreen_action.setShortcut(QKeySequence("F11"))
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(fullscreen_action)

        # Ctrl+F 搜索
        search_action = QAction(self)
        search_action.setShortcut(QKeySequence("Ctrl+F"))
        search_action.triggered.connect(self.focus_search)
        self.addAction(search_action)

        # Ctrl+C 复制
        copy_action = QAction(self)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        copy_action.triggered.connect(self.copy_log)
        self.addAction(copy_action)

        # Ctrl+S 保存
        save_action = QAction(self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_log)
        self.addAction(save_action)

        # Ctrl+W 关闭
        close_action = QAction(self)
        close_action.setShortcut(QKeySequence("Ctrl+W"))
        close_action.triggered.connect(self.close)
        self.addAction(close_action)

        # Esc 退出全屏
        esc_action = QAction(self)
        esc_action.setShortcut(QKeySequence("Escape"))
        esc_action.triggered.connect(self.escape_pressed)
        self.addAction(esc_action)

        # Ctrl+Enter 发送命令
        send_action = QAction(self)
        send_action.setShortcut(QKeySequence("Ctrl+Return"))
        send_action.triggered.connect(self.send_command)
        self.addAction(send_action)

    def toggle_fullscreen(self):
        """切换全屏模式"""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_btn.setText("📺 全屏")
            self.status_label.setText("窗口模式")
        else:
            self.showFullScreen()
            self.fullscreen_btn.setText("📱 窗口")
            self.status_label.setText("全屏模式")

    def escape_pressed(self):
        """ESC键处理"""
        if self.isFullScreen():
            self.showNormal()
            self.fullscreen_btn.setText("📺 全屏")
            self.status_label.setText("窗口模式")

    def focus_search(self):
        """聚焦到搜索框"""
        self.search_edit.setFocus()
        self.search_edit.selectAll()

    def send_command(self):
        """发送命令"""
        cmd = self.command_edit.text().strip()
        if not cmd:
            return

        # 发送命令信号
        self.command_sent.emit(cmd)

        # 添加到历史记录
        self.add_to_history(cmd)

        # 清空输入框
        self.command_edit.clear()

        # 聚焦回输入框，方便连续输入
        self.command_edit.setFocus()

    def add_to_history(self, command: str):
        """添加到历史记录"""
        if not command:
            return

        # 避免重复
        for i in range(self.history_combo.count()):
            if self.history_combo.itemText(i) == command:
                return

        self.history_combo.addItem(command)
        if self.history_combo.count() > 20:  # 限制历史记录数量
            self.history_combo.removeItem(0)

    def select_history_command(self, index: int):
        """选择历史命令"""
        if index >= 0:
            command = self.history_combo.itemText(index)
            self.command_edit.setText(command)
            self.command_edit.setFocus()
            self.command_edit.selectAll()

    def append_log(self, text: str):
        """添加日志"""
        self.log_text.append(text)
        # 自动滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.status_label.setText("日志已清空")

    def save_log(self):
        """保存日志到文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存日志", f"fullscreen_log_{timestamp}.txt",
                "文本文件 (*.txt);;所有文件 (*)"
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.status_label.setText(f"日志已保存到: {file_path}")
                QMessageBox.information(self, "保存成功", f"日志已保存到:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "保存错误", f"保存失败:\n{str(e)}")

    def copy_log(self):
        """复制日志内容"""
        if self.log_text.toPlainText():
            self.log_text.selectAll()
            self.log_text.copy()
            self.status_label.setText("日志内容已复制到剪贴板")

    def search_text(self):
        """搜索文本"""
        search_text = self.search_edit.text().strip()
        if not search_text:
            return

        # 移动到文档开始
        cursor = self.log_text.textCursor()
        cursor.setPosition(0)
        self.log_text.setTextCursor(cursor)

        # 搜索
        found = self.log_text.find(search_text)
        if not found:
            self.status_label.setText(f"未找到: {search_text}")
        else:
            self.status_label.setText(f"找到: {search_text}")

    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showNormal()
            event.accept()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """关闭事件"""
        if self.parent():
            self.parent().on_fullscreen_log_closed()
        event.accept()


# ==================== 数据结构定义 ====================
@dataclass
class Parameter:
    """参数数据结构"""
    id: int
    name: str
    value: int
    is_selected: bool = False  # 默认不选中
    is_monitoring: bool = False


@dataclass
class BatchCommand:
    """批量指令数据结构"""
    is_selected: bool = True
    command: str = ""
    delay_ms: int = 0  # 延时（毫秒）


@dataclass
class CustomCommand:
    """自定义快捷命令数据结构"""
    name: str = ""
    command: str = ""


# ==================== 自定义组件 ====================
class StyledTableWidget(QTableWidget):
    """带样式的表格组件"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_style()

    def setup_style(self):
        """设置表格样式"""
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setHighlightSections(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件，允许编辑"""
        item = self.itemAt(event.position().toPoint())
        if item:
            self.editItem(item)
        super().mouseDoubleClickEvent(event)


class LogTextEdit(QTextEdit):
    """日志输出组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()

    def setup_style(self):
        """设置日志样式"""
        self.setReadOnly(True)
        font = QFont("Consolas", 10)
        self.setFont(font)
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f9fa;
                padding: 5px;
            }
        """)

    def append_log(self, text: str, color: str = "black"):
        """添加带颜色的日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
        html = f'<span style="color:gray;">{timestamp}</span> '
        html += f'<span style="color:{color};">{text}</span>'

        # 使用QTextEdit的append方法
        self.append(html)

        # 自动滚动到底部
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        """清空日志"""
        self.clear()


class CustomCommandDialog(QDialog):
    """添加/编辑自定义命令对话框"""

    def __init__(self, command: CustomCommand = None, parent=None):
        super().__init__(parent)
        self.command = command if command else CustomCommand()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("自定义快捷命令" if not self.command.name else f"编辑: {self.command.name}")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 命令名称
        name_layout = QHBoxLayout()
        name_label = QLabel("命令名称:")
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.command.name)
        self.name_edit.setPlaceholderText("例如: 重启设备")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit, 1)
        layout.addLayout(name_layout)

        # 命令内容
        command_layout = QVBoxLayout()
        command_label = QLabel("命令内容:")
        self.command_edit = QTextEdit()
        self.command_edit.setText(self.command.command)
        self.command_edit.setMaximumHeight(100)
        self.command_edit.setPlaceholderText("输入要发送的指令...")
        command_layout.addWidget(command_label)
        command_layout.addWidget(self.command_edit)
        layout.addLayout(command_layout)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn = QPushButton("确定")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setDefault(True)

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.ok_btn)
        layout.addLayout(button_layout)

    def get_command(self) -> CustomCommand:
        """获取输入的命令"""
        return CustomCommand(
            name=self.name_edit.text().strip(),
            command=self.command_edit.toPlainText().strip()
        )


# ==================== 串口线程 ====================
class SerialReader(QThread):
    """串口读取线程"""
    data_received = Signal(str)  # 信号与槽机制
    error_occurred = Signal(str)
    connection_status = Signal(bool, str)  # (是否连接, 状态信息)

    def __init__(self, port: str, baudrate: int, timeout: float):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.running = True

    def run(self):
        """线程主循环"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.connection_status.emit(True, f"已连接 {self.port}")

            while self.running and self.ser and self.ser.is_open:
                try:
                    if self.ser.in_waiting > 0:
                        data = self.ser.readline()
                        if data:
                            try:
                                text = data.decode('utf-8', errors='ignore').strip()
                                if text:
                                    self.data_received.emit(text)
                            except UnicodeDecodeError:
                                # 尝试其他编码
                                try:
                                    text = data.decode('gbk', errors='ignore').strip()
                                    if text:
                                        self.data_received.emit(text)
                                except:
                                    pass
                except (serial.SerialException, OSError) as e:
                    self.error_occurred.emit(f"串口读取错误: {str(e)}")
                    break
                except Exception as e:
                    self.error_occurred.emit(f"未知错误: {str(e)}")
                    break

                self.msleep(1)  # 避免CPU占用过高

        except serial.SerialException as e:
            self.connection_status.emit(False, f"连接失败: {str(e)}")
        except Exception as e:
            self.connection_status.emit(False, f"未知错误: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        """清理资源"""
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except:
                pass

    def stop(self):
        """停止线程"""
        self.running = False
        if self.ser and self.ser.is_open:
            try:
                self.ser.cancel_read()
                self.ser.cancel_write()
            except:
                pass
        self.wait(1000)  # 等待1秒

    def send_command(self, command: str) -> bool:
        """发送命令"""
        if not self.ser or not self.ser.is_open:
            return False

        try:
            if not command.endswith('\n'):
                command += '\n'
            self.ser.write(command.encode('utf-8'))
            self.ser.flush()
            return True
        except Exception as e:
            self.error_occurred.emit(f"发送失败: {str(e)}")
            return False


# ==================== 批量命令管理对话框 ====================
class BatchCommandManagerDialog(QDialog):
    """批量命令管理对话框"""

    def __init__(self, batch_commands: List[dict], parent=None):
        super().__init__(parent)
        self.batch_commands = batch_commands
        self.setup_ui()
        self.load_commands()

    def setup_ui(self):
        self.setWindowTitle("批量命令管理")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # 命令表格
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["指令", "延时(ms)", "选择"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        layout.addWidget(self.table)

        # 按钮布局
        button_layout = QHBoxLayout()

        self.load_btn = QPushButton("📂 导入")
        self.load_btn.clicked.connect(self.load_from_file)

        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self.save_to_file)

        self.clear_btn = QPushButton("🗑 清空")
        self.clear_btn.clicked.connect(self.clear_table)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def load_commands(self):
        """加载命令到表格"""
        self.table.setRowCount(0)
        for cmd in self.batch_commands:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # 指令
            cmd_item = QTableWidgetItem(cmd['command'])
            self.table.setItem(row, 0, cmd_item)

            # 延时
            delay_item = QTableWidgetItem(str(cmd['delay_ms']))
            self.table.setItem(row, 1, delay_item)

            # 选择
            checkbox = QCheckBox()
            checkbox.setChecked(cmd.get('is_selected', True))
            self.table.setCellWidget(row, 2, checkbox)

    def get_commands(self) -> List[dict]:
        """从表格获取命令"""
        commands = []
        for row in range(self.table.rowCount()):
            cmd_item = self.table.item(row, 0)
            delay_item = self.table.item(row, 1)
            checkbox = self.table.cellWidget(row, 2)

            if cmd_item and cmd_item.text().strip():
                commands.append({
                    'command': cmd_item.text().strip(),
                    'delay_ms': int(delay_item.text()) if delay_item and delay_item.text().isdigit() else 0,
                    'is_selected': checkbox.isChecked() if checkbox else True
                })
        return commands

    def load_from_file(self):
        """从文件导入"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入批量命令", "", "JSON文件 (*.json);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    commands = json.load(f)

                self.batch_commands = commands
                self.load_commands()
                QMessageBox.information(self, "导入成功", f"已从 {file_path} 导入 {len(commands)} 条命令")
            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"导入失败: {str(e)}")

    def save_to_file(self):
        """保存到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存批量命令", "", "JSON文件 (*.json);;所有文件 (*)"
        )
        if file_path:
            try:
                commands = self.get_commands()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(commands, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "保存成功", f"已保存 {len(commands)} 条命令到 {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存失败: {str(e)}")

    def clear_table(self):
        """清空表格"""
        reply = QMessageBox.question(self, "确认清空", "确定要清空所有命令吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.table.setRowCount(0)


# ==================== 历史命令管理器 ====================
class CommandHistoryManager:
    """命令历史记录管理器"""

    def __init__(self, max_history_size=50):
        self.max_history_size = max_history_size
        self.history: List[str] = []
        self.current_index = -1  # -1 表示当前没有浏览历史
        self.temp_command = ""  # 临时保存正在输入的命令

    def add_command(self, command: str):
        """添加命令到历史记录"""
        if not command or not command.strip():
            return

        # 避免重复
        if command in self.history:
            self.history.remove(command)

        # 添加到列表开头
        self.history.insert(0, command)

        # 限制历史记录大小
        if len(self.history) > self.max_history_size:
            self.history = self.history[:self.max_history_size]

        # 重置浏览索引
        self.current_index = -1

    def get_previous(self, current_text: str = "") -> str:
        """获取上一条历史命令"""
        if not self.history:
            return current_text

        # 如果是第一次按上键，保存当前输入
        if self.current_index == -1:
            self.temp_command = current_text

        # 增加索引
        if self.current_index < len(self.history) - 1:
            self.current_index += 1

        return self.history[self.current_index]

    def get_next(self) -> str:
        """获取下一条历史命令"""
        if not self.history:
            return ""

        # 减少索引
        if self.current_index > 0:
            self.current_index -= 1
            return self.history[self.current_index]
        elif self.current_index == 0:
            self.current_index = -1
            return self.temp_command

        return ""

    def clear(self):
        """清空历史记录"""
        self.history.clear()
        self.current_index = -1
        self.temp_command = ""

    def get_all(self) -> List[str]:
        """获取所有历史记录"""
        return self.history.copy()


# ==================== 支持方向键的QLineEdit ====================
class CommandLineEdit(QLineEdit):
    """支持方向键浏览历史命令的QLineEdit"""

    def __init__(self, history_manager: CommandHistoryManager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager

    def keyPressEvent(self, event):
        """键盘事件处理"""
        if event.key() == Qt.Key_Up:
            # 上键：获取上一条历史命令
            previous_command = self.history_manager.get_previous(self.text())
            self.setText(previous_command)
            event.accept()
            return

        elif event.key() == Qt.Key_Down:
            # 下键：获取下一条历史命令
            next_command = self.history_manager.get_next()
            self.setText(next_command)
            event.accept()
            return

        # 其他按键保持默认行为
        super().keyPressEvent(event)


# ==================== 主窗口 ====================
class SerialTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_variables()
        self.init_ui()
        self.setup_connections()
        self.refresh_ports()

        # 加载保存的自定义命令
        self.load_custom_commands()
        # 加载批量命令配置
        self.load_batch_commands()
        # 加载参数说明信息
        self.load_parameter_descriptions()

    def setup_window(self):
        """窗口设置"""
        self.setWindowTitle("硬测工具包")
        self.resize(1400, 900)
        self.setMinimumSize(1000, 700)

    def setup_variables(self):
        """初始化变量"""
        # 串口相关
        self.serial_reader: Optional[SerialReader] = None
        self.is_connected = False

        # 参数管理
        self.parameters: List[Parameter] = []
        self.is_monitoring = False
        self.parameter_timer = QTimer()
        self.parameter_timer.timeout.connect(self.update_parameter_values)

        # 指令处理
        self.info_a_flag = False
        self.info_a_count = 0
        self.batch_commands: List[dict] = []

        # 批量命令线程
        self.batch_thread: Optional[BatchCommandSender] = None

        # 自定义快捷命令
        self.custom_commands: List[CustomCommand] = []
        self.custom_command_buttons: List[QPushButton] = []

        # 快捷命令列表
        self.quick_commands: List[CustomCommand] = []

        # 日志
        self.log_file = None
        self.fullscreen_log_window: Optional[FullScreenLogWindow] = None

        # 监控频率（毫秒）
        self.monitor_frequency = 100

        # 命令历史记录管理器
        self.command_history_manager = CommandHistoryManager(max_history_size=50)

        # 配置文件路径
        self.custom_commands_file = "custom_commands.json"
        self.batch_commands_file = "batch_commands.json"

        # 新增：参数说明文件路径
        self.parameter_description_file = "parameter_descriptions.json"

        # 参数说明信息存储字典 {参数名: 说明}
        self.parameter_descriptions: Dict[str, str] = {}

        # 面板复用控制
        self.current_panel = "parameter"  # 当前显示的面板，默认显示参数打印栏

        # EXCEL日志记录相关
        self.excel_log_enabled = False
        self.excel_log_data: List[Dict[str, str]] = []
        self.excel_file_path = None

        # 波形窗口
        self.waveform_window: Optional[WaveformWindow] = None

        # 插件系统
        self.plugin_manager: Optional[PluginManager] = None

    def init_ui(self):
        """初始化UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 使用垂直布局
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setSpacing(6)
        self.main_layout.setContentsMargins(8, 8, 8, 8)

        # 第0行：窗口配置栏
        self.main_layout.addWidget(self.create_config_bar())

        # 创建主分隔器，用于动态调整复用面板和日志显示栏的大小
        self.create_main_splitter()
        self.main_layout.addWidget(self.main_splitter, 1)  # 1表示可拉伸

        # 第3行：手动指令
        self.manual_group = self.create_manual_group()
        self.main_layout.addWidget(self.manual_group)

        # 第4行：自定义快捷命令栏
        self.custom_commands_group = self.create_custom_commands_group()
        self.main_layout.addWidget(self.custom_commands_group)

        # 设置样式
        self.setup_styles()

        # 创建菜单栏
        self.create_menu_bar()

        # 初始化插件系统
        self.initialize_plugin_system()

    def initialize_plugin_system(self):
        """初始化插件系统"""
        # 创建插件管理器
        self.plugin_manager = PluginManager(self)

        # 连接插件信号
        self.plugin_manager.plugin_loaded.connect(self.on_plugin_loaded)
        self.plugin_manager.plugin_error.connect(self.on_plugin_error)

        # 加载所有插件
        loaded_count = self.plugin_manager.load_all_plugins()
        self.append_log_to_all(f"已加载 {loaded_count} 个插件", "blue")

        # 只在第一次初始化时创建插件菜单
        self.create_plugin_menu()

    def create_plugin_menu(self):
        """创建插件菜单"""
        # 检查是否已存在插件菜单
        menubar = self.menuBar()

        # 查找是否已存在"🔌 插件"菜单
        existing_menu = None
        for action in menubar.actions():
            if action.menu() and action.text().startswith("🔌 插件"):
                existing_menu = action.menu()
                break

        if existing_menu:
            # 清空现有菜单项（保留基本项）
            existing_menu.clear()
        else:
            # 创建新菜单
            existing_menu = menubar.addMenu("🔌 插件")

        # 插件管理
        manage_action = QAction("⚙ 插件管理", self)
        manage_action.triggered.connect(self.open_plugin_manager)
        existing_menu.addAction(manage_action)

        existing_menu.addSeparator()

        # 动态添加插件菜单项
        self.update_plugin_menu(existing_menu)

        # 重新加载插件
        reload_action = QAction("🔄 重新加载所有插件", self)
        reload_action.triggered.connect(self.reload_all_plugins)
        existing_menu.addAction(reload_action)

    def update_plugin_menu(self, plugin_menu: QMenu):
        """更新插件菜单"""
        # 清除现有插件子菜单（保留前2个固定项：插件管理和分隔符）
        actions_to_remove = []

        # 只保留前2个固定项（插件管理和分隔符）
        menu_actions = plugin_menu.actions()
        if len(menu_actions) > 2:
            for i in range(2, len(menu_actions)):
                actions_to_remove.append(menu_actions[i])

        # 移除多余的插件子菜单
        for action in actions_to_remove:
            plugin_menu.removeAction(action)

        # 添加启用的插件菜单
        if self.plugin_manager:
            for plugin_name, plugin in self.plugin_manager.plugins.items():
                info = self.plugin_manager.plugin_info.get(plugin_name)
                if info and info.enabled:
                    plugin_actions = plugin.get_menu_actions()
                    if plugin_actions:
                        plugin_submenu = plugin_menu.addMenu(f"📦 {plugin_name}")
                        for action in plugin_actions:
                            plugin_submenu.addAction(action)

    def open_plugin_manager(self):
        """打开插件管理器"""
        if self.plugin_manager:
            dialog = PluginManagerDialog(self.plugin_manager, self)
            dialog.exec()

            # 刷新菜单
            plugin_menu = self.menuBar().findChild(QMenu, "🔌 插件")
            if plugin_menu:
                self.update_plugin_menu(plugin_menu)

    def reload_all_plugins(self):
        """重新加载所有插件"""
        reply = QMessageBox.question(
            self, "确认重新加载",
            "确定要重新加载所有插件吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 先清理
            if self.plugin_manager:
                self.plugin_manager.cleanup()

            # 重新初始化
            self.initialize_plugin_system()

            self.append_log_to_all("所有插件已重新加载", "green")

    def on_plugin_loaded(self, plugin_name: str, status: str):
        """插件加载信号处理"""
        self.append_log_to_all(f"插件 '{plugin_name}' {status}", "blue")

    def on_plugin_error(self, plugin_name: str, error_msg: str):
        """插件错误信号处理"""
        self.append_log_to_all(f"插件 '{plugin_name}' 错误: {error_msg}", "red")

    def create_main_splitter(self):
        """创建主分隔器，包含复用面板和日志显示栏"""
        # 创建垂直分隔器
        self.main_splitter = QSplitter(Qt.Vertical)

        # 创建复用面板
        self.create_reusable_panel()
        self.main_splitter.addWidget(self.reusable_panel_group)

        # 创建日志显示栏
        self.log_group = self.create_log_group()
        self.main_splitter.addWidget(self.log_group)

        # 设置分隔器的初始大小比例（复用面板:日志显示栏 = 6:4）
        self.main_splitter.setSizes([600, 400])

        # 设置分隔器样式
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #dee2e6;
                height: 4px;
            }
            QSplitter::handle:hover {
                background-color: #adb5bd;
            }
        """)

        # 保存分隔器位置
        self.main_splitter.splitterMoved.connect(self.on_splitter_moved)

    def on_splitter_moved(self, pos: int, index: int):
        """分隔器移动时的处理"""
        # 可以在这里保存用户偏好设置
        pass

    def create_config_bar(self) -> QWidget:
        """创建窗口配置栏"""
        config_widget = QWidget()
        config_layout = QHBoxLayout(config_widget)
        config_layout.setContentsMargins(5, 2, 5, 2)
        config_layout.setSpacing(8)

        # 设置最小高度
        config_widget.setMaximumHeight(70)

        # 左侧：串口配置
        serial_config_widget = QWidget()
        serial_layout = QHBoxLayout(serial_config_widget)
        serial_layout.setContentsMargins(0, 0, 0, 0)
        serial_layout.setSpacing(8)

        serial_layout.addWidget(QLabel("端口:"), 0, Qt.AlignLeft)
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        self.port_combo.setMaximumHeight(30)
        serial_layout.addWidget(self.port_combo, 0)

        serial_layout.addWidget(QLabel("波特率:"), 0, Qt.AlignLeft)
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200', '230400'])
        self.baud_combo.setCurrentText('115200')
        self.baud_combo.setMinimumWidth(100)
        self.baud_combo.setMaximumHeight(30)
        serial_layout.addWidget(self.baud_combo, 0)

        serial_layout.addWidget(QLabel("超时(秒):"), 0, Qt.AlignLeft)
        self.timeout_edit = QLineEdit("1.0")
        self.timeout_edit.setFixedWidth(80)
        self.timeout_edit.setMaximumHeight(30)
        serial_layout.addWidget(self.timeout_edit, 0)

        # 串口控制按钮
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setMaximumHeight(30)
        self.refresh_btn.clicked.connect(self.refresh_ports)

        self.connect_btn = QPushButton("🔗 连接")
        self.connect_btn.setMaximumHeight(30)
        self.connect_btn.setStyleSheet("background-color: #28a745; color: white;")
        self.connect_btn.clicked.connect(self.connect_serial)

        self.disconnect_btn = QPushButton("🔌 断开")
        self.disconnect_btn.setMaximumHeight(30)
        self.disconnect_btn.setStyleSheet("background-color: #dc3545; color: white;")
        self.disconnect_btn.clicked.connect(self.disconnect_serial)
        self.disconnect_btn.setEnabled(False)

        serial_layout.addWidget(self.refresh_btn)
        serial_layout.addWidget(self.connect_btn)
        serial_layout.addWidget(self.disconnect_btn)

        # 添加到主配置布局
        config_layout.addWidget(serial_config_widget, 4)

        # 状态显示
        self.status_label = QLabel("状态: 未连接")
        self.status_label.setAlignment(Qt.AlignLeft)
        config_layout.addWidget(self.status_label, 2)

        # 设置背景色
        config_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
            QLabel {
                font-size: 11px;
                padding: 2px;
            }
        """)

        return config_widget

    def create_reusable_panel(self):
        """创建复用面板"""
        # 创建分组框
        self.reusable_panel_group = QGroupBox("复用面板")
        panel_layout = QVBoxLayout(self.reusable_panel_group)
        panel_layout.setContentsMargins(8, 15, 8, 8)  # 增加上边距为按钮留出空间

        # 创建面板切换按钮栏
        self.create_panel_switch_bar()
        panel_layout.addWidget(self.panel_switch_bar)

        # 创建堆叠窗口
        self.panel_stack = QStackedWidget()
        self.panel_stack.setStyleSheet("""
            QStackedWidget {
                border: none;
            }
        """)

        # 创建参数监控面板
        self.parameter_panel = self.create_parameter_panel()
        self.panel_stack.addWidget(self.parameter_panel)

        # 创建批量命令面板
        self.batch_panel = self.create_batch_panel()
        self.panel_stack.addWidget(self.batch_panel)

        # 设置默认显示参数打印面板
        self.panel_stack.setCurrentWidget(self.parameter_panel)
        self.current_panel = "parameter"

        panel_layout.addWidget(self.panel_stack, 1)  # 给堆叠窗口权重

    def create_panel_switch_bar(self):
        """创建面板切换按钮栏"""
        self.panel_switch_bar = QWidget()
        switch_layout = QHBoxLayout(self.panel_switch_bar)
        switch_layout.setContentsMargins(0, 0, 0, 5)
        switch_layout.setSpacing(10)

        # 参数打印按钮
        self.parameter_panel_btn = QPushButton("📊 参数打印")
        self.parameter_panel_btn.setMaximumHeight(30)
        self.parameter_panel_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.parameter_panel_btn.clicked.connect(lambda: self.switch_panel("parameter"))

        # 批量命令按钮
        self.batch_panel_btn = QPushButton("📋 批量命令")
        self.batch_panel_btn.setMaximumHeight(30)
        self.batch_panel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.batch_panel_btn.clicked.connect(lambda: self.switch_panel("batch"))

        switch_layout.addWidget(self.parameter_panel_btn)
        switch_layout.addWidget(self.batch_panel_btn)
        switch_layout.addStretch()

    def create_parameter_panel(self) -> QWidget:
        """创建参数打印面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)  # 减少组件间距

        # 控制面板 - 减少高度
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("参数操作:"), 0)

        self.select_all_btn = QPushButton("☑ 全选")
        self.select_all_btn.setMaximumHeight(25)
        self.select_all_btn.clicked.connect(self.select_all_parameters)

        self.clear_select_btn = QPushButton("☐ 全不选")
        self.clear_select_btn.setMaximumHeight(25)
        self.clear_select_btn.clicked.connect(self.clear_parameter_selection)

        self.init_param_btn = QPushButton("🔧 初始化参数")
        self.init_param_btn.setMaximumHeight(25)
        self.init_param_btn.setStyleSheet("background-color: #007bff; color: white;")
        self.init_param_btn.clicked.connect(self.init_parameter)

        self.start_monitor_btn = QPushButton("▶ 开始打印参数")
        self.start_monitor_btn.setMaximumHeight(25)
        self.start_monitor_btn.setStyleSheet("background-color: #28a745; color: white;")
        self.start_monitor_btn.clicked.connect(self.start_monitoring)

        self.stop_monitor_btn = QPushButton("⏸ 停止打印参数")
        self.stop_monitor_btn.setMaximumHeight(25)
        self.stop_monitor_btn.setStyleSheet("background-color: #ffc107; color: black;")
        self.stop_monitor_btn.clicked.connect(self.stop_monitoring)
        self.stop_monitor_btn.setEnabled(True)

        control_layout.addWidget(QLabel("显示频率(ms):"))

        self.freq_edit = QLineEdit("100")
        self.freq_edit.setFixedWidth(60)
        self.freq_edit.setMaximumHeight(25)
        control_layout.addWidget(self.freq_edit)

        control_layout.addWidget(self.init_param_btn)
        control_layout.addWidget(self.start_monitor_btn)
        control_layout.addWidget(self.stop_monitor_btn)
        control_layout.addWidget(self.select_all_btn)
        control_layout.addWidget(self.clear_select_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)

        # 参数表格 - 占据大部分空间
        self.param_table = StyledTableWidget(0, 6)  # 修改为6列，新增"说明"列
        self.param_table.setHorizontalHeaderLabels(["选择", "ID", "参数名", "当前值", "状态", "说明"])  # 添加"说明"列
        self.param_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.param_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.param_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.param_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.param_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.param_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)  # 说明列可拉伸

        # 设置表格样式，增加行高
        self.param_table.setStyleSheet("""
            QTableWidget {
                font-size: 11px;
                border: none;
            }
            QTableWidget::item {
                padding: 4px;
                min-height: 24px;
            }
        """)

        # 连接表格项改变信号
        self.param_table.itemChanged.connect(self.on_parameter_item_changed)

        layout.addWidget(self.param_table, 8)  # 增加表格的布局权重

        # 统计信息 - 压缩高度
        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(0, 2, 0, 0)
        self.param_count_label = QLabel("参数总数: 0")
        self.selected_count_label = QLabel("已选择: 0")
        self.monitoring_count_label = QLabel("监控中: 0")
        self.param_count_label.setStyleSheet("font-size: 10px;")
        self.selected_count_label.setStyleSheet("font-size: 10px;")
        self.monitoring_count_label.setStyleSheet("font-size: 10px;")
        stats_layout.addWidget(self.param_count_label)
        stats_layout.addWidget(self.selected_count_label)
        stats_layout.addWidget(self.monitoring_count_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        return panel

    def create_batch_panel(self) -> QWidget:
        """创建批量命令面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)  # 减少组件间距

        # 控制面板 - 减少高度
        control_panel = self.create_batch_control_panel()
        layout.addWidget(control_panel)

        # 按钮控制 - 减少高度
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.add_cmd_btn = QPushButton("➕ 添加命令")
        self.add_cmd_btn.setMaximumHeight(25)
        self.add_cmd_btn.clicked.connect(self.add_batch_command)

        self.del_cmd_btn = QPushButton("🗑 删除选中")
        self.del_cmd_btn.setMaximumHeight(25)
        self.del_cmd_btn.clicked.connect(self.delete_selected_commands)

        self.send_cmd_btn = QPushButton("📤 发送选中")
        self.send_cmd_btn.setMaximumHeight(25)
        self.send_cmd_btn.setStyleSheet("background-color: #28a745; color: white;")
        self.send_cmd_btn.clicked.connect(self.send_selected_commands)

        self.stop_cmd_btn = QPushButton("⏹ 终止发送")
        self.stop_cmd_btn.setMaximumHeight(25)
        self.stop_cmd_btn.setStyleSheet("background-color: #dc3545; color: white;")
        self.stop_cmd_btn.clicked.connect(self.stop_batch_sending)
        self.stop_cmd_btn.setVisible(False)

        self.select_all_btn_batch = QPushButton("☑ 全选")
        self.select_all_btn_batch.setMaximumHeight(25)
        self.select_all_btn_batch.clicked.connect(self.select_all_commands)

        self.deselect_all_btn = QPushButton("☐ 全不选")
        self.deselect_all_btn.setMaximumHeight(25)
        self.deselect_all_btn.clicked.connect(self.deselect_all_commands)

        # 批量命令管理按钮
        self.import_btn = QPushButton("📂 导入")
        self.import_btn.setMaximumHeight(25)
        self.import_btn.clicked.connect(self.import_batch_commands)
        self.import_btn.setToolTip("导入保存的批量命令")

        self.export_btn = QPushButton("💾 保存")
        self.export_btn.setMaximumHeight(25)
        self.export_btn.clicked.connect(self.export_batch_commands)
        self.export_btn.setToolTip("保存当前批量命令")

        self.manage_btn = QPushButton("⚙ 管理")
        self.manage_btn.setMaximumHeight(25)
        self.manage_btn.clicked.connect(self.manage_batch_commands)
        self.manage_btn.setToolTip("管理批量命令")

        self.clear_batch_btn = QPushButton("🗑 清空")
        self.clear_batch_btn.setMaximumHeight(25)
        self.clear_batch_btn.clicked.connect(self.clear_batch_commands)
        self.clear_batch_btn.setToolTip("清空所有批量命令")

        button_layout.addWidget(self.add_cmd_btn)
        button_layout.addWidget(self.del_cmd_btn)
        button_layout.addWidget(self.send_cmd_btn)
        button_layout.addWidget(self.stop_cmd_btn)
        button_layout.addWidget(self.select_all_btn_batch)
        button_layout.addWidget(self.deselect_all_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.manage_btn)
        button_layout.addWidget(self.clear_batch_btn)
        layout.addLayout(button_layout)

        # 指令表格 - 占据大部分空间
        self.batch_table = StyledTableWidget(0, 3)
        self.batch_table.setHorizontalHeaderLabels(["选择", "指令", "延时(ms)"])
        self.batch_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.batch_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.batch_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

        # 设置双击可编辑
        self.batch_table.setEditTriggers(QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)

        # 设置延时列为整数输入
        self.batch_table.itemChanged.connect(self.on_batch_item_changed)

        # 设置表格样式，增加行高
        self.batch_table.setStyleSheet("""
            QTableWidget {
                font-size: 11px;
                alternate-background-color: #f8f9fa;
                background-color: white;
                selection-background-color: #e6f2ff;
                selection-color: black;
            }
            QTableWidget::item {
                padding: 4px;
                min-height: 24px;
            }
            QTableWidget::item:selected {
                background-color: #e6f2ff;
                color: black;
            }
            QTableWidget::item {
                border-bottom: 1px solid #f0f0f0;
            }
        """)

        layout.addWidget(self.batch_table, 8)  # 增加表格的布局权重

        # 进度条和状态标签 - 压缩高度
        progress_layout = QHBoxLayout()
        progress_layout.setContentsMargins(0, 2, 0, 0)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("font-size: 10px;")
        progress_layout.addWidget(self.progress_bar, 4)
        progress_layout.addWidget(self.progress_label, 1)
        layout.addLayout(progress_layout)

        return panel

    def create_batch_control_panel(self) -> QWidget:
        """创建批量命令控制面板（添加执行模式）"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # 循环模式
        layout.addWidget(QLabel("循环模式:"))

        # 无限循环单选按钮
        self.infinite_loop_radio = QRadioButton("无限循环")
        self.infinite_loop_radio.setMaximumHeight(20)
        self.infinite_loop_radio.setChecked(True)
        self.infinite_loop_radio.toggled.connect(self.on_loop_mode_changed)
        layout.addWidget(self.infinite_loop_radio)

        # 有限循环单选按钮
        self.finite_loop_radio = QRadioButton("有限循环")
        self.finite_loop_radio.setMaximumHeight(20)
        self.finite_loop_radio.toggled.connect(self.on_loop_mode_changed)
        layout.addWidget(self.finite_loop_radio)

        # 循环次数输入框
        layout.addWidget(QLabel("循环次数:"))
        self.loop_spin = QSpinBox()
        self.loop_spin.setMinimum(1)
        self.loop_spin.setMaximum(9999)
        self.loop_spin.setValue(1)
        self.loop_spin.setMaximumWidth(80)
        self.loop_spin.setMaximumHeight(25)
        self.loop_spin.setEnabled(False)  # 默认禁用，因为默认是无限循环
        layout.addWidget(self.loop_spin)

        # 执行模式
        layout.addWidget(QLabel("执行模式:"))

        self.exec_mode_combo = QComboBox()
        self.exec_mode_combo.addItems(["先执行后延时", "先延时后执行"])
        self.exec_mode_combo.setMaximumWidth(120)
        self.exec_mode_combo.setMaximumHeight(25)
        layout.addWidget(self.exec_mode_combo)

        layout.addStretch()

        # 自动加载标签
        self.auto_load_cb = QCheckBox("启动时自动加载命令")
        self.auto_load_cb.setMaximumHeight(20)
        self.auto_load_cb.setChecked(True)
        self.auto_load_cb.setToolTip("程序启动时自动加载保存的批量命令")
        layout.addWidget(self.auto_load_cb)

        return panel

    def on_loop_mode_changed(self):
        """循环模式改变事件"""
        if self.finite_loop_radio.isChecked():
            self.loop_spin.setEnabled(True)
        else:
            self.loop_spin.setEnabled(False)

    def on_batch_item_changed(self, item):
        """批量表格项改变事件"""
        if item.column() == 2:  # 延时列
            try:
                # 确保输入的是整数
                text = item.text().strip()
                if text:
                    value = int(text)
                    if value < 0:
                        item.setText("0")
            except ValueError:
                item.setText("0")

    def create_custom_commands_group(self) -> QGroupBox:
        """创建自定义快捷命令组"""
        group = QGroupBox("📌 快捷命令")
        layout = QVBoxLayout()
        layout.setContentsMargins(6, 8, 6, 6)  # 减少内边距
        layout.setSpacing(4)  # 减少间距

        # 控制面板
        control_layout = QHBoxLayout()

        # 左侧：管理按钮
        self.add_custom_btn = QPushButton("➕ 添加")
        self.add_custom_btn.clicked.connect(self.add_custom_command)
        self.add_custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #20c997;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 10px;
                height: 25px;
            }
            QPushButton:hover {
                background-color: #1ba87e;
            }
        """)
        control_layout.addWidget(self.add_custom_btn)

        self.manage_custom_btn = QPushButton("⚙ 管理")
        self.manage_custom_btn.clicked.connect(self.manage_custom_commands)
        self.manage_custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 10px;
                height: 25px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        control_layout.addWidget(self.manage_custom_btn)

        self.clear_custom_btn = QPushButton("🗑 清空")
        self.clear_custom_btn.clicked.connect(self.clear_custom_commands)
        self.clear_custom_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 10px;
                height: 25px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        control_layout.addWidget(self.clear_custom_btn)

        # 命令数量标签
        self.custom_count_label = QLabel("自定义: 0")
        self.custom_count_label.setStyleSheet("color: #6c757d; font-size: 10px; padding: 2px;")
        control_layout.addWidget(self.custom_count_label)

        control_layout.addStretch()

        # 右侧：自定义命令滚动区域
        self.custom_commands_scroll = QScrollArea()
        self.custom_commands_scroll.setWidgetResizable(True)
        self.custom_commands_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.custom_commands_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.custom_commands_scroll.setMinimumHeight(45)
        self.custom_commands_scroll.setMaximumHeight(45)
        self.custom_commands_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 3px;
                background-color: #f8f9fa;
            }
            QScrollArea > QWidget > QWidget {
                background-color: #f8f9fa;
            }
        """)

        # 滚动区域的内容部件
        self.custom_commands_container = QWidget()
        self.custom_commands_layout = QHBoxLayout(self.custom_commands_container)
        self.custom_commands_layout.setContentsMargins(3, 3, 3, 3)
        self.custom_commands_layout.setSpacing(3)
        self.custom_commands_layout.addStretch()

        self.custom_commands_scroll.setWidget(self.custom_commands_container)
        control_layout.addWidget(self.custom_commands_scroll, 3)

        layout.addLayout(control_layout)

        group.setLayout(layout)
        group.setMaximumHeight(70)
        return group

    def create_custom_command_button(self, command: CustomCommand) -> QPushButton:
        """创建自定义命令按钮"""
        btn = QPushButton(command.name)
        btn.setToolTip(f"点击发送: {command.command[:50]}{'...' if len(command.command) > 50 else ''}")
        btn.setMinimumHeight(28)
        btn.setMaximumHeight(28)
        btn.setMaximumWidth(120)

        # 设置样式
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #6610f2;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 10px;
                margin: 1px;
            }}
            QPushButton:hover {{
                background-color: #520dc2;
            }}
            QPushButton:pressed {{
                background-color: #450ba3;
            }}
            QPushButton::menu-indicator {{
                subcontrol-position: right center;
                padding-right: 3px;
            }}
        """)

        # 为按钮添加右键菜单
        btn.setContextMenuPolicy(Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(
            lambda pos, cmd=command, b=btn: self.show_custom_command_context_menu(cmd, b, pos))

        # 连接点击事件
        btn.clicked.connect(lambda checked, cmd=command.command: self.send_custom_command(cmd))

        return btn

    def show_custom_command_context_menu(self, command: CustomCommand, button: QPushButton, position):
        """显示自定义命令的右键菜单"""
        menu = QMenu(self)

        # 编辑命令
        edit_action = QAction("✏ 编辑", self)
        edit_action.triggered.connect(lambda: self.edit_custom_command(command))
        menu.addAction(edit_action)

        # 删除命令
        delete_action = QAction("🗑 删除", self)
        delete_action.triggered.connect(lambda: self.delete_custom_command(command))
        menu.addAction(delete_action)

        menu.addSeparator()

        # 查看命令内容
        view_action = QAction("👁 查看命令内容", self)
        view_action.triggered.connect(lambda: self.view_command_content(command))
        menu.addAction(view_action)

        # 在弹出位置显示菜单
        menu.exec(button.mapToGlobal(position))

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        # 全屏日志菜单项
        fullscreen_log_action = QAction("全屏日志窗口", self)
        fullscreen_log_action.triggered.connect(self.open_fullscreen_log)
        file_menu.addAction(fullscreen_log_action)

        file_menu.addSeparator()

        # 保存日志菜单项
        save_log_action = QAction("保存日志", self)
        save_log_action.triggered.connect(self.save_log)
        file_menu.addAction(save_log_action)

        file_menu.addSeparator()

        # 退出菜单项
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 视图菜单
        view_menu = menubar.addMenu("视图")

        # 面板控制
        toggle_param_action = QAction("切换到参数打印栏", self)
        toggle_param_action.triggered.connect(lambda: self.switch_panel("parameter"))
        view_menu.addAction(toggle_param_action)

        toggle_batch_action = QAction("切换到批量命令栏", self)
        toggle_batch_action.triggered.connect(lambda: self.switch_panel("batch"))
        view_menu.addAction(toggle_batch_action)

        view_menu.addSeparator()

        # 全屏日志菜单项
        view_menu.addAction(fullscreen_log_action)

    def create_log_group(self) -> QGroupBox:
        """创建日志输出组"""
        group = QGroupBox("📝 日志显示")
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 12, 8, 8)

        # 日志控制
        log_control_layout = QHBoxLayout()
        self.clear_log_btn = QPushButton("🗑 清空txt日志")
        self.clear_log_btn.clicked.connect(self.clear_log)

        self.save_log_btn = QPushButton("💾 保存txt日志")
        self.save_log_btn.clicked.connect(self.save_log)

        self.fullscreen_btn = QPushButton("📺 全屏查看")
        self.fullscreen_btn.setStyleSheet("background-color: #17a2b8; color: white;")
        self.fullscreen_btn.clicked.connect(self.open_fullscreen_log)

        # 创建复选框时设置初始状态
        self.log_to_excel_cb = QCheckBox("开始记录日志到EXCEL")
        self.log_to_excel_cb.setChecked(False)  # 初始未选中
        self.log_to_excel_cb.stateChanged.connect(self.toggle_log_to_excel)

        # 添加清除EXCEL日志按钮
        self.clear_excel_btn = QPushButton("🗑 清除EXCEL日志")
        self.clear_excel_btn.setStyleSheet("background-color: #dc3545; color: white;")
        self.clear_excel_btn.clicked.connect(self.clear_excel_log_data)
        self.clear_excel_btn.setEnabled(False)  # 初始状态下禁用
        self.clear_excel_btn.setToolTip("清除已记录的EXCEL日志数据")

        # 添加保存EXCEL按钮
        self.save_excel_btn = QPushButton("📊 保存EXCEL日志")
        self.save_excel_btn.setStyleSheet("background-color: #20c997; color: white;")
        self.save_excel_btn.clicked.connect(self.save_log_to_excel)
        self.save_excel_btn.setEnabled(False)  # 初始状态下禁用

        # 添加波形绘制按钮
        self.waveform_btn = QPushButton("📈 绘制波形")
        self.waveform_btn.setStyleSheet("background-color: #6f42c1; color: white;")
        self.waveform_btn.clicked.connect(self.open_waveform_window)
        self.waveform_btn.setToolTip("打开波形绘制窗口")

        log_control_layout.addWidget(self.clear_log_btn)
        log_control_layout.addWidget(self.save_log_btn)
        log_control_layout.addWidget(self.fullscreen_btn)
        log_control_layout.addWidget(self.waveform_btn)
        log_control_layout.addWidget(self.log_to_excel_cb)
        log_control_layout.addWidget(self.clear_excel_btn)
        log_control_layout.addWidget(self.save_excel_btn)
        log_control_layout.addStretch()
        layout.addLayout(log_control_layout)

        # 日志显示
        self.log_text = LogTextEdit()
        self.log_text.setFont(QFont("Consolas", 11))
        layout.addWidget(self.log_text, 1)

        group.setLayout(layout)
        return group

    def create_manual_group(self) -> QGroupBox:
        """创建手动指令组"""
        group = QGroupBox("⌨ 命令输入")
        layout = QHBoxLayout()

        # 使用自定义的CommandLineEdit，支持方向键浏览历史
        self.manual_cmd_edit = CommandLineEdit(self.command_history_manager)
        self.manual_cmd_edit.setPlaceholderText("输入指令后按Enter或点击发送...按上下方向键浏览历史命令")
        self.manual_cmd_edit.returnPressed.connect(self.send_manual_command)

        self.send_manual_btn = QPushButton("📤 发送")
        self.send_manual_btn.setStyleSheet("background-color: #007bff; color: white;")
        self.send_manual_btn.clicked.connect(self.send_manual_command)

        # 移除历史命令下拉框，改为简单的状态标签
        history_layout = QHBoxLayout()
        history_layout.addWidget(QLabel("历史:"))
        self.history_status_label = QLabel("(使用↑↓键浏览历史)")
        self.history_status_label.setStyleSheet("color: #6c757d; font-size: 11px;")
        history_layout.addWidget(self.history_status_label)

        layout.addWidget(self.manual_cmd_edit, 4)
        layout.addWidget(self.send_manual_btn, 1)
        layout.addLayout(history_layout, 2)

        group.setLayout(layout)
        return group

    def setup_styles(self):
        """设置全局样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                margin-top: 6px;
                padding-top: 10px;
                font-weight: bold;
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                font-size: 12px;
            }
            QLineEdit, QComboBox {
                border: 1px solid #ced4da;
                border-radius: 3px;
                padding: 4px;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #80bdff;
                outline: none;
            }
        """)

    def setup_connections(self):
        """设置信号槽连接"""
        self.parameter_timer.timeout.connect(self.update_parameter_values)

    # ============ 复用面板切换方法 ============
    def switch_panel(self, panel_name: str):
        """切换面板"""
        if panel_name == self.current_panel:
            return

        if panel_name == "parameter":
            self.panel_stack.setCurrentWidget(self.parameter_panel)
            self.current_panel = "parameter"
            self.parameter_panel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            self.batch_panel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            self.append_log_to_all("切换到参数打印栏", "blue")

        elif panel_name == "batch":
            self.panel_stack.setCurrentWidget(self.batch_panel)
            self.current_panel = "batch"
            self.batch_panel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            self.parameter_panel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            self.append_log_to_all("切换到批量命令栏", "blue")

    # ============ 波形窗口方法 ============
    def open_waveform_window(self):
        """打开波形绘制窗口"""
        if not self.waveform_window:
            self.waveform_window = WaveformWindow(self)

        self.waveform_window.show()
        self.waveform_window.raise_()
        self.waveform_window.activateWindow()

        self.append_log_to_all("打开波形绘制窗口", "blue")

    def on_waveform_window_closed(self):
        """波形窗口关闭时的处理"""
        self.waveform_window = None
        self.append_log_to_all("波形绘制窗口已关闭", "blue")

    def send_data_to_waveform(self, data_str: str):
        """发送数据到波形窗口"""
        if self.waveform_window and self.waveform_window.isVisible():
            # 先尝试从日志数据中添加
            self.waveform_window.add_data_from_log(data_str)

    # ============ 批量命令管理方法 ============
    def import_batch_commands(self):
        """导入批量命令"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入批量命令", "", "JSON文件 (*.json);;所有文件 (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    commands = json.load(f)

                # 清空现有表格
                self.batch_table.setRowCount(0)

                # 加载命令到表格
                for cmd in commands:
                    row = self.batch_table.rowCount()
                    self.batch_table.insertRow(row)

                    # 选择框
                    checkbox = QCheckBox()
                    checkbox.setChecked(cmd.get('is_selected', True))
                    self.batch_table.setCellWidget(row, 0, checkbox)

                    # 指令
                    cmd_item = QTableWidgetItem(cmd['command'])
                    self.batch_table.setItem(row, 1, cmd_item)

                    # 延时
                    delay_item = QTableWidgetItem(str(cmd.get('delay_ms', 0)))
                    self.batch_table.setItem(row, 2, delay_item)

                self.batch_commands = commands
                self.save_batch_commands()
                self.append_log_to_all(f"已从 {file_path} 导入 {len(commands)} 条批量命令", "green")

            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"导入失败: {str(e)}")

    def export_batch_commands(self):
        """导出批量命令"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存批量命令", "", "JSON文件 (*.json);;所有文件 (*)"
        )
        if file_path:
            try:
                commands = self.get_batch_commands_from_table()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(commands, f, ensure_ascii=False, indent=2)
                self.append_log_to_all(f"已保存 {len(commands)} 条批量命令到 {file_path}", "green")
            except Exception as e:
                QMessageBox.critical(self, "保存失败", f"保存失败: {str(e)}")

    def manage_batch_commands(self):
        """管理批量命令"""
        commands = self.get_batch_commands_from_table()
        dialog = BatchCommandManagerDialog(commands, self)
        if dialog.exec():
            updated_commands = dialog.get_commands()
            # 更新表格
            self.batch_table.setRowCount(0)
            for cmd in updated_commands:
                row = self.batch_table.rowCount()
                self.batch_table.insertRow(row)

                checkbox = QCheckBox()
                checkbox.setChecked(cmd['is_selected'])
                self.batch_table.setCellWidget(row, 0, checkbox)

                cmd_item = QTableWidgetItem(cmd['command'])
                self.batch_table.setItem(row, 1, cmd_item)

                delay_item = QTableWidgetItem(str(cmd['delay_ms']))
                self.batch_table.setItem(row, 2, delay_item)

            self.batch_commands = updated_commands
            self.save_batch_commands()

    def clear_batch_commands(self):
        """清空批量命令"""
        reply = QMessageBox.question(self, "确认清空",
                                     "确定要清空所有批量命令吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.batch_table.setRowCount(0)
            self.batch_commands = []
            self.save_batch_commands()
            self.append_log_to_all("已清空所有批量命令", "blue")

    def load_batch_commands(self):
        """从文件加载批量命令"""
        try:
            if os.path.exists(self.batch_commands_file):
                with open(self.batch_commands_file, 'r', encoding='utf-8') as f:
                    commands = json.load(f)

                # 如果启用了自动加载，则加载到表格
                if self.auto_load_cb.isChecked():
                    for cmd in commands:
                        row = self.batch_table.rowCount()
                        self.batch_table.insertRow(row)

                        checkbox = QCheckBox()
                        checkbox.setChecked(cmd.get('is_selected', True))
                        self.batch_table.setCellWidget(row, 0, checkbox)

                        cmd_item = QTableWidgetItem(cmd['command'])
                        self.batch_table.setItem(row, 1, cmd_item)

                        delay_item = QTableWidgetItem(str(cmd.get('delay_ms', 0)))
                        self.batch_table.setItem(row, 2, delay_item)

                self.batch_commands = commands
                self.append_log_to_all(f"已加载 {len(commands)} 条批量命令", "blue")
        except Exception as e:
            self.append_log_to_all(f"加载批量命令失败: {str(e)}", "red")

    def save_batch_commands(self):
        """保存批量命令到文件"""
        try:
            commands = self.get_batch_commands_from_table()
            with open(self.batch_commands_file, 'w', encoding='utf-8') as f:
                json.dump(commands, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.append_log_to_all(f"保存批量命令失败: {str(e)}", "red")

    def get_batch_commands_from_table(self) -> List[dict]:
        """从表格获取批量命令"""
        commands = []
        for row in range(self.batch_table.rowCount()):
            checkbox = self.batch_table.cellWidget(row, 0)
            cmd_item = self.batch_table.item(row, 1)
            delay_item = self.batch_table.item(row, 2)

            if cmd_item and cmd_item.text().strip():
                commands.append({
                    'command': cmd_item.text().strip(),
                    'delay_ms': int(delay_item.text()) if delay_item and delay_item.text().isdigit() else 0,
                    'is_selected': checkbox.isChecked() if checkbox else True
                })
        return commands

    # ============ 自定义命令管理方法 ============
    def add_custom_command(self):
        """添加自定义命令"""
        dialog = CustomCommandDialog(parent=self)
        if dialog.exec():
            new_command = dialog.get_command()
            if new_command.name and new_command.command:
                # 检查是否已存在同名命令
                for cmd in self.custom_commands:
                    if cmd.name == new_command.name:
                        reply = QMessageBox.question(self, "确认",
                                                     f"已存在名为 '{new_command.name}' 的命令，是否替换？",
                                                     QMessageBox.Yes | QMessageBox.No)
                        if reply == QMessageBox.No:
                            return
                        # 移除旧命令
                        self.custom_commands = [cmd for cmd in self.custom_commands if cmd.name != new_command.name]
                        break

                self.custom_commands.append(new_command)
                self.update_custom_commands_display()
                self.save_custom_commands()
                self.append_log_to_all(f"已添加自定义命令: {new_command.name}", "green")

    def edit_custom_command(self, command: CustomCommand):
        """编辑自定义命令"""
        dialog = CustomCommandDialog(command, self)
        if dialog.exec():
            updated_command = dialog.get_command()
            if updated_command.name and updated_command.command:
                # 更新命令
                for i, cmd in enumerate(self.custom_commands):
                    if cmd.name == command.name:
                        self.custom_commands[i] = updated_command
                        break

                self.update_custom_commands_display()
                self.save_custom_commands()
                self.append_log_to_all(f"已更新自定义命令: {updated_command.name}", "blue")

    def delete_custom_command(self, command: CustomCommand):
        """删除自定义命令"""
        reply = QMessageBox.question(self, "确认删除",
                                     f"确定要删除自定义命令 '{command.name}' 吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.custom_commands = [cmd for cmd in self.custom_commands if cmd.name != command.name]
            self.update_custom_commands_display()
            self.save_custom_commands()
            self.append_log_to_all(f"已删除自定义命令: {command.name}", "orange")

    def clear_custom_commands(self):
        """清空所有自定义命令"""
        if not self.custom_commands:
            return

        reply = QMessageBox.question(self, "确认清空",
                                     f"确定要清空所有 {len(self.custom_commands)} 个自定义命令吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.custom_commands.clear()
            self.update_custom_commands_display()
            self.save_custom_commands()
            self.append_log_to_all("已清空所有自定义命令", "orange")

    def manage_custom_commands(self):
        """管理自定义命令"""
        if not self.custom_commands:
            QMessageBox.information(self, "提示", "暂无自定义命令")
            return

        # 创建管理对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("管理自定义命令")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        # 表格
        table = QTableWidget(len(self.custom_commands), 3)
        table.setHorizontalHeaderLabels(["命令名称", "命令内容", "操作"])
        table.horizontalHeader().setStretchLastSection(True)

        for i, cmd in enumerate(self.custom_commands):
            # 名称
            name_item = QTableWidgetItem(cmd.name)
            table.setItem(i, 0, name_item)

            # 命令内容（显示前50个字符）
            content_preview = cmd.command[:50] + ("..." if len(cmd.command) > 50 else "")
            content_item = QTableWidgetItem(content_preview)
            content_item.setToolTip(cmd.command)
            table.setItem(i, 1, content_item)

            # 操作按钮
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.setContentsMargins(0, 0, 0, 0)

            edit_btn = QPushButton("编辑")
            edit_btn.clicked.connect(lambda checked, c=cmd: self.edit_custom_command_in_management(c, dialog))

            delete_btn = QPushButton("删除")
            delete_btn.setStyleSheet("background-color: #dc3545; color: white;")
            delete_btn.clicked.connect(lambda checked, c=cmd: self.delete_custom_command_in_management(c, dialog))

            button_layout.addWidget(edit_btn)
            button_layout.addWidget(delete_btn)
            button_layout.addStretch()

            table.setCellWidget(i, 2, button_widget)

        table.resizeColumnsToContents()
        layout.addWidget(table)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)

        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        dialog.exec()

    def edit_custom_command_in_management(self, command: CustomCommand, parent_dialog):
        """在管理对话框中编辑命令"""
        parent_dialog.close()
        self.edit_custom_command(command)

    def delete_custom_command_in_management(self, command: CustomCommand, parent_dialog):
        """在管理对话框中删除命令"""
        reply = QMessageBox.question(self, "确认删除",
                                     f"确定要删除自定义命令 '{command.name}' 吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.custom_commands = [cmd for cmd in self.custom_commands if cmd.name != command.name]
            self.update_custom_commands_display()
            self.save_custom_commands()
            self.append_log_to_all(f"已删除自定义命令: {command.name}", "orange")
            parent_dialog.close()
            self.manage_custom_commands()

    def view_command_content(self, command: CustomCommand):
        """查看命令内容"""
        QMessageBox.information(self, f"命令内容: {command.name}",
                                f"命令: {command.command}")

    def send_custom_command(self, command: str):
        """发送自定义命令"""
        if not self.is_connected:
            QMessageBox.warning(self, "警告", "请先连接串口")
            return

        self.send_command(command)

    def update_custom_commands_display(self):
        """更新自定义命令显示"""
        # 清除现有按钮
        for button in self.custom_command_buttons:
            button.deleteLater()
        self.custom_command_buttons.clear()

        # 添加新按钮
        for command in self.custom_commands:
            button = self.create_custom_command_button(command)
            self.custom_command_buttons.append(button)
            # 在布局的倒数第二个位置插入按钮（在stretch之前）
            self.custom_commands_layout.insertWidget(self.custom_commands_layout.count() - 1, button)

        # 更新计数标签
        self.custom_count_label.setText(f"自定义: {len(self.custom_commands)}")

    def load_custom_commands(self):
        """从文件加载自定义命令"""
        try:
            if os.path.exists(self.custom_commands_file):
                with open(self.custom_commands_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.custom_commands = [CustomCommand(**cmd) for cmd in data]
                    self.update_custom_commands_display()
                    self.append_log_to_all(f"已加载 {len(self.custom_commands)} 个自定义命令", "blue")
        except Exception as e:
            self.append_log_to_all(f"加载自定义命令失败: {str(e)}", "red")

    def save_custom_commands(self):
        """保存自定义命令到文件"""
        try:
            data = [{"name": cmd.name, "command": cmd.command} for cmd in self.custom_commands]
            with open(self.custom_commands_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.append_log_to_all(f"保存自定义命令失败: {str(e)}", "red")

    # ============ 全屏日志窗口方法 ============

    def open_fullscreen_log(self):
        """打开全屏日志窗口"""
        if not self.fullscreen_log_window:
            self.fullscreen_log_window = FullScreenLogWindow(self)
            # 连接命令发送信号
            self.fullscreen_log_window.command_sent.connect(self.send_command_from_fullscreen)

            # 将现有日志内容复制到全屏窗口
            full_log_content = self.log_text.toPlainText()
            if full_log_content:
                # 逐行添加以保持格式
                lines = full_log_content.split('\n')
                for line in lines:
                    if line.strip():
                        self.fullscreen_log_window.append_log(line)

            # 使用命令历史管理器
            history_commands = self.command_history_manager.get_all()
            for command in history_commands:
                self.fullscreen_log_window.add_to_history(command)

        self.fullscreen_log_window.show()
        self.fullscreen_log_window.raise_()
        self.fullscreen_log_window.activateWindow()
        self.fullscreen_log_window.command_edit.setFocus()

    def send_command_from_fullscreen(self, command: str):
        """从全屏窗口发送命令"""
        # 在主窗口的历史记录中添加
        self.add_to_history(command)

        # 发送命令
        self.send_command(command)

    def on_fullscreen_log_closed(self):
        """全屏日志窗口关闭时的处理"""
        self.fullscreen_log_window = None

    def append_log_to_all(self, text: str, color: str = "black"):
        """同时向主窗口和全屏窗口添加日志"""
        # 向主窗口添加
        self.append_log(text, color)

        # 如果全屏窗口存在，也向其添加
        if self.fullscreen_log_window and self.fullscreen_log_window.isVisible():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
            log_text = f"{timestamp} {text}"
            self.fullscreen_log_window.append_log(log_text)

    # ============ 参数说明信息管理方法 ============
    def load_parameter_descriptions(self):
        """从文件加载参数说明信息"""
        try:
            if os.path.exists(self.parameter_description_file):
                with open(self.parameter_description_file, 'r', encoding='utf-8') as f:
                    self.parameter_descriptions = json.load(f)
                    self.append_log_to_all(f"已加载 {len(self.parameter_descriptions)} 条参数说明", "blue")
            else:
                self.parameter_descriptions = {}
                self.append_log_to_all("未找到参数说明文件，将创建新文件", "orange")
        except Exception as e:
            self.parameter_descriptions = {}
            self.append_log_to_all(f"加载参数说明失败: {str(e)}", "red")

    def save_parameter_descriptions(self):
        """保存参数说明信息到文件"""
        try:
            with open(self.parameter_description_file, 'w', encoding='utf-8') as f:
                json.dump(self.parameter_descriptions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.append_log_to_all(f"保存参数说明失败: {str(e)}", "red")

    def get_description_for_parameter(self, param_name: str) -> str:
        """获取参数的说明信息"""
        return self.parameter_descriptions.get(param_name, "")

    def set_description_for_parameter(self, param_name: str, description: str):
        """设置参数的说明信息"""
        if description:
            self.parameter_descriptions[param_name] = description
        elif param_name in self.parameter_descriptions:
            del self.parameter_descriptions[param_name]

    def on_parameter_item_changed(self, item):
        """参数表格项改变事件"""
        if item.column() == 5:  # 说明列（索引5）
            # 获取参数名
            row = item.row()
            param_name_item = self.param_table.item(row, 2)  # 参数名在第2列
            if param_name_item:
                param_name = param_name_item.text()
                description = item.text()

                # 更新参数说明信息
                self.set_description_for_parameter(param_name, description)

                # 保存到文件
                self.save_parameter_descriptions()

    # ============ 核心功能方法 ============
    def refresh_ports(self):
        """刷新串口列表"""
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            self.port_combo.clear()
            self.port_combo.addItems(ports)
            if ports:
                self.port_combo.setCurrentIndex(0)
                self.append_log_to_all(f"发现 {len(ports)} 个串口", "blue")
            else:
                self.append_log_to_all("未发现可用串口", "orange")
        except Exception as e:
            self.append_log_to_all(f"刷新串口失败: {str(e)}", "red")

    def connect_serial(self):
        """连接串口"""
        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "警告", "请选择串口端口")
            return

        try:
            baudrate = int(self.baud_combo.currentText())
            timeout = float(self.timeout_edit.text())

            # 创建串口线程
            self.serial_reader = SerialReader(port, baudrate, timeout)
            self.serial_reader.data_received.connect(self.on_data_received)
            self.serial_reader.error_occurred.connect(self.on_receive_error)
            self.serial_reader.connection_status.connect(self.on_connection_status)
            self.serial_reader.start()

            # 更新UI状态
            self.connect_btn.setEnabled(False)
            self.port_combo.setEnabled(False)
            self.timeout_edit.setEnabled(False)
            self.refresh_btn.setEnabled(False)
            self.baud_combo.setEnabled(False)
            self.disconnect_btn.setEnabled(True)

        except ValueError as e:
            QMessageBox.critical(self, "错误", f"参数错误: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接失败: {str(e)}")

    def disconnect_serial(self):
        """断开串口连接"""
        if self.serial_reader:
            self.serial_reader.stop()
            self.serial_reader = None

        self.is_connected = False
        self.status_label.setText("状态: 已断开")

        # 更新UI状态
        self.port_combo.setEnabled(True)
        self.timeout_edit.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.baud_combo.setEnabled(True)
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)

        # 停止监控
        self.stop_monitoring()

        self.append_log_to_all("串口已断开", "blue")

    def on_connection_status(self, connected: bool, message: str):
        """处理连接状态"""
        self.is_connected = connected
        color = "green" if connected else "red"
        self.append_log_to_all(message, color)
        self.status_label.setText(f"状态: {message}")

    def send_command(self, command: str, is_batch: bool = False) -> bool:
        """发送命令"""
        if not self.is_connected or not self.serial_reader:
            self.append_log_to_all("未连接串口", "red")
            return False

        try:
            if command == 'info -a':
                self.info_a_flag = True
            else:
                self.info_a_flag = False
            success = self.serial_reader.send_command(command)
            if success:
                self.append_log_to_all(f" {command.strip()}", "green")     #增添send内容
                if not is_batch and command.strip():
                    # 添加到历史记录管理器
                    self.command_history_manager.add_command(command.strip())

                    # 广播给插件
                    if self.plugin_manager:
                        self.plugin_manager.broadcast_data_sent(command)

            return success
        except Exception as e:
            self.append_log_to_all(f"发送失败: {str(e)}", "red")
            return False

    def add_to_history(self, command: str):
        """添加到历史记录"""
        # 使用新的历史记录管理器
        self.command_history_manager.add_command(command)

        # 同时添加到全屏窗口
        if self.fullscreen_log_window:
            self.fullscreen_log_window.add_to_history(command)

    def send_manual_command(self):
        """发送手动指令"""
        cmd = self.manual_cmd_edit.text().strip()
        if not cmd:
            return

        self.send_command(cmd)
        self.manual_cmd_edit.clear()

    # ============ 参数管理方法 ============
    def init_parameter(self):
        """初始化参数"""
        if not self.is_connected:
            QMessageBox.warning(self, "警告", "请先连接串口")
            return

        # 清空现有参数
        self.parameters.clear()
        self.param_table.setRowCount(0)
        self.info_a_count = 0
        self.info_a_flag = False

        # 发送初始化命令
        self.send_command("<QUIT>")

        time.sleep(0.5)

        # 设置标志，准备接收参数
        self.info_a_flag = True
        self.send_command("info -a")

        self.append_log_to_all("开始初始化参数...", "blue")

    def update_parameter_values(self):
        """更新参数值（定时器触发）"""
        # 定时更新参数值
        if self.parameters:
            # 可以定期发送获取参数值的命令
            pass

    def start_monitoring(self):
        """开始监控"""
        if not self.parameters:
            QMessageBox.warning(self, "警告", "请先初始化参数")
            return

        # 获取选中的参数ID
        selected_ids = self.get_selected_parameter_ids()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请选择要打印的参数")
            return

        try:
            # 获取监控频率
            frequency = int(self.freq_edit.text())
            self.monitor_frequency = frequency

            # 构建监控命令: mon -m{频率} /参数ID1/参数ID2/...
            id_list = '/'.join(map(str, selected_ids))
            monitor_cmd = f"mon -m{frequency} /{id_list}"

            # 发送监控命令
            if self.send_command(monitor_cmd):
                self.is_monitoring = True

                # 更新参数监控状态
                for param in self.parameters:
                    if param.id in selected_ids:
                        param.is_monitoring = True

                # 更新表格中的状态显示
                self.update_monitoring_status()

                # 更新按钮状态
                self.start_monitor_btn.setEnabled(True)
                self.stop_monitor_btn.setEnabled(True)

                self.append_log_to_all(f"开始打印参数: {id_list}", "green")
                self.update_parameter_stats()

        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的监控频率")

    def stop_monitoring(self):
        """停止监控"""
        # 发送停止命令
        if self.send_command("\\"):
            self.is_monitoring = False

            # 更新参数监控状态
            for param in self.parameters:
                param.is_monitoring = False

            # 更新表格中的状态显示
            self.update_monitoring_status()

            # 更新按钮状态
            self.start_monitor_btn.setEnabled(True)
            self.stop_monitor_btn.setEnabled(True)

            self.append_log_to_all("停止打印参数", "blue")
            self.update_parameter_stats()

    def get_selected_parameter_ids(self) -> List[int]:
        """获取选中的参数ID列表"""
        selected_ids = []

        for row in range(self.param_table.rowCount()):
            checkbox = self.param_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                id_item = self.param_table.item(row, 1)
                if id_item:
                    try:
                        selected_ids.append(int(id_item.text()))
                    except ValueError:
                        continue

        return sorted(selected_ids)  # 返回排序后的ID列表

    def update_monitoring_status(self):
        """更新监控状态显示"""
        for row in range(self.param_table.rowCount()):
            id_item = self.param_table.item(row, 1)
            if id_item:
                try:
                    param_id = int(id_item.text())
                    # 找到对应的参数
                    param = next((p for p in self.parameters if p.id == param_id), None)
                    if param:
                        # 更新状态列
                        status_item = QTableWidgetItem("打印中" if param.is_monitoring else "未打印")
                        if param.is_monitoring:
                            status_item.setForeground(QBrush(QColor("green")))
                        else:
                            status_item.setForeground(QBrush(QColor("gray")))
                        self.param_table.setItem(row, 4, status_item)
                except ValueError:
                    continue

    def select_all_parameters(self):
        """全选参数"""
        for row in range(self.param_table.rowCount()):
            checkbox = self.param_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)
        self.update_parameter_stats()

    def clear_parameter_selection(self):
        """清空参数选择"""
        for row in range(self.param_table.rowCount()):
            checkbox = self.param_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
        self.update_parameter_stats()

    def update_parameter_stats(self):
        """更新参数统计"""
        selected_count = 0
        monitoring_count = 0

        for param in self.parameters:
            if param.is_selected:
                selected_count += 1
            if param.is_monitoring:
                monitoring_count += 1

        self.param_count_label.setText(f"参数总数: {len(self.parameters)}")
        self.selected_count_label.setText(f"已选择: {selected_count}")
        self.monitoring_count_label.setText(f"打印中: {monitoring_count}")

    # ============ 批量指令管理方法 ============
    def add_batch_command(self):
        """添加批量指令"""
        row = self.batch_table.rowCount()
        self.batch_table.insertRow(row)

        # 选择框
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(self.update_batch_selection)
        self.batch_table.setCellWidget(row, 0, checkbox)

        # 指令输入
        cmd_item = QTableWidgetItem("")
        self.batch_table.setItem(row, 1, cmd_item)

        # 延时输入（毫秒）
        delay_item = QTableWidgetItem("0")
        self.batch_table.setItem(row, 2, delay_item)

        self.batch_table.scrollToBottom()

    def delete_selected_commands(self):
        """删除选中指令"""
        rows_to_delete = []
        for row in range(self.batch_table.rowCount()):
            checkbox = self.batch_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                rows_to_delete.append(row)

        for row in reversed(rows_to_delete):
            self.batch_table.removeRow(row)

        if rows_to_delete:
            self.append_log_to_all(f"删除了 {len(rows_to_delete)} 条指令", "blue")

    def select_all_commands(self):
        """全选指令"""
        for row in range(self.batch_table.rowCount()):
            checkbox = self.batch_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)

    def deselect_all_commands(self):
        """取消全选"""
        for row in range(self.batch_table.rowCount()):
            checkbox = self.batch_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)

    def update_batch_selection(self):
        """更新批量指令选择状态"""
        selected_count = 0
        for row in range(self.batch_table.rowCount()):
            checkbox = self.batch_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                selected_count += 1
        self.send_cmd_btn.setText(f"📤 发送选中({selected_count})")

    def send_selected_commands(self):
        """发送选中指令（使用线程）"""
        if not self.is_connected:
            QMessageBox.warning(self, "警告", "请先连接串口")
            return

        commands_to_send = []
        for row in range(self.batch_table.rowCount()):
            checkbox = self.batch_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                cmd_item = self.batch_table.item(row, 1)
                if cmd_item and cmd_item.text().strip():
                    # 获取延时时间（毫秒）
                    delay_item = self.batch_table.item(row, 2)
                    delay_ms = 0
                    if delay_item and delay_item.text().strip():
                        try:
                            delay_ms = int(delay_item.text())
                        except ValueError:
                            delay_ms = 0

                    commands_to_send.append({
                        'command': cmd_item.text().strip(),
                        'delay_ms': delay_ms
                    })

        if not commands_to_send:
            QMessageBox.warning(self, "警告", "没有选中的有效指令")
            return

        # 获取循环模式
        loop_count = -1 if self.infinite_loop_radio.isChecked() else self.loop_spin.value()
        # 获取执行模式
        exec_mode_str = self.exec_mode_combo.currentText()
        exec_mode = "exec_first" if exec_mode_str == "先执行后延时" else "delay_first"

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(100)  # 百分比显示
        self.progress_bar.setValue(0)
        self.progress_label.setText("准备发送...")

        # 更新按钮状态
        self.send_cmd_btn.setVisible(False)
        self.stop_cmd_btn.setVisible(True)
        self.add_cmd_btn.setEnabled(False)
        self.del_cmd_btn.setEnabled(False)
        self.select_all_btn_batch.setEnabled(False)
        self.deselect_all_btn.setEnabled(False)
        self.import_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.manage_btn.setEnabled(False)
        self.clear_batch_btn.setEnabled(False)

        # 创建并启动批量发送线程
        self.batch_thread = BatchCommandSender(commands_to_send, loop_count, exec_mode)
        self.batch_thread.progress_updated.connect(self.on_batch_progress_updated)
        self.batch_thread.current_command_highlight.connect(self.on_current_command_highlight)
        self.batch_thread.finished.connect(self.on_batch_finished)
        self.batch_thread.error_occurred.connect(self.on_batch_error)
        self.batch_thread.start()

    def stop_batch_sending(self):
        """停止批量发送"""
        if self.batch_thread and self.batch_thread.isRunning():
            self.batch_thread.stop()
            self.append_log_to_all("批量发送已终止", "orange")
            self.on_batch_finished()

    def on_batch_progress_updated(self, progress: int, current_command: str, current_loop: int):
        """批量发送进度更新"""
        self.progress_bar.setValue(progress)

        # 更新状态标签
        if self.infinite_loop_radio.isChecked():
            loop_text = f"无限循环 - 第{current_loop}轮"
        else:
            loop_text = f"{current_loop}/{self.loop_spin.value()}"
        self.progress_label.setText(f"进度: {progress}% | 循环: {loop_text} | 模式: {self.exec_mode_combo.currentText()}")

        # 发送当前命令
        if current_command and not current_command.startswith("循环"):
            self.send_command(current_command, is_batch=True)

    def on_current_command_highlight(self, row_index: int, highlight: bool):
        """当前命令高亮显示（行高亮）"""
        if row_index < 0 or row_index >= self.batch_table.rowCount():
            return

        # 遍历该行的所有列，设置背景色
        for col in range(self.batch_table.columnCount()):
            item = self.batch_table.item(row_index, col)
            # 如果是第0列，获取QTableWidgetItem用于设置背景色
            if col == 0:
                # 对于第0列，只能通过其他方式设置背景色
                # 创建一个临时项来设置背景色
                temp_item = self.batch_table.item(row_index, 1)  # 使用第1列的项
                if not temp_item:
                    temp_item = QTableWidgetItem()
                    self.batch_table.setItem(row_index, 1, temp_item)

                if highlight:
                    # 高亮显示为绿色
                    temp_item.setBackground(QBrush(QColor("#d4edda")))  # 浅绿色背景
                    # 同时设置其他列的项
                    for c in range(self.batch_table.columnCount()):
                        item_col = self.batch_table.item(row_index, c)
                        if item_col:
                            item_col.setBackground(QBrush(QColor("#d4edda")))
                else:
                    # 恢复原样
                    # 根据行号设置交替颜色
                    if row_index % 2 == 0:
                        bg_color = QColor("white")
                    else:
                        bg_color = QColor("#f8f9fa")

                    for c in range(self.batch_table.columnCount()):
                        item_col = self.batch_table.item(row_index, c)
                        if item_col:
                            item_col.setBackground(QBrush(bg_color))

                # 确保更新显示
                self.batch_table.viewport().update()
                break

    def on_batch_finished(self):
        """批量发送完成"""
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")

        # 恢复按钮状态
        self.send_cmd_btn.setVisible(True)
        self.stop_cmd_btn.setVisible(False)
        self.add_cmd_btn.setEnabled(True)
        self.del_cmd_btn.setEnabled(True)
        self.select_all_btn_batch.setEnabled(True)
        self.deselect_all_btn.setEnabled(True)
        self.import_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.manage_btn.setEnabled(True)
        self.clear_batch_btn.setEnabled(True)

        # 清理线程
        if self.batch_thread:
            self.batch_thread.wait()
            self.batch_thread = None

        # 清除所有高亮
        for row in range(self.batch_table.rowCount()):
            for col in range(self.batch_table.columnCount()):
                item = self.batch_table.item(row, col)
                if item:
                    # 根据行号设置交替颜色
                    if row % 2 == 0:
                        item.setBackground(QBrush(QColor("white")))
                    else:
                        item.setBackground(QBrush(QColor("#f8f9fa")))

    def on_batch_error(self, error_msg: str):
        """批量发送错误"""
        self.append_log_to_all(error_msg, "red")
        self.on_batch_finished()

    # ============ EXCEL日志记录方法 ============
    def toggle_log_to_excel(self, state: int):
        """切换EXCEL日志记录"""
        if state == Qt.CheckState.Checked.value:  # 使用 CheckState.Checked 的值
            # 复选框被选中 - 开始记录
            self.excel_log_enabled = True
            self.save_excel_btn.setEnabled(True)
            self.clear_excel_btn.setEnabled(True)  # 启用清除按钮
            self.append_log_to_all("开始记录日志到EXCEL", "green")

            # 记录开始时间
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            start_record = {
                "时间戳": timestamp,
                "原始数据": "=== 开始记录EXCEL日志 ==="
            }
            self.excel_log_data.append(start_record)

            # 更新复选框文本
            self.log_to_excel_cb.setText("停止记录日志到EXCEL")
            self.status_label.setText(f"状态: 正在记录EXCEL日志 - 已记录 {len(self.excel_log_data)} 条")

        else:
            # 复选框被取消选中 - 停止记录
            self.excel_log_enabled = False
            self.save_excel_btn.setEnabled(True)  # 仍然允许保存已记录的数据
            self.clear_excel_btn.setEnabled(True)  # 仍然允许清除已记录的数据

            # 记录结束时间
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            end_record = {
                "时间戳": timestamp,
                "原始数据": "=== 停止记录EXCEL日志 ==="
            }
            self.excel_log_data.append(end_record)

            self.append_log_to_all("停止记录日志到EXCEL", "blue")

            # 更新复选框文本
            self.log_to_excel_cb.setText("开始记录日志到EXCEL")

            # 如果已经有数据，提示用户保存
            if len(self.excel_log_data) > 2:  # 排除开始和结束记录
                self.status_label.setText(f"状态: 已停止记录 - 有 {len(self.excel_log_data) - 2} 条数据待保存")
            else:
                self.status_label.setText("状态: 记录已停止")

    def clear_excel_log_data(self):
        """清除已记录的EXCEL日志数据"""
        if not self.excel_log_data:
            QMessageBox.information(self, "提示", "没有可清除的EXCEL日志数据")
            return

        # 获取当前记录条数
        data_count = len(self.excel_log_data)
        if data_count > 2:  # 排除开始和结束记录
            actual_count = data_count - 2
        else:
            actual_count = data_count

        # 询问确认
        reply = QMessageBox.question(
            self, "确认清除",
            f"确定要清除已记录的 {actual_count} 条EXCEL日志数据吗？\n\n"
            "注意：清除后数据将无法恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 保存清除前的状态
            was_enabled = self.excel_log_enabled

            # 清空数据
            self.excel_log_data.clear()

            # 如果之前是正在记录状态，重新添加开始记录标记
            if was_enabled:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                start_record = {
                    "时间戳": timestamp,
                    "原始数据": "=== 开始记录EXCEL日志 ==="
                }
                self.excel_log_data.append(start_record)

                self.append_log_to_all("已清除EXCEL日志数据，重新开始记录", "orange")
                self.status_label.setText(f"状态: 正在记录EXCEL日志 - 已记录 1 条")
            else:
                self.append_log_to_all(f"已清除 {actual_count} 条EXCEL日志数据", "orange")
                self.status_label.setText("状态: EXCEL日志数据已清除")

            # 更新按钮状态
            if not self.excel_log_data:
                self.save_excel_btn.setEnabled(False)
                self.clear_excel_btn.setEnabled(False)

    def extract_variables_from_data(self, data: str) -> Tuple[str, Dict[str, str]]:
        """
        从接收到的数据中提取变量名和值
        返回格式: (原始数据, {变量名: 值})
        """
        variables = {}

        #  解析参数格式（如**chgVolt(mV) :0 **batTemp :212）
        kv_pattern = r'\*\*(\w+(?:\([^)]+\))?)\s*:\s*([^\s*]+)'
        kv_matches = re.findall(kv_pattern, data)
        if kv_matches:
            for var_name, var_value in kv_matches:
                variables[var_name] = int(var_value)
            if variables:
                return data, variables

        if not self.info_a_flag:
            kv_pattern = r'(\w+(?:\([^)]+\))?)\s*:\s*([^\s*]+)'
            kv_matches = re.findall(kv_pattern, data)
            if kv_matches:
                for var_name, var_value in kv_matches:
                    variables[var_name] = int(var_value)
                if variables:
                    return data, variables

        return data, variables

    @Slot(str)
    def on_data_received(self, data: str):
        """处理接收到的数据"""
        # 处理info -a期间的参数提取
        if self.info_a_flag:
            # 解析参数格式如
            pattern = r'\*(\d+)\s+Var:(\w+(?:\([^\)]+\))?)\s*.*Val:(-*\d+)\s*'
            match = re.match(pattern, data)
            if match:
                param_id = int(match.group(1))
                param_name = match.group(2)
                param_value = int(match.group(3))
                existing_param = next((p for p in self.parameters if p.id == param_id), None)
                if not existing_param:
                    param = Parameter(
                        id=param_id,
                        name=param_name,
                        value=param_value,
                        is_selected=False
                    )
                    self.parameters.append(param)
                    self.add_parameter_to_table(param)

        # 显示所有接收到的数据
        self.append_log_to_all(f" {data}", "black")         # 增添received

        # 如果启用了EXCEL日志记录，提取变量信息
        if self.excel_log_enabled:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")[:-3]
            original_data, variables = self.extract_variables_from_data(data)

            # 构建日志记录
            log_record = {
                "时间戳": timestamp,
                "原始数据": original_data
            }

            # 添加提取的变量
            if variables:
                for var_name, var_value in variables.items():
                    log_record[var_name] = var_value

            self.excel_log_data.append(log_record)

            # 更新状态栏显示当前记录的变量数量
            if variables:
                var_count = len(variables)
                self.status_label.setText(f"状态: 正在记录EXCEL日志 - 已记录 {len(self.excel_log_data)} 条")

        # 发送数据到波形窗口
        self.send_data_to_waveform(data)

        # 解析参数值，添加到波形窗口
        try:
            # 匹配各种数据格式
            # 参数名: 值
            if ':' in data and not data.startswith('*'):
                # 键值对正则匹配
                kv_pattern = r'(\w+)\s*:\s*(-?\d+)'
                matches = re.findall(kv_pattern, data)
                for param_name, value_str in matches:
                    value = float(value_str)

                    # 发送到波形窗口
                    if self.waveform_window and self.waveform_window.isVisible():
                        self.waveform_window.add_data_point(param_name, value)

            # **参数名: 值
            elif data.startswith('**'):
                # 键值对kv_pattern正则匹配
                kv_pattern = r'\*\*(\w+(?:\([^)]+\))?)\s*:\s*([^\s*]+)'
                matches = re.findall(kv_pattern, data)
                for param_name, value_str in matches:
                    value = float(value_str)
                    # 发送到波形窗口
                    if self.waveform_window and self.waveform_window.isVisible():
                        self.waveform_window.add_data_point(param_name, value)

        except Exception as e:
            # 解析失败不显示错误
            pass

        # 广播给插件
        if self.plugin_manager:
            self.plugin_manager.broadcast_data_received(data)

    def save_log_to_excel(self):
        """保存日志到EXCEL文件"""
        if not self.excel_log_data:
            QMessageBox.warning(self, "警告", "没有可保存的日志数据")
            return
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"serial_log_{timestamp}.xlsx"

            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存日志到EXCEL", default_filename,
                "Excel文件 (*.xlsx);;所有文件 (*)"
            )
            if file_path:
                # 确保文件扩展名
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'

                # 转换为DataFrame
                df = pd.DataFrame(self.excel_log_data)

                # 重新排列列，使时间戳和原始数据在前
                cols = ["时间戳", "原始数据"]
                other_cols = [col for col in df.columns if col not in cols]
                df = df[cols + other_cols]

                # 保存到Excel
                with pd.ExcelWriter(f'{file_path}', engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name=f'打印数据', index=False)
                    workbook = writer.book
                    worksheet = writer.sheets[f'打印数据']

                    # 根据单元格内容自动调整列宽
                    for i, col in enumerate(df.columns):
                        column_width = max(len(str(col)), df[col].astype(str).map(len).max())
                        worksheet.set_column(i, i, column_width + 2)  # 设置第 i 列宽度
                    # 冻结第一行
                    worksheet.freeze_panes(1, 0)
                    # 隐藏B列
                    worksheet.set_column('B:B', None, None, {'hidden': True})

                self.append_log_to_all(f"已保存 {len(self.excel_log_data)} 条日志到EXCEL文件: {file_path}", "green")
                QMessageBox.information(self, "保存成功", f"日志已保存到EXCEL文件:\n{file_path}")

                # 清空已保存的数据
                self.excel_log_data.clear()
                self.status_label.setText("状态: 日志已保存到EXCEL")

                # 更新按钮状态
                self.save_excel_btn.setEnabled(False)
                self.clear_excel_btn.setEnabled(False)

                # 如果之前是记录状态，重新开始记录
                if self.excel_log_enabled:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    start_record = {
                        "时间戳": timestamp,
                        "原始数据": "=== 开始记录EXCEL日志 ==="
                    }
                    self.excel_log_data.append(start_record)
                    self.save_excel_btn.setEnabled(True)
                    self.clear_excel_btn.setEnabled(True)

        except Exception as e:
            error_msg = f"保存EXCEL日志失败: {str(e)}"
            self.append_log_to_all(error_msg, "red")
            QMessageBox.critical(self, "保存失败", error_msg)

    # ============ 提取参数到参数打印栏 ============
    def add_parameter_to_table(self, param: Parameter):
        """添加参数到表格"""
        row = self.param_table.rowCount()
        self.param_table.insertRow(row)

        # 选择框（默认不选中）
        checkbox = QCheckBox()
        checkbox.setChecked(param.is_selected)
        checkbox.stateChanged.connect(lambda checked, p=param: self.on_parameter_checkbox_changed(p, checked))
        checkbox.stateChanged.connect(self.update_parameter_stats)
        self.param_table.setCellWidget(row, 0, checkbox)

        # ID
        id_item = QTableWidgetItem(str(param.id))
        id_item.setTextAlignment(Qt.AlignCenter)
        self.param_table.setItem(row, 1, id_item)

        # 参数名
        name_item = QTableWidgetItem(param.name)
        self.param_table.setItem(row, 2, name_item)

        # 当前值
        value_item = QTableWidgetItem(str(param.value))
        value_item.setTextAlignment(Qt.AlignCenter)
        self.param_table.setItem(row, 3, value_item)

        # 状态
        status_item = QTableWidgetItem("未打印")
        status_item.setForeground(QBrush(QColor("gray")))
        self.param_table.setItem(row, 4, status_item)

        # 说明列 - 从已加载的说明信息中获取
        description = self.get_description_for_parameter(param.name)
        description_item = QTableWidgetItem(description)
        description_item.setToolTip(description if description else "双击添加说明")
        self.param_table.setItem(row, 5, description_item)

        # 更新统计
        self.update_parameter_stats()

    def on_parameter_checkbox_changed(self, param: Parameter, checked: bool):
        """参数复选框状态改变"""
        param.is_selected = checked

    @Slot(str)
    def on_receive_error(self, error_msg: str):
        """处理接收错误"""
        self.append_log_to_all(f"错误: {error_msg}", "red")

    def append_log(self, text: str, color: str = "black"):
        """添加日志到主窗口"""
        self.log_text.append_log(text, color)

    def clear_log(self):
        """清空日志"""
        self.log_text.clear_log()
        self.append_log_to_all("日志已清空", "blue")

        # 同时清空EXCEL日志数据
        if self.excel_log_data:
            self.excel_log_data.clear()
            self.status_label.setText("状态: 日志已清空")
            self.save_excel_btn.setEnabled(False)
            self.clear_excel_btn.setEnabled(False)

    def save_log(self):
        """保存日志到文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存日志", f"serial_log_{timestamp}.txt",
                "文本文件 (*.txt);;所有文件 (*)"
            )

            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.append_log_to_all(f"日志已保存到: {file_path}", "green")
        except Exception as e:
            self.append_log_to_all(f"保存日志失败: {str(e)}", "red")

    # 显式关闭
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.disconnect_serial()
        if self.log_file:
            self.log_file.close()
        if self.fullscreen_log_window:
            self.fullscreen_log_window.close()
        if self.waveform_window:
            self.waveform_window.close()
        if self.batch_thread and self.batch_thread.isRunning():
            self.batch_thread.stop()
            self.batch_thread.wait()
        self.parameter_timer.stop()
        self.save_custom_commands()
        self.save_batch_commands()
        self.save_parameter_descriptions()  # 保存参数说明信息

        # 清理插件系统
        if self.plugin_manager:
            self.plugin_manager.cleanup()

        event.accept()

def main():
    """主函数"""
    if sys.platform == "win32":
        import ctypes
        #
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com..serialtool")

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon("666.ico"))
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    window = SerialTool()
    window.setWindowTitle("硬测工具包")
    window.setWindowIcon(QIcon("666.ico"))
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()