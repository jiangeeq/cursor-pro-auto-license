#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import logging
from pathlib import Path
import requests
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, 
    QFormLayout, QFileDialog, QMessageBox, QStatusBar, 
    QGraphicsDropShadowEffect, QFrame
)
from PySide6.QtCore import (
    Qt, Signal, Slot, QThread, QTimer, QPropertyAnimation,
    QEasingCurve, QSize, QPoint
)
from PySide6.QtGui import (
    QIcon, QPixmap, QFont, QTextCursor, QColor
)

# 导入项目中的其他模块
from config import Config
from cursor_auth_manager import CursorAuthManager
from device_auth_manager import DeviceAuthManager, get_machine_device_id, get_machine_backup_id
from gui_worker import WorkerThread
from db_manager import DatabaseManager
from device_id_generator import DeviceIDGenerator
from logger import logging
from language import get_translation
from version_checker import VersionChecker

# 导入自定义组件
from gui_components import ModernButton, CardWidget, ModernProgressBar, LicenseStatusIndicator, LoadingDialog, ModernMessageBox, PaymentQRCodeDialog, UpdateDialog
from gui_tabs import TabManager

# 自定义日志处理器，将日志输出到GUI
class LogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
    def emit(self, record):
        msg = self.format(record)
        # 确保在GUI线程中更新UI
        self.text_widget.append(msg)
        self.text_widget.moveCursor(QTextCursor.MoveOperation.End)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cursor Pro 自动化工具")
        self.setMinimumSize(900, 650)
        
        # 线程管理字典，用于跟踪活动的工作线程
        self.active_workers = {}
        
        # 设置应用图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 设置为完全不透明
        self.setWindowOpacity(1.0)
        
        # 创建主布局
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # 创建标签页
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)  # 使用更现代的文档模式
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # 自定义标签栏样式
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
                border-radius: 8px;
            }
            
            QTabBar::tab {
                background-color: #f7f2fa;
                color: #49454f;
                padding: 12px 20px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
                font-size: 14px;
                font-weight: normal;
            }
            
            QTabBar::tab:selected {
                background-color: #6750a4;
                color: white;
                font-weight: bold;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #e8def8;
                color: #6750a4;
            }
        """)
        
        self.main_layout.addWidget(self.tabs)
        
        # 初始化UI元素引用
        self.machine_id_label = None
        self.license_code_label = None
        self.license_status_label = None
        self.license_indicator = None
        self.license_days_label = None
        self.renew_license_btn = None
        self.log_text = None
        self.cursor_version_label = None
        self.auth_status_label = None
        self.license_code_input = None
        self.cursor_machine_id_label = None
        
        # 创建标签页管理器
        self.tab_manager = TabManager(self)
        
        # 创建各个标签页
        self.tab_manager.setup_home_tab()
        self.tab_manager.setup_logs_tab()
        # 移除用量统计标签页
        # self.tab_manager.setup_usage_tab()
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 添加永久显示的版本标签
        self.version_label = QLabel()
        self.version_label.setStyleSheet("color: #6750a4; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.version_label)
        
        # 显示就绪状态
        self.status_bar.showMessage("就绪")
        
        # 初始化设备授权管理器
        self.device_auth_manager = DeviceAuthManager()
        
        # 初始化配置
        self.load_config()
        
        # 应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f7f2fa;
            }
        """)
        
        # 检查设备注册和授权状态
        QTimer.singleShot(500, self.check_device_auth_status)
        
        # 检查应用更新
        QTimer.singleShot(1000, self.check_app_updates)
    
    def check_device_auth_status(self):
        """检查设备注册和授权状态"""
        try:
            # 如果已经有相同类型的工作线程在运行，则不创建新的
            if "register_device" in self.active_workers and self.active_workers["register_device"].isRunning():
                self.update_log("已有设备授权检查任务在运行中，请等待完成")
                return
                
            # 创建工作线程注册设备
            self.worker = WorkerThread("register_device", {})
            self.worker.update_signal.connect(self.update_log)
            self.worker.finished_signal.connect(self.device_registration_finished)
            
            # 保存线程引用并启动
            self.active_workers["register_device"] = self.worker
            self.worker.start()
            
        except Exception as e:
            self.update_log(f"设备授权检查错误: {str(e)}")
            logging.error(f"设备授权检查错误: {str(e)}")
    
    def device_registration_finished(self, success, message):
        """设备注册完成回调"""
        # 清理已完成的线程引用
        if "register_device" in self.active_workers:
            del self.active_workers["register_device"]
            
        if success:
            try:
                # 解析返回的设备信息
                device_info = json.loads(message)
                self.update_log("设备注册和验证成功")
                
                # 更新设备ID显示
                if device_info and "machine_device_id" in device_info and self.machine_id_label:
                    machine_id = device_info["machine_device_id"]
                    if len(machine_id) > 32:
                        display_id = machine_id[:32] + "......"
                    else:
                        display_id = machine_id
                    self.machine_id_label.setText(display_id)
                
                # 加载保存的授权信息
                self.load_saved_license()
                
            except Exception as e:
                self.update_log(f"处理设备注册结果失败: {str(e)}")
                logging.error(f"处理设备注册结果失败: {str(e)}")
        else:
            self.update_log("设备注册和验证失败")
            ModernMessageBox.warning(self, "警告", "设备注册失败，请检查网络连接和API设置")
    
    def load_saved_license(self):
        """加载保存的授权信息"""
        try:
            # 如果已经有相同类型的工作线程在运行，则不创建新的
            if "verify_license" in self.active_workers and self.active_workers["verify_license"].isRunning():
                self.update_log("已有授权验证任务在运行中，请等待完成")
                return
                
            # 创建授权管理器实例
            auth_manager = DeviceAuthManager()
            
            # 从文件加载授权信息
            auth_info = auth_manager.load_license_info()
            if not auth_info or "license_code" not in auth_info:
                self.update_log("未找到有效的授权信息")
                return
            
            license_code = auth_info["license_code"]
            
            # 创建工作线程验证授权码
            params = {
                "license_code": license_code
            }
            self.worker = WorkerThread("verify_license", params)
            self.worker.update_signal.connect(self.update_log)
            self.worker.finished_signal.connect(self.saved_license_verification_finished)
            
            # 保存线程引用并启动
            self.active_workers["verify_license"] = self.worker
            self.worker.start()
            
        except Exception as e:
            self.update_log(f"加载授权信息失败: {str(e)}")
            logging.error(f"加载授权信息失败: {str(e)}")
    
    def saved_license_verification_finished(self, success, message):
        """保存的授权验证完成回调"""
        # 清理已完成的线程引用
        if "verify_license" in self.active_workers:
            del self.active_workers["verify_license"]
            
        try:
            if success:
                try:
                    # 解析返回的授权信息和绑定信息
                    result = json.loads(message)
                    license_info = result.get("license_info")
                    binding_info = result.get("binding_info")
                    
                    if license_info and binding_info:
                        self.update_log("已加载有效的授权信息")
                        
                        # 更新授权信息显示
                        self.update_license_display(license_info, binding_info)
                    else:
                        self.update_log("未找到有效的授权信息")
                except Exception as e:
                    self.update_log(f"处理授权验证结果失败: {str(e)}")
                    logging.error(f"处理授权验证结果失败: {str(e)}")
            else:
                self.update_log("保存的授权码无效")
                # 更新状态为未授权
                if self.license_indicator and self.license_status_label:
                    self.license_indicator.update_status("invalid")
                    self.license_status_label.setText("授权状态: 授权码无效")
                    self.license_status_label.setStyleSheet("font-weight: bold; color: #b3261e;")
                
                if self.license_days_label:
                    self.license_days_label.setText("0天")
        except Exception as e:
            logging.error(f"处理授权验证结果失败: {str(e)}")
    
    def update_license_display(self, license_info, binding_info):
        """更新授权信息显示"""
        try:
            if license_info and "license_code" in license_info:
                # 更新授权码显示
                if self.license_code_label:
                    self.license_code_label.setText(license_info["license_code"])
                
                # 更新授权状态
                if self.license_status_label:
                    self.license_status_label.setText("已授权")
                    self.license_status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
                
                if self.license_indicator:
                    self.license_indicator.update_status("valid")
                
                # 更新剩余天数
                if "expire_date" in license_info and self.license_days_label:
                    try:
                        expiry_date = datetime.fromisoformat(license_info["expire_date"].replace("Z", "+00:00"))
                        now = datetime.now()
                        time_diff = expiry_date - now
                        
                        # 如果过期时间在当前时间之后，但差值不足1天，显示为1天
                        if time_diff.total_seconds() > 0 and time_diff.days == 0:
                            days_left = 1
                        else:
                            days_left = time_diff.days
                            
                        self.license_days_label.setText(f"{max(0, days_left)}天")
                    except Exception as e:
                        logging.error(f"解析过期日期错误: {str(e)}")
                        if self.license_days_label:
                            self.license_days_label.setText("未知")
                
                # 显示续期按钮
                if self.renew_license_btn:
                    self.renew_license_btn.setVisible(True)
        except Exception as e:
            logging.error(f"更新授权显示错误: {str(e)}")
    
    def check_license_valid(self):
        """检查授权是否有效
        
        Returns:
            bool: 如果授权有效返回True，否则返回False
        """
        try:
            # 检查授权状态文本
            if not self.license_status_label or self.license_status_label.text() != "已授权":
                return False
                
            # 检查剩余天数
            if not self.license_days_label:
                return False
                
            days_text = self.license_days_label.text()
            if days_text == "未知":
                return False
                
            try:
                days = int(days_text.replace("天", ""))
                if days <= 0:
                    return False
            except ValueError:
                return False
                
            return True
        except Exception as e:
            logging.error(f"检查授权状态出错: {str(e)}")
            return False
        
    def load_config(self):
        """加载配置"""
        try:
            self.config = Config()
            self.api_base_url = self.config.get_api_base_url()
            self.current_version = self.config.get_current_version()
            
            # 更新版本标签
            if hasattr(self, 'version_label'):
                self.version_label.setText(f"当前应用版本: {self.current_version}")
                
            logging.info(f"当前应用版本: {self.current_version}")
        except Exception as e:
            logging.error(f"加载配置失败: {str(e)}")
            ModernMessageBox.warning(self, "错误", f"加载配置失败: {str(e)}")
            sys.exit(1)
    
    def check_app_updates(self):
        """检查应用更新"""
        if not self.api_base_url:
            logging.warning("API未启用，跳过版本检查")
            return
        
        try:
            logging.info("正在检查应用更新...")
            # 创建版本检查器
            version_checker = VersionChecker(self.api_base_url, self.current_version)
            
            # 检查更新
            needs_update, version_info = version_checker.check_for_updates()
            
            if needs_update and version_info:
                # 弹出更新提示对话框
                is_force_update = version_info.get("is_force_update", False)
                update_dialog = UpdateDialog(self, version_info, is_force_update)
                update_dialog.exec()
        except Exception as e:
            logging.error(f"检查更新失败: {str(e)}")
    
    def start_registration(self):
        """开始注册账号"""
        try:
            # 如果已经有相同类型的工作线程在运行，则不创建新的
            if "register" in self.active_workers and self.active_workers["register"].isRunning():
                self.update_log("已有注册任务在运行中，请等待完成")
                return
                
            # 创建加载对话框
            self.loading_dialog = LoadingDialog(self, "正在注册账号...")
            
            # 创建工作线程
            self.worker = WorkerThread("register", {"headless": True})
            
            # 连接信号
            self.worker.update_signal.connect(self.update_log)
            self.worker.update_progress_signal.connect(self.loading_dialog.update_message)
            self.worker.finished_signal.connect(self.registration_finished)
            self.worker.account_created_signal.connect(self._handle_account_created)
            
            # 关联工作线程到对话框
            self.loading_dialog.set_worker(self.worker)
            self.loading_dialog.dialog_closed.connect(self._handle_dialog_closed)
            
            # 保存线程引用并启动
            self.active_workers["register"] = self.worker
            self.worker.start()
            
            # 显示加载对话框
            self.loading_dialog.exec()
            
        except Exception as e:
            self.update_log(f"启动注册过程时出错: {str(e)}")
            logging.error(f"启动注册过程时出错: {str(e)}")
    
    def _handle_account_created(self, email, access_token, refresh_token, user_id):
        """处理账号创建成功信号"""
        # 更新认证状态
        if self.auth_status_label:
            self.auth_status_label.setText("已认证")
            self.auth_status_label.setStyleSheet("font-weight: bold; color: #03a9f4;")
        # 其他相关处理可以在这里添加

    def registration_finished(self, success, message):
        """注册完成回调"""
        # 关闭加载对话框
        if hasattr(self, 'loading_dialog') and self.loading_dialog:
            self.loading_dialog.close()
            
        # 清理已完成的线程引用
        if "register" in self.active_workers:
            del self.active_workers["register"]
            
        if success:
            ModernMessageBox.information(self, "成功", "注册成功")
            self.check_system_status()  # 更新系统状态
        else:
            ModernMessageBox.error(self, "错误", "注册失败: " + message)
    
    def _handle_dialog_closed(self):
        """处理对话框被用户关闭的情况"""
        # 记录日志
        self.update_log("操作已被用户取消")
        
        # 在UI中更新状态
        self.status_bar.showMessage("操作已取消")
    
    def reset_machine_id(self):
        """重置机器ID"""
        try:
            # 如果已经有相同类型的工作线程在运行，则不创建新的
            if "reset_machine_id" in self.active_workers and self.active_workers["reset_machine_id"].isRunning():
                self.update_log("已有重置机器ID任务在运行中，请等待完成")
                return
                
            # 创建加载对话框
            self.loading_dialog = LoadingDialog(self, "正在重置机器ID...")
            
            # 创建工作线程
            self.worker = WorkerThread("reset_machine_id", {})
            
            # 连接信号
            self.worker.update_signal.connect(self.update_log)
            self.worker.update_progress_signal.connect(self.loading_dialog.update_message)
            self.worker.finished_signal.connect(self.reset_machine_finished)
            
            # 关联工作线程到对话框
            self.loading_dialog.set_worker(self.worker)
            self.loading_dialog.dialog_closed.connect(self._handle_dialog_closed)
            
            # 保存线程引用并启动
            self.active_workers["reset_machine_id"] = self.worker
            self.worker.start()
            
            # 显示加载对话框
            self.loading_dialog.exec()
            
        except Exception as e:
            self.update_log(f"启动重置过程时出错: {str(e)}")
            logging.error(f"启动重置过程时出错: {str(e)}")
    
    def reset_machine_finished(self, success, message):
        """重置机器ID完成回调"""
        # 关闭加载对话框
        if hasattr(self, 'loading_dialog') and self.loading_dialog:
            self.loading_dialog.close()
            
        # 清理已完成的线程引用
        if "reset_machine_id" in self.active_workers:
            del self.active_workers["reset_machine_id"]
            
        if success:
            ModernMessageBox.information(self, "成功", "机器ID重置成功")
            self.check_system_status()  # 更新系统状态
        else:
            ModernMessageBox.error(self, "错误", "机器ID重置失败: " + message)
    
    def check_system_status(self):
        """检查系统状态"""
        try:
            # 如果已经有相同类型的工作线程在运行，则不创建新的
            if "check_status" in self.active_workers and self.active_workers["check_status"].isRunning():
                self.update_log("已有状态检查任务在运行中，请等待完成")
                return
                
            # 创建工作线程
            self.worker = WorkerThread("check_status", {})
            self.worker.update_signal.connect(self.update_log)
            self.worker.finished_signal.connect(self.status_check_finished)
            
            # 保存线程引用并启动
            self.active_workers["check_status"] = self.worker
            self.worker.start()
            
        except Exception as e:
            self.update_log(f"启动状态检查时出错: {str(e)}")
            logging.error(f"启动状态检查时出错: {str(e)}")
    
    def status_check_finished(self, success, message):
        """状态检查完成回调"""
        # 清理已完成的线程引用
        if "check_status" in self.active_workers:
            del self.active_workers["check_status"]
            
        if success:
            try:
                # 解析状态信息
                status_info = json.loads(message)
                
                # 更新版本信息显示
                if "version" in status_info and self.cursor_version_label:
                    self.cursor_version_label.setText(status_info["version"])
                
                # 更新机器ID显示
                if "machine_id" in status_info and self.machine_id_label:
                    self.machine_id_label.setText(status_info["machine_id"])
                    
                # 更新Cursor机器ID显示
                if "cursor_machine_id" in status_info and hasattr(self, 'cursor_machine_id_label') and self.cursor_machine_id_label:
                    self.cursor_machine_id_label.setText(status_info["cursor_machine_id"])
                
                # 更新授权状态显示
                if "auth_status" in status_info and self.auth_status_label:
                    auth_status = status_info["auth_status"]
                    # 检查auth_status是否包含"已登录"字符串
                    if "已登录" in auth_status:
                        # 显示包括邮箱的详细状态
                        self.auth_status_label.setText(auth_status)
                        self.auth_status_label.setStyleSheet("font-weight: bold; color: #03a9f4;")
                    else:
                        self.auth_status_label.setText(auth_status)
                        self.auth_status_label.setStyleSheet("font-weight: bold; color: #b3261e;")
                
            except Exception as e:
                self.update_log(f"处理状态检查结果失败: {str(e)}")
                logging.error(f"处理状态检查结果失败: {str(e)}")
        else:
            self.update_log("状态检查失败")
    
    def update_log(self, message):
        """更新日志"""
        if hasattr(self, 'log_text') and self.log_text:
            self.log_text.append(message)
    
    def clear_logs(self):
        """清除日志"""
        if self.log_text:
            self.log_text.clear()
    
    def export_logs(self):
        """导出日志"""
        try:
            if not self.log_text:
                return
                
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "导出日志",
                os.path.join(os.path.expanduser("~"), "cursor_pro_logs.txt"),
                "文本文件 (*.txt)"
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                logging.info(f"日志已导出到 {file_path}")
                ModernMessageBox.information(self, "成功", f"日志已成功导出到:\n{file_path}")
        except Exception as e:
            logging.error(f"导出日志失败: {str(e)}")
            ModernMessageBox.warning(self, "导出失败", f"导出日志时出错: {str(e)}")

    def activate_license(self):
        """激活授权码"""
        try:
            # 获取输入的授权码
            if not self.license_code_input:
                ModernMessageBox.warning(self, "错误", "UI组件未初始化")
                return
                
            license_code = self.license_code_input.text().strip()
            if not license_code:
                ModernMessageBox.warning(self, "错误", "请输入授权码")
                return
                
            # 如果已经有相同类型的工作线程在运行，则不创建新的
            if "verify_license" in self.active_workers and self.active_workers["verify_license"].isRunning():
                self.update_log("已有授权验证任务在运行中，请等待完成")
                return
                
            # 创建加载对话框
            self.loading_dialog = LoadingDialog(self, "正在验证授权码...")
            
            # 创建工作线程验证授权码
            params = {
                "license_code": license_code
            }
            self.worker = WorkerThread("verify_license", params)
            self.worker.update_signal.connect(self.update_log)
            self.worker.update_progress_signal.connect(self.loading_dialog.update_message)
            self.worker.finished_signal.connect(self.license_verification_finished)
            
            # 关联工作线程到对话框
            self.loading_dialog.set_worker(self.worker)
            self.loading_dialog.dialog_closed.connect(self._handle_dialog_closed)
            
            # 保存线程引用并启动
            self.active_workers["verify_license"] = self.worker
            self.worker.start()
            
            # 显示加载对话框
            self.loading_dialog.exec()
            
        except Exception as e:
            self.update_log(f"启动授权验证过程时出错: {str(e)}")
            logging.error(f"启动授权验证过程时出错: {str(e)}")
    
    def license_verification_finished(self, success, message):
        """授权验证完成回调"""
        # 关闭加载对话框
        if hasattr(self, 'loading_dialog') and self.loading_dialog:
            self.loading_dialog.close()
            
        # 清理已完成的线程引用
        if "verify_license" in self.active_workers:
            del self.active_workers["verify_license"]
            
        if success:
            try:
                # 解析返回的授权信息和绑定信息
                result = json.loads(message)
                license_info = result.get("license_info")
                binding_info = result.get("binding_info")
                
                if license_info and binding_info:
                    # 更新授权信息显示
                    self.update_license_display(license_info, binding_info)
                    
                    # 显示成功消息
                    ModernMessageBox.information(self, "成功", "授权码激活成功！")
                    
                    # 清空输入框
                    if self.license_code_input:
                        self.license_code_input.setText("")
                    
                    # 改变状态效果动画
                    self.animate_status_change()
                else:
                    ModernMessageBox.warning(self, "警告", "授权信息无效")
            except Exception as e:
                self.update_log(f"处理授权验证结果失败: {str(e)}")
                logging.error(f"处理授权验证结果失败: {str(e)}")
                ModernMessageBox.error(self, "错误", "处理授权验证结果失败")
        else:
            ModernMessageBox.error(self, "错误", "授权码验证失败: " + message)
    
    def renew_license(self):
        """续期授权"""
        # 获取当前授权码
        if not self.license_code_label:
            ModernMessageBox.warning(self, "错误", "UI组件未初始化")
            return
            
        license_code = self.license_code_label.text()
        if license_code == "无":
            ModernMessageBox.warning(self, "错误", "没有有效的授权码")
            return
        
        # 显示支付二维码对话框
        payment_dialog = PaymentQRCodeDialog(self, license_code)
        payment_dialog.exec()
        
        self.status_bar.showMessage("请在支付完成后重新激活授权码")
    
    def animate_status_change(self):
        """授权状态变更动画"""
        if not self.license_status_label:
            return
            
        # 创建高亮效果
        highlight = QGraphicsDropShadowEffect()
        highlight.setColor(QColor(76, 175, 80, 150))  # 绿色
        highlight.setBlurRadius(50)
        highlight.setOffset(0, 0)
        
        # 应用效果到授权卡片
        original_effect = self.license_status_label.graphicsEffect()
        self.license_status_label.setGraphicsEffect(highlight)
        
        # 创建动画
        def restore_effect():
            if self.license_status_label:
                self.license_status_label.setGraphicsEffect(original_effect)
        
        # 延时恢复原效果
        QTimer.singleShot(1000, restore_effect)

    def one_click_enjoy(self):
        """一键畅享功能"""
        try:
            # 如果已经有相同类型的工作线程在运行，则不创建新的
            if "one_click_enjoy" in self.active_workers and self.active_workers["one_click_enjoy"].isRunning():
                self.update_log("已有一键畅享任务在运行中，请等待完成")
                return
                
            # 创建加载对话框
            self.loading_dialog = LoadingDialog(self, "正在执行一键畅享...")
            
            # 创建工作线程
            self.worker = WorkerThread("one_click_enjoy", {"headless": True})
            
            # 连接信号
            self.worker.update_signal.connect(self.update_log)
            self.worker.update_progress_signal.connect(self.loading_dialog.update_message)
            self.worker.finished_signal.connect(self.one_click_enjoy_finished)
            self.worker.account_created_signal.connect(self._handle_account_created)
            
            # 关联工作线程到对话框
            self.loading_dialog.set_worker(self.worker)
            self.loading_dialog.dialog_closed.connect(self._handle_dialog_closed)
            
            # 保存线程引用并启动
            self.active_workers["one_click_enjoy"] = self.worker
            self.worker.start()
            
            # 显示加载对话框
            self.loading_dialog.exec()
            
        except Exception as e:
            self.update_log(f"启动一键畅享过程时出错: {str(e)}")
            logging.error(f"启动一键畅享过程时出错: {str(e)}")
    
    def one_click_enjoy_finished(self, success, message):
        """一键畅享完成回调"""
        # 清理已完成的线程引用
        if "one_click_enjoy" in self.active_workers:
            del self.active_workers["one_click_enjoy"]
            
        # 关闭加载对话框
        if hasattr(self, 'loading_dialog') and self.loading_dialog.isVisible():
            self.loading_dialog.close()
            
        if success:
            self.update_log("一键畅享操作完成！")
            ModernMessageBox.information(self, "操作成功", "一键畅享操作已成功完成！")
            
            # 更新状态
            QTimer.singleShot(500, self.check_system_status)
        else:
            self.update_log(f"一键畅享操作失败: {message}")
            ModernMessageBox.warning(self, "操作失败", f"一键畅享操作失败:\n{message}")
    
    def quick_switch_account(self):
        """快速换号功能"""
        self.update_log("开始快速换号操作...")
        
        # 如果已经有相同类型的工作线程在运行，则不创建新的
        if "quick_switch_account" in self.active_workers and self.active_workers["quick_switch_account"].isRunning():
            self.update_log("已有快速换号任务在运行中，请等待完成")
            return
        
        # 显示加载对话框
        from gui_components import LoadingDialog
        loading_dialog = LoadingDialog(self, "正在获取账号信息...")
        loading_dialog.show()
        
        try:
            # 步骤1: 从接口获取账号信息
            config = Config()
            api_url = f"{config.api_base_url}/api/v1/accounts/min-usage?status=ACTIVE&account_type=FREE"
            
            import requests
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code != 200:
                    raise Exception(f"API请求失败 (状态码: {response.status_code})")
                
                account_data = response.json()
                
                # 检查必要字段
                if not account_data.get("email") or not account_data.get("password"):
                    raise Exception("API返回的账号数据不完整")
                
                # 关闭加载对话框
                loading_dialog.close()
                
                # 显示获取到的账号信息
                account_email = account_data.get("email")
                self.update_log(f"成功获取账号: {account_email}")
                
                # 使用获取到的账号创建工作线程登录获取token
                worker_params = {
                    "email": account_data.get("email"),
                    "password": account_data.get("password")
                }
                
                # 创建新的加载对话框
                login_dialog = LoadingDialog(self, "正在登录账号获取token...")
                login_dialog.show()
                
                # 创建工作线程进行登录和token获取
                self.worker = WorkerThread("login_account", worker_params)
                self.worker.update_signal.connect(self.update_log)
                self.worker.update_progress_signal.connect(login_dialog.update_message)
                self.worker.finished_signal.connect(lambda success, message: self.quick_switch_finished(success, message, login_dialog))
                self.worker.account_created_signal.connect(self._handle_account_created)
                
                # 保存线程引用并启动
                self.active_workers["quick_switch_account"] = self.worker
                self.worker.start()
                
            except Exception as e:
                loading_dialog.close()
                self.update_log(f"获取账号信息失败: {str(e)}")
                ModernMessageBox.warning(self, "操作失败", f"获取账号信息失败:\n{str(e)}")
                
        except Exception as e:
            if loading_dialog.isVisible():
                loading_dialog.close()
            self.update_log(f"快速换号操作失败: {str(e)}")
            ModernMessageBox.warning(self, "操作失败", f"快速换号操作失败:\n{str(e)}")
    
    def quick_switch_finished(self, success, message, dialog):
        """快速换号完成回调"""
        # 关闭加载对话框
        if dialog and dialog.isVisible():
            dialog.close()
            
        # 清理已完成的线程引用
        if "quick_switch_account" in self.active_workers:
            del self.active_workers["quick_switch_account"]
        
        if success:
            self.update_log("快速换号操作完成！")
            ModernMessageBox.information(self, "操作成功", "账号切换成功！请重新启动Cursor软件使更改生效。")
            
            # 更新状态
            QTimer.singleShot(500, self.check_system_status)
        else:
            self.update_log(f"快速换号操作失败: {message}")
            ModernMessageBox.warning(self, "操作失败", f"快速换号操作失败:\n{message}")
    
    # 在窗口关闭时确保所有线程安全退出
    def closeEvent(self, event):
        """窗口关闭事件，确保所有线程安全退出"""
        # 遍历所有活动的工作线程
        for task_type, worker in list(self.active_workers.items()):
            if worker and worker.isRunning():
                self.update_log(f"正在终止{task_type}任务...")
                worker.requestInterruption()  # 请求中断线程
                
                # 等待最多2秒让线程结束
                if not worker.wait(2000):
                    self.update_log(f"{task_type}任务未能及时结束，强制终止")
                    # 如果线程包含浏览器资源，尝试清理
                    if hasattr(worker, 'cleanupBrowser'):
                        worker.cleanupBrowser()
                
        # 记录关闭信息
        self.update_log("应用程序正在关闭...")
                
        # 调用父类方法
        super().closeEvent(event) 