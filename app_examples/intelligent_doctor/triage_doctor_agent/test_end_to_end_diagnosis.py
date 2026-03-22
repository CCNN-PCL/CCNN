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
端到端测试脚本 - 验证分布式推理诊断流程
========================================

测试目标：
1. 验证与云上专科内科服务的连接（北京和上海）
2. 验证完整的分布式推理诊断流程
3. 验证诊断日志是否正确生成到 diagnosis.log.md

使用方法：
    python test_end_to_end_diagnosis.py

作者: QSIR
版本: 1.0
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量（指向云上的服务）
os.environ["INTERNAL_MEDICINE_BEIJING_URL"] = "http://192.168.193.78:30226"
os.environ["INTERNAL_MEDICINE_SHANGHAI_URL"] = "http://192.168.193.78:31416"
os.environ["INTERNAL_MEDICINE_BEIJING_API_KEY"] = "test_api_key"
os.environ["INTERNAL_MEDICINE_SHANGHAI_API_KEY"] = "test_api_key"
os.environ["ENABLE_DIAGNOSIS_LOG"] = "true"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 导入必要的模块
from shared.utils.diagnosis_logger import DiagnosisLogger
from shared.clients.specialist_service_client import SpecialistServiceClient
from shared.agents.coordinator.two_round_diagnosis_coordinator import TwoRoundDiagnosisCoordinator
from shared.agents.utils.shared_context import SharedContext


async def test_service_connection():
    """测试与云上服务的连接"""
    logger.info("=" * 80)
    logger.info("测试1: 验证与云上专科内科服务的连接")
    logger.info("=" * 80)
    
    services = {
        "北京内科": {
            "base_url": os.getenv("INTERNAL_MEDICINE_BEIJING_URL", "http://192.168.193.78:30226"),
            "api_key": os.getenv("INTERNAL_MEDICINE_BEIJING_API_KEY", "test_api_key")
        },
        "上海内科": {
            "base_url": os.getenv("INTERNAL_MEDICINE_SHANGHAI_URL", "http://192.168.193.78:31416"),
            "api_key": os.getenv("INTERNAL_MEDICINE_SHANGHAI_API_KEY", "test_api_key")
        }
    }
    
    results = {}
    for name, config in services.items():
        try:
            logger.info(f"\n测试连接: {name}")
            logger.info(f"  服务地址: {config['base_url']}")
            
            client = SpecialistServiceClient(
                base_url=config["base_url"],
                api_key=config["api_key"],
                timeout=10.0
            )
            
            # 健康检查
            try:
                health = await client.health_check()
                logger.info(f"  ✅ {name} 健康检查成功: {health}")
                results[name] = {"status": "success", "health": health}
            except Exception as e:
                logger.warning(f"  ⚠️ {name} 健康检查失败: {e}")
                # 健康检查失败不代表服务不可用，继续测试诊断接口
                results[name] = {"status": "health_check_failed", "error": str(e)}
            
            # 测试诊断接口
            try:
                test_result = await client.diagnose(
                    user_input="我最近总是感觉口渴，喝水很多，尿量也比以前多，体重好像也有点下降。",
                    user_id="test_user_001",
                    intent="内科咨询",
                    data_addresses=[],
                    user_info={"userid": "test_user_001", "username": "测试用户"},
                    shared_context={},
                    metadata={"location": "beijing" if "北京" in name else "shanghai", "specialization": "internal_medicine", "round": 1}
                )
                logger.info(f"  ✅ {name} 诊断接口调用成功")
                logger.info(f"  诊断结果摘要: {str(test_result)[:200]}...")
                results[name]["diagnosis"] = "success"
                results[name]["diagnosis_result"] = test_result
            except Exception as e:
                logger.error(f"  ❌ {name} 诊断接口调用失败: {e}")
                results[name]["diagnosis"] = "failed"
                results[name]["diagnosis_error"] = str(e)
                
        except Exception as e:
            logger.error(f"  ❌ {name} 连接测试失败: {e}")
            results[name] = {"status": "failed", "error": str(e)}
    
    logger.info("\n" + "=" * 80)
    logger.info("连接测试结果汇总:")
    logger.info("=" * 80)
    for name, result in results.items():
        status = result.get("status", "unknown")
        diagnosis = result.get("diagnosis", "not_tested")
        logger.info(f"{name}:")
        logger.info(f"  - 连接状态: {status}")
        logger.info(f"  - 诊断接口: {diagnosis}")
    
    return results


