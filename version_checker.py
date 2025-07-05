#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import logging
from packaging import version

class VersionChecker:
    """版本检查器，用于检查应用程序是否有更新"""
    
    def __init__(self, api_base_url, current_version):
        """
        初始化版本检查器
        
        Args:
            api_base_url (str): API基础URL
            current_version (str): 当前应用版本
        """
        self.api_base_url = api_base_url
        self.current_version = current_version
        self.latest_version_info = None
    
    def check_for_updates(self):
        """
        检查是否有新版本
        
        Returns:
            tuple: (是否需要更新, 最新版本信息)
        """
        try:
            # 获取最新版本信息
            response = requests.get(f"{self.api_base_url}/api/v1/versions/latest", 
                                   headers={'accept': 'application/json'})
            
            if response.status_code == 200 and response.json() is not None:
                self.latest_version_info = response.json()
                
                # 比较版本号
                current = version.parse(self.current_version)
                latest = version.parse(self.latest_version_info["version"])
                
                # 如果最新版本大于当前版本，则需要更新
                needs_update = latest > current
                logging.info(f"{current}, {latest} 比较结果: {latest > current}, {latest == current}, {latest < current}")
                
                # 是否需要强制更新
                force_update = self.latest_version_info.get("is_force_update", False) and self.latest_version_info.get("version") != self.current_version
                
                return needs_update or force_update, self.latest_version_info
            else:
                logging.error(f"获取版本信息失败，状态码: {response.status_code}")
                return False, None
                
        except Exception as e:
            logging.error(f"检查更新时出错: {str(e)}")
            return False, None
    
    def get_latest_version_info(self):
        """
        获取最新版本信息
        
        Returns:
            dict: 最新版本信息
        """
        return self.latest_version_info 