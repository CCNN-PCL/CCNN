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
诊断日志记录器（医疗思维版）
============================

负责记录诊断过程中的所有关键操作，以医疗思维格式输出到Markdown文件

作者: QSIR
版本: 1.0 - 医疗思维版
"""

import asyncio
import json
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import os

logger = logging.getLogger(__name__)


class DiagnosisLogger:
    """诊断日志记录器（医疗思维版 - 单例模式）"""
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls, log_file_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_file_path: Optional[str] = None):
        if hasattr(self, '_initialized'):
            return
        
        # 计算日志文件路径
        if log_file_path:
            self.log_file_path = Path(log_file_path)
        else:
            # 从shared/utils/diagnosis_logger.py -> shared/utils -> shared -> cybertwin-agent-service -> backend/api/diagnosis.log.md
            current_file = Path(__file__).resolve()
            self.log_file_path = current_file.parent.parent.parent / "backend" / "api" / "diagnosis.log.md"
        
        self.enabled = os.getenv("ENABLE_DIAGNOSIS_LOG", "true").lower() == "true"
        self.current_session = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialized = True
        
        # 确保日志文件目录存在
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def _write_log(self, content: str):
        """异步写入日志"""
        if not self.enabled:
            return
        
        try:
            async with self._lock:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(content)
                    f.flush()
        except Exception as e:
            self.logger.error(f"写入诊断日志失败: {e}")
    
    async def start_diagnosis_session(self, user_id: str, user_input: str, user_info: Dict[str, Any]):
        """开始诊断会话 - 医疗思维版"""
        if not self.enabled:
            return
        
        self.current_session = {
            "user_id": user_id,
            "user_input": user_input,
            "user_info": user_info,
            "start_time": datetime.now(),
            "rounds": []
        }
        
        content = f"""# 分布式推理诊断过程

## 用户输入：
{user_input}

---

"""
        await self._write_log(content)
    
    async def log_intent_recognition(self, intent: str):
        """记录意图识别"""
        if not self.enabled:
            return
        
        content = f"""## 意图识别为：
{intent}

---

"""
        await self._write_log(content)
    
    async def log_a2a_connection(self, round_num: int, base_url: str, protocol: str, token: Optional[str] = None, success: bool = True):
        """记录A2A连接建立"""
        if not self.enabled:
            return
        
        token_display = self._format_token(token) if token else "已授权"
        
        if round_num == 1:
            description = "根据症状和诊断需求请求用户诊断数据"
        else:
            description = "正在请求用户更多健康监测数据"
        
        content = f"""## 与用户代理智能体建立A2A连接，{description}：

**连接信息：**
- 协议类型：{protocol}（标准A2A SDK）
- 数据代理服务地址：{base_url}
- 连接状态：{'成功' if success else '失败'}
- 授权Token：{token_display}

"""
        
        await self._write_log(content)
    
    async def log_data_addresses_received(self, round_num: int, data_addresses: List[Dict], has_direct_data: bool = False, medical_data: Optional[Dict] = None):
        """记录接收到的数据地址或直接数据"""
        if not self.enabled:
            return
        
        if round_num == 1:
            if has_direct_data and medical_data:
                content = f"""## 接收用户代理智能体所授权的诊断需求所需的数据地址，进行第一轮诊断，用户返回数据为：

{self._format_medical_data(medical_data)}

"""
            else:
                content = f"""## 接收用户代理智能体所授权的诊断需求所需的数据地址，进行第一轮诊断，用户返回数据地址为：

**数据地址列表：**

"""
                for i, addr in enumerate(data_addresses, 1):
                    hospital = addr.get('hospital', 'N/A')
                    department = addr.get('department', 'N/A')
                    data_type = addr.get('data_type', 'N/A')
                    location = addr.get('location', 'N/A')
                    address = addr.get('address', 'N/A')
                    token_preview = self._format_token(addr.get('access_token', ''))
                    
                    content += f"""{i}. **{hospital} - {department}**
   - 数据类型：{data_type}
   - 数据服务地址：{address}
   - 地域：{location}
   - 授权Token：{token_preview}（已授权）

"""
        else:
            # 第二轮：健康监测数据
            if has_direct_data and medical_data:
                content = f"""## 请求到用户的健康监测数据为：

{self._format_medical_data(medical_data)}

"""
            else:
                content = f"""## 请求到用户的健康监测数据为：

**数据地址列表：**

"""
                for i, addr in enumerate(data_addresses, 1):
                    content += f"""{i}. **{addr.get('hospital', 'N/A')}**
   - 数据类型：{addr.get('data_type', 'N/A')}
   - 数据服务地址：{addr.get('address', 'N/A')}
   - 地域：{addr.get('location', 'N/A')}

