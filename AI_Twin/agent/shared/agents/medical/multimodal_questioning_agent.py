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
多模态医生追问智能体 (MultimodalQuestioningAgent)
==============================================

专门利用多模态医疗大模型进行智能追问和症状分析。

主要功能：
1. 多模态症状分析
2. 智能追问生成
3. 医疗图像理解
4. 综合症状评估

作者: AI开发团队
版本: 1.0
"""

import logging
from typing import Dict, Any, Optional, List, Union
import sys
import os
import base64
from io import BytesIO
from PIL import Image
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.base_agent import BaseAgent


class MultimodalQuestioningAgent(BaseAgent):
    """
    多模态医生追问智能体
    
    专门利用多模态医疗大模型进行：
    - 多模态症状分析
    - 智能追问生成
    - 医疗图像理解
    - 综合症状评估
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        初始化多模态医生追问智能体
        
        参数：
            model_config (Dict[str, Any]): 模型配置
        """
        super().__init__(model_config)
        self.agent_id = "multimodal_questioning"
        self.name = "多模态医生追问智能体"
        self.specialization = "多模态症状分析"
        
        # 多模态症状分析模板
        self.multimodal_templates = {
            "症状描述": {
                "text_prompt": "请详细描述您的症状，包括：",
                "image_prompt": "请上传相关的医疗图像或照片，帮助我更好地理解您的症状。",
                "combined_prompt": "基于您的症状描述和图像，我将进行综合分析。"
            },
            "疼痛分析": {
                "text_prompt": "请描述疼痛的具体情况：",
                "image_prompt": "如果可能，请拍摄疼痛部位的照片，注意光线充足。",
                "questions": [
                    "疼痛的具体位置在哪里？",
                    "疼痛是什么性质的？（刺痛、胀痛、隐痛等）",
                    "疼痛的强度如何？（1-10分）",
                    "疼痛是持续的还是间歇性的？",
                    "什么情况下疼痛会加重或缓解？"
                ]
            },
            "皮肤症状": {
                "text_prompt": "请详细描述皮肤症状：",
                "image_prompt": "请拍摄清晰的皮肤照片，注意光线和角度。",
                "questions": [
                    "皮疹的颜色、形状、大小如何？",
                    "是否有瘙痒、疼痛等感觉？",
                    "皮疹出现多长时间了？",
                    "是否有扩散或变化？",
                    "之前是否接触过特殊物质？"
                ]
            },
            "眼部症状": {
                "text_prompt": "请描述眼部症状：",
                "image_prompt": "请拍摄眼部照片，注意不要直视光源。",
                "questions": [
                    "眼睛是否有疼痛、干涩、流泪？",
                    "视力是否有变化？",
                    "是否有分泌物？",
                    "症状持续多长时间了？",
                    "是否有其他伴随症状？"
                ]
            }
        }
        
        self.logger.info(f"[{self.name}] 初始化完成")
    
    async def execute(self, user_input: str, user_id: str, user_info: Optional[Dict] = None, 
                     images: Optional[List[Any]] = None) -> Any:
        """
        执行多模态症状分析
        
        参数：
            user_input (str): 用户输入的症状描述
            user_id (str): 用户ID
            user_info (Dict, optional): 用户信息
            images (List[Any], optional): 图像数据列表
            
        返回：
            Any: 多模态分析结果
        """
        try:
            # 验证输入
            if not self.validate_input(user_input):
                return "⚠️ 输入无效，请提供有效的症状描述。"
            
            # 获取对话历史
            context = self.get_context_from_memory(user_id)
            
            # 分析症状类型
            symptom_type = await self._analyze_symptom_type(user_input, images)
            
            # 进行多模态症状分析
            analysis_result = await self._multimodal_symptom_analysis(
                user_input, images, context, user_info, symptom_type
            )
            
            # 生成智能追问
            questions = await self._generate_intelligent_questions(
                user_input, images, analysis_result, symptom_type
            )
            
            # 构建分析结果
            result = {
                "symptom_type": symptom_type,
                "multimodal_analysis": analysis_result,
                "questions": questions,
                "specialization": self.specialization,
                "has_images": images is not None and len(images) > 0,
                "follow_up_needed": len(questions) > 0
            }
            
            # 记录对话轮次
            self.add_turn_to_memory(user_id, user_input, self.name, str(result))
            
            self.logger.info(f"[{self.name}] 多模态分析完成")
            return result
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 执行错误：{str(e)}")
            return f"⚠️ 多模态分析错误：{str(e)}"
    
    async def _analyze_symptom_type(self, user_input: str, images: Optional[List[Any]]) -> str:
        """
        分析症状类型
        
        参数：
            user_input (str): 用户输入
            images (List[Any], optional): 图像数据
            
        返回：
            str: 症状类型
        """
        try:
            # 构建多模态分析提示
            if images and len(images) > 0:
                prompt = f"""作为专业的多模态医疗AI，请分析以下症状：

