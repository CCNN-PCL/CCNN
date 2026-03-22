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

from fastapi import FastAPI, HTTPException, Response  
import joblib
import re
import string
import os
from pydantic import BaseModel  # 用于定义请求体格式

# 初始化FastAPI应用
app = FastAPI(title="内容敏感度评分API")

# ==============================================================================
# 1. 加载规则引擎（复用原逻辑，无需训练）
# ==============================================================================
class RuleEngine:
    def __init__(self):
        self.keyword_rules = {
            5: [
                "密码", "身份证", "人脸照片", "CVV", "支付密码", "指纹",
                "抑郁症", "自杀念头", "ADHD", "双相情感障碍"
            ],
            4: [
                "银行卡号", "医保卡", "家庭住址", "门牌号", 
                "体检报告", "高血压", "工资条",
                "胃镜", "X光", "溃疡", "影像数据", "手术记录","病史数据"
            ],
            3: [
                "超市买", "社区医院", "购物小票", "感冒", "微信好友", "旅游", "手机号", "抑郁情绪",
                "脱敏胃镜", "脱敏X光", "急诊", "化验报告", "用药记录"
            ],
            2: [
                "电影","感冒药", "血压计"
            ]
        }
        
        self.pattern_rules = {
            5: [
                r'\b\d{18}\b',  # 身份证号（18位）
                r'CVV\s*码?\s*\d{3}\b'  # CVV码（3位）
            ],
            4: [
                r'\b\d{16,19}\b',  # 银行卡号（16-19位）
                r'住址\s*[:：]\s*[\u4e00-\u9fa50-9]+[小区楼栋室]'  # 家庭住址
            ],
            3: [
                r'\b1[3-9]\d{9}\b'  # 手机号（11位）
            ]
        }
        
        self.prepared_keywords = self._prepare_keywords()
    
    def _prepare_keywords(self):
        all_keywords = []
        for score, keywords in self.keyword_rules.items():
            for keyword in keywords:
                all_keywords.append({
                    'keyword': keyword,
                    'score': score,
                    'length': len(keyword)
                })
        all_keywords.sort(key=lambda x: (-x['length'], -x['score']))
        return all_keywords
    
    def preprocess_text(self, text):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text
    
    def get_rule_based_score(self, content):
        content = self.preprocess_text(content)
        score = 1  # 默认是 Python int
        
        for kw in self.prepared_keywords:
            if kw['keyword'].lower() in content:
                score = kw['score']
                return int(score)  # 显式转换为 Python int
        
        for s in sorted(self.pattern_rules.keys(), reverse=True):
            for pattern in self.pattern_rules[s]:
                if re.search(pattern, content):
                    score = s
                    return int(score)  # 显式转换为 Python int
        
        return int(score)  # 最后返回时转换


# ==============================================================================
# 2. 加载训练好的机器学习模型组件
# ==============================================================================
class MLModel:
    def __init__(self):
        # 加载保存的TF-IDF向量器和决策树模型
        self.vectorizer = joblib.load("models/tfidf_vectorizer.joblib")
        self.model = joblib.load("models/decision_tree_model.joblib")
    
    def preprocess_text(self, text):
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text
    
    def predict_score(self, content):
        processed_text = self.preprocess_text(content)
        X_tfidf = self.vectorizer.transform([processed_text])
        # 关键：将 numpy.int64 转换为 Python int
        return int(self.model.predict(X_tfidf)[0])  # 新增 int() 转换


# ==============================================================================
# 3. 综合评分器（复用逻辑，用于API推理）
# ==============================================================================
class SensitivityScorer:
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.ml_model = MLModel()  # 加载预训练模型
    
    def get_final_score(self, content, data_type="text"):
        rule_score = self.rule_engine.get_rule_based_score(content)
        ml_score = self.ml_model.predict_score(content)
        
        # 融合分数时，确保结果是 Python int（round 可能返回 numpy 类型，视环境而定）
        final_score = int(round(0.6 * rule_score + 0.4 * ml_score))  # 新增 int()
        final_score = max(1, min(5, final_score))
        
        # 映射敏感度级别
        level_map = {
            1: "极低敏感",
            2: "低敏感",
            3: "中敏感",
            4: "高敏感",
            5: "极高敏感"
        }
        
        return {
            "data_type": data_type,
            "content": content,
            "rule_based_score": rule_score,
            "ml_based_score": ml_score,
            "final_sensitivity_score": final_score,
            "sensitivity_level": level_map[final_score]
        }


# ==============================================================================
# 4. 定义API接口
# ==============================================================================
# 定义请求体格式（使用Pydantic验证输入）
class PredictionRequest(BaseModel):
    content: str  # 待评分的内容（文本或图片描述）
    data_type: str = "text"  # 类型：text/image，默认text


# 初始化评分器（启动时加载模型）
try:
    scorer = SensitivityScorer()
    print("模型加载成功，API服务就绪")
except Exception as e:
    print(f"模型加载失败：{str(e)}")
    raise  # 启动失败


# 定义预测接口
@app.post("/predict_sensitivity", summary="预测内容的敏感度评分")
def predict_sensitivity(request: PredictionRequest, response: Response):
    # 新增：强制响应头指定UTF-8编码
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    try:
        result = scorer.get_final_score(
            content=request.content,
            data_type=request.data_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推理失败：{str(e)}")

# 启动命令：uvicorn inference_api:app --host 0.0.0.0 --port 8000

# 确认代码中存在以下接口，且路径是小写的 /health
@app.get("/health", summary="健康检查接口")
def health_check():
    return {"status": "healthy", "service": "sensitivity-inference"}