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

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.shared.config.model_config import CONFIG_DICT


class Settings(BaseSettings):
    # 应用配置
    PROJECT_NAME: str = "Cybertwin内科医生Agent"
    PROJECT_DESCRIPTION: str = "智能医疗辅助系统内科医生Agetn"
    VERSION: str = "0.1.10"
    API_PREFIX: str = "/api/"
    DEBUG: bool = True

    SERVICE_NAME: str = "internal-medicine"
    SERVICE_PORT: int = 8002
    LOCATION: str = "beijing"
    SPECIALIZATION: str = "内科"
    MODEL_NAME: str = "huatuo2"
    API_KEY: str = ""

    # CORS配置
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://172.25.21.129:8089",
        "http://172.25.23.89:8002",
    ]

    # 日志配置
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        extra="allow",  # 默认为 ignore，可改为 allow/forbid
    )

    @field_validator("MODEL_NAME")
    @classmethod
    def model_name_validator(cls, v: str):
        if v not in CONFIG_DICT:
            raise ValueError(f"{v} is no config model")
        return v


settings = Settings()
