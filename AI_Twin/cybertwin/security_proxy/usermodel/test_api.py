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

import requests

url = "http://localhost:8001/evaluate"
data = {
    "subject_type": "user",
    "common_device": True,
    "time": 8,
    "location": "office",
    "bio": 0.78,
    "pswd": 1,
    "access_network_score": 0.8,
    "network_risk": 0.5
}

response = requests.post(url, json=data)
print("响应状态码：", response.status_code)
print("响应内容：", response.json())