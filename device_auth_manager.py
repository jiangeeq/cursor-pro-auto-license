import requests
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Optional, Tuple, Any, Union
from config import Config
from language import get_translation
from device_id_generator import DeviceIDGenerator  # 添加导入

def get_app_data_dir(app_name: str = "CursorPro") -> str:
    """获取应用数据目录路径，确保目录存在
    
    Args:
        app_name: 应用程序名称
        
    Returns:
        str: 应用数据目录路径
    """
    if os.name == 'nt':  # Windows系统
        # 在Windows下使用AppData/Local目录
        app_data_dir = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), app_name)
    elif os.name == 'posix':  # Linux/Mac系统
        if sys.platform == 'darwin':  # macOS
            app_data_dir = os.path.join(os.path.expanduser('~/Library/Application Support'), app_name)
        else:  # Linux
            app_data_dir = os.path.join(os.path.expanduser('~/.config'), app_name)
    else:  # 其他系统
        app_data_dir = os.path.join(os.path.expanduser('~'), f'.{app_name.lower()}')
    
    # 确保目录存在
    os.makedirs(app_data_dir, exist_ok=True)
    
    # 记录应用数据目录路径
    logging.debug(f"应用数据目录: {app_data_dir}")
    
    return app_data_dir

def get_machine_device_id() -> str:
    """获取设备主ID"""
    # 获取应用数据目录
    app_data_dir = get_app_data_dir()
    
    # 设备信息文件路径
    device_info_path = os.path.join(app_data_dir, "device_info.json")
    
    # 如果设备信息文件不存在，先生成
    if not os.path.exists(device_info_path):
        _generate_and_save_device_info(device_info_path)
    
    try:
        with open(device_info_path, 'r') as f:
            device_info = json.load(f)
            return device_info.get("device_id", "")
    except Exception as e:
        logging.error(f"获取设备ID失败: {str(e)}")
        return ""

def get_machine_backup_id() -> str:
    """获取设备备用ID"""
    # 获取应用数据目录
    app_data_dir = get_app_data_dir()
    
    # 设备信息文件路径
    device_info_path = os.path.join(app_data_dir, "device_info.json")
    
    # 如果设备信息文件不存在，先生成
    if not os.path.exists(device_info_path):
        _generate_and_save_device_info(device_info_path)
    
    try:
        with open(device_info_path, 'r') as f:
            device_info = json.load(f)
            return device_info.get("backup_id", "")
    except Exception as e:
        logging.error(f"获取备用设备ID失败: {str(e)}")
        return ""

def _generate_and_save_device_info(device_info_path: Optional[str] = None) -> Dict[str, Any]:
    """生成并保存设备信息"""
    try:
        logging.info("设备信息文件不存在，正在生成...")
        
        if device_info_path is None:
            # 获取应用数据目录
            app_data_dir = get_app_data_dir()
            
            # 设备信息文件路径
            device_info_path = os.path.join(app_data_dir, "device_info.json")
        
        # 断言设备信息文件路径不为None，供类型检查器使用
        assert device_info_path is not None, "设备信息文件路径不能为None"
        
        # 使用设备ID生成器
        generator = DeviceIDGenerator()
        device_info = generator.generate_device_info()
        
        # 保存设备信息
        with open(device_info_path, 'w') as f:
            json.dump(device_info, f, indent=4)
        
        return device_info
    except Exception as e:
        logging.error(f"生成设备信息失败: {str(e)}")
        # 如果生成失败，返回带有随机ID的基本信息
        import uuid
        import hashlib
        
        random_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        random_backup_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        
        basic_info = {
            "device_id": random_id,
            "backup_id": random_backup_id,
            "hardware_hash": hashlib.sha256((random_id + random_backup_id).encode()).hexdigest(),
            "raw_identifiers": {
                "generated": "fallback_random"
            }
        }
        
        # 尝试保存基本信息，确保device_info_path不为None
        if device_info_path is not None:
            try:
                with open(device_info_path, 'w') as f:
                    json.dump(basic_info, f, indent=4)
            except Exception as save_err:
                logging.error(f"保存基本设备信息失败: {str(save_err)}")
        
        return basic_info

