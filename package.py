#!/usr/bin/env python3
import zipfile
import os
from pathlib import Path

def create_clean_zip():
    """创建干净的发布压缩包，排除不必要的文件"""
    
    script_dir = Path(__file__).parent
    zip_path = script_dir.parent / "xhs_pm_skill_delivery.zip"
    
    # 要包含的文件
    include_files = [
        "README.md",
        "SKILL.md",
        "xhs_analyzer_pipeline.py",
        "install.sh",
        "run.sh",
        "install.bat",
        "run.bat",
        "install_skill_to_trae.py",
        ".gitignore",
        ".dummy",
        "skills-lock.json"
    ]
    
    # 要排除的目录
    exclude_dirs = [".git", "__pycache__", ".pytest_cache"]
    
    print(f"📦 正在创建压缩包: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(script_dir):
            # 移除要排除的目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(script_dir.parent)
                
                # 检查是否在包含列表中，或者是安装/运行脚本
                if str(rel_path.name) in include_files or str(rel_path).startswith("xhs_pm_skill_delivery/"):
                    zipf.write(file_path, rel_path)
                    print(f"  ✅ 添加: {rel_path}")
    
    print(f"\n🎉 压缩包创建成功!")
    print(f"   位置: {zip_path}")
    print(f"   大小: {zip_path.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    create_clean_zip()