用户描述：{user_input}

请结合文本描述和图像信息，识别主要症状类型：
- 疼痛分析
- 皮肤症状  
- 眼部症状
- 消化系统
- 呼吸系统
- 神经系统
- 其他

请返回最匹配的症状类型。"""
                
                # 使用多模态模型分析
                analysis = await self._call_multimodal_model(prompt, images[0])
            else:
                prompt = f"""作为专业医疗AI，请分析以下症状类型：

用户描述：{user_input}

请识别主要症状类型：
- 疼痛分析
- 皮肤症状
- 眼部症状  
- 消化系统
- 呼吸系统
- 神经系统
- 其他

请返回最匹配的症状类型。"""
                
                analysis = await self.caller(prompt, self.model_config)
            
            # 提取症状类型
            for symptom_type in self.multimodal_templates.keys():
                if symptom_type in analysis:
                    return symptom_type
            
            return "症状描述"
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 症状类型分析失败: {str(e)}")
            return "症状描述"
    
    async def _multimodal_symptom_analysis(self, user_input: str, images: Optional[List[Any]], 
                                         context: str, user_info: Optional[Dict], 
                                         symptom_type: str) -> Dict[str, Any]:
        """
        进行多模态症状分析
        
        参数：
            user_input (str): 用户输入
            images (List[Any], optional): 图像数据
            context (str): 对话上下文
            user_info (Dict, optional): 用户信息
            symptom_type (str): 症状类型
            
        返回：
            Dict[str, Any]: 分析结果
        """
        try:
            # 构建多模态分析提示
            template = self.multimodal_templates.get(symptom_type, self.multimodal_templates["症状描述"])
            
            if images and len(images) > 0:
                # 多模态分析
                prompt = f"""作为专业的多模态医疗AI，请进行综合症状分析：

患者描述：{user_input}

对话历史：
{context}

用户信息：
{self._format_user_info(user_info)}

请进行以下分析：
1. 症状特征提取：从文本和图像中提取关键症状特征
2. 严重程度评估：评估症状的严重程度和紧急程度
3. 可能病因分析：基于多模态信息分析可能的病因
4. 图像分析：分析图像中的医学特征
5. 综合评估：提供综合的症状评估

请用专业但易懂的语言回答。"""
                
                analysis = await self._call_multimodal_model(prompt, images[0])
            else:
                # 纯文本分析
                prompt = f"""作为专业医疗AI，请进行症状分析：

患者描述：{user_input}

对话历史：
{context}

用户信息：
{self._format_user_info(user_info)}

请进行以下分析：
1. 症状特征提取：从描述中提取关键症状特征
2. 严重程度评估：评估症状的严重程度和紧急程度
3. 可能病因分析：分析可能的病因
4. 完整性评估：评估症状描述的完整性
5. 综合评估：提供综合的症状评估

请用专业但易懂的语言回答。"""
                
                analysis = await self.caller(prompt, self.model_config)
            
            return {
                "analysis": analysis,
                "symptom_type": symptom_type,
                "has_images": images is not None and len(images) > 0,
                "confidence": self._calculate_confidence(analysis, images)
            }
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 多模态分析失败: {str(e)}")
            return {
                "analysis": "分析失败，请重新描述症状",
                "symptom_type": symptom_type,
                "has_images": False,
                "confidence": 0.0
            }
    
    async def _generate_intelligent_questions(self, user_input: str, images: Optional[List[Any]], 
                                            analysis_result: Dict[str, Any], 
                                            symptom_type: str) -> List[str]:
        """
        生成智能追问问题
        
        参数：
            user_input (str): 用户输入
            images (List[Any], optional): 图像数据
            analysis_result (Dict[str, Any]): 分析结果
            symptom_type (str): 症状类型
            
        返回：
            List[str]: 追问问题列表
        """
        try:
            # 获取基础问题模板
            template = self.multimodal_templates.get(symptom_type, self.multimodal_templates["症状描述"])
            base_questions = template.get("questions", [])
            
            if not base_questions:
                return []
            
            # 构建智能追问提示
            if images and len(images) > 0:
                prompt = f"""作为专业的多模态医疗AI，基于以下信息生成2-3个针对性追问问题：