class DeviceAuthManager:
    """设备授权管理类，处理设备注册和授权相关操作"""
    
    def __init__(self, api_base_url: Optional[str] = None):
        """
        初始化设备授权管理器
        
        Args:
            api_base_url: API服务器基础URL，如果为None则从配置中读取
        """
        if api_base_url is None:
            config = Config()
            api_url = config.get_api_base_url()
            self.api_base_url = api_url if api_url else "http://localhost:8000"
        else:
            self.api_base_url = api_base_url
        self.logger = logging.getLogger("cursor-pro")
        
        # 使用应用数据目录存储授权信息
        app_data_dir = get_app_data_dir()
        
        # 授权信息保存路径
        self.auth_info_path = os.path.join(app_data_dir, "license_info.json")
    
    def find_device(self, machine_device_id: Optional[str] = None, machine_backup_id: Optional[str] = None, 
                    license_code: Optional[str] = None, include_deleted: bool = False) -> Optional[Dict]:
        """
        查询设备绑定信息
        
        Args:
            machine_device_id: 主设备ID
            machine_backup_id: 备用设备ID
            license_code: 授权码
            include_deleted: 是否包含已删除的记录
            
        Returns:
            设备信息字典或None（如果未找到）
        """
        if not self.api_base_url:
            self.logger.error(get_translation("api_url_not_set"))
            return None
            
        # 构建查询参数
        params = {}
        if machine_device_id:
            params['machine_device_id'] = machine_device_id
        if machine_backup_id:
            params['machine_backup_id'] = machine_backup_id
        if license_code:
            params['license_code'] = license_code
        params['include_deleted'] = str(include_deleted).lower()
        
        try:
            response = requests.get(
                f"{self.api_base_url}/api/v1/devices/find",
                params=params,
                headers={"accept": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                self.logger.info(get_translation("device_not_found"))
                return None
            else:
                self.logger.error(get_translation("device_query_failed", status=response.status_code, response=response.text))
                return None
                
        except Exception as e:
            self.logger.error(get_translation("device_query_error", error=str(e)))
            return None
    
    def register_device(self, machine_device_id: Optional[str] = None, machine_backup_id: Optional[str] = None) -> Optional[Dict]:
        """
        注册设备
        
        Args:
            machine_device_id: 主设备ID，如果为None则自动获取
            machine_backup_id: 备用设备ID，如果为None则自动获取
            
        Returns:
            注册成功返回设备信息字典，失败返回None
        """
        if not self.api_base_url:
            self.logger.error(get_translation("api_url_not_set"))
            return None
            
        # 如果未提供设备ID，则自动获取
        device_id = machine_device_id if machine_device_id is not None else get_machine_device_id()
        backup_id = machine_backup_id if machine_backup_id is not None else get_machine_backup_id()
            
        device_data = {
            "machine_device_id": device_id,
            "machine_backup_id": backup_id
        }
        
        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/devices/",
                json=device_data,
                headers={"Content-Type": "application/json", "accept": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                self.logger.info(get_translation("device_register_success"))
                return response.json()
            else:
                self.logger.error(get_translation("device_register_failed", status=response.status_code, response=response.text))
                return None
                
        except Exception as e:
            self.logger.error(get_translation("device_register_error", error=str(e)))
            return None
    
    def get_license_info(self, license_code: str) -> Optional[Dict]:
        """
        获取授权码信息
        
        Args:
            license_code: 授权码
            
        Returns:
            授权信息字典或None（如果未找到或发生错误）
        """
        if not self.api_base_url:
            self.logger.error(get_translation("api_url_not_set"))
            return None
            
        try:
            response = requests.get(
                f"{self.api_base_url}/api/v1/licenses/{license_code}",
                headers={"accept": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                self.logger.info(get_translation("license_not_found"))
                return None
            else:
                self.logger.error(get_translation("license_query_failed", status=response.status_code, response=response.text))
                return None
                
        except Exception as e:
            self.logger.error(get_translation("license_query_error", error=str(e)))
            return None
    
    def bind_license(self, license_code: str, machine_device_id: Optional[str] = None, machine_backup_id: Optional[str] = None) -> Optional[Dict]:
        """
        将授权码绑定到设备
        
        Args:
            license_code: 授权码
            machine_device_id: 主设备ID，如果为None则自动获取
            machine_backup_id: 备用设备ID，如果为None则自动获取
            
        Returns:
            绑定成功返回绑定信息字典，失败返回None
        """
        if not self.api_base_url:
            self.logger.error(get_translation("api_url_not_set"))
            return None
            
        # 如果未提供设备ID，则自动获取
        device_id = machine_device_id if machine_device_id is not None else get_machine_device_id()
        backup_id = machine_backup_id if machine_backup_id is not None else get_machine_backup_id()
            
        bind_data = {
            "machine_device_id": device_id,
            "machine_backup_id": backup_id,
            "license_code": license_code
        }
        
        try:
            response = requests.post(
                f"{self.api_base_url}/api/v1/licenses/bind",
                json=bind_data,
                headers={"Content-Type": "application/json", "accept": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                self.logger.info(get_translation("license_bind_success"))
                return response.json()
            else:
                self.logger.error(get_translation("license_bind_failed", status=response.status_code, response=response.text))
                return None
                
        except Exception as e:
            self.logger.error(get_translation("license_bind_error", error=str(e)))
            return None
    
    def register_and_verify_device(self) -> Tuple[bool, Optional[Dict]]:
        """
        注册并验证设备
        
        首先尝试查找设备，如果未找到则注册新设备
        
        Returns:
            (成功标志, 设备信息)
        """
        # 获取设备ID
        machine_device_id = get_machine_device_id()
        machine_backup_id = get_machine_backup_id()
        
        # 尝试查找设备
        device_info = self.find_device(
            machine_device_id=machine_device_id,
            machine_backup_id=machine_backup_id
        )
        
        # 如果找到设备，直接返回
        if device_info:
            self.logger.info(get_translation("device_found"))
            return True, device_info
            
        # 未找到设备，注册新设备
        self.logger.info(get_translation("device_not_found_registering"))
        device_info = self.register_device(
            machine_device_id=machine_device_id,
            machine_backup_id=machine_backup_id
        )
        
        if device_info:
            return True, device_info
        else:
            return False, None
    
    def verify_and_bind_license(self, license_code: str) -> Tuple[bool, Optional[Dict], Optional[Dict]]:
        """
        验证授权码并绑定到当前设备
        
        Args:
            license_code: 授权码
            
        Returns:
            (成功标志, 授权信息, 绑定信息)
        """
        # 验证授权码
        license_info = self.get_license_info(license_code)
        if not license_info:
            return False, None, None
            
        # 获取设备ID
        machine_device_id = get_machine_device_id()
        machine_backup_id = get_machine_backup_id()
        
        # 检查设备是否已绑定此授权码
        device_info = self.find_device(
            machine_device_id=machine_device_id,
            machine_backup_id=machine_backup_id,
            license_code=license_code
        )
        
        # 如果已绑定，直接返回
        if device_info:
            self.logger.info(get_translation("device_already_bound"))
            # 保存授权信息到本地
            self._save_license_info_internal(license_code, license_info, device_info)
            return True, license_info, device_info
            
        # 未绑定，执行绑定操作
        binding_info = self.bind_license(
            license_code=license_code,
            machine_device_id=machine_device_id,
            machine_backup_id=machine_backup_id
        )
        
        if binding_info:
            # 保存授权信息到本地
            self._save_license_info_internal(license_code, license_info, binding_info)
            return True, license_info, binding_info
        else:
            return False, license_info, None
    
    def _save_license_info_internal(self, license_code: str, license_info: Dict, binding_info: Dict) -> bool:
        """
        内部方法：保存授权信息到本地文件，不会触发递归调用
        
        Args:
            license_code: 授权码
            license_info: 授权信息
            binding_info: 绑定信息
            
        Returns:
            是否保存成功
        """
        try:
            # 组合授权信息
            auth_info = {
                "license_code": license_code,
                "license_info": license_info,
                "binding_info": binding_info,
                "saved_at": datetime.now().isoformat()
            }
            
            # 保存到文件
            with open(self.auth_info_path, 'w', encoding='utf-8') as f:
                json.dump(auth_info, f, ensure_ascii=False, indent=4)
            
            # self.logger.info(f"授权信息已保存到本地: {self.auth_info_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存授权信息失败: {str(e)}, 路径: {self.auth_info_path}")
            return False
    
    def save_license_info(self, license_code: str, license_info: Dict, binding_info: Dict) -> bool:
        """
        保存授权信息到本地文件
        
        Args:
            license_code: 授权码
            license_info: 授权信息
            binding_info: 绑定信息
            
        Returns:
            是否保存成功
        """
        return self._save_license_info_internal(license_code, license_info, binding_info)
    
    def load_license_info(self) -> Optional[Dict]:
        """
        从本地文件加载授权信息
        
        Returns:
            授权信息字典或None（如果未找到或发生错误）
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(self.auth_info_path):
                self.logger.info(get_translation("license_info_file_not_found"))
                return None
            
            # 从文件加载
            with open(self.auth_info_path, 'r', encoding='utf-8') as f:
                auth_info = json.load(f)
            
            self.logger.info(get_translation("license_info_loaded"))
            return auth_info
        except Exception as e:
            self.logger.error(get_translation("license_info_load_failed", error=str(e)))
            return None
    
    def verify_saved_license(self) -> Tuple[bool, Optional[Dict], Optional[Dict]]:
        """
        验证保存的授权信息
        
        先从本地加载授权信息，然后验证授权码是否有效，设备是否仍然绑定
        
        Returns:
            (成功标志, 授权信息, 绑定信息)
        """
        # 加载授权信息
        auth_info = self.load_license_info()
        if not auth_info or "license_code" not in auth_info:
            self.logger.info(get_translation("no_saved_license"))
            return False, None, None
        
        license_code = auth_info["license_code"]
        
        # 验证授权码
        license_info = self.get_license_info(license_code)
        if not license_info:
            self.logger.warning(get_translation("saved_license_invalid"))
            return False, None, None
        
        # 获取设备ID
        machine_device_id = get_machine_device_id()
        machine_backup_id = get_machine_backup_id()
        
        # 检查设备是否仍然绑定此授权码
        device_info = self.find_device(
            machine_device_id=machine_device_id,
            machine_backup_id=machine_backup_id,
            license_code=license_code
        )
        
        if device_info:
            self.logger.info(get_translation("saved_license_valid"))
            # 更新保存的授权信息，使用内部方法避免递归
            self._save_license_info_internal(license_code, license_info, device_info)
            return True, license_info, device_info
        else:
            self.logger.warning(get_translation("device_binding_lost"))
            return False, license_info, None


# 使用示例
if __name__ == "__main__":
    # 初始化日志
    logging.basicConfig(level=logging.INFO)
    
    # 创建设备授权管理器
    auth_manager = DeviceAuthManager("http://localhost:8000")
    
    # 注册并验证设备
    success, device_info = auth_manager.register_and_verify_device()
    print(f"设备注册结果: {success}")
    if device_info:
        print(f"设备信息: {json.dumps(device_info, indent=2, ensure_ascii=False)}")
    
    # 验证并绑定授权码
    test_license = "test-license-code"
    success, license_info, binding_info = auth_manager.verify_and_bind_license(test_license)
    print(f"授权绑定结果: {success}")
    if license_info:
        print(f"授权信息: {json.dumps(license_info, indent=2, ensure_ascii=False)}")
    if binding_info:
        print(f"绑定信息: {json.dumps(binding_info, indent=2, ensure_ascii=False)}")
    
    # 验证保存的授权信息
    success, license_info, binding_info = auth_manager.verify_saved_license()
    print(f"保存的授权验证结果: {success}")
    if license_info:
        print(f"授权信息: {json.dumps(license_info, indent=2, ensure_ascii=False)}")
    if binding_info:
        print(f"绑定信息: {json.dumps(binding_info, indent=2, ensure_ascii=False)}") 