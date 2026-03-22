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

"""
PostgreSQL启动脚本
=================

启动PostgreSQL数据库服务并初始化数据库
"""

import subprocess
import sys
import os
import time
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_postgresql_installed():
    """检查PostgreSQL是否已安装"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"PostgreSQL已安装: {result.stdout.strip()}")
            return True
        else:
            logger.error("PostgreSQL未安装")
            return False
    except FileNotFoundError:
        logger.error("PostgreSQL未安装或未添加到PATH")
        return False

def start_postgresql_service():
    """启动PostgreSQL服务"""
    try:
        # Windows系统
        if os.name == 'nt':
            logger.info("启动PostgreSQL服务...")
            result = subprocess.run(['net', 'start', 'postgresql-x64-13'], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                logger.info("PostgreSQL服务启动成功")
                return True
            else:
                logger.error(f"PostgreSQL服务启动失败: {result.stderr}")
                return False
        else:
            # Linux/macOS系统
            logger.info("启动PostgreSQL服务...")
            result = subprocess.run(['sudo', 'systemctl', 'start', 'postgresql'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("PostgreSQL服务启动成功")
                return True
            else:
                logger.error(f"PostgreSQL服务启动失败: {result.stderr}")
                return False
    except Exception as e:
        logger.error(f"启动PostgreSQL服务失败: {str(e)}")
        return False

def create_database():
    """创建数据库"""
    try:
        logger.info("创建数据库...")
        
        # 创建数据库的SQL命令
        create_db_sql = """
        CREATE DATABASE private_doctor_db;
        CREATE USER doctor_user WITH PASSWORD 'doctor_password';
        GRANT ALL PRIVILEGES ON DATABASE private_doctor_db TO doctor_user;
        """
        
        # 执行SQL命令
        result = subprocess.run(['psql', '-U', 'postgres', '-c', create_db_sql], 
                              capture_output=True, text=True, input='')
        
        if result.returncode == 0:
            logger.info("数据库创建成功")
            return True
        else:
            logger.error(f"数据库创建失败: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"创建数据库失败: {str(e)}")
        return False

def initialize_database():
    """初始化数据库表结构"""
    try:
        logger.info("初始化数据库表结构...")
        
        # 读取初始化SQL文件
        init_sql_path = Path("scripts/init_postgresql.sql")
        if not init_sql_path.exists():
            logger.error("初始化SQL文件不存在")
            return False
        
        # 执行初始化SQL
        result = subprocess.run(['psql', '-U', 'doctor_user', '-d', 'private_doctor_db', '-f', str(init_sql_path)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("数据库表结构初始化成功")
            return True
        else:
            logger.error(f"数据库表结构初始化失败: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"初始化数据库失败: {str(e)}")
        return False

def test_connection():
    """测试数据库连接"""
    try:
        logger.info("测试数据库连接...")
        
        test_sql = "SELECT version();"
        result = subprocess.run(['psql', '-U', 'doctor_user', '-d', 'private_doctor_db', '-c', test_sql], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("数据库连接测试成功")
            logger.info(f"PostgreSQL版本: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"数据库连接测试失败: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"测试数据库连接失败: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("开始PostgreSQL启动流程...")
    
    # 1. 检查PostgreSQL是否已安装
    if not check_postgresql_installed():
        logger.error("请先安装PostgreSQL")
        return False
    
    # 2. 启动PostgreSQL服务
    if not start_postgresql_service():
        logger.error("PostgreSQL服务启动失败")
        return False
    
    # 等待服务启动
    logger.info("等待PostgreSQL服务启动...")
    time.sleep(5)
    
    # 3. 创建数据库
    if not create_database():
        logger.error("数据库创建失败")
        return False
    
    # 4. 初始化数据库表结构
    if not initialize_database():
        logger.error("数据库表结构初始化失败")
        return False
    
    # 5. 测试连接
    if not test_connection():
        logger.error("数据库连接测试失败")
        return False
    
    logger.info("PostgreSQL启动完成！")
    logger.info("数据库信息:")
    logger.info("  主机: localhost")
    logger.info("  端口: 5432")
    logger.info("  数据库: private_doctor_db")
    logger.info("  用户: doctor_user")
    logger.info("  密码: doctor_password")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
