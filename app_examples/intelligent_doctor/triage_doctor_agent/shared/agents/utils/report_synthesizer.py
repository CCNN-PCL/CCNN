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
综合诊断报告生成器（重构版）
============================

负责综合多个专科医生的诊断结果，生成综合诊断报告。

主要功能：
1. 诊断结果汇总
2. 多轮演进信息提取
3. 冲突检测和解决
4. 综合报告生成

作者: QSIR
版本: 2.0 - 重构版（支持多轮演进）
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from shared.agents.utils.shared_context import SharedContext


@dataclass
class DiagnosisSummary:
    """诊断结果汇总"""
    diagnoses: List[Dict[str, Any]]
    locations: List[str]
    data_sources: List[str]
    confidence_scores: List[float]
    avg_confidence: float
    specialist_count: int


@dataclass
class ConflictInfo:
    """冲突信息"""
    conflict_type: str  # "diagnosis", "treatment", "confidence"
    severity: str  # "low", "medium", "high"
    description: str
    affected_specialists: List[str]
    resolution: Optional[str] = None


@dataclass
class EvolutionInfo:
    """诊断演进信息"""
    total_rounds: int
    rounds: List[Dict[str, Any]]
    confidence_trend: str  # "improving", "stable", "declining"
    data_evolution: Dict[str, Any]


