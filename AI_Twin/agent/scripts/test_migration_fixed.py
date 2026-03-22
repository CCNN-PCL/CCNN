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
测试修复后的PostgreSQL迁移
==========================
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_postgresql_connection():
    """测试PostgreSQL连接"""
    try:
        import asyncpg
        
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            database='private_doctor_db',
            user='doctor_user',
            password='doctor_password'
        )
        
        # 测试查询
        version = await conn.fetchval('SELECT version()')
        print(f"[OK] PostgreSQL连接成功: {version}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] PostgreSQL连接失败: {str(e)}")
        return False

async def test_sqlite_data():
    """测试SQLite数据"""
    try:
        import sqlite3
        
        # 检查SQLite数据库文件
        db_files = [
            'data/auth.db',
            'data/chat_history.db',
            'data/medical_records.db',
            'data/user_profiles.db'
        ]
        
        total_records = 0
        for db_file in db_files:
            if os.path.exists(db_file):
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # 获取表名
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                db_records = 0
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    db_records += count
                
                print(f"[DATA] {db_file}: {db_records} 条记录")
                total_records += db_records
                
                conn.close()
        
        print(f"[DATA] SQLite总记录数: {total_records}")
        return total_records > 0
        
    except Exception as e:
        print(f"[ERROR] SQLite数据检查失败: {str(e)}")
        return False

async def test_migration():
    """测试迁移过程"""
    try:
        from migrate_sqlite_to_postgresql_fixed_v2 import SQLiteToPostgreSQLMigratorV2
        
        # SQLite数据库路径
        sqlite_dbs = {
            'auth': 'data/auth.db',
            'chat_history': 'data/chat_history.db',
            'medical_records': 'data/medical_records.db',
            'user_profiles': 'data/user_profiles.db',
            'permissions': 'data/permissions.db',
            'audit': 'data/audit.db'
        }
        
        # PostgreSQL配置
        postgres_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'private_doctor_db',
            'user': 'doctor_user',
            'password': 'doctor_password'
        }
        
        print("[START] 开始测试迁移...")
        
        # 创建迁移器
        migrator = SQLiteToPostgreSQLMigratorV2(sqlite_dbs, postgres_config)
        
        # 运行迁移
        await migrator.run_migration()
        
        print("[OK] 迁移测试完成")
        return True
        
    except Exception as e:
        print(f"[ERROR] 迁移测试失败: {str(e)}")
        return False

async def test_postgresql_data():
    """测试PostgreSQL数据"""
    try:
        import asyncpg
        
        conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            database='private_doctor_db',
            user='doctor_user',
            password='doctor_password'
        )
        
        # 统计各表记录数
        tables = ['users', 'chat_history', 'medical_images', 'medical_records', 'hospitals']
        
        total_records = 0
        for table in tables:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"[DATA] PostgreSQL {table}: {count} 条记录")
                total_records += count
            except Exception as e:
                print(f"[WARN] 表 {table} 不存在或查询失败: {str(e)}")
        
        print(f"[DATA] PostgreSQL总记录数: {total_records}")
        
        await conn.close()
        return total_records > 0
        
    except Exception as e:
        print(f"[ERROR] PostgreSQL数据检查失败: {str(e)}")
        return False

async def main():
    """主函数"""
    print("[START] 开始PostgreSQL迁移测试...")
    print("=" * 50)
    
    # 1. 测试PostgreSQL连接
    print("\n[STEP 1] 测试PostgreSQL连接...")
    if not await test_postgresql_connection():
        print("[ERROR] PostgreSQL连接失败，请先启动PostgreSQL服务")
        return False
    
    # 2. 测试SQLite数据
    print("\n[STEP 2] 测试SQLite数据...")
    if not await test_sqlite_data():
        print("[ERROR] SQLite数据检查失败")
        return False
    
    # 3. 测试迁移
    print("\n[STEP 3] 测试迁移过程...")
    if not await test_migration():
        print("[ERROR] 迁移测试失败")
        return False
    
    # 4. 测试PostgreSQL数据
    print("\n[STEP 4] 测试PostgreSQL数据...")
    if not await test_postgresql_data():
        print("[ERROR] PostgreSQL数据检查失败")
        return False
    
    print("\n[SUCCESS] 所有测试通过！PostgreSQL迁移成功")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
