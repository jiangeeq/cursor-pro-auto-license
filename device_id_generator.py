import os
import uuid
import hashlib
import platform
import subprocess
import wmi  # 需要添加到 requirements.txt
import json
from typing import Dict, List, Optional, Any, Union
from logger import logging

class DeviceIDGenerator:
    def __init__(self):
        self.wmi_client = wmi.WMI() if platform.system() == "Windows" else None
        
    def _hash_combine(self, values: List[str]) -> str:
        """组合多个值并生成哈希"""
        combined = "|".join(str(v) for v in values if v)
        return hashlib.sha256(combined.encode()).hexdigest()
        
    def _get_cpu_id(self) -> str:
        """获取CPU ID"""
        try:
            if platform.system() == "Windows" and self.wmi_client:
                cpu = self.wmi_client.Win32_Processor()[0]
                return f"{cpu.ProcessorId.strip()}"
            elif platform.system() == "Darwin":  # macOS
                cmd = "sysctl -n machdep.cpu.brand_string"
                output = subprocess.check_output(cmd, shell=True).decode().strip()
                return output
            else:  # Linux
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if line.startswith("processor"):
                            return line.split(":")[1].strip()
            return ""
        except Exception as e:
            logging.error(f"获取CPU ID失败: {str(e)}")
            return ""

    def _get_motherboard_serial(self) -> str:
        """获取主板序列号"""
        try:
            if platform.system() == "Windows" and self.wmi_client:
                board = self.wmi_client.Win32_BaseBoard()[0]
                return f"{board.SerialNumber.strip()}"
            elif platform.system() == "Darwin":  # macOS
                cmd = "ioreg -l | grep IOPlatformSerialNumber"
                output = subprocess.check_output(cmd, shell=True).decode().strip()
                return output.split("=")[-1].strip().replace('"', '')
            else:  # Linux
                with open("/sys/class/dmi/id/board_serial", "r") as f:
                    return f.read().strip()
            return ""
        except Exception as e:
            logging.error(f"获取主板序列号失败: {str(e)}")
            return ""

    def _get_bios_uuid(self) -> str:
        """获取BIOS UUID"""
        try:
            if platform.system() == "Windows" and self.wmi_client:
                comp = self.wmi_client.Win32_ComputerSystemProduct()[0]
                return f"{comp.UUID.strip()}"
            elif platform.system() == "Darwin":  # macOS
                cmd = "ioreg -rd1 -c IOPlatformExpertDevice | grep -i UUID"
                output = subprocess.check_output(cmd, shell=True).decode().strip()
                return output.split("=")[-1].strip().replace('"', '')
            else:  # Linux
                with open("/sys/class/dmi/id/product_uuid", "r") as f:
                    return f.read().strip()
            return ""
        except Exception as e:
            logging.error(f"获取BIOS UUID失败: {str(e)}")
            return ""

    def _get_disk_serial(self) -> str:
        """获取主硬盘序列号"""
        try:
            if platform.system() == "Windows" and self.wmi_client:
                for disk in self.wmi_client.Win32_DiskDrive():
                    if disk.Size:  # 获取第一个有大小的磁盘
                        return f"{disk.SerialNumber.strip()}"
            elif platform.system() == "Darwin":  # macOS
                cmd = "diskutil info /dev/disk0 | grep 'Disk / Partition UUID'"
                output = subprocess.check_output(cmd, shell=True).decode().strip()
                return output.split(":")[-1].strip()
            else:  # Linux
                cmd = "lsblk --nodeps -no serial /dev/sda"
                output = subprocess.check_output(cmd, shell=True).decode().strip()
                return output
            return ""
        except Exception as e:
            logging.error(f"获取硬盘序列号失败: {str(e)}")
            return ""

    def _get_primary_mac(self) -> str:
        """获取主网卡MAC地址"""
        try:
            if platform.system() == "Windows" and self.wmi_client:
                for nic in self.wmi_client.Win32_NetworkAdapter():
                    if nic.PhysicalAdapter and nic.MACAddress:
                        return f"{nic.MACAddress.strip()}"
            elif platform.system() == "Darwin":  # macOS
                cmd = "networksetup -listallhardwareports | grep -A 1 'Hardware Port: Wi-Fi' | grep 'Ethernet Address:'"
                output = subprocess.check_output(cmd, shell=True).decode().strip()
                return output.split(":")[-1].strip()
            else:  # Linux
                cmd = "ip link show | grep link/ether | head -n 1"
                output = subprocess.check_output(cmd, shell=True).decode().strip()
                return output.split()[1].strip()
            return ""
        except Exception as e:
            logging.error(f"获取MAC地址失败: {str(e)}")
            return ""

    def generate_device_info(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """生成设备信息"""
        # 收集硬件标识符
        identifiers = {
            'cpu': self._get_cpu_id(),
            'motherboard': self._get_motherboard_serial(),
            'bios': self._get_bios_uuid(),
            'disk': self._get_disk_serial(),
            'mac': self._get_primary_mac()
        }
        
        # 生成主标识符（CPU + 主板 + BIOS）
        primary_id = self._hash_combine([
            identifiers['cpu'],
            identifiers['motherboard'],
            identifiers['bios']
        ])
        
        # 生成备用标识符（硬盘 + MAC）
        backup_id = self._hash_combine([
            identifiers['disk'],
            identifiers['mac']
        ])
        
        # 生成完整的硬件哈希
        hardware_hash = self._hash_combine(list(identifiers.values()))
        
        # 返回设备信息
        return {
            'device_id': primary_id,
            'backup_id': backup_id,
            'hardware_hash': hardware_hash,
            'raw_identifiers': identifiers  # 用于调试和验证
        }

    def save_device_info(self, file_path: str, device_info: Dict[str, Union[str, Dict[str, str]]]) -> None:
        """保存设备信息到文件"""
        try:
            with open(file_path, 'w') as f:
                json.dump(device_info, f, indent=4)
        except Exception as e:
            logging.error(f"保存设备信息失败: {str(e)}")

    def load_device_info(self, file_path: str) -> Optional[Dict[str, Union[str, Dict[str, str]]]]:
        """从文件加载设备信息"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"加载设备信息失败: {str(e)}")
        return None 