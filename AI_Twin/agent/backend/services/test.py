# Copyright (c) 2026 PCL-CCNN
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import json
from typing import Dict, Any, Optional

def jwt_generate(url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 300) -> Dict[str, Any]:
    """
    同步发送 POST 请求传递 JSON 数据
    
    Args:
        url: 请求的 URL
        json_data: 要发送的 JSON 数据
        headers: 请求头，默认为 {'Content-Type': 'application/json'}
        timeout: 请求超时时间（秒）
    
    Returns:
        Dict: 响应数据，如果失败返回错误信息
        
    Raises:
        Exception: 请求失败时抛出异常
    """
    # 设置默认请求头
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    try:
        newURL = url + '/jwt/generate'
        response = requests.post(
            url=newURL,
            json=json_data,
            headers=headers,
            timeout=timeout
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        # 尝试解析 JSON 响应
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"text": response.text, "status_code": response.status_code}
            
    except requests.exceptions.RequestException as e:
        error_info = {
            "error": str(e),
            "type": type(e).__name__,
            "url": url
        }
        if hasattr(e, 'response') and e.response is not None:
            error_info["status_code"] = e.response.status_code
            error_info["response_text"] = e.response.text
        raise Exception(f"请求失败: {error_info}")

def jwt_verify(url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 300) -> Dict[str, Any]:
    """
    同步发送 POST 请求传递 JSON 数据
    
    Args:
        url: 请求的 URL
        json_data: 要发送的 JSON 数据
        headers: 请求头，默认为 {'Content-Type': 'application/json'}
        timeout: 请求超时时间（秒）
    
    Returns:
        Dict: 响应数据，如果失败返回错误信息
        
    Raises:
        Exception: 请求失败时抛出异常
    """
    # 设置默认请求头
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    try:
        newURL = url + '/jwt/verify'
        response = requests.post(
            url=newURL,
            json=json_data,
            headers=headers,
            timeout=timeout
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        # 尝试解析 JSON 响应
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"text": response.text, "status_code": response.status_code}
            
    except requests.exceptions.RequestException as e:
        error_info = {
            "error": str(e),
            "type": type(e).__name__,
            "url": url
        }
        if hasattr(e, 'response') and e.response is not None:
            error_info["status_code"] = e.response.status_code
            error_info["response_text"] = e.response.text
        raise Exception(f"请求失败: {error_info}")

def rbac_verify(url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 300) -> Dict[str, Any]:
    # 设置默认请求头
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    try:
        newURL = url + '/auth/app-role'
        response = requests.post(
            url=newURL,
            json=json_data,
            headers=headers,
            timeout=timeout
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        # 尝试解析 JSON 响应
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"text": response.text, "status_code": response.status_code}
            
    except requests.exceptions.RequestException as e:
        error_info = {
            "error": str(e),
            "type": type(e).__name__,
            "url": url
        }
        if hasattr(e, 'response') and e.response is not None:
            error_info["status_code"] = e.response.status_code
            error_info["response_text"] = e.response.text
        raise Exception(f"请求失败: {error_info}")

def cybertwin_auth(url: str, json_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 300) -> Dict[str, Any]:
    # 设置默认请求头
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    try:
        newURL = url + '/auth/5g'
        response = requests.post(
            url=newURL,
            json=json_data,
            headers=headers,
            timeout=timeout
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        # 尝试解析 JSON 响应
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"text": response.text, "status_code": response.status_code}
            
    except requests.exceptions.RequestException as e:
        error_info = {
            "error": str(e),
            "type": type(e).__name__,
            "url": url
        }
        if hasattr(e, 'response') and e.response is not None:
            error_info["status_code"] = e.response.status_code
            error_info["response_text"] = e.response.text
        raise Exception(f"请求失败: {error_info}")

# 使用示例
if __name__ == "__main__":
    try:
        # result = jwt_generate(
        #     url="http://192.168.193.12:31111",
        #     json_data={"payload": {"name": "u123"}}
        # )
        # print("jwt_generate 请求成功:", result)

        # token = result['token']
        # print("token:", token)
        # result = jwt_verify(
        #     url="http://192.168.193.12:31111",
        #     json_data={"token": token}
        # )
        # print("jwt_verify 请求成功:", result)

        # result = rbac_verify(
        #     url="http://192.168.193.9:31124",
        #     json_data={"app_name": "medicalAI", "data_type": "medical", "operation_type": "read"}
        # )
        # print("rbac_verify 请求成功:", result)

        result = cybertwin_auth(
            url="http://192.168.193.9:31124",
            json_data={"mac":"70:C9:4E:E2:FF:1B", "imsi":"466920000000001"}
        )
        print("cybertwin_auth 请求成功:", result)

    except Exception as e:
        print("请求失败:", e)