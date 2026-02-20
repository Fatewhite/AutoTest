"""
基于加减乘除的简易计算器插件
作者: WJW^_^
版本: 1.0.1
功能: 提供计算器功能便于计算
"""

from PySide6.QtWidgets import (QDialog, QFrame, QLineEdit, QVBoxLayout, 
                               QGridLayout, QPushButton, QMenuBar, QMenu)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFont, QKeyEvent
import sys
import re
import json
import os
import pandas as pd
from datetime import datetime
from collections import deque

class CaculatorPlugin(BasePlugin):
    """计算器插件"""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.name = "计算器"
        self.version = "1.0.1"
        self.author = "WJW^_^"
        self.description = "提供基于加减乘除的计算器功能"
        self.icon = "📏"     #计算器的图标
        # self.hotkey = "Ctrl+L"
        
        self.dialog = None
    
    def initialize(self):
        # 初始化插件
        
        print(f"插件 {self.name} 初始化")
        
        # 创建默认配置文件目录
        self.plugin_config_dir = os.path.join(os.path.dirname(__file__), "configs")
        os.makedirs(self.plugin_config_dir, exist_ok=True)

        # 插件配置文件
        self.config_file = os.path.join(self.plugin_config_dir, "calculator_config.json")
        
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
        """创建主程序的插件UI"""
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 插件标题
        title_label = QLabel("📏 计算器")
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
        1. 支持基于加减乘除的简单计算功能
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
        quick_btn = QPushButton("📏 打开计算器")
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
        quick_btn.clicked.connect(self.open_calculator_tool)
        layout.addWidget(quick_btn)
        
        # 添加占位空间
        layout.addStretch()

        return widget
        
    def get_menu_actions(self):
        """创建主程序菜单栏"""
        
        actions = []
        
        #打开计算器插件
        action = QAction("📏 打开计算器工具", self.main_window)
        #action.setShortcut(QKeySequence("Ctrl+L"))
        action.triggered.connect(self.open_calculator_tool)
        actions.append(action)
        
        return actions
    
    def open_calculator_tool(self):
        """打开计算器插件"""
        if not self.dialog:
            self.dialog = CalculatorDialog(self.main_window)

        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
        
    def cleanup(self):
        """清理插件资源"""
        print(f"插件 {self.name} 清理完成")

        # 关闭对话框
        if self.dialog:
            self.dialog.close()
            self.dialog = None