class ReportSynthesizer:
    """
    综合诊断报告生成器（重构版）
    
    支持多轮演进和冲突检测
    """
    
    def __init__(self, llm_caller=None, model_config=None):
        """
        初始化报告综合生成器
        
        参数：
            llm_caller: LLM调用器
            model_config: 模型配置
        """
        self.llm_caller = llm_caller
        self.model_config = model_config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def generate_comprehensive_report(
        self,
        user_input: str,
        specialist_results: List[Dict[str, Any]],
        user_info: Optional[Dict] = None,
        shared_context: Optional[SharedContext] = None,
        include_evolution: bool = True
    ) -> Dict[str, Any]:
        """
        生成综合诊断报告（支持多轮演进）
        
        参数：
            user_input (str): 用户输入
            specialist_results (List[Dict[str, Any]]): 专科医生诊断结果列表
            user_info (Dict, optional): 用户信息
            shared_context (SharedContext, optional): 共享上下文
            include_evolution (bool): 是否包含诊断演进信息
            
        返回：
            Dict[str, Any]: 综合报告，包含：
                - report: 报告内容
                - evolution: 演进信息
                - conflicts: 冲突信息
                - summary: 诊断摘要
        """
        try:
            # 1. 汇总诊断结果
            diagnosis_summary = self._summarize_diagnoses(specialist_results)
            
            # 2. 提取演进信息（如果有共享上下文）
            evolution_info = None
            if shared_context and include_evolution:
                evolution_info = self._extract_evolution_info(shared_context)
            
            # 3. 识别冲突
            conflicts = self._identify_conflicts(specialist_results)
            
            # 4. 构建综合报告提示
            prompt = self._build_comprehensive_prompt(
                user_input,
                diagnosis_summary,
                conflicts,
                user_info,
                evolution_info,
                specialist_results
            )
            
            # 5. 调用LLM生成综合报告
            comprehensive_report = None
            if self.llm_caller:
                print(f"[报告综合器] 开始调用LLM生成综合报告...")
                comprehensive_report = await self.llm_caller(prompt, self.model_config)
                print(f"[报告综合器] LLM综合报告调用完成，结果长度: {len(str(comprehensive_report))} 字符")
            else:
                # 如果没有LLM调用器，生成简化版报告
                comprehensive_report = self._generate_simple_report(
                    diagnosis_summary, conflicts, evolution_info
                )
            
            # 6. 格式化报告
            formatted_report = self._format_report(
                comprehensive_report,
                specialist_results,
                evolution_info,
                conflicts
            )
            
            return {
                "report": formatted_report,
                "evolution": evolution_info,
                "conflicts": [c.__dict__ for c in conflicts],
                "summary": {
                    "avg_confidence": diagnosis_summary.avg_confidence,
                    "specialist_count": diagnosis_summary.specialist_count,
                    "locations": diagnosis_summary.locations,
                    "data_sources": diagnosis_summary.data_sources
                }
            }
        
        except Exception as e:
            self.logger.error(f"[ReportSynthesizer] 生成综合报告失败: {str(e)}")
            return {
                "report": f"生成综合诊断报告时发生错误: {str(e)}",
                "evolution": None,
                "conflicts": [],
                "summary": {}
            }
    
    def _summarize_diagnoses(self, specialist_results: List[Dict[str, Any]]) -> DiagnosisSummary:
        """
        汇总诊断结果
        
        参数：
            specialist_results (List[Dict[str, Any]]): 专科医生诊断结果列表
            
        返回：
            DiagnosisSummary: 诊断结果汇总
        """
        diagnoses = []
        locations = set()
        data_sources = []
        confidence_scores = []
        
        for result in specialist_results:
            diagnoses.append(result.get("diagnosis", {}))
            locations.add(result.get("location", "unknown"))
            data_sources.extend(result.get("data_sources", []))
            confidence_scores.append(result.get("confidence", 0.0))
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return DiagnosisSummary(
            diagnoses=diagnoses,
            locations=list(locations),
            data_sources=list(set(data_sources)),  # 去重
            confidence_scores=confidence_scores,
            avg_confidence=avg_confidence,
            specialist_count=len(specialist_results)
        )
    
    def _extract_evolution_info(self, shared_context: SharedContext) -> EvolutionInfo:
        """
        提取诊断演进信息
        
        参数：
            shared_context (SharedContext): 共享上下文
            
        返回：
            EvolutionInfo: 演进信息
        """
        evolution_rounds = []
        
        # 为每一轮提取关键信息
        for i, history_item in enumerate(shared_context.data_addresses_history, 1):
            round_info = {
                "round_number": i,
                "data_addresses_count": len(history_item.get("data_addresses", [])),
                "data_types": [
                    addr.get("data_type")
                    for addr in history_item.get("data_addresses", [])
                    if addr.get("data_type")
                ]
            }
            
            # 获取对应轮次的诊断结果
            round_results = [
                r for r in shared_context.diagnosis_results_history
                if r.get("round") == i
            ]
            
            if round_results:
                round_info["diagnosis_confidence"] = sum(
                    r.get("confidence", 0.0) for r in round_results
                ) / len(round_results)
                round_info["specialist_count"] = len(round_results)
            
            evolution_rounds.append(round_info)
        
        # 分析置信度趋势
        confidence_trend = self._analyze_confidence_trend(evolution_rounds)
        
        # 分析数据演进
        data_evolution = self._analyze_data_evolution(shared_context.data_addresses_history)
        
        return EvolutionInfo(
            total_rounds=shared_context.round_number,
            rounds=evolution_rounds,
            confidence_trend=confidence_trend,
            data_evolution=data_evolution
        )
    
    def _analyze_confidence_trend(self, rounds: List[Dict[str, Any]]) -> str:
        """
        分析置信度趋势
        
        参数：
            rounds (List[Dict[str, Any]]): 各轮次信息
            
        返回：
            str: 趋势（"improving", "stable", "declining"）
        """
        confidences = [
            r.get("diagnosis_confidence", 0.0)
            for r in rounds
            if "diagnosis_confidence" in r
        ]
        
        if len(confidences) < 2:
            return "stable"
        
        if confidences[-1] > confidences[0] + 0.1:
            return "improving"
        elif confidences[-1] < confidences[0] - 0.1:
            return "declining"
        else:
            return "stable"
    
    def _analyze_data_evolution(self, data_addresses_history: List[Dict]) -> Dict[str, Any]:
        """
        分析数据演进
        
        参数：
            data_addresses_history (List[Dict]): 数据地址历史
            
        返回：
            Dict[str, Any]: 数据演进信息
        """
        all_data_types = set()
        location_counts = {}
        
        for history_item in data_addresses_history:
            for addr in history_item.get("data_addresses", []):
                data_type = addr.get("data_type")
                location = addr.get("location")
                
                if data_type:
                    all_data_types.add(data_type)
                
                if location:
                    location_counts[location] = location_counts.get(location, 0) + 1
        
        return {
            "total_data_types": list(all_data_types),
            "location_distribution": location_counts,
            "total_rounds": len(data_addresses_history)
        }
    
    def _build_data_info_section(self, specialist_results: List[Dict[str, Any]]) -> str:
        """
        构建数据信息章节，为LLM提供足够的数据信息
        
        参数：
            specialist_results (List[Dict[str, Any]]): 专科医生诊断结果列表
            
        返回：
            str: 数据信息章节内容
        """
        if not specialist_results:
            return ""
        
        # 按轮次分组
        round1_results = []
        round2_results = []
        
        for result in specialist_results:
            if not isinstance(result, dict):
                continue
            
            # 从 metadata 或结果中获取轮次信息
            metadata = result.get("metadata", {})
            round_num = metadata.get("round") or result.get("round", 1)
            
            if round_num == 1:
                round1_results.append(result)
            elif round_num == 2:
                round2_results.append(result)
            else:
                round1_results.append(result)
        
        section = "## 诊断使用的数据详情\n\n"
        
        # 第一轮数据信息
        if round1_results:
            section += "### 第一轮诊断使用的数据\n\n"
            section += "第一轮诊断主要使用病历数据、检查报告等历史医疗数据：\n\n"
            
            for i, result in enumerate(round1_results, 1):
                location = result.get("location", "未知")
                specialization = result.get("specialization", "未知")
                
                section += f"**专科医生{i}（{location} - {specialization}）：**\n"
                
                # 数据来源
                data_sources = result.get("data_sources", [])
                if data_sources:
                    section += f"- 数据来源（医院/机构）：{', '.join(data_sources)}\n"
                
                # 数据类型
                data_types = []
                data_addresses = result.get("data_addresses", [])
                if data_addresses:
                    for addr in data_addresses:
                        dt = addr.get("data_type")
                        if dt and dt not in data_types:
                            data_types.append(dt)
                
                available_data_types = result.get("available_data_types", [])
                if available_data_types:
                    for dt in available_data_types:
                        if dt and dt not in data_types:
                            data_types.append(dt)
                
                if data_types:
                    section += f"- 数据类型：{', '.join(data_types)}\n"
                else:
                    section += "- 数据类型：病历数据、检查报告\n"
                
                # 数据摘要
                data_summary = result.get("data_summary") or result.get("mcp_interaction", {}).get("data_summary")
                if data_summary and isinstance(data_summary, dict):
                    section += "- 数据内容摘要：\n"
                    for key, value in data_summary.items():
                        section += f"  * {key}：{value}\n"
                
                # 数据使用说明（如果有）
                data_usage_summary = result.get("data_usage_summary")
                if data_usage_summary:
                    section += f"- 数据使用说明：{data_usage_summary}\n"
                
                section += "\n"
        
        # 第二轮数据信息
        if round2_results:
            section += "### 第二轮诊断使用的数据\n\n"
            section += "第二轮诊断主要使用健康监测数据等实时数据：\n\n"
            
            for i, result in enumerate(round2_results, 1):
                location = result.get("location", "未知")
                specialization = result.get("specialization", "未知")
                
                section += f"**专科医生{i}（{location} - {specialization}）：**\n"
                
                # 数据来源
                data_sources = result.get("data_sources", [])
                if data_sources:
                    section += f"- 数据来源（医院/机构）：{', '.join(data_sources)}\n"
                
                # 数据类型
                data_types = []
                data_addresses = result.get("data_addresses", [])
                if data_addresses:
                    for addr in data_addresses:
                        dt = addr.get("data_type")
                        if dt and dt not in data_types:
                            data_types.append(dt)
                
                available_data_types = result.get("available_data_types", [])
                if available_data_types:
                    for dt in available_data_types:
                        if dt and dt not in data_types:
                            data_types.append(dt)
                
                if data_types:
                    section += f"- 数据类型：{', '.join(data_types)}\n"
                else:
                    section += "- 数据类型：健康监测数据（实时血压、心率、血糖等）\n"
                
                # 数据摘要
                data_summary = result.get("data_summary") or result.get("mcp_interaction", {}).get("data_summary")
                if data_summary and isinstance(data_summary, dict):
                    section += "- 数据内容摘要：\n"
                    for key, value in data_summary.items():
                        section += f"  * {key}：{value}\n"
                else:
                    section += "- 数据内容摘要：\n"
                    section += "  * 健康监测数据：已获取（包含实时血压、心率、血糖等监测数据）\n"
                
                # 数据使用说明（如果有）
                data_usage_summary = result.get("data_usage_summary")
                if data_usage_summary:
                    section += f"- 数据使用说明：{data_usage_summary}\n"
                
                section += "\n"
        
        section += "\n"
        return section
    
    def _identify_conflicts(self, specialist_results: List[Dict[str, Any]]) -> List[ConflictInfo]:
        """
        识别诊断结果冲突
        
        参数：
            specialist_results (List[Dict[str, Any]]): 专科医生诊断结果列表
            
        返回：
            List[ConflictInfo]: 冲突信息列表
        """
        conflicts = []
        
        # 检查置信度差异
        confidences = [r.get("confidence", 0.0) for r in specialist_results]
        if confidences:
            max_conf = max(confidences)
            min_conf = min(confidences)
            if max_conf - min_conf > 0.3:  # 置信度差异过大
                conflicts.append(ConflictInfo(
                    conflict_type="confidence",
                    severity="medium",
                    description=f"专科医生诊断置信度差异较大（{min_conf:.2f} - {max_conf:.2f}）",
                    affected_specialists=[r.get("agent", "") for r in specialist_results],
                    resolution="建议综合多个专科医生的意见，考虑置信度差异"
                ))
        
        # TODO: 可以使用LLM或规则引擎进行更深入的冲突检测
        # 例如：检查诊断结论是否一致、治疗方案是否冲突等
        
        return conflicts
    
    def _build_comprehensive_prompt(
        self,
        user_input: str,
        diagnosis_summary: DiagnosisSummary,
        conflicts: List[ConflictInfo],
        user_info: Optional[Dict],
        evolution_info: Optional[EvolutionInfo],
        specialist_results: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        构建综合诊断报告提示
        
        参数：
            user_input (str): 用户输入
            diagnosis_summary (DiagnosisSummary): 诊断摘要
            conflicts (List[ConflictInfo]): 冲突信息
            user_info (Dict, optional): 用户信息
            evolution_info (EvolutionInfo, optional): 演进信息
            
        返回：
            str: 综合报告提示
        """
        prompt = f"""作为一位经验丰富的全科医生，请根据以下专科医生的诊断结果，生成一份综合诊断报告。

患者症状描述：{user_input}

"""
        
        # 添加用户信息
        if user_info:
            user_name = user_info.get("full_name", "患者")
            prompt += f"患者信息：{user_name}\n\n"
        
        # 添加诊断演进信息
        if evolution_info:
            prompt += f"""## 诊断演进过程

本次诊断共进行了{evolution_info.total_rounds}轮：

"""
            for round_info in evolution_info.rounds:
                round_num = round_info.get("round_number", 0)
                confidence = round_info.get("diagnosis_confidence", 0.0)
                data_types = round_info.get("data_types", [])
                prompt += f"### 第{round_num}轮诊断\n"
                prompt += f"- 置信度: {confidence:.2f}\n"
                if data_types:
                    prompt += f"- 数据类型: {', '.join(data_types)}\n"
                prompt += "\n"
            
            prompt += f"置信度趋势: {evolution_info.confidence_trend}\n\n"
        
        # 添加专科医生诊断结果
        prompt += f"""## 专科医生诊断结果

共{diagnosis_summary.specialist_count}位专科医生参与诊断，平均置信度: {diagnosis_summary.avg_confidence:.2f}

"""
        for i, diagnosis in enumerate(diagnosis_summary.diagnoses):
            if isinstance(diagnosis, dict):
                diagnosis_text = diagnosis.get("diagnosis", "无诊断结果")
            else:
                diagnosis_text = str(diagnosis)
            prompt += f"专科医生{i+1}：{diagnosis_text}\n"
        
        prompt += f"\n数据来源：{', '.join(diagnosis_summary.data_sources)}\n\n"
        
        # 添加详细的数据使用信息（为LLM提供足够信息以生成准确的说明）
        if specialist_results:
            data_info_section = self._build_data_info_section(specialist_results)
            if data_info_section:
                prompt += data_info_section
        
        # 添加冲突信息
        if conflicts:
            prompt += "## 诊断冲突说明\n\n"
            for conflict in conflicts:
                prompt += f"- {conflict.description}\n"
                if conflict.resolution:
                    prompt += f"  解决方案：{conflict.resolution}\n"
            prompt += "\n"
        
        prompt += """请生成一份温柔亲切、专业负责的综合诊断报告，包括：

1. **症状分析总结**
   - 综合各专科医生的症状分析
   - 评估症状的严重程度

2. **综合诊断结论**
   - 基于所有专科医生的诊断意见
   - 说明使用了哪些数据包含医院名称、健康监测数据等来支撑诊断，以及这些数据（包含数据内容等信息）是如何帮助得出诊断结论
   - 说明诊断的置信度
   - 如果有冲突，说明如何处理

3. **治疗建议**
   - 综合治疗建议
   - 考虑不同地域专科医生的意见

4. **注意事项**
   - 日常注意事项
   - 何时需要就医
   - 紧急情况处理

报告要求：
- 语言温暖亲切，让患者感到被理解和关怀
- 专业准确，避免引起不必要的担心
- 条理清晰，便于患者理解
- 如果有诊断演进过程，说明诊断的改进过程
- **签名要求**：报告结尾请使用"您的智慧医生 小白"，不要使用"此致 敬礼 [您的医生姓名] [您的医院名称] [日期]"这样的格式
"""
        
        return prompt
    
    def _format_report(
        self,
        report: str,
        specialist_results: List[Dict[str, Any]],
        evolution_info: Optional[EvolutionInfo],
        conflicts: List[ConflictInfo]
    ) -> str:
        """
        格式化报告
        
        参数：
            report (str): LLM生成的报告
            specialist_results (List[Dict[str, Any]]): 专科医生诊断结果
            evolution_info (EvolutionInfo, optional): 演进信息
            conflicts (List[ConflictInfo]): 冲突信息
            
        返回：
            str: 格式化后的报告
        """
        # 基础格式化（可以添加更多的格式化逻辑）
        formatted = report.strip()
        
        # 如果有演进信息，添加演进总结
        if evolution_info:
            formatted += f"\n\n---\n\n## 诊断过程总结\n\n"
            formatted += f"本次诊断共进行了{evolution_info.total_rounds}轮，置信度趋势：{evolution_info.confidence_trend}\n"
        
        # 如果有冲突，添加冲突说明
        if conflicts:
            formatted += f"\n\n## 诊断冲突说明\n\n"
            for conflict in conflicts:
                formatted += f"- {conflict.description}\n"
                if conflict.resolution:
                    formatted += f"  {conflict.resolution}\n"
        
        return formatted
    
    def _generate_simple_report(
        self,
        diagnosis_summary: DiagnosisSummary,
        conflicts: List[ConflictInfo],
        evolution_info: Optional[EvolutionInfo]
    ) -> str:
        """
        生成简化版报告（当没有LLM调用器时）
        
        参数：
            diagnosis_summary (DiagnosisSummary): 诊断摘要
            conflicts (List[ConflictInfo]): 冲突信息
            evolution_info (EvolutionInfo, optional): 演进信息
            
        返回：
            str: 简化版报告
        """
        report = f"""# 综合诊断报告

## 诊断摘要

共{diagnosis_summary.specialist_count}位专科医生参与诊断，平均置信度: {diagnosis_summary.avg_confidence:.2f}

## 专科医生诊断意见

"""
        for i, diagnosis in enumerate(diagnosis_summary.diagnoses):
            if isinstance(diagnosis, dict):
                diagnosis_text = diagnosis.get("diagnosis", "无诊断结果")
            else:
                diagnosis_text = str(diagnosis)
            report += f"{i+1}. {diagnosis_text}\n"
        
        report += f"\n## 数据来源\n\n{', '.join(diagnosis_summary.data_sources)}\n"
        
        if evolution_info:
            report += f"\n## 诊断演进\n\n共{evolution_info.total_rounds}轮诊断，置信度趋势：{evolution_info.confidence_trend}\n"
        
        if conflicts:
            report += "\n## 诊断冲突\n\n"
            for conflict in conflicts:
                report += f"- {conflict.description}\n"
        
        return report

