import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from language import get_translation

# 设置日志格式
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(log_format)

# 获取日志目录路径
log_dir = os.environ.get("LOGS_DIR", "logs")
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except Exception as e:
        print(f"无法创建日志目录 {log_dir}: {str(e)}")
        # 如果无法创建日志目录，使用临时目录
        import tempfile
        log_dir = os.path.join(tempfile.gettempdir(), "cursor_pro_logs")
        os.makedirs(log_dir, exist_ok=True)

class DebugFormatter(logging.Formatter):
    """Custom formatter that adds an open source project prefix to DEBUG level logs"""
    def format(self, record):
        if record.levelno == logging.DEBUG:
            record.msg = f"[Cursor Pro] {record.msg}"
        return super().format(record)

# 创建日志处理器
file_handler = RotatingFileHandler(
    os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log"),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(formatter)

# 创建控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(DebugFormatter(log_format))

# 配置根日志记录器
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# 配置第三方库的日志级别
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("DrissionPage").setLevel(logging.WARNING)

# 输出初始化信息
logging.info(get_translation("logger_initialized", dir=os.path.abspath(log_dir)))


def main_task():
    """
    Main task execution function. Simulates a workflow and handles errors.
    """
    try:
        logging.info("Starting the main task...")

        # Simulated task and error condition
        if some_condition():
            raise ValueError("Simulated error occurred.")

        logging.info("Main task completed successfully.")

    except ValueError as ve:
        logging.error(f"ValueError occurred: {ve}", exc_info=True)
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}", exc_info=True)
    finally:
        logging.info("Task execution finished.")


def some_condition():
    """
    Simulates an error condition. Returns True to trigger an error.
    Replace this logic with actual task conditions.
    """
    return True


if __name__ == "__main__":
    # Application workflow
    logging.info("Application started.")
    main_task()
    logging.info("Application exited.")