async def test_diagnosis_logger():
    """测试诊断日志记录器"""
    logger.info("\n" + "=" * 80)
    logger.info("测试2: 验证诊断日志记录器")
    logger.info("=" * 80)
    
    # 初始化日志记录器
    logger_instance = DiagnosisLogger()
    log_file_path = logger_instance.log_file_path
    
    logger.info(f"日志文件路径: {log_file_path}")
    logger.info(f"日志功能已启用: {logger_instance.enabled}")
    
    # 清空日志
    await logger_instance.clear_log()
    logger.info("已清空日志文件")
    
    # 测试日志记录
    await logger_instance.start_diagnosis_session(
        user_id="test_user_001",
        user_input="我最近总是感觉口渴，喝水很多，尿量也比以前多，体重好像也有点下降。",
        user_info={"userid": "test_user_001", "username": "测试用户"}
    )
    logger.info("✅ 已记录诊断会话开始")
    
    await logger_instance.log_intent_recognition("内科咨询")
    logger.info("✅ 已记录意图识别")
    
    await logger_instance.log_routing(
        location_groups={
            "beijing": [{"hospital": "北京医院", "department": "内科", "data_type": "病历数据", "location": "beijing", "address": "http://example.com/data"}],
            "shanghai": [{"hospital": "上海医院", "department": "内科", "data_type": "病历数据", "location": "shanghai", "address": "http://example.com/data"}]
        },
        specialty_type="internal_medicine",
        service_configs={
            "internal_medicine": {
                "beijing": {"base_url": os.getenv("INTERNAL_MEDICINE_BEIJING_URL")},
                "shanghai": {"base_url": os.getenv("INTERNAL_MEDICINE_SHANGHAI_URL")}
            }
        }
    )
    logger.info("✅ 已记录路由信息")
    
    # 检查日志文件是否存在且有内容
    if log_file_path.exists():
        content = log_file_path.read_text(encoding='utf-8')
        logger.info(f"✅ 日志文件已生成，大小: {len(content)} 字节")
        logger.info(f"日志文件前500字符预览:\n{content[:500]}")
        return True
    else:
        logger.error("❌ 日志文件未生成")
        return False


