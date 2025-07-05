#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QPushButton, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QGraphicsDropShadowEffect, QProgressBar, QWidget, QDialog, QApplication, QGridLayout,
    QLineEdit, QTextEdit, QFormLayout, QMessageBox, QFileDialog, QSizePolicy, QDialogButtonBox,
    QComboBox, QCheckBox, QTabWidget
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QTimer, QSize, Signal, Slot, QUrl
from PySide6.QtGui import QColor, QPainter, QFont, QBrush, QPen, QPainterPath, QRadialGradient, QIcon, QPixmap, QPalette, QTextCursor, QDesktopServices
import os

# 自定义现代化消息对话框
class ModernMessageBox(QDialog):
    """自定义美观的消息对话框，替代QMessageBox"""
    
    # 对话框类型
    Information = 0
    Warning = 1
    Error = 2
    Question = 3
    
    # 按钮类型
    Ok = 0
    OkCancel = 1
    YesNo = 2
    
    # 返回结果
    Ok_Result = 0
    Cancel_Result = 1
    Yes_Result = 2
    No_Result = 3
    
    def __init__(self, parent=None, title="提示", message="", box_type=Information, buttons=Ok):
        super().__init__(parent)
        self.result_value = self.Cancel_Result
        
        # 设置窗口属性
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.setMinimumWidth(400)
        self.setMaximumWidth(600)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 创建标题和图标布局
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(15)
        
        # 创建图标
        icon_label = QLabel()
        icon_size = QSize(32, 32)
        
        # 根据类型设置图标和颜色
        if box_type == self.Information:
            icon_color = QColor(25, 118, 210)  # 蓝色
            icon_char = "ℹ"
        elif box_type == self.Warning:
            icon_color = QColor(255, 152, 0)  # 橙色
            icon_char = "⚠"
        elif box_type == self.Error:
            icon_color = QColor(211, 47, 47)  # 红色
            icon_char = "✖"
        elif box_type == self.Question:
            icon_color = QColor(76, 175, 80)  # 绿色
            icon_char = "?"
        
        # 创建图标
        pixmap = QPixmap(icon_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制圆形背景
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(icon_color.lighter(115)))
        painter.drawEllipse(0, 0, icon_size.width(), icon_size.height())
        
        # 绘制图标文字
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Arial", 18, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, icon_char)
        painter.end()
        
        icon_label.setPixmap(pixmap)
        header_layout.addWidget(icon_label)
        
        # 创建标题标签
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1c1b1f;")
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        
        # 创建消息标签
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 14px; color: #49454f; margin: 10px 0;")
        message_label.setMinimumHeight(50)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        button_layout.addStretch(1)
        
        # 根据按钮类型创建按钮
        if buttons == self.Ok:
            ok_btn = ModernButton("确定", primary=True)
            ok_btn.clicked.connect(self._on_ok_clicked)
            button_layout.addWidget(ok_btn)
            
        elif buttons == self.OkCancel:
            cancel_btn = ModernButton("取消", primary=False)
            ok_btn = ModernButton("确定", primary=True)
            
            cancel_btn.clicked.connect(self._on_cancel_clicked)
            ok_btn.clicked.connect(self._on_ok_clicked)
            
            button_layout.addWidget(cancel_btn)
            button_layout.addWidget(ok_btn)
            
        elif buttons == self.YesNo:
            no_btn = ModernButton("否", primary=False)
            yes_btn = ModernButton("是", primary=True)
            
            no_btn.clicked.connect(self._on_no_clicked)
            yes_btn.clicked.connect(self._on_yes_clicked)
            
            button_layout.addWidget(no_btn)
            button_layout.addWidget(yes_btn)
        
        # 添加各部分到主布局
        main_layout.addLayout(header_layout)
        main_layout.addWidget(message_label)
        main_layout.addLayout(button_layout)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 0px;  /* 移除圆角 */
            }
        """)
        
        # 添加右上角关闭按钮
        close_btn = QPushButton("×", self)
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #49454f;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #e8def8;
            }
            QPushButton:pressed {
                background-color: #d0bcff;
            }
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        close_btn.move(self.width() - 30, 5)  # 放在右上角
        
        # 保存关闭按钮引用
        self.close_btn = close_btn
        
    def resizeEvent(self, event):
        """处理窗口大小变化事件"""
        # 先调用父类的方法
        super().resizeEvent(event)
        # 然后更新关闭按钮位置
        if hasattr(self, 'close_btn'):
            self.close_btn.move(self.width() - 30, 5)
    
    def _on_ok_clicked(self):
        self.result_value = self.Ok_Result
        self.accept()
    
    def _on_cancel_clicked(self):
        self.result_value = self.Cancel_Result
        self.reject()
    
    def _on_yes_clicked(self):
        self.result_value = self.Yes_Result
        self.accept()
    
    def _on_no_clicked(self):
        self.result_value = self.No_Result
        self.reject()
    
    @staticmethod
    def information(parent, title, message):
        """显示信息对话框"""
        dialog = ModernMessageBox(parent, title, message, ModernMessageBox.Information, ModernMessageBox.Ok)
        dialog.exec()
        return ModernMessageBox.Ok_Result
    
    @staticmethod
    def warning(parent, title, message):
        """显示警告对话框"""
        dialog = ModernMessageBox(parent, title, message, ModernMessageBox.Warning, ModernMessageBox.Ok)
        dialog.exec()
        return ModernMessageBox.Ok_Result
    
    @staticmethod
    def error(parent, title, message):
        """显示错误对话框"""
        dialog = ModernMessageBox(parent, title, message, ModernMessageBox.Error, ModernMessageBox.Ok)
        dialog.exec()
        return ModernMessageBox.Ok_Result
    
    @staticmethod
    def question(parent, title, message):
        """显示询问对话框"""
        dialog = ModernMessageBox(parent, title, message, ModernMessageBox.Question, ModernMessageBox.YesNo)
        result = dialog.exec()
        return ModernMessageBox.Yes_Result if result == QDialog.DialogCode.Accepted else ModernMessageBox.No_Result

# 自定义加载对话框
class LoadingDialog(QDialog):
    # 添加关闭信号，当对话框被用户关闭时触发
    dialog_closed = Signal()
    
    def __init__(self, parent=None, message="正在处理，请稍候..."):
        super().__init__(parent)
        self.setWindowTitle("处理中")
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        
        # 初始化关联的工作线程
        self.associated_worker = None
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 添加消息标签
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.message_label)
        
        # 添加进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 设置为不确定模式
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e8def8;
                border-radius: 5px;
                background-color: #f7f2fa;
                height: 10px;
            }
            
            QProgressBar::chunk {
                background-color: #6750a4;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 0px;
            }
        """)
        
        # 添加右上角关闭按钮
        close_btn = QPushButton("×", self)
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #49454f;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #e8def8;
            }
            QPushButton:pressed {
                background-color: #d0bcff;
            }
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        close_btn.move(self.width() - 30, 5)  # 放在右上角
        
        # 保存关闭按钮引用
        self.close_btn = close_btn
    
    def set_worker(self, worker):
        """设置关联的工作线程"""
        self.associated_worker = worker
    
    def closeEvent(self, event):
        """重写关闭事件，处理线程中断"""
        if self.associated_worker and self.associated_worker.isRunning():
            # 请求中断线程
            self.associated_worker.requestInterruption()
            
            # 尝试清理浏览器资源（如果存在）
            if hasattr(self.associated_worker, 'cleanupBrowser'):
                self.associated_worker.cleanupBrowser()
                
            # 发送关闭信号
            self.dialog_closed.emit()
            
            # 设置短暂延时，让线程有时间响应中断请求
            QTimer.singleShot(100, lambda: None)
            
        # 调用父类方法
        super().closeEvent(event)
    
    def reject(self):
        """用户点击关闭按钮或按下Esc键时调用"""
        # 处理线程中断
        if self.associated_worker and self.associated_worker.isRunning():
            # 请求中断线程
            self.associated_worker.requestInterruption()
            
            # 尝试清理浏览器资源（如果存在）
            if hasattr(self.associated_worker, 'cleanupBrowser'):
                self.associated_worker.cleanupBrowser()
                
            # 发送关闭信号
            self.dialog_closed.emit()
            
            # 设置短暂延时，让线程有时间响应中断请求
            QTimer.singleShot(100, lambda: None)
            
        # 调用父类方法
        super().reject()
        
    def resizeEvent(self, event):
        """处理窗口大小变化事件"""
        # 先调用父类的方法
        super().resizeEvent(event)
        # 然后更新关闭按钮位置
        if hasattr(self, 'close_btn'):
            self.close_btn.move(self.width() - 30, 5)
    
    def update_message(self, message):
        """更新对话框消息"""
        self.message_label.setText(message)

