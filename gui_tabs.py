#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QTextEdit, QFormLayout, QFileDialog, QMessageBox, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QFont, QPainter, QColor, QDesktopServices
from PySide6.QtCore import QUrl

from gui_components import ModernButton, CardWidget, ModernProgressBar, LicenseStatusIndicator

class TabManager:
    """标签页管理器，负责创建和管理主窗口的各个标签页"""
    
    def __init__(self, main_window):
        """
        初始化标签页管理器
        
        Args:
            main_window: 主窗口实例
        """
        self.main_window = main_window
    
    def setup_home_tab(self):
        """设置主页标签"""
        home_tab = QWidget()
        home_layout = QVBoxLayout(home_tab)
        home_layout.setContentsMargins(20, 20, 20, 20)
        home_layout.setSpacing(20)
        
        # 创建主内容区域布局
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # 左侧信息卡片
        info_card = CardWidget()
        
        # 添加说明文本
        description_label = QLabel("功能介绍")
        description_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #6750a4; margin-bottom: 10px;")
        
        # 使用QLabel替代QTextEdit，避免滚动条
        description_text = QLabel()
        description_text.setWordWrap(True)  # 允许文本换行
        description_text.setTextFormat(Qt.TextFormat.RichText)  # 支持富文本
        description_text.setStyleSheet("font-size: 14px; color: #1c1b1f; background: transparent;")
        description_text.setText("""
        <p style="line-height: 1.5; margin-bottom: 15px;">本工具可以帮助您自动化完成以下任务：</p>
        <ul style="margin-left: 20px; line-height: 1.6;">
            <li>自动注册 Cursor Pro 账号</li>
            <li>重置机器 ID 延长试用期</li>
            <li>查看使用统计数据</li>
            <li>一键式解决方案</li>
        </ul>
        
        <p style="margin-top: 20px; line-height: 1.5; margin-bottom: 15px;"><strong>使用步骤：</strong></p>
        <ol style="margin-left: 20px; line-height: 1.6;">
            <li>点击"独享注册"按钮自动注册账号</li>
            <li>如需重置机器ID，请点击"重置机器ID"按钮</li>
            <li>或者直接点击"一键畅享"完成全部操作</li>
            <li>点击"检查状态"查看系统状态和使用统计</li>
        </ol>
        """)
        
        # 添加"使用指南"按钮
        guide_btn = ModernButton("使用指南", primary=False)
        guide_btn.setStyleSheet("background-color: #f7f2fa; color: #1976D2; font-weight: bold; border: 1px solid #e8def8; border-radius: 8px; padding: 8px 16px;")
        guide_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://bytlwddzcb.feishu.cn/docx/S88ldGgUQoTRuCxeXWrc43lXnfg?from=from_copylink")))
        
        # 添加"免费试用"按钮
        free_trial_btn = ModernButton("免费试用", primary=False)
        free_trial_btn.setStyleSheet("background-color: #f7f2fa; color: #4CAF50; font-weight: bold; border: 1px solid #e8def8; border-radius: 8px; padding: 8px 16px;")
        free_trial_btn.clicked.connect(self._show_free_trial_message)
        
        info_card.addWidget(description_label)
        info_card.addWidget(description_text)
        info_card.addWidget(guide_btn)
        info_card.addWidget(free_trial_btn)
        info_card.addStretch()
        
        # 右侧功能区域
        functions_area = QVBoxLayout()
        functions_area.setSpacing(15)
        
        # 授权信息卡片
        license_card = self._create_license_card()
        
        # 操作卡片
        actions_card = self._create_actions_card()
        
        # 状态卡片
        status_card = self._create_status_card()
        
        # 将卡片添加到右侧功能区域
        functions_area.addWidget(license_card, 1)
        functions_area.addWidget(actions_card, 1)
        functions_area.addWidget(status_card, 2)
        
        # 将左右两侧添加到内容布局
        content_layout.addWidget(info_card, 3)
        content_layout.addLayout(functions_area, 4)
        
        # 将内容区域添加到主布局
        home_layout.addLayout(content_layout)
        
        # 添加带图标的标签页
        home_icon = self._create_tab_icon("🏠")
        self.main_window.tabs.addTab(home_tab, "主页")
        self.main_window.tabs.setTabIcon(0, home_icon)
    
    def _create_license_card(self):
        """创建授权信息卡片"""
        license_card = CardWidget()
        license_layout = QFormLayout()
        license_layout.setSpacing(12)
        license_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        license_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        license_title = QLabel("授权信息")
        license_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #6750a4; margin-bottom: 5px;")
        
        # 添加状态指示灯
        self.main_window.license_indicator = LicenseStatusIndicator(status="unknown")
        
        # 创建水平布局用于状态和天数显示
        status_days_layout = QHBoxLayout()
        
        # 状态部分
        status_layout = QHBoxLayout()
        self.main_window.license_status_label = QLabel("未授权")
        self.main_window.license_status_label.setStyleSheet("font-weight: bold; color: #b3261e;")
        status_layout.addWidget(self.main_window.license_indicator)
        status_layout.addWidget(self.main_window.license_status_label)
        status_layout.addStretch(1)
        
        # 天数部分
        days_layout = QHBoxLayout()
        days_title = QLabel("剩余天数:")
        days_title.setStyleSheet("color: #49454f;")
        self.main_window.license_days_label = QLabel("0天")
        self.main_window.license_days_label.setStyleSheet("font-weight: bold;")
        days_layout.addWidget(days_title)
        days_layout.addWidget(self.main_window.license_days_label)
        
        # 将状态和天数添加到同一行
        status_days_layout.addLayout(status_layout, 1)
        status_days_layout.addLayout(days_layout)
        
        # 创建授权码布局（包含授权码标签和续期按钮）
        license_code_layout = QHBoxLayout()
        self.main_window.license_code_label = QLabel("无")
        self.main_window.license_code_label.setStyleSheet("font-family: monospace;")
        license_code_layout.addWidget(self.main_window.license_code_label)
        license_code_layout.addStretch(1)
        
        # 添加续期按钮（初始隐藏）
        self.main_window.renew_license_btn = ModernButton("续期授权", primary=True, color=QColor(76, 175, 80))  # 绿色按钮
        self.main_window.renew_license_btn.clicked.connect(self.main_window.renew_license)
        self.main_window.renew_license_btn.setVisible(False)  # 初始隐藏
        self.main_window.renew_license_btn.setFixedWidth(100)  # 与激活按钮宽度一致
        license_code_layout.addWidget(self.main_window.renew_license_btn)
        
        # 添加授权码输入和激活按钮
        license_input_layout = QHBoxLayout()
        self.main_window.license_code_input = QLineEdit()
        self.main_window.license_code_input.setPlaceholderText("请输入授权码")
        self.main_window.license_code_input.setMaxLength(32)
        self.main_window.license_code_input.setStyleSheet("padding: 8px;")
        
        activate_btn = ModernButton("激活", primary=False)
        activate_btn.clicked.connect(self.main_window.activate_license)
        activate_btn.setFixedWidth(100)
        
        license_input_layout.addWidget(self.main_window.license_code_input)
        license_input_layout.addWidget(activate_btn)
        
        license_card.addWidget(license_title)
        
        # 使用QFormLayout添加状态和天数的组合行，以及其他行
        license_layout = QFormLayout()
        license_layout.setSpacing(12)
        license_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        license_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        license_layout.addRow("授权状态:", status_days_layout)
        license_layout.addRow("授权码:", license_code_layout)
        license_layout.addRow("激活授权:", license_input_layout)
        license_card.addLayout(license_layout)
        
        return license_card
    
    def _create_actions_card(self):
        """创建操作卡片"""
        actions_card = CardWidget()
        
        actions_title = QLabel("快速操作")
        actions_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #6750a4; margin-bottom: 10px;")
        
        # 创建水平布局来放置按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # 快速操作按钮 - 蓝色主题
        start_register_btn = ModernButton(
            "独享注册", 
            primary=True, 
            color=QColor(25, 118, 210)  # 蓝色 #1976D2
        )
        start_register_btn.clicked.connect(lambda: self._check_license_and_execute(
            self.main_window.start_registration
        ))
        
        # 重置机器ID按钮 - 橙色主题
        reset_machine_btn = ModernButton(
            "重置机器ID", 
            primary=True, 
            color=QColor(255, 152, 0)  # 橙色 #FF9800
        )
        reset_machine_btn.clicked.connect(lambda: self._check_license_and_execute(
            self.main_window.reset_machine_id
        ))
        
        # 一键畅享按钮 - 绿色主题
        one_click_btn = ModernButton(
            "一键畅享", 
            primary=True, 
            color=QColor(76, 175, 80)  # 绿色 #4CAF50
        )
        one_click_btn.clicked.connect(lambda: self._check_license_and_execute(
            self.main_window.one_click_enjoy
        ))
        one_click_btn.setFont(QFont(one_click_btn.font().family(), 10, QFont.Weight.Bold))
        
        # 快速换号按钮 - 紫色主题
        quick_switch_btn = ModernButton(
            "快速换号", 
            primary=True, 
            color=QColor(156, 39, 176)  # 紫色 #9C27B0
        )
        quick_switch_btn.clicked.connect(lambda: self._check_license_and_execute(
            self.main_window.quick_switch_account
        ))
        
        # 将按钮添加到水平布局中
        buttons_layout.addWidget(start_register_btn)
        buttons_layout.addWidget(reset_machine_btn)
        buttons_layout.addWidget(one_click_btn)
        buttons_layout.addWidget(quick_switch_btn)
        
        # 添加标题和按钮布局到卡片
        actions_card.addWidget(actions_title)
        actions_card.addLayout(buttons_layout)
        
        return actions_card
    
    def _check_license_and_execute(self, callback_function):
        """检查授权状态并执行回调函数
        
        Args:
            callback_function: 如果授权有效要执行的回调函数
        """
        from gui_components import ModernMessageBox
        
        # 检查当前是否有工作线程在运行
        for task_type, worker in list(self.main_window.active_workers.items()):
            if worker.isRunning():
                ModernMessageBox.information(
                    self.main_window, 
                    "操作提示", 
                    f"已有任务正在执行中，请等待其完成后再试。"
                )
                return

        # 检查授权是否有效
        if self.main_window.check_license_valid():
            callback_function()
        else:
            # 如果没有有效的授权，提示用户激活授权
            result = ModernMessageBox.question(
                self.main_window,
                "未授权",
                "未检测到有效授权。您想要继续操作吗？"
            )
            
            if result == ModernMessageBox.Yes_Result:
                callback_function()
            else:
                # 显示提示用户激活授权的消息
                ModernMessageBox.information(
                    self.main_window, 
                    "授权提示", 
                    "请激活授权码以继续使用所有功能。"
                )
    
    def _create_status_card(self):
        """创建状态卡片"""
        status_card = CardWidget()
        
        # 标题行
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        status_title = QLabel("系统状态")
        status_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #6750a4;")
        
        # 刷新按钮
        refresh_btn = ModernButton("检查状态", primary=False)
        refresh_btn.setFixedWidth(120)
        refresh_btn.clicked.connect(self.main_window.check_system_status)
        
        title_layout.addWidget(status_title)
        title_layout.addStretch()
        title_layout.addWidget(refresh_btn)
        
        # 创建网格布局来放置状态信息
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(1, 1)  # 让第二列（值）可以伸展
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)
        
        # Cursor版本
        cursor_version_title = QLabel("Cursor版本:")
        cursor_version_title.setStyleSheet("font-weight: bold;")
        self.main_window.cursor_version_label = QLabel("未知")
        
        # 机器ID
        machine_id_title = QLabel("机器ID:")
        machine_id_title.setStyleSheet("font-weight: bold;")
        self.main_window.machine_id_label = QLabel("未知")
        self.main_window.machine_id_label.setWordWrap(True)  # 允许文本换行
        
        # Cursor机器ID
        cursor_machine_id_title = QLabel("Cursor机器ID:")
        cursor_machine_id_title.setStyleSheet("font-weight: bold;")
        self.main_window.cursor_machine_id_label = QLabel("未知")
        self.main_window.cursor_machine_id_label.setWordWrap(True)  # 允许文本换行
        
        # 认证状态
        auth_status_title = QLabel("认证状态:")
        auth_status_title.setStyleSheet("font-weight: bold;")
        self.main_window.auth_status_label = QLabel("未知")
        
        # 添加到网格布局
        grid_layout.addWidget(cursor_version_title, 0, 0)
        grid_layout.addWidget(self.main_window.cursor_version_label, 0, 1)
        
        grid_layout.addWidget(machine_id_title, 1, 0)
        grid_layout.addWidget(self.main_window.machine_id_label, 1, 1)
        
        grid_layout.addWidget(cursor_machine_id_title, 2, 0)
        grid_layout.addWidget(self.main_window.cursor_machine_id_label, 2, 1)
        
        grid_layout.addWidget(auth_status_title, 3, 0)
        grid_layout.addWidget(self.main_window.auth_status_label, 3, 1)
        
        # 将所有元素添加到卡片
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.addLayout(title_layout)
        main_layout.addLayout(grid_layout)
        
        # 设置卡片的主布局
        status_card.layout.setContentsMargins(20, 20, 20, 20)
        status_card.addLayout(main_layout)
        
        return status_card
    
    def setup_logs_tab(self):
        """设置日志标签页"""
        logs_tab = QWidget()
        layout = QVBoxLayout(logs_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 创建日志卡片
        log_card = CardWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(0, 0, 0, 0)
        
        # 日志标题
        log_title = QLabel("系统日志")
        log_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #6750a4; margin-bottom: 10px;")
        
        # 日志内容区域
        self.main_window.log_text = QTextEdit()
        self.main_window.log_text.setReadOnly(True)
        self.main_window.log_text.setStyleSheet("""
            background-color: #f7f2fa;
            border: 1px solid #e8def8;
            border-radius: 8px;
            padding: 10px;
            font-family: monospace;
            font-size: 12px;
        """)
        
        # 底部按钮区域
        buttons_layout = QHBoxLayout()
        
        clear_logs_btn = ModernButton("清除日志", primary=False)
        clear_logs_btn.setFixedWidth(150)
        clear_logs_btn.clicked.connect(self.main_window.clear_logs)
        
        export_logs_btn = ModernButton("导出日志", primary=False)
        export_logs_btn.setFixedWidth(150)
        export_logs_btn.clicked.connect(self.main_window.export_logs)
        
        buttons_layout.addWidget(clear_logs_btn)
        buttons_layout.addWidget(export_logs_btn)
        buttons_layout.addStretch()
        
        log_layout.addWidget(log_title)
        log_layout.addWidget(self.main_window.log_text)
        log_layout.addLayout(buttons_layout)
        
        log_card.addLayout(log_layout)
        layout.addWidget(log_card)
        
        # 添加带图标的标签页
        logs_icon = self._create_tab_icon("📋")
        self.main_window.tabs.addTab(logs_tab, "日志")
        self.main_window.tabs.setTabIcon(1, logs_icon)
        
        # 设置日志处理器
        from main_window import LogHandler
        self.main_window.log_handler = LogHandler(self.main_window.log_text)
        logging.getLogger().addHandler(self.main_window.log_handler)
        
        # 记录一条初始日志
        logging.info("GUI日志系统初始化完成")
    
    def setup_usage_tab(self):
        """设置用量统计标签页"""
        usage_tab = QWidget()
        layout = QVBoxLayout(usage_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 创建用量卡片
        usage_card = CardWidget()
        
        # 用量标题
        usage_title = QLabel("用量统计数据")
        usage_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #6750a4; margin-bottom: 10px;")

        # 用量信息展示区
        self.main_window.usage_text = QTextEdit()
        self.main_window.usage_text.setReadOnly(True)
        self.main_window.usage_text.setStyleSheet("""
            background-color: #f7f2fa;
            border: 1px solid #e8def8;
            border-radius: 8px;
            padding: 10px;
            font-family: monospace;
            font-size: 12px;
        """)

        # 刷新按钮
        refresh_btn = ModernButton("刷新用量数据", primary=False)
        refresh_btn.setFixedWidth(200)
        refresh_btn.clicked.connect(self.main_window.refresh_usage)

        usage_card.addWidget(usage_title)
        usage_card.addWidget(self.main_window.usage_text)
        usage_card.addWidget(refresh_btn)

        layout.addWidget(usage_card)

        # 添加带图标的标签页
        usage_icon = self._create_tab_icon("📊")
        self.main_window.tabs.addTab(usage_tab, "用量统计")
        self.main_window.tabs.setTabIcon(2, usage_icon)
    
    def _create_tab_icon(self, emoji):
        """创建标签页图标"""
        # 创建一个QPixmap来绘制图标
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # 创建画笔
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置字体
        font = QFont("Segoe UI Emoji", 12)
        painter.setFont(font)
        
        # 绘制emoji
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()
        
        # 创建图标
        return QIcon(pixmap)
    
    def _show_free_trial_message(self):
        """显示免费试用的消息框，先显示Loading 2秒，然后提示'免费额度目前紧张，请稍后再试'"""
        from gui_components import LoadingDialog, ModernMessageBox
        from PySide6.QtCore import QTimer
        
        # 创建加载对话框
        loading_dialog = LoadingDialog(self.main_window, "正在检查免费额度...")
        
        # 2秒后关闭对话框并显示消息
        def show_message():
            # 关闭加载对话框
            loading_dialog.close()
            # 显示消息框
            ModernMessageBox.information(
                self.main_window, 
                "免费额度提示", 
                "免费额度目前紧张，请稍后再试"
            )
        
        # 设置定时器，2秒后执行show_message函数
        QTimer.singleShot(2000, show_message)
        
        # 显示加载对话框
        loading_dialog.exec() 