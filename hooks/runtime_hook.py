
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
    """获取资源的绝对路径，适用于开发环境和PyInstaller打包后的环境"""
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
