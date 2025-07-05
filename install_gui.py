#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform

def print_header(text):
    """打印带有格式的标题"""
    print("\n" + "=" * 60)
    print(f" {text} ".center(60, "="))
    print("=" * 60)

def print_step(text):
    """打印步骤信息"""
    print(f"\n>> {text}")

def run_command(command):
    """运行命令并返回结果"""
    print(f"执行命令: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def check_python_version():
    """检查Python版本"""
    print_step("检查Python版本")
    version = sys.version_info
    print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("错误: 需要Python 3.6或更高版本")
        return False
    return True

def install_dependencies():
    """安装依赖"""
    print_step("安装依赖")
    
    # 安装基础依赖
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt"):
        return False
    
    # 安装PySide6
    print_step("安装PySide6")
    if not run_command(f"{sys.executable} -m pip install PySide6==6.5.2"):
        return False
    
    return True

def create_shortcut():
    """创建桌面快捷方式"""
    print_step("创建桌面快捷方式")
    
    system = platform.system()
    
    if system == "Windows":
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Cursor Pro 自动化工具.lnk")
            
            target = os.path.abspath(os.path.join(os.path.dirname(__file__), "gui_app.py"))
            wDir = os.path.dirname(target)
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = wDir
            shortcut.save()
            
            print(f"桌面快捷方式已创建: {path}")
            return True
        except ImportError:
            print("创建快捷方式需要安装winshell和pywin32")
            choice = input("是否安装这些依赖? (y/n): ")
            if choice.lower() == 'y':
                run_command(f"{sys.executable} -m pip install winshell pywin32")
                print("请重新运行此脚本以创建快捷方式")
            return False
        except Exception as e:
            print(f"创建快捷方式失败: {str(e)}")
            return False
    elif system == "Linux":
        # 创建.desktop文件
        desktop_file = os.path.expanduser("~/Desktop/cursor-auto-tool.desktop")
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "gui_app.py"))
        
        with open(desktop_file, "w") as f:
            f.write(f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Cursor Pro 自动化工具
Comment=Cursor Pro自动化注册和管理工具
Exec={sys.executable} "{script_path}"
Path={os.path.dirname(script_path)}
Terminal=false
Categories=Utility;
""")
        
        # 设置可执行权限
        os.chmod(desktop_file, 0o755)
        print(f"桌面快捷方式已创建: {desktop_file}")
        return True
    elif system == "Darwin":  # macOS
        # 创建.command文件
        desktop_file = os.path.expanduser("~/Desktop/Cursor Pro 自动化工具.command")
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "gui_app.py"))
        
        with open(desktop_file, "w") as f:
            f.write(f"""#!/bin/bash
cd "{os.path.dirname(script_path)}"
"{sys.executable}" "{script_path}"
""")
        
        # 设置可执行权限
        os.chmod(desktop_file, 0o755)
        print(f"桌面快捷方式已创建: {desktop_file}")
        return True
    else:
        print(f"不支持的操作系统: {system}")
        return False

def main():
    """主函数"""
    print_header("Cursor Pro 自动化工具 - GUI安装程序")
    
    # 检查Python版本
    if not check_python_version():
        input("按Enter键退出...")
        return
    
    # 安装依赖
    if not install_dependencies():
        print("安装依赖失败，请检查错误信息")
        input("按Enter键退出...")
        return
    
    # 创建桌面快捷方式
    create_choice = input("\n是否创建桌面快捷方式? (y/n): ")
    if create_choice.lower() == 'y':
        create_shortcut()
    
    print_header("安装完成")
    print("现在可以通过运行以下命令启动GUI界面:")
    print(f"  {sys.executable} gui_app.py")
    
    launch_choice = input("\n是否立即启动GUI界面? (y/n): ")
    if launch_choice.lower() == 'y':
        print("\n正在启动GUI界面...")
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "gui_app.py"))
        subprocess.Popen([sys.executable, script_path])
    
    input("\n按Enter键退出安装程序...")

if __name__ == "__main__":
    main() 