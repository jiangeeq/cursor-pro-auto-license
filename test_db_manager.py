#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试 db_manager.py Web API 连接和操作的独立脚本
"""

import os
import sys
import json
import random
import string
import logging
from datetime import datetime

# 配置基本日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 导入 DatabaseManager
try:
    from db_manager import DatabaseManager
    from config import Config
except ImportError:
    # 如果在不同目录执行，添加当前目录到 path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)
    from db_manager import DatabaseManager
    from config import Config

class APITester:
    """API 连接和操作测试类"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        # 检查 API 是否可用
        if not self.db_manager.api_base_url:
            logging.error("API 未配置或禁用，请检查 .env 文件中的 API_ENABLED 和 API_BASE_URL 设置")
            sys.exit(1)
        
        logging.info(f"API 基础 URL: {self.db_manager.api_base_url}")
        
    def generate_random_email(self):
        """生成随机邮箱地址用于测试"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"test_{random_str}@example.com"
    
    def test_connection(self):
        """测试 API 连接"""
        logging.info("测试 API 连接...")
        result = self.db_manager._check_connection()
        if result:
            logging.info("✅ API 连接成功")
        else:
            logging.error("❌ API 连接失败")
        return result
    
    def test_create_account(self):
        """测试创建账号"""
        logging.info("测试创建账号...")
        email = self.generate_random_email()
        
        # 准备测试数据
        test_data = {
            "email": email,
            "password": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
            "usage_limit": "5000",
            "access_token": "test_access_token_" + email.split("@")[0],
            "refresh_token": "test_refresh_token_" + email.split("@")[0],
            "user_id": "test_user_id_" + email.split("@")[0]
        }
        
        # 保存账号
        result = self.db_manager.save_account(**test_data)
        if result:
            logging.info(f"✅ 账号创建成功: {email}")
        else:
            logging.error(f"❌ 账号创建失败: {email}")
        
        # 返回创建的账号邮箱，用于后续测试
        return email if result else None
    
    def test_get_accounts(self):
        """测试获取账号列表"""
        logging.info("测试获取账号列表...")
        accounts = self.db_manager.get_all_accounts(skip=0, limit=5)
        
        if accounts:
            logging.info(f"✅ 获取账号列表成功，共 {len(accounts)} 个账号")
            # 显示第一个账号的信息
            if len(accounts) > 0:
                first_account = accounts[0]
                logging.info(f"第一个账号: {json.dumps(first_account, indent=2, ensure_ascii=False)}")
        else:
            logging.warning("⚠️ 获取账号列表成功，但列表为空")
        
        return accounts
    
    def test_update_account(self, email=None):
        """测试更新账号"""
        # 如果没有提供邮箱，则先获取一个账号
        if not email:
            accounts = self.test_get_accounts()
            if not accounts:
                logging.error("❌ 无法测试更新账号，因为没有可用的账号")
                return False
            email = accounts[0].get("email")
        
        logging.info(f"测试更新账号: {email}")
        
        # 获取账号 ID
        account_id = self.db_manager._get_account_id_by_email(email)
        if not account_id:
            logging.error(f"❌ 找不到邮箱为 {email} 的账号ID")
            return False
        
        # 准备更新数据
        update_data = {
            "access_token": f"updated_access_token_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "refresh_token": f"updated_refresh_token_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        
        # 更新账号
        result = self.db_manager.update_account(account_id, **update_data)
        if result:
            logging.info(f"✅ 账号 {email} (ID: {account_id}) 更新成功")
        else:
            logging.error(f"❌ 账号 {email} (ID: {account_id}) 更新失败")
        
        return result
    
    def test_update_by_email(self, email=None):
        """测试通过邮箱更新账号"""
        # 如果没有提供邮箱，则先获取一个账号
        if not email:
            accounts = self.test_get_accounts()
            if not accounts:
                logging.error("❌ 无法测试通过邮箱更新账号，因为没有可用的账号")
                return False
            email = accounts[0].get("email")
        
        logging.info(f"测试通过邮箱更新账号: {email}")
        
        # 准备更新数据
        update_data = {
            "access_token": f"email_updated_token_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "refresh_token": f"email_updated_refresh_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": f"email_updated_user_id_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        
        # 通过邮箱更新账号
        result = self.db_manager.update_account_by_email(
            email, 
            access_token=update_data["access_token"],
            refresh_token=update_data["refresh_token"],
            user_id=update_data["user_id"]
        )
        
        if result:
            logging.info(f"✅ 通过邮箱更新账号 {email} 成功")
        else:
            logging.error(f"❌ 通过邮箱更新账号 {email} 失败")
        
        return result
    
    def run_all_tests(self):
        """运行所有测试"""
        logging.info("开始运行所有测试...")
        
        # 测试连接
        if not self.test_connection():
            logging.error("API 连接失败，终止测试")
            return False
        
        # 测试创建账号
        email = self.test_create_account()
        
        # 测试获取账号列表
        self.test_get_accounts()
        
        # 如果创建账号成功，测试更新该账号
        if email:
            self.test_update_account(email)
            self.test_update_by_email(email)
        else:
            # 尝试更新任意一个现有账号
            self.test_update_account()
            self.test_update_by_email()
        
        logging.info("所有测试完成")
        return True

def main():
    """主函数"""
    print("=" * 50)
    print("Web API 连接和操作测试")
    print("=" * 50)
    
    tester = APITester()
    tester.run_all_tests()
    
    print("\n" + "=" * 50)
    print("测试完成，按回车键退出...")
    input()

if __name__ == "__main__":
    main() 