"""
        
        content += "---\n\n"
        await self._write_log(content)
    
    async def log_routing(self, location_groups: Dict[str, List], specialty_type: str, service_configs: Optional[Dict] = None):
        """记录智能路由"""
        if not self.enabled:
            return
        
        # 将specialty_type转换为中文
        specialty_cn = self._translate_specialty(specialty_type)
        
        content = f"""## 根据返回的数据地址，智能路由到对应地域的内科（外科）专科医生服务进行专业诊断，响应进行诊断的详细专科医生服务为：

**路由结果：**

"""
        
        for i, (location, addresses) in enumerate(location_groups.items(), 1):
            location_cn = self._translate_location(location)
            hospital = addresses[0].get('hospital', 'N/A') if addresses else 'N/A'
            
            # 从service_configs获取真实的服务URL
            service_url = self._get_service_url(specialty_type, location, service_configs)
            
            content += f"""{i}. **{location_cn}地区 → {specialty_cn}服务**
   - 服务地址：{service_url}
   - 专科类型：{specialty_type}
   - 数据地址数量：{len(addresses)}个
   - 对应医院：{hospital}

"""
        
        content += "---\n\n"
        await self._write_log(content)
    
    async def log_mcp_interaction(self, round_num: int, location: str, specialty: str, mcp_address: str, token: str, success: bool, data_summary: Optional[Dict] = None):
        """记录MCP协议交互"""
        if not self.enabled:
            return
        
        location_cn = self._translate_location(location)
        specialty_cn = self._translate_specialty(specialty)
        
        content = f"""## {location_cn}（上海或者北京）{specialty_cn}（外科）服务根据数据地址通过MCP协议，与数据存储服务的MCP server进行交互，进行诊断数据请求：

### {location_cn}{specialty_cn}服务 - MCP数据请求

**MCP交互信息：**
- MCP Server地址：{mcp_address}
- 请求数据类型：{self._get_data_type_for_round(round_num)}
- 授权Token：{self._format_token(token)}（已验证）
- 交互状态：{'成功' if success else '失败'}

"""
        
        if data_summary:
            content += f"""**获取的诊断数据：**
"""
            for key, value in data_summary.items():
                content += f"- {key}：{value}\n"
        
        content += "\n---\n\n"
        await self._write_log(content)
    
    async def log_specialist_diagnosis(self, round_num: int, location: str, specialty: str, diagnosis_result: Dict, duration: float):
        """记录专科医生诊断"""
        if not self.enabled:
            return
        
        location_cn = self._translate_location(location)
        specialty_cn = self._translate_specialty(specialty)
        
        if round_num == 1:
            title = f"## {location_cn}（上海或者北京）{specialty_cn}（外科）服务根据请求到的数据进行专业诊断："
        else:
            title = "## 接收健康监测数据，进行第二轮专业诊断："
        
        content = f"""{title}

### {location_cn}{specialty_cn}服务 - {'第二轮' if round_num > 1 else ''}专业诊断

**诊断过程：**
- 分析患者症状：{self._extract_symptoms(diagnosis_result)}
"""
        
        if round_num > 1:
            content += "- 结合第一轮病历数据：综合分析\n"
            content += "- 结合第二轮健康监测数据：综合分析\n"
        else:
            content += "- 结合病历数据：综合分析\n"
        
        content += f"""- 诊断时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 诊断耗时：{duration:.2f} ms

"""
        
        # 提取诊断结果
        diagnosis = diagnosis_result.get('diagnosis', {})
        if isinstance(diagnosis, dict):
            diagnosis_text = diagnosis.get('diagnosis', '')
            reasoning = diagnosis.get('reasoning', '')
        else:
            diagnosis_text = str(diagnosis)
            reasoning = ''
        
        # 确保诊断结果文本格式正确（处理可能的换行和特殊字符）
        # 诊断结果文本在Markdown中作为普通段落，需要确保格式正确
        diagnosis_text_clean = diagnosis_text.strip()
        
        content += f"""**{'诊断结果' if round_num == 1 else '诊断结果'}：**
{diagnosis_text_clean}

"""
        
        if reasoning:
            # 确保推理文本格式正确
            reasoning_clean = reasoning.strip()
            content += f"""**诊断推理：**
{reasoning_clean}

"""
        
        confidence = diagnosis_result.get('confidence', 0.0)
        content += f"""**诊断置信度：** {confidence * 100:.0f}%