# 自定义按钮类，支持悬停和点击效果
class ModernButton(QPushButton):
    def __init__(self, text="", parent=None, primary=True, color=None):
        super().__init__(text, parent)
        self.primary = primary
        self.custom_color = color  # 自定义颜色
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 设置动画属性
        self._hover_value = 0
        self._press_value = 0
        
        # 创建阴影效果
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 3)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(self.shadow)
        
        # 悬停动画
        self.hover_anim = QPropertyAnimation(self, b"hoverValue")
        self.hover_anim.setDuration(200)
        self.hover_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 点击动画
        self.press_anim = QPropertyAnimation(self, b"pressValue")
        self.press_anim.setDuration(100)
        self.press_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def getHoverValue(self):
        return self._hover_value
    
    def setHoverValue(self, value):
        self._hover_value = value
        self.update()
    
    def getPressValue(self):
        return self._press_value
    
    def setPressValue(self, value):
        self._press_value = value
        self.shadow.setBlurRadius(15 - value * 10)
        self.shadow.setOffset(0, 3 - value * 2)
        self.update()
    
    # 定义属性
    hoverValue = Property(float, getHoverValue, setHoverValue)
    pressValue = Property(float, getPressValue, setPressValue)
    
    def enterEvent(self, event):
        self.hover_anim.setStartValue(self._hover_value)
        self.hover_anim.setEndValue(1)
        self.hover_anim.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.hover_anim.setStartValue(self._hover_value)
        self.hover_anim.setEndValue(0)
        self.hover_anim.start()
        
        self.press_anim.setStartValue(self._press_value)
        self.press_anim.setEndValue(0)
        self.press_anim.start()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        self.press_anim.setStartValue(self._press_value)
        self.press_anim.setEndValue(1)
        self.press_anim.start()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        self.press_anim.setStartValue(self._press_value)
        self.press_anim.setEndValue(0)
        self.press_anim.start()
        super().mouseReleaseEvent(event)
    
    def paintEvent(self, event):
        # 自定义绘制
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 计算实际颜色
        if self.custom_color:
            # 使用自定义颜色
            base_color = self.custom_color
            text_color = QColor(255, 255, 255)  # 白色文字
            hover_color = QColor(
                min(base_color.red() + 20, 255),
                min(base_color.green() + 20, 255),
                min(base_color.blue() + 20, 255)
            )  # 稍微亮一些的颜色
        elif self.primary:
            base_color = QColor(103, 80, 164)  # Material Design紫色
            text_color = QColor(255, 255, 255)
            hover_color = QColor(123, 97, 192)  # 略浅一些的紫色
        else:
            base_color = QColor(243, 237, 247)  # 浅紫色
            text_color = QColor(103, 80, 164)  # 深紫色文字
            hover_color = QColor(229, 221, 236)  # 更浅的紫色
        
        # 混合颜色，制造悬停效果
        r = base_color.red() * (1 - self._hover_value) + hover_color.red() * self._hover_value
        g = base_color.green() * (1 - self._hover_value) + hover_color.green() * self._hover_value
        b = base_color.blue() * (1 - self._hover_value) + hover_color.blue() * self._hover_value
        
        button_color = QColor(int(r), int(g), int(b))
        
        if not self.isEnabled():
            # 禁用状态
            button_color = QColor(200, 200, 200)
            text_color = QColor(150, 150, 150)
        
        # 绘制按钮背景
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        
        # 按下效果 - 略微缩小
        margin = self._press_value * 2
        pressed_path = QPainterPath()
        pressed_path.addRoundedRect(margin, margin, self.width() - margin * 2, self.height() - margin * 2, 20, 20)
        
        painter.fillPath(pressed_path, QBrush(button_color))
        
        # 绘制文字
        painter.setPen(text_color)
        painter.setFont(self.font())
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

