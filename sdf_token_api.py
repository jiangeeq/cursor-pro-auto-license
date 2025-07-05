#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import logging
import sys
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def get_token(session_token=None):
    """测试通过API获取token信息
    
    参数:
        session_token: WorkosCursorSessionToken值，如果为None则提示用户输入
    
    返回:
        Dict | None: 成功返回包含token信息的字典，失败返回None
    """
    if not session_token:
        print("请输入WorkosCursorSessionToken值:")
        session_token = input("> ").strip()
    
    if not session_token:
        logging.error("没有提供token")
        return None
        
    try:
        # 调用API获取token信息
        api_url = f"https://token.cursorpro.com.cn/reftoken?token={session_token}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        
        logging.info("请求API获取token信息")
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == 0 and data.get("msg") == "获取成功":
                token_data = data.get("data", {})
                logging.info(f"成功获取token信息，有效期至: {token_data.get('expire_time')}")
                
                # 返回完整的token数据
                return {
                    "user_id": token_data.get("user_id"),
                    "accessToken": token_data.get("accessToken"),
                    "refreshToken": token_data.get("refreshToken"),
                    "expire_time": token_data.get("expire_time"),
                    "days_left": token_data.get("days_left")
                }
            else:
                logging.error(f"API返回错误: {data.get('msg')}")
        else:
            logging.error(f"API请求失败，状态码: {response.status_code}")
    
    except Exception as e:
        logging.error(f"获取token失败: {str(e)}")
    
    return None

def format_token_info(token_data):
    """格式化显示token信息"""
    if not token_data:
        return "没有获取到token信息"
    
    # 截断token，只显示前10个字符
    access_token = token_data.get("accessToken", "")
    refresh_token = token_data.get("refreshToken", "")
    
    access_token_display = f"{access_token[:10]}..." if access_token else "无"
    refresh_token_display = f"{refresh_token[:10]}..." if refresh_token else "无"
    
    # 格式化输出
    output = [
        "-" * 50,
        "Token信息",
        "-" * 50,
        f"用户ID: {token_data.get('user_id', '无')}",
        f"访问令牌: {access_token_display}",
        f"刷新令牌: {refresh_token_display}",
        f"过期时间: {token_data.get('expire_time', '无')}",
        f"剩余天数: {token_data.get('days_left', '无')}",
        "-" * 50,
    ]
    
    return "\n".join(output)

def save_token_to_file(token_data, filename="token_data.json"):
    """将token数据保存到文件"""
    if not token_data:
        logging.error("没有token数据可保存")
        return False
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, ensure_ascii=False, indent=2)
        logging.info(f"Token数据已保存到文件: {filename}")
        return True
    except Exception as e:
        logging.error(f"保存token数据失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("Token API 测试工具")
    print("================")
    
    # 测试API调用
    token_data = get_token( 'user_01JZA3AXERQ9Q1T3JGFE5RPC7X%3A%3AeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdXRoMHx1c2VyXzAxSlpBM0FYRVJROVExVDNKR0ZFNVJQQzdYIiwidGltZSI6IjE3NTE2MjQ4MzUiLCJyYW5kb21uZXNzIjoiZmFhZDRlZDQtZTA3NS00OWVlIiwiZXhwIjoxNzU2ODA4ODM1LCJpc3MiOiJodHRwczovL2F1dGhlbnRpY2F0aW9uLmN1cnNvci5zaCIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwgb2ZmbGluZV9hY2Nlc3MiLCJhdWQiOiJodHRwczovL2N1cnNvci5jb20iLCJ0eXBlIjoid2ViIn0.iddNOuhVNnh7EayfkfocYcxvqm3MH0tRROBbxEPSZ3A')
    
    if token_data:
        # 格式化显示token信息
        print(format_token_info(token_data))
        
        # 询问是否保存到文件
        save = input("\n是否保存token数据到文件? (y/n): ").strip().lower()
        if save == 'y':
            save_token_to_file(token_data)
    else:
        print("获取token失败，请检查输入的session token是否正确")
    
    # 防止窗口立即关闭
    input("\n按回车键退出...") 