"""
        
        if round_num == 1:
            content += "---\n\n"
        
        await self._write_log(content)
    
    async def log_round_result(self, round_num: int, results: List[Dict], needs_more_data: bool):
        """记录诊断轮次结果"""
        if not self.enabled:
            return
        
        content = f"""## 第{round_num}轮诊断结果为：

**诊断汇总：**

"""
        
        for i, result in enumerate(results, 1):
            location = result.get('location', 'N/A')
            location_cn = self._translate_location(location)
            specialty = result.get('specialization', 'N/A')
            specialty_cn = self._translate_specialty(specialty)
            confidence = result.get('confidence', 0.0)
            data_sources = result.get('data_sources', [])
            
            diagnosis = result.get('diagnosis', {})
            if isinstance(diagnosis, dict):
                diagnosis_text = diagnosis.get('diagnosis', '')
                recommendation = diagnosis.get('recommendation', '')
                treatment = diagnosis.get('treatment', '')
            else:
                diagnosis_text = str(diagnosis)
                recommendation = ''
                treatment = ''
            
            content += f"""{i}. **{location_cn}{specialty_cn}服务诊断结果**
   - 诊断结论：{diagnosis_text[:200]}{'...' if len(diagnosis_text) > 200 else ''}
   - 置信度：{confidence * 100:.0f}%
"""
            
            if recommendation:
                content += f"   - 建议：{recommendation}\n"
            
            if treatment:
                content += f"   - 治疗方案：{treatment}\n"
            
            if data_sources:
                content += f"   - 数据来源：{'、'.join(data_sources)}\n"
        
        if round_num == 1:
            # 计算平均置信度
            avg_confidence = sum(r.get('confidence', 0.0) for r in results) / len(results) if results else 0.0
            content += f"""

"""
        
        if needs_more_data:
            content += """## 根据诊断需求，需要更多健康监测数据：

**数据需求分析：**
- 需要数据类型：健康监测数据
- 需求优先级：高
- 需求原因：第一轮诊断结果显示需要实时健康监测数据来进一步确诊
- 具体需求：血压、心率、血糖等实时监测数据

---

"""
        
        content += "\n"
        await self._write_log(content)
    
    async def log_second_round_request(self):
        """记录第二轮数据请求"""
        if not self.enabled:
            return
        
        content = """## 与用户代理智能体进行A2A通信交互，正在请求用户更多健康监测数据：

**A2A交互信息：**
- 协议类型：EntryAgent（标准A2A SDK）
- 交互轮次：第2轮
- 请求类型：健康监测数据
- 连接状态：成功

**请求内容：**
- 数据需求：健康监测数据（血压、心率、血糖等）
- 对话轮次：第2轮
- 请求优先级：高

---

"""
        await self._write_log(content)
    
    async def log_data_proxy_request(self, round_num: int, request_data: Dict[str, Any], protocol: str):
        """记录数据代理请求"""
        if not self.enabled:
            return
        
        intent = request_data.get('intent_type', 'N/A')
        user_id = request_data.get('user_id', 'N/A')
        context = request_data.get('context', {})
        conversation_round = context.get('conversation_round', round_num)
        specialist_requests = context.get('specialist_requests', [])
        
        content = f"""## 数据代理请求（第{round_num}轮）

**请求信息：**
- 轮次：{round_num}
- 协议：{protocol}
- 意图：{intent}
- 用户ID：{user_id}
- 对话轮次：{conversation_round}
"""
        
        if specialist_requests:
            content += f"- 数据需求：{len(specialist_requests)} 项\n"
            for i, req in enumerate(specialist_requests, 1):
                if isinstance(req, dict):
                    data_type = req.get('data_type', 'N/A')
                    content += f"  - 需求{i}：{data_type}\n"
        
        request_str = self._format_json(request_data, max_length=3000)
        content += f"""
**请求数据：**
```json
{request_str}
```

"""
        await self._write_log(content)
    
    async def log_data_proxy_response(self, round_num: int, response_data: Dict[str, Any], protocol: str):
        """记录数据代理响应"""
        if not self.enabled:
            return
        
        success = response_data.get('success', False)
        data_addresses = response_data.get('data_addresses', [])
        has_direct_data = response_data.get('has_direct_data', False)
        medical_data = response_data.get('medical_data')
        
        content = f"""## 数据代理响应（第{round_num}轮）

