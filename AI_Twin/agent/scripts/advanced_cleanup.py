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
高级项目清理脚本
================

清理不需要的代码和文件，优化项目结构
"""

import os
import shutil
import glob
from pathlib import Path
from datetime import datetime
import json

class AdvancedProjectCleaner:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.cleanup_log = []
        self.backup_dir = self.project_root / "backup" / f"advanced_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
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
        self.log_action("CREATE", str(self.backup_dir), "高级清理备份目录")
    
    def cleanup_sqlite_files(self):
        """清理SQLite相关文件（已切换到PostgreSQL）"""
        print("\n[STEP 1] 清理SQLite相关文件...")
        
        # SQLite数据库文件
        sqlite_files = [
            "data/auth.db",
            "data/chat_history.db", 
            "data/medical_records.db",
            "data/user_profiles.db",
            "data/permissions.db",
            "data/audit.db",
            "data/user_data.db",
            "data/chat_history.db-shm",
            "data/chat_history.db-wal",
            "data/medical_records.db-shm",
            "data/medical_records.db-wal",
        ]
        
        for file_path in sqlite_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                # 移动到备份目录
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "SQLite数据库文件（已切换到PostgreSQL）")
        
        # 医院特定的SQLite数据库
        hospital_dirs = [
            "data/上海",
            "data/北京", 
            "data/测试城市"
        ]
        
        for dir_path in hospital_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                backup_path = self.backup_dir / dir_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "医院SQLite数据库目录")
    
    def cleanup_sqlite_related_code(self):
        """清理SQLite相关代码"""
        print("\n[STEP 2] 清理SQLite相关代码...")
        
        # SQLite相关的数据库管理器
        sqlite_files = [
            "shared/database_manager.py",  # 旧的SQLite管理器
            "backend/utils/database.py",   # 旧的SQLite工具
        ]
        
        for file_path in sqlite_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "SQLite相关代码文件")
    
    def cleanup_duplicate_docs(self):
        """清理重复和过时的文档"""
        print("\n[STEP 3] 清理重复和过时文档...")
        
        # 重复的README文件
        duplicate_readme = [
            "docs/README-new.md",
            "docs/README-前后端分离.md",
        ]
        
        for file_path in duplicate_readme:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "重复的README文件")
        
        # 过时的运行指南
        outdated_guides = [
            "docs/运行说明.md",
            "docs/项目运行总结.md",
            "docs/项目运行成功总结.md",
            "docs/项目运行指南.md",
            "运行指南.md",
        ]
        
        for file_path in outdated_guides:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "过时的运行指南")
    
    def cleanup_analysis_reports(self):
        """清理分析报告目录"""
        print("\n[STEP 4] 清理分析报告...")
        
        analysis_dir = self.project_root / "docs" / "analysis_reports"
        if analysis_dir.exists():
            backup_path = self.backup_dir / "analysis_reports"
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(analysis_dir), str(backup_path))
            self.log_action("MOVE", str(analysis_dir), "分析报告目录")
    
    def cleanup_individual_reports(self):
        """清理根目录的单独报告文件"""
        print("\n[STEP 5] 清理根目录报告文件...")
        
        report_files = [
            "DoctorConsultation用户ID抓取修复报告.md",
            "外科咨询完整测试方案和用例.md",
            "完整智能体调用链分析报告.md",
            "影像分析智能体提示内容优化方案.md",
            "影像分析格式分段问题修复方案.md",
            "数据库操作指南.md",
            "数据库架构和存储总结报告.md",
            "数据库调用接口列表.md",
            "智能体LLM模型调用梳理报告.md",
            "病史智能体分析结果传递验证报告.md",
            "病史智能体检索内容和诊断结果分析.md",
            "病史智能体病历关联分析优化总结.md",
            "病史智能体病历关联分析测试方案.md",
            "第12和13步智能体调用分析报告.md",
        ]
        
        for file_path in report_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "根目录报告文件")
    
    def cleanup_scripts_data(self):
        """清理scripts目录中的测试数据"""
        print("\n[STEP 6] 清理scripts测试数据...")
        
        scripts_data_dir = self.project_root / "scripts" / "data"
        if scripts_data_dir.exists():
            backup_path = self.backup_dir / "scripts_data"
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(scripts_data_dir), str(backup_path))
            self.log_action("MOVE", str(scripts_data_dir), "scripts测试数据目录")
        
        # 清理测试报告
        test_reports_dir = self.project_root / "scripts" / "test_reports"
        if test_reports_dir.exists():
            backup_path = self.backup_dir / "test_reports"
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(test_reports_dir), str(backup_path))
            self.log_action("MOVE", str(test_reports_dir), "测试报告目录")
    
    def cleanup_remaining_test_files(self):
        """清理剩余的测试文件"""
        print("\n[STEP 7] 清理剩余测试文件...")
        
        test_files = [
            "scripts/direct_query_zhang_san.py",
            "scripts/enhance_zhang_san_medical_data.py",
            "scripts/generate_vitals_for_zhang_san.py",
            "scripts/simple_enhance_zhang_san.py",
            "scripts/README_zhang_san_tests.md",
        ]
        
        for file_path in test_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "剩余测试文件")
    
    def cleanup_shared_utilities(self):
        """清理shared目录中的工具文件"""
        print("\n[STEP 8] 清理shared工具文件...")
        
        utility_files = [
            "shared/compare_functionality.py",
            "shared/data_consistency_manager.py",
            "shared/database_auth.py",
            "shared/permission_admin.py",
            "shared/permission_database.py",
        ]
        
        for file_path in utility_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "shared工具文件")
    
    def cleanup_startup_files(self):
        """清理启动相关文件"""
        print("\n[STEP 9] 清理启动文件...")
        
        startup_files = [
            "start_app_postgresql.py",  # 已集成到scripts/startup/
        ]
        
        for file_path in startup_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                backup_path = self.backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(full_path), str(backup_path))
                self.log_action("MOVE", str(full_path), "重复的启动文件")
    
    def organize_docs_structure(self):
        """整理docs目录结构"""
        print("\n[STEP 10] 整理docs目录结构...")
        
        # 创建分类目录
        doc_categories = {
            "architecture": [
                "微服务架构设计方案.md",
                "微服务架构设计.md",
                "系统架构流程图.md",
                "project_architecture_diagram.md",
            ],
            "api": [
                "FastAPI-影像分析服务说明.md",
                "项目接口梳理文档.md",
            ],
            "agents": [
                "医疗智能体微服务细分方案.md",
                "多智能体关系图.md",
                "智能体交互优化总结.md",
                "智能体交互优化说明.md",
                "智能体数据库接口流程图.md",
                "智能体数据库认证修复总结.md",
                "智能体数据库认证机制分析.md",
            ],
            "medical": [
                "多模态医疗大模型使用说明.md",
                "影像分析问题修复总结.md",
                "影像智能体认证授权流程图_最终版.md",
                "影像智能体认证授权流程图_可视化.md",
                "影像智能体认证授权流程图.md",
                "电子病历上传功能实现总结.md",
            ],
            "data": [
                "数据存储和读取检索方式分析.md",
                "MCP数据库操作实现方案.md",
            ],
            "testing": [
                "权限测试指南.md",
                "测试指南.md",
            ],
            "user_management": [
                "用户信息获取问题修复总结.md",
                "用户管理系统使用说明.md",
            ],
            "intent": [
                "意图识别问题修复总结.md",
            ],
            "history": [
                "病史智能体分析结果传递验证报告.md",
                "病史智能体检索内容和诊断结果分析.md",
                "病史智能体病历关联分析优化总结.md",
                "病史智能体病历关联分析测试方案.md",
            ]
        }
        
        docs_dir = self.project_root / "docs"
        
        for category, files in doc_categories.items():
            category_dir = docs_dir / category
            category_dir.mkdir(exist_ok=True)
            
            for file_name in files:
                src_path = docs_dir / file_name
                if src_path.exists():
                    dst_path = category_dir / file_name
                    shutil.move(str(src_path), str(dst_path))
                    self.log_action("ORGANIZE", str(src_path), f"移动到 {category}/")
    
    def create_cleanup_report(self):
        """创建清理报告"""
        report_path = self.backup_dir / "advanced_cleanup_report.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 高级项目清理报告\n\n")
            f.write(f"**清理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**备份目录**: {self.backup_dir}\n\n")
            f.write("## 清理操作记录\n\n")
            
            for log_entry in self.cleanup_log:
                f.write(f"- {log_entry}\n")
            
            f.write("\n## 清理后的项目结构\n\n")
            f.write("```\n")
            f.write("项目根目录/\n")
            f.write("├── backend/                 # 后端服务\n")
            f.write("├── frontend/                # 前端服务\n")
            f.write("├── shared/                  # 共享模块\n")
            f.write("├── config/                  # 配置\n")
            f.write("├── scripts/\n")
            f.write("│   ├── migration/          # 迁移脚本\n")
            f.write("│   ├── startup/             # 启动脚本\n")
            f.write("│   └── utils/               # 工具脚本\n")
            f.write("├── docs/\n")
            f.write("│   ├── architecture/        # 架构文档\n")
            f.write("│   ├── api/                 # API文档\n")
            f.write("│   ├── agents/              # 智能体文档\n")
            f.write("│   ├── medical/             # 医疗相关文档\n")
            f.write("│   └── ...                  # 其他分类文档\n")
            f.write("├── backup/                  # 备份文件\n")
            f.write("└── [核心配置文件]\n")
            f.write("```\n")
        
        self.log_action("CREATE", str(report_path), "高级清理报告")
    
    def run_advanced_cleanup(self):
        """执行高级清理操作"""
        print("[START] 开始高级项目清理...")
        print("=" * 50)
        
        # 创建备份目录
        self.create_backup_dir()
        
        # 执行各项清理
        self.cleanup_sqlite_files()
        self.cleanup_sqlite_related_code()
        self.cleanup_duplicate_docs()
        self.cleanup_analysis_reports()
        self.cleanup_individual_reports()
        self.cleanup_scripts_data()
        self.cleanup_remaining_test_files()
        self.cleanup_shared_utilities()
        self.cleanup_startup_files()
        self.organize_docs_structure()
        
        # 创建清理报告
        print("\n[STEP 11] 创建清理报告...")
        self.create_cleanup_report()
        
        print("\n[SUCCESS] 高级清理完成！")
        print(f"[INFO] 备份目录: {self.backup_dir}")
        print(f"[INFO] 清理报告: {self.backup_dir}/advanced_cleanup_report.md")

def main():
    """主函数"""
    project_root = os.getcwd()
    cleaner = AdvancedProjectCleaner(project_root)
    cleaner.run_advanced_cleanup()

if __name__ == "__main__":
    main()
