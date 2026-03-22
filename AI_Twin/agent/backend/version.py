#!/usr/bin/env python3
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
版本信息管理模块

提供项目版本信息、构建信息、版权信息等管理功能。
"""

import datetime
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


class VersionInfo:
    """版本信息类"""

    def __init__(self):
        self._version_data = self._load_version_data()

    def _load_version_data(self) -> Dict[str, Any]:
        """加载版本数据"""
        # 默认版本信息
        version_data = {
            "version": "1.0.0",
            "build": "dev",
            "build_date": datetime.datetime.now().isoformat(),
            "git": {"commit": "", "branch": "", "tag": "", "dirty": False},
            "python": {
                "version": sys.version,
                "implementation": sys.implementation.name
                if hasattr(sys, "implementation")
                else "unknown",
            },
            "system": {
                "platform": sys.platform,
                "machine": os.uname().machine if hasattr(os, "uname") else "unknown",
            },
            "copyright": {
                "owner": "",
                "email": "",
                "year": datetime.datetime.now().year,
            },
            "metadata": {
                "project_name": "User-agent",
                "description": "UserAgent辅助系统后端API",
                "license": "Proprietary",
            },
        }

        # 尝试加载版本文件
        version_file = PROJECT_ROOT / "VERSION.json"
        if version_file.exists():
            try:
                with open(version_file, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    version_data.update(file_data)
            except Exception as e:
                logger.warning(f"Failed to load version file: {e}")

        # 获取Git信息
        git_info = self._get_git_info()
        if git_info:
            version_data["git"].update(git_info)

        # 获取版权信息
        copyright_info = self._get_copyright_info()
        if copyright_info:
            version_data["copyright"].update(copyright_info)

        # 环境变量优先覆盖（编译时注入）
        # 支持 VERSION, BUILD, BUILD_DATE, GIT_COMMIT, GIT_BRANCH 等
        env_version = os.getenv("VERSION")
        if env_version:
            version_data["version"] = env_version
        env_build = os.getenv("BUILD")
        if env_build:
            version_data["build"] = env_build
        env_build_date = os.getenv("BUILD_DATE")
        if env_build_date:
            version_data["build_date"] = env_build_date
        env_git_commit = os.getenv("GIT_COMMIT")
        if env_git_commit:
            version_data["git"]["commit"] = env_git_commit
        env_git_branch = os.getenv("GIT_BRANCH")
        if env_git_branch:
            version_data["git"]["branch"] = env_git_branch

        return version_data

    def _get_git_info(self) -> Optional[Dict[str, Any]]:
        """获取Git仓库信息"""
        try:
            # 检查是否在Git仓库中
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )

            if result.returncode != 0:
                return None

            # 获取当前提交哈希
            commit_result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            commit = (
                commit_result.stdout.strip() if commit_result.returncode == 0 else ""
            )

            # 获取当前分支
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            branch = (
                branch_result.stdout.strip() if branch_result.returncode == 0 else ""
            )

            # 获取最近标签
            tag_result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            tag = tag_result.stdout.strip() if tag_result.returncode == 0 else ""

            # 检查是否有未提交的更改
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            dirty = bool(status_result.stdout.strip())

            return {"commit": commit, "branch": branch, "tag": tag, "dirty": dirty}

        except Exception as e:
            logger.debug(f"Failed to get git info: {e}")
            return None

    def _get_copyright_info(self) -> Optional[Dict[str, str]]:
        """获取版权信息"""
        try:
            # 获取Git配置的用户名和邮箱
            name_result = subprocess.run(
                ["git", "config", "user.name"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            email_result = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )

            owner = name_result.stdout.strip() if name_result.returncode == 0 else ""
            email = email_result.stdout.strip() if email_result.returncode == 0 else ""

            return {"owner": owner, "email": email}

        except Exception as e:
            logger.debug(f"Failed to get copyright info: {e}")
            return None

    def get_version(self) -> str:
        """获取版本号"""
        return self._version_data["version"]

    def get_build(self) -> str:
        """获取构建标识"""
        return self._version_data["build"]

    def get_build_date(self) -> str:
        """获取构建日期"""
        return self._version_data["build_date"]

    def get_git_info(self) -> Dict[str, Any]:
        """获取Git信息"""
        return self._version_data["git"]

    def get_copyright_info(self) -> Dict[str, str]:
        """获取版权信息"""
        return self._version_data["copyright"]

    def get_metadata(self) -> Dict[str, str]:
        """获取项目元数据"""
        return self._version_data["metadata"]

    def get_python_info(self) -> Dict[str, str]:
        """获取Python环境信息"""
        return self._version_data["python"]

    def get_system_info(self) -> Dict[str, str]:
        """获取系统信息"""
        return self._version_data["system"]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self._version_data.copy()

    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self._version_data, indent=indent, ensure_ascii=False)

    def to_string(self, format: str = "simple") -> str:
        """转换为字符串格式

        Args:
            format: 输出格式，可选值: simple, full, compact
        """
        if format == "simple":
            return f"v{self.get_version()}-{self.get_build()}"
        elif format == "compact":
            git_info = self.get_git_info()
            commit = git_info.get("commit", "")[:8]
            dirty = "*" if git_info.get("dirty", False) else ""
            return f"v{self.get_version()}-{self.get_build()}+{commit}{dirty}"
        elif format == "full":
            return self.to_json()
        else:
            return self.to_json()

    def save_to_file(self, filepath: Optional[Path] = None) -> bool:
        """保存版本信息到文件"""
        try:
            if filepath is None:
                filepath = PROJECT_ROOT / "VERSION.json"

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self._version_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Version info saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save version info: {e}")
            return False

    def update_version(self, new_version: str) -> bool:
        """更新版本号"""
        try:
            self._version_data["version"] = new_version
            self._version_data["build_date"] = datetime.datetime.now().isoformat()
            return self.save_to_file()
        except Exception as e:
            logger.error(f"Failed to update version: {e}")
            return False

    def update_build(self, new_build: str) -> bool:
        """更新构建标识"""
        try:
            self._version_data["build"] = new_build
            self._version_data["build_date"] = datetime.datetime.now().isoformat()
            return self.save_to_file()
        except Exception as e:
            logger.error(f"Failed to update build: {e}")
            return False


# 全局版本信息实例
_version_info: Optional[VersionInfo] = None


def get_version_info() -> VersionInfo:
    """获取全局版本信息实例"""
    global _version_info
    if _version_info is None:
        _version_info = VersionInfo()
    return _version_info


def get_version() -> str:
    """获取版本号（快捷函数）"""
    return get_version_info().get_version()


def get_build() -> str:
    """获取构建标识（快捷函数）"""
    return get_version_info().get_build()


def get_version_string(format: str = "simple") -> str:
    """获取版本字符串（快捷函数）"""
    return get_version_info().to_string(format)


if __name__ == "__main__":
    # 命令行接口
    import argparse

    parser = argparse.ArgumentParser(description="版本信息管理工具")
    parser.add_argument(
        "--format",
        choices=["simple", "compact", "full", "json"],
        default="simple",
        help="输出格式",
    )
    parser.add_argument("--save", action="store_true", help="保存版本信息到文件")
    parser.add_argument("--update-version", help="更新版本号")
    parser.add_argument("--update-build", help="更新构建标识")

    args = parser.parse_args()

    version_info = get_version_info()

    if args.update_version:
        if version_info.update_version(args.update_version):
            print(f"版本号已更新为: {args.update_version}")
        else:
            print("版本号更新失败")
            sys.exit(1)

    if args.update_build:
        if version_info.update_build(args.update_build):
            print(f"构建标识已更新为: {args.update_build}")
        else:
            print("构建标识更新失败")
            sys.exit(1)

    if args.save:
        if version_info.save_to_file():
            print("版本信息已保存到 VERSION.json")
        else:
            print("版本信息保存失败")
            sys.exit(1)

    # 输出版本信息
    if args.format == "json":
        print(version_info.to_json())
    else:
        print(version_info.to_string(args.format))

