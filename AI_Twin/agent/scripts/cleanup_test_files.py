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
测试文件清理脚本
================

清理项目中的测试文件、临时文件和重复文件
"""

import os
import shutil
import glob
from pathlib import Path
from datetime import datetime

class TestFileCleaner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.cleanup_log = []
        self.backup_dir = self.project_root / "backup" / f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def log_action(self, action: str, file_path: str, reason: str = ""):
        """记录清理操作"""
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] {action}: {file_path}"
        if reason:
            log_entry += f" - {reason}"
        self.cleanup_log.append(log_entry)
        print(log_entry)
    
    def create_backup_dir(self):
        """创建备份目录"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.log_action("CREATE", str(self.backup_dir), "备份目录")
    
    def cleanup_duplicate_migration_scripts(self):
        """清理重复的迁移脚本"""
        migration_files = [
            "scripts/migrate_sqlite_to_postgresql.py",  # 原始版本
            "scripts/migrate_sqlite_to_postgresql_fixed.py",  # 修复版本1
            # 保留: migrate_sqlite_to_postgresql_fixed_v2.py (最新版本)
        ]
        
        for file_path in migration_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                # 移动到备份目录
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "重复的迁移脚本")
    
    def cleanup_test_scripts(self):
        """清理测试脚本"""
        test_files = [
            "test_format_fix.py",
            "simple_format_test.py", 
            "trace_error.py",
            "simple_db_browser.py",
            "database_import_tool.py",
            "database_query_tool.py",
            "fix_auth_database.py",
            "setup_passwords.py",
            "update_timeout_settings.py",
        ]
        
        for file_path in test_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                # 移动到备份目录
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "测试/调试脚本")
    
    def cleanup_scripts_test_files(self):
        """清理scripts目录中的测试文件"""
        test_files = [
            "scripts/test_migration_simple.py",
            "scripts/test_postgresql_simple.py", 
            "scripts/test_postgresql_manager.py",
            "scripts/quick_test_zhang_san.py",
            "scripts/test_zhang_san_medical_data.py",
            "scripts/test_medical_profile_fix.py",
            "scripts/test_enhanced_history_agent.py",
            "scripts/test_history_analysis_optimization.py",
            "scripts/test_history_agent_flow.py",
            "scripts/setup_test_user_passwords.py",
            "scripts/generate_test_medical_data.py",
            "scripts/run_all_zhang_san_tests.py",
            "scripts/run_complete_test.py",
            "scripts/demo_heart_palpitation_consultation.py",
            "scripts/quick_demo_heart_palpitation.py",
            "scripts/validate_migration.py",
            "scripts/verify_config.py",
            "scripts/update_app_config.py",
            "scripts/rollback_to_sqlite.py",
            "scripts/unlock_user.py",
            "scripts/reset_password.py",
        ]
        
        for file_path in test_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                # 移动到备份目录
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "测试脚本")
    
    def cleanup_log_files(self):
        """清理日志文件"""
        log_files = [
            "migration.log",
            "migration_v2.log",
        ]
        
        for file_path in log_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                # 移动到备份目录
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "日志文件")
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        temp_patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/*.pyd",
            "**/.DS_Store",
            "**/Thumbs.db",
        ]
        
        for pattern in temp_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        self.log_action("DELETE", str(file_path), "临时文件")
                    except Exception as e:
                        self.log_action("ERROR", str(file_path), f"删除失败: {e}")
                elif file_path.is_dir():
                    try:
                        shutil.rmtree(str(file_path))
                        self.log_action("DELETE", str(file_path), "临时目录")
                    except Exception as e:
                        self.log_action("ERROR", str(file_path), f"删除失败: {e}")
    
    def cleanup_duplicate_docs(self):
        """清理重复的文档文件"""
        duplicate_docs = [
            "PROJECT_RUN_GUIDE.md",
            "STARTUP_GUIDE.md", 
            "STREAMING_UPGRADE_GUIDE.md",
            "MIGRATION_COMPLETE.md",
        ]
        
        for file_path in duplicate_docs:
            full_path = self.project_root / file_path
            if full_path.exists():
                # 移动到备份目录
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "重复文档")
    
    def organize_scripts(self):
        """整理scripts目录结构"""
        # 创建子目录
        subdirs = {
            "migration": [
                "migrate_sqlite_to_postgresql_fixed_v2.py",
                "migrate_database.py",
                "init_postgresql.sql",
            ],
            "startup": [
                "start_all.py",
                "start_backend.py", 
                "start_frontend.py",
                "start_postgresql.py",
                "start.py",
                "start.bat",
                "start.sh",
            ],
            "utils": [
                "install_dependencies.py",
            ]
        }
        
        for subdir, files in subdirs.items():
            subdir_path = self.project_root / "scripts" / subdir
            subdir_path.mkdir(exist_ok=True)
            
            for file_name in files:
                src_path = self.project_root / "scripts" / file_name
                if src_path.exists():
                    dst_path = subdir_path / file_name
                    shutil.move(str(src_path), str(dst_path))
                    self.log_action("ORGANIZE", str(src_path), f"移动到 {subdir}/")
    
    def create_cleanup_report(self):
        """创建清理报告"""
        report_path = self.backup_dir / "cleanup_report.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 测试文件清理报告\n\n")
            f.write(f"**清理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**备份目录**: {self.backup_dir}\n\n")
            f.write("## 清理操作记录\n\n")
            
            for log_entry in self.cleanup_log:
                f.write(f"- {log_entry}\n")
            
            f.write("\n## 清理后的项目结构\n\n")
            f.write("```\n")
            f.write("项目根目录/\n")
            f.write("├── scripts/\n")
            f.write("│   ├── migration/          # 迁移相关脚本\n")
            f.write("│   ├── startup/            # 启动相关脚本\n")
            f.write("│   └── utils/              # 工具脚本\n")
            f.write("├── backup/                 # 备份文件\n")
            f.write("└── ...\n")
            f.write("```\n")
        
        self.log_action("CREATE", str(report_path), "清理报告")
    
    def run_cleanup(self):
        """执行清理操作"""
        print("[START] 开始清理测试文件...")
        print("=" * 50)
        
        # 创建备份目录
        self.create_backup_dir()
        
        # 清理重复的迁移脚本
        print("\n[STEP 1] 清理重复的迁移脚本...")
        self.cleanup_duplicate_migration_scripts()
        
        # 清理根目录测试文件
        print("\n[STEP 2] 清理根目录测试文件...")
        self.cleanup_test_scripts()
        
        # 清理scripts目录测试文件
        print("\n[STEP 3] 清理scripts目录测试文件...")
        self.cleanup_scripts_test_files()
        
        # 清理日志文件
        print("\n[STEP 4] 清理日志文件...")
        self.cleanup_log_files()
        
        # 清理临时文件
        print("\n[STEP 5] 清理临时文件...")
        self.cleanup_temp_files()
        
        # 清理重复文档
        print("\n[STEP 6] 清理重复文档...")
        self.cleanup_duplicate_docs()
        
        # 整理scripts目录
        print("\n[STEP 7] 整理scripts目录结构...")
        self.organize_scripts()
        
        # 创建清理报告
        print("\n[STEP 8] 创建清理报告...")
        self.create_cleanup_report()
        
        print("\n[SUCCESS] 清理完成！")
        print(f"[INFO] 备份目录: {self.backup_dir}")
        print(f"[INFO] 清理报告: {self.backup_dir}/cleanup_report.md")

def main():
    """主函数"""
    project_root = os.getcwd()
    cleaner = TestFileCleaner(project_root)
    cleaner.run_cleanup()

if __name__ == "__main__":
    main()
