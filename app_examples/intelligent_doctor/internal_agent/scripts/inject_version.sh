#!/bin/bash

# 版本注入脚本
# 将版本信息注入到 Python 源代码

VERSION="$1"
GIT_COMMIT="$2"
BUILD_DATE="$3"
VERSION_FILE="$4"

# 创建目录
mkdir -p "$(dirname "$VERSION_FILE")"

# 生成版本文件
cat > "$VERSION_FILE" << EOF
# -*- coding: utf-8 -*-
"""
Version information module

Automatic version information file injected during build.
"""

__version__ = "$VERSION"
__git_commit__ = "$GIT_COMMIT"
__build_date__ = "$BUILD_DATE"
VERSION_STRING = f"{__version__}+{__git_commit__}"

VERSION_INFO = {
    "version": __version__,
    "git_commit": __git_commit__,
    "build_date": __build_date__,
    "version_string": VERSION_STRING,
}

def get_version() -> str:
    """Get version number"""
    return __version__

def get_version_info() -> dict:
    """Get complete version information"""
    return VERSION_INFO.copy()

def get_version_string() -> str:
    """Get complete version string"""
    return VERSION_STRING
EOF

echo "Version file generated: $VERSION_FILE"
