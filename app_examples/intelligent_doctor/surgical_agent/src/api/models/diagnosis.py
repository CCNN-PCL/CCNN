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

from datetime import datetime
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class DataAddress(BaseModel):
    data_type: str
    location: str
    address: str
    hospital: str
    department: str
    access_token: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "data_types": self.data_type,
            "location": self.location,
            "address": self.address,
            "hospital": self.hospital,
            "department": self.department,
            "access_token": self.access_token,
        }


class SharedContext(BaseModel):
    user_id: str = ""
    intent: str = ""
    user_input: str = ""
    round_number: int = 0
    max_rounds: int = 0
    data_addresses_history: list[Any] = []
    diagnosis_results_history: list[Any] = []
    specialist_requests: list[Any] = []
    data_proxy_conversation_history: list[Any] = []
    direct_medical_data: dict[str, Any] | None = {}
    diagnosis_status: str = ""


    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "intent": self.intent,
            "user_input": self.user_input,
            "round_number": self.round_number,
            "max_rounds": self.max_rounds,
            "data_addresses_history": self.data_addresses_history
            if self.data_addresses_history
            else [],
            "diagnosis_results_history": self.diagnosis_results_history
            if self.diagnosis_results_history
            else [],
            "specialist_requests": self.specialist_requests,
            "data_proxy_conversation_history": self.data_proxy_conversation_history,
            "direct_medical_data": self.direct_medical_data,
            "diagnosis_status": self.diagnosis_status,
        }


class UserInfo(BaseModel):
    userid: str = ""
    username: str = ""
    id_token: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "userid": self.userid,
            "id_token": self.id_token,
        }


class Metadata(BaseModel):
    request_id: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    source: str = ""


class DiagnosisRequest(BaseModel):
    user_input: str
    user_id: str
    intent: str
    user_info: UserInfo | None = None
    data_addresses: list[DataAddress] | None = None
    shared_context: SharedContext | None = None
    metadata: Metadata | None = None


class Status(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class DiagnosisResult(BaseModel):
    diagnosis: str
    confidence: float
    reasoning: str
    symptoms_analysis: str
    data_usage_summary: str
    recommendations: list[str] | None
    surgical_indication: Any | None


class DiagnosisResponse(BaseModel):
    status: Status
    agent: str
    location: str
    specialization: str
    diagnosis: Dict
    needs_more_data: bool = False
    data_requirements: list[Any]
    data_sources: list[str]

    available_data_types: list[str]
    data_usage_summary: Any
    confidence: float
    processing_time: float
    timestamp: datetime
    data_content: Dict | None = None
    reasoning: Any


def from_dict(v: Dict[str, Any]) -> DiagnosisResponse:
    model = DiagnosisResponse(**v)
    return model
