#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import platform
import subprocess
import datetime
import argparse

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
        # 设置环境变量，解决中文编码问题
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            text=True,
            encoding="utf-8",  # 明确指定编码为UTF-8
            errors="replace",  # 替换无法解码的字符
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            env=env
        )
        
        if result.stdout:
            print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stderr:
            print(e.stderr)
        return False, e.stderr

def create_virtual_env():
    """创建并激活虚拟环境"""
    print_step("创建虚拟环境")
    
    venv_dir = "build_venv"
    
    # 检查是否已经存在虚拟环境
    if os.path.exists(venv_dir):
        print(f"虚拟环境已存在: {venv_dir}")
        return True
    
    # 创建虚拟环境
    try:
        print(f"创建虚拟环境: {venv_dir}")
        import venv
        venv.create(venv_dir, with_pip=True)
    except Exception as e:
        print(f"创建虚拟环境失败: {str(e)}")
        return False
    
    # 安装必要的依赖
    print_step("安装依赖")
    pip_install_cmd = f"{get_python_executable()} -m pip install -r requirements.txt"
    success, _ = run_command(pip_install_cmd)
    
    if not success:
        print("安装依赖失败")
        return False
    
    return True

def get_python_executable():
    """获取Python可执行文件路径"""
    # 检查是否使用conda环境
    if os.environ.get('CONDA_PREFIX') is not None:
        if sys.platform.startswith('win'):
            return "python.exe"
        else:
            return "python"
    
    venv_dir = "build_venv"
    if sys.platform.startswith('win'):
        return os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        return os.path.join(venv_dir, "bin", "python")

def create_spec_file():
    """创建自定义spec文件"""
    print_step("创建spec文件")
    
    # 使用更简单的方式，不创建spec文件，直接使用命令行参数
    return True

def build_executable():
    """构建可执行文件"""
    print_step("构建可执行文件")
    
    # 检查输出目录是否存在，如果存在则询问是否删除
    dist_dir = os.path.join("dist")
    if os.path.exists(dist_dir):
        auto_delete = os.environ.get('AUTO_DELETE_OUTPUT', 'no').lower() == 'yes'
        
        if auto_delete:
            print(f"自动删除已存在的输出目录: {dist_dir}")
            try:
                shutil.rmtree(dist_dir)
                print("目录已删除")
            except Exception as e:
                print(f"删除目录失败: {str(e)}")
                return False
        else:
            print(f"发现已存在的输出目录: {dist_dir}")
            choice = input("是否删除已存在的输出目录? (y/n): ")
            if choice.lower() == 'y':
                try:
                    print(f"正在删除目录: {dist_dir}")
                    shutil.rmtree(dist_dir)
                    print("目录已删除")
                except Exception as e:
                    print(f"删除目录失败: {str(e)}")
                    return False
            else:
                print("构建取消")
                return False
    
    # 检查是否使用conda环境
    is_conda = os.environ.get('CONDA_PREFIX') is not None
    python_cmd = "python" if is_conda else get_python_executable()
    
    # 创建运行时钩子
    runtime_hook = create_runtime_hook()
    
    # 直接使用命令行参数构建
    icon_param = ""
    if os.path.exists("img/icon.png"):
        icon_param = f"--icon=img/icon.png"
    
    # 收集数据文件
    data_files = collect_data_files()
    
    # 添加所有必要的参数，使用--onefile选项
    command = (
        f"{python_cmd} -m PyInstaller "
        f"--name=\"Cursor Pro 自动化工具\" "
        f"--onefile "  # 使用onefile选项
        f"--windowed "
        f"{icon_param} "
        f"{data_files} "
        f"--hidden-import PySide6.QtCore "
        f"--hidden-import PySide6.QtGui "
        f"--hidden-import PySide6.QtWidgets "
        f"--hidden-import requests "
        f"--hidden-import openpyxl "
        f"--hidden-import openpyxl.cell "
        f"--hidden-import openpyxl.cell._writer "
        f"--hidden-import openpyxl.worksheet "
        f"--hidden-import openpyxl.worksheet._writer "
        f"--hidden-import openpyxl.drawing "
        f"--hidden-import openpyxl.styles "
        f"--hidden-import openpyxl.utils "
        f"--hidden-import openpyxl.workbook "
        f"--hidden-import openpyxl.reader "
        f"--hidden-import openpyxl.writer "
        f"--hidden-import DataRecorder "
        f"--hidden-import DrissionPage "
        f"--additional-hooks-dir=hooks "  # 使用钩子目录
        f"--runtime-hook=\"{runtime_hook}\" "  # 添加运行时钩子
        f"--clean "
        f"gui_app.py"
    )
    
    success, _ = run_command(command)
    
    if success:
        print("构建成功!")
        return True
    else:
        print("构建失败!")
        return False