患者症状：{user_input}
症状类型：{symptom_type}
分析结果：{analysis_result.get('analysis', '')}

基础问题模板：
{base_questions}

请生成具体、有针对性的追问问题，帮助收集缺失的关键信息。
每个问题要简洁明了，便于患者回答。

请直接返回问题列表，每行一个问题："""
                
                questions_text = await self._call_multimodal_model(prompt, images[0])
            else:
                prompt = f"""作为专业医疗AI，基于以下信息生成2-3个针对性追问问题：

患者症状：{user_input}
症状类型：{symptom_type}
分析结果：{analysis_result.get('analysis', '')}

基础问题模板：
{base_questions}

请生成具体、有针对性的追问问题，帮助收集缺失的关键信息。
每个问题要简洁明了，便于患者回答。

请直接返回问题列表，每行一个问题："""
                
                questions_text = await self.caller(prompt, self.model_config)
            
            # 解析问题
            questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
            return questions[:3]  # 限制问题数量
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 生成智能追问失败: {str(e)}")
            return base_questions[:2] if base_questions else []
    
    async def _call_multimodal_model(self, text: str, image: Any) -> str:
        """
        调用多模态模型
        
        参数：
            text (str): 文本提示
            image (Any): 图像数据
            
        返回：
            str: 模型响应
        """
        try:
            # 构建多模态输入
            multimodal_input = {
                "text": text,
                "image": image
            }
            
            # 调用多模态模型
            response = await self.caller(multimodal_input, self.model_config)
            return response
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 多模态模型调用失败: {str(e)}")
            return "多模态分析失败，请重新尝试。"
    
    def _format_user_info(self, user_info: Optional[Dict]) -> str:
        """
        格式化用户信息
        
        参数：
            user_info (Dict, optional): 用户信息
            
        返回：
            str: 格式化后的用户信息
        """
        if not user_info:
            return "用户信息：未知"
        
        info_parts = []
        if user_info.get('age'):
            info_parts.append(f"年龄：{user_info['age']}")
        if user_info.get('gender'):
            info_parts.append(f"性别：{user_info['gender']}")
        if user_info.get('medical_history'):
            info_parts.append(f"既往病史：{user_info['medical_history']}")
        
        return "用户信息：" + "，".join(info_parts) if info_parts else "用户信息：未知"
    
    def _calculate_confidence(self, analysis: str, images: Optional[List[Any]]) -> float:
        """
        计算分析置信度
        
        参数：
            analysis (str): 分析结果
            images (List[Any], optional): 图像数据
            
        返回：
            float: 置信度分数 (0-1)
        """
        try:
            base_confidence = 0.5
            
            # 基于分析长度调整置信度
            if len(analysis) > 200:
                base_confidence += 0.2
            elif len(analysis) > 100:
                base_confidence += 0.1
            
            # 基于图像存在调整置信度
            if images and len(images) > 0:
                base_confidence += 0.2
            
            # 基于关键词调整置信度
            medical_keywords = ["症状", "诊断", "治疗", "检查", "建议"]
            keyword_count = sum(1 for keyword in medical_keywords if keyword in analysis)
            base_confidence += min(keyword_count * 0.05, 0.2)
            
            return min(base_confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"[{self.name}] 置信度计算失败: {str(e)}")
            return 0.5
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specialization": self.specialization,
            "description": "利用多模态医疗大模型进行智能追问和症状分析",
            "capabilities": [
                "多模态症状分析",
                "智能追问生成",
                "医疗图像理解",
                "综合症状评估"
            ],
            "supported_modalities": ["text", "image"],
            "model_type": "multimodal_medical"
        }