async def test_full_diagnosis_flow():
    """测试完整的诊断流程"""
    logger.info("\n" + "=" * 80)
    logger.info("测试3: 验证完整的分布式推理诊断流程")
    logger.info("=" * 80)
    
    # 初始化诊断日志记录器
    diagnosis_logger = DiagnosisLogger()
    await diagnosis_logger.clear_log()
    
    # 初始化两轮诊断协调器
    specialists = {
        "internal_medicine": {
            "beijing": {
                "base_url": os.getenv("INTERNAL_MEDICINE_BEIJING_URL", "http://192.168.193.78:30226"),
                "api_key": os.getenv("INTERNAL_MEDICINE_BEIJING_API_KEY", "test_api_key")
            },
            "shanghai": {
                "base_url": os.getenv("INTERNAL_MEDICINE_SHANGHAI_URL", "http://192.168.193.78:31416"),
                "api_key": os.getenv("INTERNAL_MEDICINE_SHANGHAI_API_KEY", "test_api_key")
            }
        }
    }
    
    coordinator = TwoRoundDiagnosisCoordinator(specialists=specialists)
    
    # 准备测试数据
    user_input = "我最近总是感觉口渴，喝水很多，尿量也比以前多，体重好像也有点下降。"
    user_id = "test_user_001"
    user_info = {
        "userid": user_id,
        "username": "测试用户",
        "id_token": "test_token"
    }
    
    # 模拟数据地址
    data_addresses = [
        {
            "hospital": "北京医院",
            "department": "内科",
            "data_type": "病历数据",
            "location": "beijing",
            "address": "http://example.com/data/beijing",
            "access_token": "test_token_beijing"
        },
        {
            "hospital": "上海医院",
            "department": "内科",
            "data_type": "病历数据",
            "location": "shanghai",
            "address": "http://example.com/data/shanghai",
            "access_token": "test_token_shanghai"
        }
    ]
    
    # 初始化共享上下文
    shared_context = SharedContext(
        user_id=user_id,
        intent="内科咨询",
        user_input=user_input,
        user_info=user_info,
        round_number=0
    )
    
    # 开始诊断会话
    await diagnosis_logger.start_diagnosis_session(
        user_id=user_id,
        user_input=user_input,
        user_info=user_info
    )
    await diagnosis_logger.log_intent_recognition("内科咨询")
    
    try:
        # 第一轮诊断
        logger.info("\n开始第一轮诊断...")
        first_round_result = await coordinator.first_round_diagnosis(
            user_input=user_input,
            user_id=user_id,
            data_addresses=data_addresses,
            shared_context=shared_context,
            intent="内科咨询",
            user_info=user_info,
            diagnosis_logger=diagnosis_logger
        )
        
        logger.info(f"第一轮诊断完成:")
        logger.info(f"  - 诊断结果数量: {len(first_round_result.get('diagnosis_results', []))}")
        logger.info(f"  - 需要更多数据: {first_round_result.get('needs_more_data', False)}")
        
        # 检查日志文件
        log_file_path = diagnosis_logger.log_file_path
        if log_file_path.exists():
            content = log_file_path.read_text(encoding='utf-8')
            logger.info(f"\n✅ 诊断日志已生成，大小: {len(content)} 字节")
            
            # 检查关键内容
            checks = [
                ("用户输入", "用户输入" in content),
                ("意图识别", "意图识别" in content),
                ("智能路由", "智能路由" in content or "路由" in content),
                ("专科医生诊断", "专科医生" in content or "诊断" in content),
            ]
            
            logger.info("\n日志内容检查:")
            all_passed = True
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                logger.info(f"  {status} {check_name}: {passed}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                logger.info("\n✅ 所有日志检查通过！")
            else:
                logger.warning("\n⚠️ 部分日志检查未通过")
            
            return True, first_round_result
        else:
            logger.error("❌ 日志文件未生成")
            return False, first_round_result
            
    except Exception as e:
        logger.error(f"❌ 诊断流程测试失败: {e}", exc_info=True)
        await diagnosis_logger.log_error(str(e), e)
        return False, None


async def main():
    """主测试函数"""
    logger.info("=" * 80)
    logger.info("开始端到端测试 - 分布式推理诊断流程")
    logger.info("=" * 80)
    logger.info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"\n配置的服务地址:")
    logger.info(f"  - 北京内科: {os.getenv('INTERNAL_MEDICINE_BEIJING_URL')}")
    logger.info(f"  - 上海内科: {os.getenv('INTERNAL_MEDICINE_SHANGHAI_URL')}")
    logger.info("=" * 80)
    
    results = {}
    
    # 测试1: 服务连接
    try:
        connection_results = await test_service_connection()
        results["connection"] = connection_results
    except Exception as e:
        logger.error(f"连接测试失败: {e}", exc_info=True)
        results["connection"] = {"error": str(e)}
    
    # 测试2: 日志记录器
    try:
        logger_result = await test_diagnosis_logger()
        results["logger"] = logger_result
    except Exception as e:
        logger.error(f"日志记录器测试失败: {e}", exc_info=True)
        results["logger"] = {"error": str(e)}
    
    # 测试3: 完整诊断流程
    try:
        flow_success, flow_result = await test_full_diagnosis_flow()
        results["full_flow"] = {
            "success": flow_success,
            "result": flow_result
        }
    except Exception as e:
        logger.error(f"完整诊断流程测试失败: {e}", exc_info=True)
        results["full_flow"] = {"error": str(e)}
    
    # 输出测试总结
    logger.info("\n" + "=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)
    
    for test_name, result in results.items():
        if isinstance(result, dict) and "error" in result:
            logger.info(f"{test_name}: ❌ 失败 - {result['error']}")
        elif isinstance(result, bool):
            logger.info(f"{test_name}: {'✅ 通过' if result else '❌ 失败'}")
        elif isinstance(result, dict) and "success" in result:
            logger.info(f"{test_name}: {'✅ 通过' if result['success'] else '❌ 失败'}")
        else:
            logger.info(f"{test_name}: ✅ 完成")
    
    logger.info("=" * 80)
    logger.info("测试完成")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