# 自定义卡片容器
class CardWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet("""
            #card {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        # 添加阴影效果
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)
        
        # 设置布局
        self.card_layout = QVBoxLayout(self)
        self.card_layout.setContentsMargins(20, 20, 20, 20)
        self.card_layout.setSpacing(15)
    
    def addWidget(self, widget):
        """添加部件到卡片布局"""
        self.card_layout.addWidget(widget)
    
    def addLayout(self, layout):
        """添加布局到卡片布局"""
        self.card_layout.addLayout(layout)
        
    def addSpacing(self, spacing):
        """添加间距到卡片布局"""
        self.card_layout.addSpacing(spacing)
    
    def addStretch(self, stretch=0):
        """添加弹性空间到卡片布局"""
        self.card_layout.addStretch(stretch)

    @property
    def layout(self):
        """获取卡片布局"""
        return self.card_layout
    
    def setContentsMargins(self, left, top, right, bottom):
        """设置布局边距"""
        self.card_layout.setContentsMargins(left, top, right, bottom)
    
    def setSpacing(self, spacing):
        """设置布局间距"""
        self.card_layout.setSpacing(spacing)

# 自定义进度条，支持波浪动画效果
class ModernProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setFixedHeight(8)
        self.animation_offset = 0
        
        # 创建动画
        self.animation = QTimer(self)
        self.animation.timeout.connect(self.update_animation)
        self.animation.start(50)
        
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #e8def8;
                border-radius: 4px;
            }
            
            QProgressBar::chunk {
                background-color: #6750a4;
                border-radius: 4px;
            }
        """)
    
    def update_animation(self):
        self.animation_offset = (self.animation_offset + 1) % 20
        self.update()
    
    def paintEvent(self, event):
        super().paintEvent(event)

