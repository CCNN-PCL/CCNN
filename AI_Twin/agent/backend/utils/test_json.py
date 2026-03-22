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

import json
from typing import List, Dict, Any
from datetime import datetime

def process_health_data(raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    处理健康数据，提取最近一天的数据并转换为指定格式
    
    Args:
        raw_data: 原始健康数据列表
        
    Returns:
        Dict: 处理后的健康数据格式
    """
    if not raw_data:
        return create_empty_response()
    
    # 找到最近一天的数据（按日期排序）
    sorted_data = sorted(raw_data, key=lambda x: x['date'], reverse=True)
    latest_data = sorted_data[0]
    
    # 构建响应数据
    result = {
        "health_monitoring": {
            "blood_pressure": {
                "systolic": latest_data['heart_rate']['max_bpm'],  # 使用最高心率作为收缩压
                "diastolic": latest_data['heart_rate']['min_bpm'], # 使用最低心率作为舒张压
                "unit": "mmHg",
                "timestamp": latest_data['date']
            },
            "blood_glucose": {
                "value": latest_data['blood_glucose']['evening_mmol'],  # 使用晚间血糖值
                "unit": "mmol/L",
                "timestamp": latest_data['date']
            },
            "heart_rate": {
                "value": latest_data['heart_rate']['avg_bpm'],  # 使用平均心率
                "unit": "bpm",
                "timestamp": latest_data['date']
            },
            "body_temperature": {
                "value": latest_data['skin_temp_celsius'],  # 使用皮肤温度作为体温
                "unit": "°C",
                "timestamp": latest_data['date']
            }
        },
        "available_data_types": ["健康监测数据"]
    }
    
    return result

def create_empty_response() -> Dict[str, Any]:
    """创建空数据响应"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    return {
        "health_monitoring": {
            "blood_pressure": {
                "systolic": 0,
                "diastolic": 0,
                "unit": "mmHg",
                "timestamp": current_date
            },
            "blood_glucose": {
                "value": 0.0,
                "unit": "mmol/L",
                "timestamp": current_date
            },
            "heart_rate": {
                "value": 0,
                "unit": "bpm",
                "timestamp": current_date
            },
            "body_temperature": {
                "value": 0.0,
                "unit": "°C",
                "timestamp": current_date
            }
        },
        "available_data_types": ["健康监测数据"]
    }

def process_health_data_from_json(json_str: str) -> Dict[str, Any]:
    """
    从 JSON 字符串处理健康数据
    
    Args:
        json_str: JSON 格式的字符串数据
        
    Returns:
        Dict: 处理后的健康数据格式
    """
    try:
        # 解析 JSON 字符串
        raw_data = json.loads(json_str)
        return process_health_data(raw_data)
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        return create_empty_response()
    except Exception as e:
        print(f"数据处理错误: {e}")
        return create_empty_response()

# 使用示例
if __name__ == "__main__":
    # 您的原始数据（注意：需要是有效的 JSON 数组格式）
    raw_json_data = '''
    [
        {
            "user_id": "111",
            "date": "2025-11-18",
            "heart_rate": {
                "avg_bpm": 72,
                "max_bpm": 135,
                "min_bpm": 55,
                "resting_bpm": 58
            },
            "blood_glucose": {
                "morning_mmol": 5.2,
                "evening_mmol": 5.8
            },
            "sleep": {
                "total_minutes": 468,
                "deep_minutes": 95,
                "light_minutes": 285,
                "rem_minutes": 88,
                "bedtime": "23:15",
                "wake_time": "07:03"
            },
            "steps": 10234,
            "distance_km": 7.8,
            "calories_kcal": 312,
            "stress_level": 28,
            "spo2_percent": 98,
            "skin_temp_celsius": 33.4
        },
        {
            "user_id": "111",
            "date": "2025-11-17",
            "heart_rate": {
                "avg_bpm": 74,
                "max_bpm": 142,
                "min_bpm": 56,
                "resting_bpm": 59
            },
            "blood_glucose": {
                "morning_mmol": 5.0,
                "evening_mmol": 6.1
            },
            "sleep": {
                "total_minutes": 445,
                "deep_minutes": 88,
                "light_minutes": 270,
                "rem_minutes": 87,
                "bedtime": "23:45",
                "wake_time": "07:10"
            },
            "steps": 8932,
            "distance_km": 6.5,
            "calories_kcal": 287,
            "stress_level": 35,
            "spo2_percent": 97,
            "skin_temp_celsius": 33.6
        }
    ]
    '''
    
    # 处理数据
    result = process_health_data_from_json(raw_json_data)
    
    # 打印结果
    print("处理后的健康数据:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 验证数据
    print(f"\n验证:")
    print(f"血压: {result['health_monitoring']['blood_pressure']['systolic']}/{result['health_monitoring']['blood_pressure']['diastolic']} {result['health_monitoring']['blood_pressure']['unit']}")
    print(f"血糖: {result['health_monitoring']['blood_glucose']['value']} {result['health_monitoring']['blood_glucose']['unit']}")
    print(f"心率: {result['health_monitoring']['heart_rate']['value']} {result['health_monitoring']['heart_rate']['unit']}")
    print(f"体温: {result['health_monitoring']['body_temperature']['value']} {result['health_monitoring']['body_temperature']['unit']}")