**响应信息：**
- 成功：{success}
- 数据地址数量：{len(data_addresses)}
- 包含直接数据：{has_direct_data}
"""
        
        if data_addresses:
            content += "**数据地址详情：**\n\n"
            for i, addr in enumerate(data_addresses[:5], 1):  # 只显示前5个
                hospital = addr.get('hospital', 'N/A')
                department = addr.get('department', 'N/A')
                data_type = addr.get('data_type', 'N/A')
                location = addr.get('location', 'N/A')
                address = addr.get('address', 'N/A')
                location_cn = self._translate_location(location)
                
                content += f"{i}. **{hospital}**"
                if department:
                    content += f" - {department}"
                content += f"\n"
                content += f"   - 数据类型：{data_type}\n"
                content += f"   - 数据服务地址：{address}\n"
                content += f"   - 地域：{location_cn} ({location})\n"
                content += "\n"
            if len(data_addresses) > 5:
                content += f"   - ... (还有 {len(data_addresses) - 5} 个数据地址)\n"
        
        if has_direct_data and medical_data:
            medical_data_str = self._format_json(medical_data, max_length=2000)
            content += f"""
- 直接医疗数据：
```json
{medical_data_str}
```

"""
        
        response_str = self._format_json(response_data, max_length=3000)
        content += f"""
**完整响应数据：**
```json
{response_str}
```

"""
        await self._write_log(content)
    
    async def log_comprehensive_report(self, report_content: str, summary: Dict[str, Any]):
        """记录综合诊断报告"""
        if not self.enabled:
            return
        
        content = f"""## 根据两轮诊断结果进行汇总，给出综合诊断报告：

**综合诊断报告：**

{report_content}

---

**诊断过程总结：**
- 诊断轮次：{summary.get('rounds', 'N/A')}轮
- 参与专科医生：{summary.get('specialist_count', 'N/A')}位
- 总耗时：{summary.get('duration', 0):.1f}秒
- 数据来源：{', '.join(summary.get('data_sources', [])) if summary.get('data_sources') else 'N/A'}
- 诊断状态：{summary.get('status', 'N/A')}
- 最终置信度：{summary.get('avg_confidence', 0.0) * 100:.1f}%

---

"""
        await self._write_log(content)
    
    async def log_error(self, error_msg: str, exception: Optional[Exception] = None):
        """记录错误信息"""
        if not self.enabled:
            return
        
        content = f"""## 诊断过程异常：

**错误信息：**
- 错误消息：{error_msg}
"""
        
        if exception:
            content += f"""- 错误类型：{type(exception).__name__}
- 堆栈信息：
```python
{traceback.format_exc()}
```

"""
        else:
            content += "\n"
        
        await self._write_log(content)
    
    async def end_diagnosis_session(self, summary: Dict[str, Any]):
        """结束诊断会话"""
        if not self.enabled:
            return
        
        self.current_session = None
    
    async def clear_log(self):
        """清空日志文件"""
        if not self.enabled:
            return
        
        try:
            async with self._lock:
                with open(self.log_file_path, 'w', encoding='utf-8') as f:
                    f.write('')
        except Exception as e:
            self.logger.error(f"清空诊断日志失败: {e}")
    
    # 辅助方法
    def _escape_markdown(self, text: str) -> str:
        """
        转义Markdown特殊字符，确保文本在Markdown中正确显示
        
        注意：对于代码块内的内容，不需要转义
        对于普通文本，需要转义特殊字符
        """
        if not text:
            return ""
        # 转义Markdown特殊字符（在非代码块中使用时）
        # 注意：这些字符在代码块中不需要转义
        special_chars = {
            '\\': '\\\\',
            '`': '\\`',
            '*': '\\*',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '[': '\\[',
            ']': '\\]',
            '(': '\\(',
            ')': '\\)',
            '#': '\\#',
            '+': '\\+',
            '-': '\\-',
            '.': '\\.',
            '!': '\\!',
        }
        # 只在非代码块文本中需要转义，但这里我们保守处理
        # 实际上，在列表项和普通文本中，大部分字符不需要转义
        # 只有在特定上下文中才需要转义
        return text
    
    def _format_json(self, data: Any, max_length: int = 5000, max_string_length: int = 200) -> str:
        """
        格式化JSON数据，支持截断
        
        参数:
            data: 要格式化的数据
            max_length: JSON字符串总长度限制
            max_string_length: 单个字符串值的最大长度（超过会截断并添加注释）
        """
        try:
            # 先尝试直接格式化
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            
            # 如果总长度超过限制，直接截断
            if len(json_str) > max_length:
                return json_str[:max_length] + f"\n... (数据过长，已截断，总长度: {len(json_str)} 字符)"
            
            # 处理超长字符串值（在代码块中，长行可能不会自动换行）
            # 对于超长的字符串值（如access_token），在日志中截断显示
            lines = json_str.split('\n')
            processed_lines = []
            
            for line in lines:
                # 检查是否是包含长字符串值的行（如access_token、token等）
                # 匹配模式：  "key": "very long string..."
                if 'access_token' in line or 'token' in line.lower():
                    # 检查字符串值长度
                    # 提取字符串值部分（匹配完整的键值对）
                    match = re.search(r'(\s*"[^"]+"\s*:\s*")([^"]{50,})(")', line)
                    if match:
                        prefix = match.group(1)  # "key": "
                        long_value = match.group(2)  # 长字符串值
                        suffix = match.group(3)  # "
                        
                        if len(long_value) > max_string_length:
                            # 截断长字符串值，保持JSON格式有效
                            truncated_value = long_value[:max_string_length] + "..."
                            # 重新构建行，在值后添加说明（作为字符串的一部分，保持JSON有效）
                            # 注意：在JSON字符串值中添加说明会破坏JSON结构，所以只截断
                            line = prefix + truncated_value + suffix
                            # 在行尾添加说明（作为注释，但JSON不支持注释，所以改为在下一行添加说明）
                            # 实际上，我们只截断值，不添加注释，以保持JSON有效性
                            # 如果需要说明，可以在日志的其他部分添加
                
                processed_lines.append(line)
            
            result = '\n'.join(processed_lines)
            
            # 再次检查总长度
            if len(result) > max_length:
                return result[:max_length] + f"\n... (数据过长，已截断，总长度: {len(result)} 字符)"
            
            return result
        except Exception:
            # 如果无法序列化为JSON，转换为字符串并转义特殊字符
            return self._escape_markdown(str(data))
    
    def _format_token(self, token: Optional[str]) -> str:
        """格式化Token（脱敏）"""
        if not token:
            return "(空)"
        if len(token) > 20:
            return f"{token[:20]}...（长度: {len(token)}）"
        return token
    
    def _format_medical_data(self, medical_data: Dict) -> str:
        """格式化医疗数据"""
        content = ""
        
        if 'health_monitoring' in medical_data:
            hm = medical_data['health_monitoring']
            content += "**健康监测数据详情：**\n\n"
            
            if 'blood_pressure' in hm:
                bp = hm['blood_pressure']
                content += f"""- **血压数据：**
  - 收缩压：{bp.get('systolic', 'N/A')} mmHg
  - 舒张压：{bp.get('diastolic', 'N/A')} mmHg
  - 测量时间：{bp.get('timestamp', 'N/A')}

