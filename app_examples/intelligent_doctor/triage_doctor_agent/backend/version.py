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
"""版本管理模块 - 自动生成 (不要手动编辑)"""

__version__ = "v0.0.0-242362e"
__major__ = v0
__minor__ = 0
__patch__ = 0-242362e
__git_commit__ = "242362e"
__build_time__ = "2026-03-03T03:02:22Z"


def get_version() -> str:
    """获取完整版本字符串"""
    return __version__


def get_version_info() -> dict:
    """获取详细的版本信息"""
    return {
        "version": __version__,
        "major": __major__,
        "minor": __minor__,
        "patch": __patch__,
        "build_time": __build_time__,
        "git_commit": __git_commit__,
    }
