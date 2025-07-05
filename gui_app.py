#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# 导入主窗口类
from main_window import MainWindow

def main():
    # 设置环境变量以过滤libpng警告
    os.environ['QT_LOGGING_RULES'] = 'qt.gui.imageio.png=false'
    
    app = QApplication(sys.argv)
    
    # 设置应用图标
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    
    # 确保窗口显示在屏幕上
    window.show()
    window.setWindowState(window.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
    window.activateWindow()
    
    # 确保窗口位于前台
    window.raise_()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 