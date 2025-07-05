import requests
from logger import logging
from language import get_translation
from config import Config


class DatabaseManager:
    """Web API 数据管理器"""

    def __init__(self):
        """初始化数据管理器"""
        self.config = Config()
        self.api_base_url = self.config.get_api_base_url()
        
        # 尝试连接API
        if self.api_base_url:
            self._check_connection()

    def _check_connection(self):
        """检查与Web API的连接"""
        try:
            response = requests.get(f"{self.api_base_url}/health-check")
            if response.status_code == 200:
                logging.info(get_translation("api_connection_success"))
                return True
            else:
                logging.error(get_translation("api_connection_failed", status=response.status_code))
        except Exception as e:
            logging.error(get_translation("api_connection_failed", status=str(e)))
        return False

    def save_account(self, email, password, first_name=None, last_name=None, usage_limit=None, access_token=None, refresh_token=None, user_id=None, login_token=None):
        """
        通过Web API保存账号信息
        
        Args:
            email: 邮箱地址
            password: 密码
            first_name: 名字
            last_name: 姓氏
            usage_limit: 使用额度
            access_token: 访问令牌
            refresh_token: 刷新令牌
            user_id: 用户ID
            login_token: 登录令牌
            
        Returns:
            bool: 是否成功保存
        """
        if not self.api_base_url:
            return False
                
        try:
            # 准备要发送的数据
            account_data = {
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "usage_limit": usage_limit,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": user_id,
                "login_token": login_token
            }
            
            # 发送POST请求创建账号
            response = requests.post(
                f"{self.api_base_url}/api/v1/accounts/", 
                json=account_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                logging.error(get_translation("api_save_account_failed", error=f"Status: {response.status_code}, Response: {response.text}"))
                return False
                
        except Exception as e:
            logging.error(get_translation("api_save_account_failed", error=str(e)))
            return False
            
    def get_all_accounts(self, skip=0, limit=100):
        """
        通过Web API获取所有已注册的账号信息
        
        Args:
            skip: 跳过的记录数
            limit: 返回的最大记录数
            
        Returns:
            list: 账号信息列表，每个账号是一个字典
        """
        if not self.api_base_url:
            return []
                
        try:
            # 发送GET请求获取账号列表，带分页参数
            response = requests.get(
                f"{self.api_base_url}/api/v1/accounts/?skip={skip}&limit={limit}",
                headers={"accept": "application/json"}
            )
            
            if response.status_code == 200:
                accounts = response.json()
                return accounts
            else:
                logging.error(f"获取账号列表失败: Status {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"获取账号列表失败: {str(e)}")
            return []
            
    def update_account(self, account_id, email=None, first_name=None, last_name=None, password=None, 
                       usage_limit=None, access_token=None, refresh_token=None, user_id=None, login_token=None):
        """
        通过Web API更新账号信息
        
        Args:
            account_id: 账号ID
            email: 邮箱地址
            first_name: 名字
            last_name: 姓氏
            password: 密码
            usage_limit: 使用额度
            access_token: 访问令牌
            refresh_token: 刷新令牌
            user_id: 用户ID
            login_token: 登录令牌
            
        Returns:
            bool: 是否成功更新
        """
        if not self.api_base_url:
            return False
                
        try:
            # 准备要更新的数据，只包含非None的字段
            update_data = {}
            if email is not None:
                update_data["email"] = email
            if first_name is not None:
                update_data["first_name"] = first_name
            if last_name is not None:
                update_data["last_name"] = last_name
            if password is not None:
                update_data["password"] = password
            if usage_limit is not None:
                update_data["usage_limit"] = usage_limit
            if access_token is not None:
                update_data["access_token"] = access_token
            if refresh_token is not None:
                update_data["refresh_token"] = refresh_token
            if user_id is not None:
                update_data["user_id"] = user_id
            if login_token is not None:
                update_data["login_token"] = login_token
            
            # 发送PUT请求更新账号
            response = requests.put(
                f"{self.api_base_url}/api/v1/accounts/{account_id}", 
                json=update_data,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code in [200, 204]:
                logging.info(f"账号 ID {account_id} 信息更新成功")
                return True
            else:
                logging.error(f"更新账号信息失败: Status {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"更新账号信息失败: {str(e)}")
            return False
            
    def update_account_by_email(self, email, access_token=None, refresh_token=None, user_id=None, login_token=None):
        """
        通过邮箱更新账号的认证信息，使用专用的邮箱更新API端点
        
        Args:
            email: 邮箱地址
            access_token: 访问令牌
            refresh_token: 刷新令牌
            user_id: 用户ID
            login_token: 登录令牌
            
        Returns:
            bool: 是否成功更新
        """
        if not self.api_base_url:
            return False
                
        try:
            # 准备要更新的数据，只包含非None的字段
            update_data = {}
            if access_token is not None:
                update_data["access_token"] = access_token
            if refresh_token is not None:
                update_data["refresh_token"] = refresh_token
            if user_id is not None:
                update_data["user_id"] = user_id
            if login_token is not None:
                update_data["login_token"] = login_token
            
            # 直接使用邮箱更新API端点
            response = requests.put(
                f"{self.api_base_url}/api/v1/accounts/email/{email}", 
                json=update_data,
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code in [200, 204]:
                logging.info(get_translation("api_update_account_success", email=email))
                return True
            else:
                logging.error(get_translation("api_update_account_failed", email=email, error=f"Status: {response.status_code}, Response: {response.text}"))
                return False
                
        except Exception as e:
            logging.error(get_translation("api_update_account_failed", email=email, error=str(e)))
            return False
    
    def _get_account_id_by_email(self, email):
        """
        通过邮箱获取账号ID
        
        Args:
            email: 邮箱地址
            
        Returns:
            int or None: 账号ID，未找到则返回None
        """
        try:
            # 查询账号列表
            accounts = self.get_all_accounts()
            
            # 查找匹配的邮箱
            for account in accounts:
                if account.get("email") == email:
                    return account.get("id")
                    
            return None
        except Exception as e:
            logging.error(f"获取账号ID失败: {str(e)}")
            return None
            
    def close(self):
        """关闭任何打开的资源（为了与原接口兼容）"""
        pass 