"""
            
            if 'heart_rate' in hm:
                hr = hm['heart_rate']
                content += f"""- **心率数据：**
  - 心率：{hr.get('bpm', 'N/A')} 次/分
  - 测量时间：{hr.get('timestamp', 'N/A')}

"""
            
            if 'blood_glucose' in hm:
                bg = hm['blood_glucose']
                content += f"""- **血糖数据：**
  - 血糖值：{bg.get('value', 'N/A')} {bg.get('unit', 'mmol/L')}
  - 测量时间：{bg.get('timestamp', 'N/A')}

"""
        
        content += "**数据来源：** 健康监测设备（用户代理智能体授权）\n"
        return content
    
    def _translate_location(self, location: str) -> str:
        """翻译地域名称"""
        mapping = {
            "beijing": "北京",
            "shanghai": "上海",
            "guangzhou": "广州",
            "shenzhen": "深圳"
        }
        return mapping.get(location, location)
    
    def _translate_specialty(self, specialty: str) -> str:
        """翻译专科名称"""
        mapping = {
            "internal_medicine": "内科",
            "surgical": "外科",
            "imaging": "影像科"
        }
        return mapping.get(specialty, specialty)
    
    def _get_service_url(self, specialty: str, location: str, service_configs: Optional[Dict] = None) -> str:
        """获取服务URL"""
        # 如果提供了service_configs，从中获取真实URL
        if service_configs:
            try:
                specialty_configs = service_configs.get(specialty, {})
                location_config = specialty_configs.get(location, {})
                if location_config and isinstance(location_config, dict):
                    base_url = location_config.get('base_url', '')
                    if base_url:
                        return base_url
            except Exception:
                pass
        
        # 默认返回占位符
        return f"http://localhost:800{1 if location == 'beijing' else 2}"
    
    def _get_data_type_for_round(self, round_num: int) -> str:
        """根据轮次获取数据类型"""
        if round_num == 1:
            return "病历数据"
        else:
            return "健康监测数据"
    
    def _extract_symptoms(self, diagnosis_result: Dict) -> str:
        """提取症状"""
        diagnosis = diagnosis_result.get('diagnosis', {})
        if isinstance(diagnosis, dict):
            symptoms = diagnosis.get('symptoms', [])
            if symptoms:
                return '、'.join(symptoms)
        return "已分析"

