import platform
import os
import subprocess
import sys
import tempfile
import threading
import time
import shutil
from pathlib import Path
from logger import logging
from language import get_translation


def go_cursor_help() -> bool: # 重置机器ID返回是否成功
    system = platform.system()
    logging.info(get_translation("current_operating_system", system=system))
    
    # 创建临时目录存储脚本
    temp_dir = Path(tempfile.gettempdir()) / "cursor_reset_scripts"
    temp_dir.mkdir(exist_ok=True)
    
    # 检查本地reset_file文件夹中是否已有脚本
    local_reset_dir = Path(__file__).parent / "reset_file"
    
    if system == "Darwin":  # macOS
        script_path = temp_dir / "cursor_mac_id_modifier.sh"
        local_script_path = local_reset_dir / "cursor_mac_id_modifier.sh"
        
        # 只使用本地脚本
        if local_script_path.exists():
            # 复制脚本到临时目录
            shutil.copy(local_script_path, script_path)
            
            # 执行脚本并捕获输出
            logging.info(get_translation("executing_macos_command"))
            try:
                # 使用subprocess捕获输出
                cmd = f'sudo bash "{script_path}"'
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # 实时读取输出并记录到日志
                def read_output(pipe, prefix):
                    for line in iter(pipe.readline, ''):
                        if line:
                            logging.info(f"{prefix}: {line.strip()}")
                
                # 创建线程读取stdout和stderr
                stdout_thread = threading.Thread(target=read_output, args=(process.stdout, "脚本输出"))
                stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "脚本错误"))
                
                # 启动线程
                stdout_thread.start()
                stderr_thread.start()
                
                # 等待进程完成
                return_code = process.wait()
                
                # 等待线程完成
                stdout_thread.join()
                stderr_thread.join()
                
                if return_code == 0:
                    logging.info("脚本执行成功完成")
                    return True
                else:
                    logging.error(f"脚本执行失败，返回代码: {return_code}")
                    return False
            except Exception as e:
                logging.error(f"执行脚本时出错: {str(e)}")
                return False
        else:
            logging.error("本地macOS脚本不存在：请将cursor_mac_id_modifier.sh脚本放到reset_file文件夹中")
            return False
    
    elif system == "Linux":
        script_path = temp_dir / "cursor_linux_id_modifier.sh"
        local_script_path = local_reset_dir / "cursor_linux_id_modifier.sh"
        
        # 只使用本地脚本
        if local_script_path.exists():
            # 复制脚本到临时目录
            shutil.copy(local_script_path, script_path)
            
            # 执行脚本并捕获输出
            logging.info(get_translation("executing_linux_command"))
            try:
                # 使用subprocess捕获输出
                cmd = f'sudo bash "{script_path}"'
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # 实时读取输出并记录到日志
                def read_output(pipe, prefix):
                    for line in iter(pipe.readline, ''):
                        if line:
                            logging.info(f"{prefix}: {line.strip()}")
                
                # 创建线程读取stdout和stderr
                stdout_thread = threading.Thread(target=read_output, args=(process.stdout, "脚本输出"))
                stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "脚本错误"))
                
                # 启动线程
                stdout_thread.start()
                stderr_thread.start()
                
                # 等待进程完成
                return_code = process.wait()
                
                # 等待线程完成
                stdout_thread.join()
                stderr_thread.join()
                
                if return_code == 0:
                    logging.info("脚本执行成功完成")
                    return True
                else:
                    logging.error(f"脚本执行失败，返回代码: {return_code}")
                    return False
            except Exception as e:
                logging.error(f"执行脚本时出错: {str(e)}")
                return False
        else:
            logging.error("本地Linux脚本不存在：请将cursor_linux_id_modifier.sh脚本放到reset_file文件夹中")
            return False
    
    elif system == "Windows":
        # 对于Windows，使用PowerShell以管理员权限执行脚本，尝试隐藏窗口
        script_path = temp_dir / "cursor_win_id_modifier.ps1"
        log_path = temp_dir / "cursor_reset_log.txt"
        local_script_path = local_reset_dir / "cursor_win_id_modifier.ps1"
        
        # 只使用本地PowerShell脚本
        if local_script_path.exists():
            # 复制脚本到临时目录
            shutil.copy(local_script_path, script_path)
            
            # 创建一个批处理文件来执行PowerShell脚本并捕获输出
            batch_path = temp_dir / "run_cursor_reset.bat"
            ps_command = f'powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File "{script_path}" > "{log_path}" 2>&1'
            
            with open(batch_path, 'w') as batch_file:
                batch_file.write(f'@echo off\n')
                batch_file.write(f'echo 正在执行Cursor机器ID重置脚本...\n')
                batch_file.write(f'{ps_command}\n')
                batch_file.write(f'echo 脚本执行完成\n')
            
            # 启动一个后台线程来监视日志文件并将内容发送到GUI日志
            def monitor_log_file():
                # 等待日志文件创建
                wait_count = 0
                while not os.path.exists(log_path) and wait_count < 30:  # 增加等待时间
                    time.sleep(1)
                    wait_count += 1
                    if wait_count % 5 == 0:
                        logging.info(f"等待日志文件创建，已等待 {wait_count} 秒...")
                
                if not os.path.exists(log_path):
                    logging.warning("日志文件未创建，无法显示脚本输出")
                    logging.warning("请检查UAC确认窗口是否被阻止或脚本是否未执行")
                    return
                
                logging.info("日志文件已创建，开始读取脚本输出")
                
                # 监视日志文件并将新行发送到GUI日志
                last_size = 0
                while True:
                    try:
                        if not os.path.exists(log_path):
                            break
                            
                        current_size = os.path.getsize(log_path)
                        if current_size > last_size:
                            with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_file:
                                log_file.seek(last_size)
                                new_content = log_file.read()
                                for line in new_content.splitlines():
                                    if line.strip():
                                        logging.info(f"脚本输出: {line.strip()}")
                            last_size = current_size
                        
                        # 检查脚本是否已完成
                        time.sleep(1)
                    except Exception as e:
                        logging.error(f"读取日志文件时出错: {str(e)}")
                        break
            
            # 启动监视线程
            log_monitor = threading.Thread(target=monitor_log_file)
            log_monitor.daemon = True
            log_monitor.start()
            
            # 使用subprocess启动，尝试隐藏窗口
            logging.info("正在启动管理员权限脚本，尝试隐藏窗口...")
            try:
                # 创建启动信息对象以隐藏窗口
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0  # SW_HIDE
                
                # 使用PowerShell启动批处理文件，设置隐藏窗口
                command = f'powershell -Command "Start-Process \'{batch_path}\' -Verb RunAs -WindowStyle Hidden"'
                
                # 使用CREATE_NO_WINDOW标志启动进程
                subprocess.Popen(
                    command,
                    shell=True,
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            
                logging.info("已启动管理员权限脚本，请在UAC提示窗口中确认")
                return True
                
            except Exception as e:
                logging.error(f"启动管理员权限脚本失败: {str(e)}")
                
                # 备用方法：尝试直接使用PowerShell执行
                try:
                    logging.info("尝试使用备用方法启动...")
                    
                    # 使用另一种方式尝试隐藏窗口
                    command = f'powershell -Command "Start-Process powershell -ArgumentList \'-ExecutionPolicy Bypass -WindowStyle Hidden -File \"{script_path}\"\' -Verb RunAs -WindowStyle Hidden"'
                    
                    subprocess.Popen(
                        command,
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    logging.info("已使用备用方法启动，请在UAC提示窗口中确认")
                    return True
                except Exception as e2:
                    logging.error(f"备用方法也失败: {str(e2)}")
                    return False
        else:
            logging.error("本地Windows脚本不存在：请将cursor_win_id_modifier.ps1脚本放到reset_file文件夹中")
            return False
    
    else:
        logging.error(get_translation("unsupported_operating_system", system=system))
        return False

def main():
    go_cursor_help()

if __name__ == "__main__":
    main()