def create_zip_archive():
    """创建ZIP归档文件"""
    print_step("创建ZIP归档文件")
    
    # 检查dist目录是否存在
    if not os.path.exists("dist"):
        print("错误: 找不到dist目录，构建可能失败")
        return False
    
    # 检查EXE文件是否存在
    exe_file = os.path.join("dist", "Cursor Pro 自动化工具.exe")
    if not os.path.exists(exe_file):
        print(f"错误: 找不到EXE文件 {exe_file}")
        return False
    
    # 创建ZIP文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"Cursor_Pro_自动化工具_单文件版_{timestamp}.zip"
    
    # 删除旧的ZIP文件
    if os.path.exists(zip_filename):
        os.remove(zip_filename)
    
    # 创建ZIP文件
    try:
        print(f"正在创建ZIP文件: {zip_filename}")
        import zipfile
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 只添加EXE文件
            zipf.write(exe_file, os.path.basename(exe_file))
        
        print(f"ZIP文件创建成功: {os.path.abspath(zip_filename)}")
        return True
    except Exception as e:
        print(f"创建ZIP文件失败: {str(e)}")
        return False

def setup_environment():
    """设置环境和安装依赖"""
    print_step("设置环境")
    
    # 检查是否使用conda环境
    is_conda = os.environ.get('CONDA_PREFIX') is not None
    
    if is_conda:
        print("检测到conda环境，将直接在当前环境中安装依赖")
        # 安装必要的依赖
        print("安装依赖...")
        run_command(f"pip install -r requirements.txt")
        
        # 确保安装了Pillow库（用于图标转换）
        print("确保安装Pillow库（用于图标转换）...")
        run_command(f"pip install pillow pyinstaller")
    else:
        # 使用venv创建虚拟环境
        venv_dir = "build_venv"
        if not os.path.exists(venv_dir):
            print(f"创建虚拟环境: {venv_dir}")
            run_command(f"python -m venv {venv_dir}")
        
        # 安装必要的依赖
        print("安装依赖...")
        run_command(f"{get_python_executable()} -m pip install -r requirements.txt")
        
        # 确保安装了Pillow库（用于图标转换）
        print("确保安装Pillow库（用于图标转换）...")
        run_command(f"{get_python_executable()} -m pip install pillow")
    
    return True

def create_hook_file():
    """创建钩子文件，确保正确打包特定模块"""
    print_step("创建钩子文件")
    
    try:
        # 创建hooks目录
        hooks_dir = "hooks"
        if not os.path.exists(hooks_dir):
            os.makedirs(hooks_dir)
        
        # 创建openpyxl钩子
        openpyxl_hook = os.path.join(hooks_dir, "hook-openpyxl.py")
        with open(openpyxl_hook, "w", encoding="utf-8") as f:
            f.write("""
# PyInstaller钩子文件，确保openpyxl模块被正确打包
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# 收集所有子模块
hiddenimports = collect_submodules('openpyxl')

# 特别添加已知可能缺失的模块
hiddenimports += [
    'openpyxl.cell._writer',
    'openpyxl.cell.cell',
    'openpyxl.worksheet._writer',
    'openpyxl.styles.fonts',
    'openpyxl.styles.fills',
]

# 收集数据文件
datas = collect_data_files('openpyxl')
""")
        
        # 创建DrissionPage钩子
        drission_hook = os.path.join(hooks_dir, "hook-DrissionPage.py")
        with open(drission_hook, "w", encoding="utf-8") as f:
            f.write("""
# PyInstaller钩子文件，确保DrissionPage模块被正确打包
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# 收集所有子模块
hiddenimports = collect_submodules('DrissionPage')
hiddenimports += collect_submodules('DataRecorder')

# 收集数据文件
datas = collect_data_files('DrissionPage')
datas += collect_data_files('DataRecorder')
""")
        
        print("钩子文件创建成功")
        return True
    except Exception as e:
        print(f"创建钩子文件失败: {str(e)}")
        return False