# ==================== 计算器对话框 ====================
class CalculatorDialog(QDialog):
    """计算器对话窗（支持界面按钮+电脑物理键盘输入）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 窗口基础设置
        self.setWindowTitle("计算器 UI ")
        self.setFixedSize(400, 550)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
        """)
        
        # 核心状态变量
        self.current_num = ""       # 当前正在输入的数字
        self.first_num = ""         # 第一个运算数
        self.operator = ""          # 运算符号（+、-、×、÷）
        self.reset_display = False  # 标记：点击运算符后是否清空输入框
        
        # 初始化UI
        self.init_ui()
        # 关键：让对话框捕获键盘事件（默认可能被子控件抢占）
        self.setFocusPolicy(Qt.StrongFocus)

    def init_ui(self):
        """UI布局（保留空位、样式）"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # 显示区域
        display_frame = QFrame()
        display_frame.setStyleSheet("""
            QFrame {
                background-color: #3c3c3c;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        display_frame.setFixedHeight(100)
        
        display_layout = QVBoxLayout(display_frame)
        display_layout.setContentsMargins(10, 5, 10, 5)
        
        # 过程显示框（展示运算步骤）
        self.process_display = QLineEdit("0")
        self.process_display.setAlignment(Qt.AlignRight)
        self.process_display.setReadOnly(True)
        self.process_display.setFont(QFont("Arial", 12))
        self.process_display.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                color: #aaaaaa;
                padding: 2px;
            }
        """)
        
        # 结果显示框（展示当前输入/计算结果）
        self.result_display = QLineEdit("0")
        self.result_display.setAlignment(Qt.AlignRight)
        self.result_display.setReadOnly(True)
        self.result_display.setFont(QFont("Arial", 24, QFont.Bold))
        self.result_display.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                color: #ffffff;
                padding: 2px;
            }
        """)
        
        display_layout.addWidget(self.process_display)
        display_layout.addWidget(self.result_display)
        main_layout.addWidget(display_frame)

        # 按钮区域（带空位）
        button_frame = QFrame()
        grid_layout = QGridLayout(button_frame)
        grid_layout.setSpacing(15)
        grid_layout.setContentsMargins(20, 20, 20, 20)

        # 按钮定义
        buttons = [
            ['C', '±', '%', '÷'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '◀️', '=']
        ]

        # 按钮样式
        number_style = """
            QPushButton {
                background-color: #4a4a4a; color: white; border: none; border-radius: 8px;
                font-size: 18px; font-weight: bold; padding: 20px; margin: 2px;
            }
            QPushButton:hover { background-color: #5a5a5a; }
            QPushButton:pressed { background-color: #3a3a3a; }
        """
        operator_style = """
            QPushButton {
                background-color: #ff9500; color: white; border: none; border-radius: 8px;
                font-size: 20px; font-weight: bold; padding: 20px; margin: 2px;
            }
            QPushButton:hover { background-color: #ffaa33; }
            QPushButton:pressed { background-color: #cc7a00; }
        """
        function_style = """
            QPushButton {
                background-color: #3a3a3a; color: white; border: none; border-radius: 8px;
                font-size: 16px; font-weight: bold; padding: 20px; margin: 2px;
            }
            QPushButton:hover { background-color: #4a4a4a; }
            QPushButton:pressed { background-color: #2a2a2a; }
        """

        # 创建按钮并绑定事件
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                btn = QPushButton(text)
                # 样式分配
                if text in ['÷', '×', '-', '+', '=']:
                    btn.setStyleSheet(operator_style)
                elif text in ['C', '±', '%', '⌫']:
                    btn.setStyleSheet(function_style)
                else:
                    btn.setStyleSheet(number_style)
                btn.setFixedSize(75, 75)
                # 0按钮占2列
                if text == '0':
                    grid_layout.addWidget(btn, i, j, 1, 2)
                else:
                    grid_layout.addWidget(btn, i, j)
                # 绑定点击事件（关键：传递当前按钮文本）
                btn.clicked.connect(lambda _, t=text: self.on_key_press(t))

        main_layout.addWidget(button_frame)

        # 菜单栏（保留）
        menubar = QMenuBar()
        menubar.setStyleSheet("""
            QMenuBar { background-color: #2b2b2b; color: white; }
            QMenuBar::item:selected { background-color: #3a3a3a; }
        """)
        for menu_name in ["文件", "编辑", "视图"]:
            menu = menubar.addMenu(menu_name)
            menu.setStyleSheet("""
                QMenu { background-color: #2b2b2b; color: white; }
                QMenu::item:selected { background-color: #3a3a3a; }
            """)
        main_layout.setMenuBar(menubar)

    # ==================== 处理键盘按键事件 ====================
    def keyPressEvent(self, event: QKeyEvent):
        """重写键盘按下事件，映射物理键盘到计算器逻辑"""
        key = event.key()
        key_text = event.text()
        
        # 1. 数字键（0-9）
        if key in [Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4,
                   Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9]:
            self.on_key_press(key_text)
        
        # 2. 小数点（.）
        elif key == Qt.Key_Period or key == Qt.Key_Comma:  # 支持小数点/逗号
            self.on_key_press(".")
        
        # 3. 运算符键
        elif key == Qt.Key_Plus:          # + 键
            self.on_key_press("+")
        elif key == Qt.Key_Minus:         # - 键
            self.on_key_press("-")
        elif key == Qt.Key_Asterisk:      # * 键（对应×）
            self.on_key_press("×")
        elif key == Qt.Key_Slash:         # / 键（对应÷）
            self.on_key_press("÷")
        
        # 4. 等于键（Enter/Equal）
        elif key == Qt.Key_Enter or key == Qt.Key_Return or key == Qt.Key_Equal:
            self.on_key_press("=")
        
        # 5. 功能键
        elif key == Qt.Key_Backspace:     # 退格键（对应⌫）
            self.on_key_press("⌫")
        elif key == Qt.Key_Escape:        # ESC键（对应C清空）
            self.on_key_press("C")
        elif key == Qt.Key_Percent:       # % 键
            self.on_key_press("%")
        
        # 6. 正负号（按Shift+- 组合键）
        elif key == Qt.Key_Minus and event.modifiers() == Qt.ShiftModifier:
            self.on_key_press("±")
        
        # 其他按键忽略
        else:
            super().keyPressEvent(event)

    def on_key_press(self, key):
        """核心：按键输入逻辑（界面按钮+键盘共用）"""
        # 1. 数字键输入（0-9）
        if key.isdigit():
            # 场景1：点击运算符后，重置当前输入（如12+ → 输入3时，current_num清空为"3"）
            if self.reset_display:
                self.current_num = ""
                self.reset_display = False
            # 场景2：避免开头多个0（如输入0001 → 显示1）
            if self.current_num == "0" and key == "0":
                return
            if self.current_num == "0" and key != "0":
                self.current_num = key
            else:
                self.current_num += key
            # 更新显示
            self.result_display.setText(self.current_num)

        # 2. 小数点输入（仅允许一个小数点）
        elif key == ".":
            if self.reset_display:
                self.current_num = "0."
                self.reset_display = False
            elif "." not in self.current_num:
                self.current_num = self.current_num if self.current_num else "0."
            self.result_display.setText(self.current_num)

        # 3. 清空键（C/ESC）：重置所有状态变量
        elif key == "C":
            self.current_num = ""
            self.first_num = ""
            self.operator = ""
            self.reset_display = False
            self.process_display.setText("0")
            self.result_display.setText("0")

        # 4. 退格键（⌫/Backspace）：删除最后一位
        elif key == "⌫":
            if self.reset_display:
                return
            self.current_num = self.current_num[:-1]
            # 空值时显示0
            show_text = self.current_num if self.current_num else "0"
            self.result_display.setText(show_text)

        # 5. 正负号（±/Shift+-）：切换当前数字正负
        elif key == "±":
            if self.reset_display or not self.current_num:
                return
            if self.current_num.startswith("-"):
                self.current_num = self.current_num[1:]
            else:
                self.current_num = "-" + self.current_num
            self.result_display.setText(self.current_num)

        # 6. 百分号（%）：当前数÷100
        elif key == "%":
            if not self.current_num or self.reset_display:
                return
            try:
                self.current_num = str(float(self.current_num) / 100)
                # 去掉末尾的.0（如100% → 1）
                if self.current_num.endswith(".0"):
                    self.current_num = self.current_num[:-2]
                self.result_display.setText(self.current_num)
            except:
                self.result_display.setText("错误")

        # 7. 运算符输入（+、-、×、÷）
        elif key in ["+", "-", "×", "÷"]:
            # 场景1：已有第一个数+运算符，直接替换运算符（如12+ → 改成12×）
            if self.first_num and self.reset_display:
                self.operator = key
                self.process_display.setText(f"{self.first_num} {self.operator}")
                return
            # 场景2：无当前输入，不处理
            if not self.current_num:
                return
            # 场景3：正常输入运算符，保存第一个数和运算符
            self.first_num = self.current_num
            self.operator = key
            self.reset_display = True  # 标记：下一次输入数字时清空current_num
            self.process_display.setText(f"{self.first_num} {self.operator}")

        # 8. 等于键（=/Enter）：执行运算
        elif key == "=":
            # 校验：必须有第一个数、运算符、当前数
            if not (self.first_num and self.operator and self.current_num):
                return
            try:
                num1 = float(self.first_num)
                num2 = float(self.current_num)
                result = 0

                # 根据运算符计算
                if self.operator == "+":
                    result = num1 + num2
                elif self.operator == "-":
                    result = num1 - num2
                elif self.operator == "×":
                    result = num1 * num2
                elif self.operator == "÷":
                    if num2 == 0:
                        self.result_display.setText("除数不能为0")
                        return
                    result = num1 / num2

                # 处理整数结果（去掉.0）
                result_str = str(int(result)) if result.is_integer() else str(result)
                # 更新显示
                self.process_display.setText(f"{self.first_num} {self.operator} {self.current_num} =")
                self.result_display.setText(result_str)
                # 连续计算：将结果设为下一次运算的第一个数
                self.first_num = result_str
                self.current_num = ""
                self.reset_display = True
            except:
                self.result_display.setText("计算错误")