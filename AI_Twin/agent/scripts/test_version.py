#!/usr/bin/env python3
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

# -*- coding: utf-8 -*-
"""
版本信息测试脚本

测试版本信息模块和API端点的功能。
"""

import sys
import os
import json
import requests
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_version_module():
    """测试版本信息模块"""
    print("=" * 60)
    print("测试版本信息模块")
    print("=" * 60)
    
    try:
        from backend.version import get_version_info, get_version_string
        
        version_info = get_version_info()
        
        print(f"版本号: {version_info.get_version()}")
        print(f"构建标识: {version_info.get_build()}")
        print(f"构建日期: {version_info.get_build_date()}")
        print(f"Git信息: {json.dumps(version_info.get_git_info(), indent=2, ensure_ascii=False)}")
        print(f"版权信息: {json.dumps(version_info.get_copyright_info(), indent=2, ensure_ascii=False)}")
        print(f"项目元数据: {json.dumps(version_info.get_metadata(), indent=2, ensure_ascii=False)}")
        
        print("\n版本字符串:")
        print(f"  简单格式: {get_version_string('simple')}")
        print(f"  紧凑格式: {get_version_string('compact')}")
        
        # 测试保存到文件
        version_file = Path("VERSION.test.json")
        if version_info.save_to_file(version_file):
            print(f"\n版本信息已保存到: {version_file}")
            with open(version_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                print(f"保存的文件内容验证: {saved_data.get('version')}")
            version_file.unlink()  # 删除测试文件
            print("测试文件已清理")
        
        print("\n✅ 版本信息模块测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 版本信息模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_version_api():
    """测试版本信息API端点"""
    print("\n" + "=" * 60)
    print("测试版本信息API端点")
    print("=" * 60)
    
    try:
        # 启动测试服务器（如果未运行）
        import time
        from multiprocessing import Process
        
        def start_server():
            import uvicorn
            from backend.main import app
            uvicorn.run(app, host="127.0.0.1", port=5051, log_level="error")
        
        # 在子进程中启动服务器
        server_process = Process(target=start_server)
        server_process.start()
        
        # 等待服务器启动
        print("启动测试服务器...")
        time.sleep(3)
        
        base_url = "http://127.0.0.1:5051"
        
        # 测试根路径
        print("\n1. 测试根路径 (/):")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   状态码: {response.status_code}")
            print(f"   消息: {data.get('message')}")
            print(f"   版本: {data.get('version')}")
        else:
            print(f"   请求失败: {response.status_code}")
        
        # 测试简单版本信息
        print("\n2. 测试简单版本信息 (/api/v1/version/simple):")
        response = requests.get(f"{base_url}/api/v1/version/simple", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   状态码: {response.status_code}")
            print(f"   版本: {data.get('version')}")
            print(f"   完整版本: {data.get('full_version')}")
        else:
            print(f"   请求失败: {response.status_code}")
        
        # 测试详细版本信息
        print("\n3. 测试详细版本信息 (/api/v1/version):")
        response = requests.get(f"{base_url}/api/v1/version", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   状态码: {response.status_code}")
            print(f"   版本: {data.get('version')}")
            print(f"   构建: {data.get('build')}")
            print(f"   Git提交: {data.get('git', {}).get('commit', 'N/A')}")
        else:
            print(f"   请求失败: {response.status_code}")
        
        # 测试状态API
        print("\n4. 测试状态API (/api/v1/status):")
        response = requests.get(f"{base_url}/api/v1/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   状态码: {response.status_code}")
            print(f"   API版本: {data.get('api_version')}")
            print(f"   服务状态: {json.dumps(data.get('services'), indent=4, ensure_ascii=False)}")
        else:
            print(f"   请求失败: {response.status_code}")
        
        # 停止服务器
        server_process.terminate()
        server_process.join()
        
        print("\n✅ 版本信息API测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 版本信息API测试失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 确保服务器进程被终止
        try:
            server_process.terminate()
            server_process.join()
        except:
            pass
        
        return False

def test_makefile_commands():
    """测试Makefile版本命令"""
    print("\n" + "=" * 60)
    print("测试Makefile版本命令")
    print("=" * 60)
    
    commands = [
        ("显示版本信息", "make version"),
        ("显示详细版本信息", "make version-show"),
        ("初始化版本信息", "make version-init"),
    ]
    
    all_passed = True
    
    for description, command in commands:
        print(f"\n测试: {description}")
        print(f"命令: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ 命令执行成功")
                # 显示部分输出
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines[:5]:  # 只显示前5行
                    print(f"   {line}")
                if len(output_lines) > 5:
                    print(f"   ... (共{len(output_lines)}行)")
            else:
                print(f"❌ 命令执行失败: {result.returncode}")
                print(f"   错误输出: {result.stderr[:200]}")
                all_passed = False
                
        except subprocess.TimeoutExpired:
            print("❌ 命令执行超时")
            all_passed = False
        except Exception as e:
            print(f"❌ 命令执行异常: {e}")
            all_passed = False
    
    return all_passed

def test_build_script():
    """测试构建脚本"""
    print("\n" + "=" * 60)
    print("测试构建脚本")
    print("=" * 60)
    
    try:
        # 测试构建脚本帮助信息
        print("\n1. 测试构建脚本帮助信息:")
        result = subprocess.run(
            ["./scripts/build.sh", "help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ 构建脚本帮助信息测试通过")
            # 显示部分帮助信息
            help_lines = result.stdout.strip().split('\n')
            for line in help_lines[:10]:
                print(f"   {line}")
        else:
            print(f"❌ 构建脚本帮助信息测试失败: {result.stderr}")
            return False
        
        # 测试版本信息显示
        print("\n2. 测试构建脚本版本信息:")
        result = subprocess.run(
            ["./scripts/build.sh", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ 构建脚本版本信息测试通过")
            version_lines = result.stdout.strip().split('\n')
            for line in version_lines:
                print(f"   {line}")
        else:
            print(f"❌ 构建脚本版本信息测试失败: {result.stderr}")
            return False
        
        print("\n✅ 构建脚本测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 构建脚本测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始版本信息注入测试")
    print("=" * 60)
    
    tests = [
        ("版本信息模块", test_version_module),
        ("Makefile命令", test_makefile_commands),
        ("构建脚本", test_build_script),
        ("版本信息API", test_version_api),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n▶ 运行测试: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed_count = 0
    total_count = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:20} {status}")
        if success:
            passed_count += 1
    
    print(f"\n通过率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！版本信息注入成功。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查问题。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
