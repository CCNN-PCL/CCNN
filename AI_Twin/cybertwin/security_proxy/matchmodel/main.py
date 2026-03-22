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

from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
import os

# 初始化API服务
app = FastAPI(title="信任度-敏感度匹配推理服务")

# 加载预训练模型（启动时加载，避免重复加载）
model_dir = "models"
models = {}
for level in range(1, 6):
    model_path = os.path.join(model_dir, f"sensitivity_{level}_model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在：{model_path}")
    models[level] = joblib.load(model_path)
    print(f"已加载敏感度等级 {level} 的模型")

# 定义API接口：接收信任分和敏感度等级，返回预测结果
@app.post("/predict")
def predict(trust_score: float, sensitivity_level: int):
    # 参数校验
    if not (0 <= trust_score <= 1):
        raise HTTPException(status_code=400, detail="信任分必须在0-1之间")
    if sensitivity_level not in [1,2,3,4,5]:
        raise HTTPException(status_code=400, detail="敏感度等级必须是1-5的整数")
    
    # 构造输入数据（与训练时特征名一致）
    input_data = pd.DataFrame({"trust_score": [trust_score]})
    
    # 调用对应模型预测
    model = models[sensitivity_level]
    prediction = model.predict(input_data)[0]  # 0=拒绝，1=允许
    probability = model.predict_proba(input_data)[0, 1]  # 允许访问的概率
    
    return {
        "sensitivity_level": sensitivity_level,
        "trust_score": trust_score,
        "allowed": bool(prediction),
        "allow_probability": float(probability)
    }

# 启动命令（供容器调用）：uvicorn inference_service:app --host 0.0.0.0 --port 8000