def collect_data_files():
    """收集所有必要的数据文件"""
    print_step("收集数据文件")
    
    data_files = []
    
    # 收集图像文件
    if os.path.exists("img"):
        for file in os.listdir("img"):
            if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".ico"):
                data_files.append(f"--add-data \"img/{file};img\"")
    
    # 添加.env文件（项目中已有）
    if os.path.exists(".env"):
        print("找到.env文件，将包含在打包中...")
        data_files.append("--add-data \".env;.\"")
    else:
        print("警告：未找到.env文件，应用可能无法正常工作")
    
    # 添加config.py文件
    if os.path.exists("config.py"):
        data_files.append("--add-data \"config.py;.\"")
    
    # 确保logs目录存在
    if not os.path.exists("logs"):
        os.makedirs("logs")
    data_files.append("--add-data \"logs;logs\"")
    
    # 添加reset_file文件夹（重置机器ID的脚本文件夹）
    if os.path.exists("reset_file"):
        print("找到reset_file文件夹，将包含在打包中...")
        data_files.append("--add-data \"reset_file;reset_file\"")
    else:
        print("警告：未找到reset_file文件夹，重置机器ID功能可能无法工作")
    
    # 添加其他可能需要的文件
    for file in ["names-dataset.txt"]:
        if os.path.exists(file):
            data_files.append(f"--add-data \"{file};.\"")
    
    # 添加turnstilePatch目录
    if os.path.exists("turnstilePatch"):
        data_files.append("--add-data \"turnstilePatch;turnstilePatch\"")
    
    return " ".join(data_files)

def create_runtime_hook():
    """创建运行时钩子，用于处理资源文件加载"""
    print_step("创建运行时钩子")
    
    # 创建钩子目录
    hooks_dir = "hooks"
    if not os.path.exists(hooks_dir):
        os.makedirs(hooks_dir)
    
    # 创建运行时钩子文件
    runtime_hook = os.path.join(hooks_dir, "runtime_hook.py")
    with open(runtime_hook, "w", encoding="utf-8") as f:
        f.write("""
# PyInstaller运行时钩子，处理资源文件加载
import os
import sys
import tempfile
import shutil
import atexit

# 创建应用程序临时目录
app_temp_dir = os.path.join(tempfile.gettempdir(), "CursorProTool")
os.makedirs(app_temp_dir, exist_ok=True)

# 在退出时清理临时文件
def cleanup_temp_files():
    try:
        if os.path.exists(app_temp_dir):
            shutil.rmtree(app_temp_dir)
    except:
        pass

atexit.register(cleanup_temp_files)

def resource_path(relative_path):
    \"\"\"获取资源的绝对路径，适用于开发环境和PyInstaller打包后的环境\"\"\"
    try:
        # PyInstaller创建临时文件夹并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 设置环境变量，指向临时目录中的文件
os.environ["ENV_FILE_PATH"] = resource_path(".env")
os.environ["LOGS_DIR"] = os.path.join(app_temp_dir, "logs")

# 创建日志目录
os.makedirs(os.environ["LOGS_DIR"], exist_ok=True)

# 打印调试信息
print(f"环境文件路径: {os.environ['ENV_FILE_PATH']}")
print(f"日志目录: {os.environ['LOGS_DIR']}")
""")
    
    print("运行时钩子文件创建成功")
    return runtime_hook

def main():
    """主函数"""
    print_header("Cursor Pro 自动化工具打包程序")
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Cursor Pro 自动化工具打包程序')
    parser.add_argument('-y', '--yes', action='store_true', help='自动删除已存在的输出目录')
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ['AUTO_DELETE_OUTPUT'] = 'yes' if args.yes else 'no'
    
    # 设置环境和安装依赖
    if not setup_environment():
        print("环境设置失败")
        return
    
    # 创建钩子文件
    if not create_hook_file():
        print("创建钩子文件失败")
        return
    
    # 创建spec文件
    if not create_spec_file():
        print("创建spec文件失败")
        return
    
    # 构建可执行文件
    if not build_executable():
        print("构建可执行文件失败")
        return
    
    # 创建ZIP归档
    create_zip_archive()
    
    print_header("打包完成")
    print("可执行文件已创建: dist/Cursor Pro 自动化工具.exe")
    print("文件大小可能较大，这是因为所有依赖都已打包到单个EXE文件中")

if __name__ == "__main__":
    main()
