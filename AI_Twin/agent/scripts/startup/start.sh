#!/bin/bash
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


echo "============================================================"
echo "医疗智能体项目启动器"
echo "============================================================"
echo

echo "检查Python环境..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python未安装或未添加到PATH"
    echo "请先安装Python 3.8+"
    exit 1
fi

echo
echo "检查依赖..."
python3 -c "import streamlit, sqlite3, asyncio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少依赖，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

echo
echo "检查智能体模块..."
python3 -c "from agents.coordinator import CybertwinAgent" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 智能体模块导入失败"
    echo "请检查agents目录是否存在"
    exit 1
fi

echo
echo "创建必要目录..."
mkdir -p data
mkdir -p data/backups
mkdir -p data/logs

echo
echo "运行快速测试..."
python3 quick_test.py
if [ $? -ne 0 ]; then
    echo "⚠️ 快速测试失败，但继续启动..."
fi

echo
echo "============================================================"
echo "启动Streamlit应用..."
echo "访问地址: http://localhost:8501"
echo "按 Ctrl+C 停止应用"
echo "============================================================"
echo

export PYTHONPATH=$PWD
python3 -m streamlit run app.py