# 授权状态指示灯类
class LicenseStatusIndicator(QWidget):
    def __init__(self, parent=None, status="unknown"):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(16, 16)
        
    def update_status(self, status):
        self.status = status
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 根据状态设置颜色
        if self.status == "valid":
            color = QColor(76, 175, 80)  # 绿色
        elif self.status == "expired":
            color = QColor(211, 47, 47)  # 红色
        else:
            color = QColor(158, 158, 158)  # 灰色
            
        # 绘制圆形指示灯
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(0, 0, self.width(), self.height())
        
        # 添加高光效果
        gradient = QRadialGradient(self.width() * 0.3, self.height() * 0.3, self.width() * 0.8)
        gradient.setColorAt(0, QColor(255, 255, 255, 150))
        gradient.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(gradient)
        painter.drawEllipse(0, 0, self.width(), self.height())

class PaymentQRCodeDialog(QDialog):
    """支付二维码对话框，用于显示支付宝二维码和支付说明"""
    
    def __init__(self, parent=None, license_code=""):
        super().__init__(parent)
        self.license_code = license_code
        
        # 设置窗口属性
        self.setWindowTitle("授权续期")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 创建标题
        title_label = QLabel("请在支付备注中输入授权码")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1c1b1f; text-align: center;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 显示授权码
        license_label = QLabel(f"授权码: {license_code}")
        license_label.setStyleSheet("font-size: 16px; color: #1976D2; font-weight: bold; text-align: center;")
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建价格信息
        price_layout = QHBoxLayout()
        price_layout.setSpacing(15)
        price_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加弹性空间（左侧）
        price_layout.addStretch(1)
        
        # 价格标题
        price_title = QLabel("授权价格:")
        price_title.setStyleSheet("font-size: 15px; font-weight: bold;")
        
        # 添加价格选项
        options = [
            {"text": "1天/2元", "color": "#1976D2"},
            {"text": "7天/10元", "color": "#388E3C"},
            {"text": "30天/25元", "color": "#D32F2F"}
        ]
        
        # 添加标题
        price_layout.addWidget(price_title)
        
        # 添加价格选项
        for option in options:
            price_label = QLabel(option["text"])
            price_label.setStyleSheet(f"font-size: 15px; color: {option['color']}; font-weight: bold;")
            price_layout.addWidget(price_label)
            
        # 添加弹性空间（右侧）
        price_layout.addStretch(1)
        
        # 创建说明标签
        description_label = QLabel("等待3-5分钟即可")
        description_label.setStyleSheet("font-size: 16px; color: #49454f; text-align: center;")
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建二维码图片
        qr_code_label = QLabel()
        qr_code_pixmap = QPixmap(os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "zhifubao.png"))
        qr_code_pixmap = qr_code_pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        qr_code_label.setPixmap(qr_code_pixmap)
        qr_code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_code_label.setStyleSheet("margin: 20px;")
        
        # 创建底部说明
        bottom_label = QLabel("打开支付宝[扫一扫]")
        bottom_label.setStyleSheet("font-size: 16px; color: #49454f; text-align: center;")
        bottom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建按钮
        close_button = ModernButton("关闭", primary=False)
        close_button.clicked.connect(self.accept)
        close_button.setFixedWidth(120)
        
        # 添加各部分到主布局
        main_layout.addWidget(title_label)
        main_layout.addWidget(license_label)
        main_layout.addLayout(price_layout)
        main_layout.addWidget(description_label)
        main_layout.addWidget(qr_code_label)
        main_layout.addWidget(bottom_label)
        main_layout.addWidget(close_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 0px;
            }
        """)
        
        # 添加右上角关闭按钮
        close_btn = QPushButton("×", self)
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #49454f;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #e8def8;
            }
            QPushButton:pressed {
                background-color: #d0bcff;
            }
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        close_btn.move(self.width() - 30, 5)  # 放在右上角
        
        # 保存关闭按钮引用
        self.close_btn = close_btn
    
    def resizeEvent(self, event):
        """处理窗口大小变化事件"""
        # 先调用父类的方法
        super().resizeEvent(event)
        # 然后更新关闭按钮位置
        if hasattr(self, 'close_btn'):
            self.close_btn.move(self.width() - 30, 5) 

class UpdateDialog(QDialog):
    """更新提示对话框，显示新版本信息并提供下载链接"""
    
    def __init__(self, parent=None, version_info=None, is_force_update=False):
        """初始化更新对话框
        
        Args:
            parent: 父窗口
            version_info (dict): 包含版本信息的字典
            is_force_update (bool): 是否强制更新
        """
        super().__init__(parent)
        self.version_info = version_info
        self.is_force_update = is_force_update
        self.setup_ui()
        
    def setup_ui(self):
        """设置对话框UI"""
        # 设置对话框属性
        self.setWindowTitle("发现新版本")
        self.setMinimumWidth(500)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 创建标题标签
        if self.version_info and "title" in self.version_info:
            title_label = QLabel(self.version_info["title"])
        else:
            title_label = QLabel("发现新版本")
            
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #6750a4;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 版本信息框
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f7f2fa;
                border-radius: 8px;
                border: 1px solid #e8def8;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        # 显示版本号
        if self.version_info and "version" in self.version_info:
            version_label = QLabel(f"版本号: {self.version_info['version']}")
            version_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
            info_layout.addWidget(version_label)
        
        # 显示更新描述
        if self.version_info and "description" in self.version_info:
            description_edit = QTextEdit(self.version_info["description"])
            description_edit.setReadOnly(True)
            description_edit.setStyleSheet("""
                QTextEdit {
                    border: none;
                    background-color: transparent;
                }
            """)
            description_edit.setMinimumHeight(100)
            info_layout.addWidget(description_edit)
            
        main_layout.addWidget(info_frame)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 强制更新时不显示"稍后再说"按钮
        if not self.is_force_update:
            later_button = QPushButton("稍后再说")
            later_button.clicked.connect(self.reject)
            later_button.setStyleSheet("""
                QPushButton {
                    background-color: #e8def8;
                    color: #6750a4;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #d0bcff;
                }
            """)
            button_layout.addWidget(later_button)
            
        # 添加弹簧
        button_layout.addStretch()
        
        # 下载按钮
        download_button = QPushButton("立即更新")
        download_button.clicked.connect(self.open_download_url)
        download_button.setStyleSheet("""
            QPushButton {
                background-color: #6750a4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7c6db8;
            }
        """)
        button_layout.addWidget(download_button)
        
        main_layout.addLayout(button_layout)
        
        # 如果是强制更新，设置对话框不可关闭
        if self.is_force_update:
            self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
    
    def open_download_url(self):
        """打开下载链接"""
        if self.version_info and "download_url" in self.version_info:
            QDesktopServices.openUrl(QUrl(self.version_info["download_url"]))
            self.accept()
        else:
            QMessageBox.warning(self, "错误", "下载链接不可用") 