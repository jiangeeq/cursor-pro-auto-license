import os
import sys
import json
import uuid
import hashlib
import shutil
from colorama import Fore, Style, init
from logger import logging

# 初始化colorama
init()

# 定义emoji和颜色常量
EMOJI = {
    "FILE": "📄",
    "BACKUP": "💾",
    "SUCCESS": "✅",
    "ERROR": "❌",
    "INFO": "ℹ️",
    "RESET": "🔄",
}


class MachineIDResetter:
    def __init__(self):
        # 判断操作系统
        if sys.platform == "win32":  # Windows
            appdata = os.getenv("APPDATA")
            if appdata is None:
                raise EnvironmentError("APPDATA 环境变量未设置")
            self.db_path = os.path.join(
                appdata, "Cursor", "User", "globalStorage", "storage.json"
            )
        elif sys.platform == "darwin":  # macOS
            self.db_path = os.path.abspath(
                os.path.expanduser(
                    "~/Library/Application Support/Cursor/User/globalStorage/storage.json"
                )
            )
        elif sys.platform == "linux":  # Linux 和其他类Unix系统
            self.db_path = os.path.abspath(
                os.path.expanduser("~/.config/Cursor/User/globalStorage/storage.json")
            )
        else:
            raise NotImplementedError(f"不支持的操作系统: {sys.platform}")

    def generate_new_ids(self):
        """生成新的机器ID"""
        # 生成新的UUID
        dev_device_id = str(uuid.uuid4())

        # 生成新的machineId (64个字符的十六进制)
        machine_id = hashlib.sha256(os.urandom(32)).hexdigest()

        # 生成新的macMachineId (128个字符的十六进制)
        mac_machine_id = hashlib.sha512(os.urandom(64)).hexdigest()

        # 生成新的sqmId
        sqm_id = "{" + str(uuid.uuid4()).upper() + "}"

        return {
            "telemetry.devDeviceId": dev_device_id,
            "telemetry.macMachineId": mac_machine_id,
            "telemetry.machineId": machine_id,
            "telemetry.sqmId": sqm_id,
        }

    def reset_machine_ids(self) -> bool: # 重置机器ID返回是否成功
        """重置机器ID并备份原文件"""
        try:
            logging.info(f"{EMOJI['INFO']} 正在检查配置文件...")

            # 检查文件是否存在
            if not os.path.exists(self.db_path):
                logging.error(f"{EMOJI['ERROR']} 配置文件不存在: {self.db_path}")
                return False

            # 检查文件权限
            if not os.access(self.db_path, os.R_OK | os.W_OK):
                logging.error(f"{EMOJI['ERROR']} 无法读写配置文件，请检查文件权限！")
                logging.error(f"{EMOJI['ERROR']} 如果你使用过 go-cursor-help 来修改 ID; 请修改文件只读权限 {self.db_path}")
                return False

            # 读取现有配置
            logging.info(f"{EMOJI['FILE']} 读取当前配置...")
            with open(self.db_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 生成新的ID
            logging.info(f"{EMOJI['RESET']} 生成新的机器标识...")
            new_ids = self.generate_new_ids()

            # 更新配置
            config.update(new_ids)

            # 保存新配置
            logging.info(f"{EMOJI['FILE']} 保存新配置...")
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)

            logging.info(f"{EMOJI['SUCCESS']} 机器标识重置成功！")
            logging.info(f"\n新的机器标识:")
            for key, value in new_ids.items():
                logging.info(f"{EMOJI['INFO']} {key}: {value}")

            return True

        except PermissionError as e:
            logging.error(f"{EMOJI['ERROR']} 权限错误: {str(e)}")
            logging.error(f"{EMOJI['INFO']} 请尝试以管理员身份运行此程序")
            return False
        except Exception as e:
            logging.error(f"{EMOJI['ERROR']} 重置过程出错: {str(e)}")

            return False


if __name__ == "__main__":
    logging.info(f"\n{'='*50}")
    logging.info(f"{EMOJI['RESET']} Cursor 机器标识重置工具")
    logging.info(f"{'='*50}")

    resetter = MachineIDResetter()
    resetter.reset_machine_ids()

    logging.info(f"\n{'='*50}")
    input(f"{EMOJI['INFO']} 按回车键退出...")
