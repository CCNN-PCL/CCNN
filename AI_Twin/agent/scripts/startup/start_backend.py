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
后端服务启动脚本
================

启动FastAPI后端服务

作者: AI开发团队
版本: 1.0
"""

import uvicorn
import sys
import os
import logging

# 禁用 Python 输出缓冲，确保日志实时输出
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
os.chdir(project_root)

#A2A协议
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from shared.agents.coordinator.user_agent import CybertwinConfig, UserAgent, UserAgentExecutor
from shared.config.model_config import get_config
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import (
    InMemoryTaskStore,
)

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 启动后端服务...")
    print("=" * 80)
    
    # 配置日志输出到控制台，禁用缓冲
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True  # 重新配置日志
    )
    
    # 设置所有日志处理器都不缓冲
    for handler in logging.root.handlers:
        handler.flush()
    
    # 设置各个模块的日志级别
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.INFO)
    
    # 设置共享模块和智能体的日志级别
    logging.getLogger('shared').setLevel(logging.INFO)
    logging.getLogger('shared.agents').setLevel(logging.INFO)
    logging.getLogger('shared.llm_caller').setLevel(logging.INFO)
    
    # 设置智能体的详细日志级别
    agent_loggers = [
        'BaseAgent', 'CybertwinAgent', 'QuestioningAgent', 'InternalMedicineAgent', 
        'SurgicalAgent', 'SummaryAgent', 'TriageAgent', 'HistoryAgent',
        'ComprehensiveAgent', 'ImageAnalysisCoordinator', 'IntentRecognition'
    ]
    for agent_name in agent_loggers:
        logging.getLogger(agent_name).setLevel(logging.INFO)
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=5050,
        reload=True,
        log_level="info",
        access_log=True,  # 启用访问日志
        use_colors=True   # 启用颜色输出
    )

    # print("=" * 80)
    # print("🚀 启动A2A服务...")
    # print("=" * 80)

    # # 说明智能体的技能
    # skill = AgentSkill(
    #     id="9090",
    #     name="user agent",
    #     description="个人助手",
    #     tags=["助手", "助理", "Cybertwin"],
    #     examples=["请求Cybertwin个人数据"],
    # )

    # # 构建AgentCard，也即智能体的名片
    # user_agent_card = AgentCard(
    #     name="个人助手智能体",
    #     description="Cybertwin的助手智能体",
    #     url="http://localhost:9090/",
    #     capabilities=AgentCapabilities(),
    #     skills=[skill],
    #     defaultInputModes=["text"],
    #     defaultOutputModes=["text"],
    #     version="1.0.0",
    # )    

    # model_config = get_config("qwen")
    # cybertwin_config = CybertwinConfig(
    #     model_config=model_config.to_dict(),
    #     enable_auth=False,  # 在服务层处理认证
    #     enable_audit=False,  # 在服务层处理审计
    #     max_context_length=4000,
    #     intent_threshold=0.7
    # )

    # # 算法代码要被client调用，得用A2A的DefaultRequestHandler封装一下，让它可以应对来自client的请求，并自动执行CodingAgentExecutor中的对应函数
    # request_handler = DefaultRequestHandler(
    #     agent_executor=UserAgentExecutor(
    #         agent=UserAgent(cybertwin_config)
    #     ),
    #     task_store=InMemoryTaskStore(),
    # )

    # # 使用A2A SDK封装一个应用服务
    # server = A2AStarletteApplication(
    #     agent_card=user_agent_card,
    #     http_handler=request_handler,
    # )

    # # 起服务
    # uvicorn.run(server.build(), host="0.0.0.0", port=9090)