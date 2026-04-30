#!/usr/bin/env python3
"""
一键将 Skill 安装到 Trae 的技能目录
"""
import os
import shutil
from pathlib import Path

def install_skill():
    """自动安装 Skill 到 Trae 目录"""
    
    script_dir = Path(__file__).parent
    
    # 可能的 Trae 技能目录位置
    possible_trae_dirs = [
        script_dir.parent / ".trae" / "skills",
        Path.home() / ".trae" / "skills",
        Path.cwd() / ".trae" / "skills",
    ]
    
    skill_name = "xhs-pm-analyzer"
    
    print("=========================================")
    print("  小红书产品经理技能分析器 - 一键安装")
    print("=========================================")
    print()
    
    # 查找 Trae 技能目录
    trae_skills_dir = None
    for dir_path in possible_trae_dirs:
        if dir_path.exists():
            trae_skills_dir = dir_path
            print(f"✅ 找到 Trae 技能目录: {trae_skills_dir}")
            break
    
    if not trae_skills_dir:
        print("❌ 未找到 Trae 技能目录")
        print()
        print("请手动将以下文件复制到你的 Trae 技能目录:")
        print(f"  源目录: {script_dir}")
        print(f"  目标: .trae/skills/{skill_name}/")
        return False
    
    # 创建目标目录
    target_dir = trae_skills_dir / skill_name
    target_dir.mkdir(exist_ok=True)
    
    # 复制必要文件
    files_to_copy = [
        "SKILL.md",
        "xhs_analyzer_pipeline.py",
        "README.md",
        ".gitignore",
        ".dummy",
        "skills-lock.json"
    ]
    
    print()
    print("📦 正在复制文件...")
    copied_count = 0
    for filename in files_to_copy:
        src = script_dir / filename
        if src.exists():
            shutil.copy2(src, target_dir / filename)
            print(f"  ✅ {filename}")
            copied_count += 1
    
    print()
    print(f"🎉 安装成功！")
    print(f"   已复制 {copied_count} 个文件到: {target_dir}")
    print()
    print("📖 下一步:")
    print("  1. 在 Trae 中刷新技能列表")
    print("  2. 对 AI 说: \"请帮我分析这个小红书产品经理技能笔记\"")
    print()
    
    return True

if __name__ == "__main__":
    install_skill()
