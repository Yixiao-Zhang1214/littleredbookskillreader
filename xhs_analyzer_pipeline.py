import sys
import urllib.request
import re
import json
import subprocess
import tempfile
import shutil
import os
import zipfile
import logging
from pathlib import Path

# ==========================================
# 日志配置
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("xhs_analyzer")

# ==========================================
# 内置安全审查规则
# ==========================================
SECURITY_RULES = {
    "RCE_RISK": {
        "pattern": r"(?i)(os\.system|subprocess\.|eval\(|exec\(|rm\s+-rf|wget\s+|curl\s+)",
        "desc": "潜在的远程代码执行 (RCE) 或危险系统命令调用",
        "penalty": 30
    },
    "DATA_EXFILTRATION": {
        "pattern": r"(?i)(requests\.post|urllib\.request|http\.client|fetch\(.*\)|axios\.)",
        "desc": "存在向外部发送数据的网络请求，可能导致敏感信息泄露",
        "penalty": 25
    },
    "XSS_RISK": {
        "pattern": r"(?i)(innerHTML|document\.write\(|v-html|dangerouslySetInnerHTML)",
        "desc": "潜在的跨站脚本 (XSS) 攻击漏洞",
        "penalty": 15
    },
    "SECRETS_LEAK": {
        "pattern": r"(?i)(api[_-]?key|secret[_-]?key|password|token)\s*[:=]\s*['\"][A-Za-z0-9\-_]{16,}['\"]",
        "desc": "硬编码的敏感凭证泄露",
        "penalty": 40
    }
}

# ==========================================
# 工具函数
# ==========================================
def extract_github_links(text):
    """从文本中提取 GitHub 链接，统一接口格式"""
    logger.info("🔍 正在从输入文本中提取 GitHub 链接...")
    repos = set()
    for match in re.findall(r'github\.com/([\w.-]+/[\w.-]+)', text):
        repos.add(f"https://github.com/{match.strip('/')}")
    for match in re.findall(r'npx\s+skills\s+add\s+([\w.-]+/[\w.-]+)', text):
        repos.add(f"https://github.com/{match.strip('/')}")
    return list(repos)

def clone_with_fallback(repo_url, target_dir):
    """渐进式获取源码：1. ZIP (免授权) -> 2. Git Clone (依赖环境授权)"""
    parts = [p for p in repo_url.split('/') if p]
    if len(parts) < 2:
        logger.error(f"无效的 GitHub 链接格式: {repo_url}")
        return False
        
    owner, repo = parts[-2], parts[-1]
    
    # 策略 1: 尝试匿名 ZIP 下载
    logger.info(f"策略 1: 尝试免授权 ZIP 下载 ({owner}/{repo})...")
    branches = ['main', 'master']
    for branch in branches:
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
        try:
            req = urllib.request.Request(zip_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
                    tmp_zip.write(response.read())
                    tmp_zip_path = tmp_zip.name
            
            with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            os.remove(tmp_zip_path)
            logger.info(f"✅ ZIP 下载成功 (分支: {branch})")
            return True
        except urllib.error.HTTPError as e:
            if e.code != 404:
                logger.warning(f"ZIP 下载 HTTP 异常: {e.code}")
        except Exception as e:
            logger.warning(f"ZIP 下载异常: {e}")

    # 策略 2: 降级使用 Git Clone
    logger.info("策略 2: ZIP 获取失败，降级尝试 Git Clone (需本地授权)...")
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, target_dir],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            logger.info("✅ Git Clone 成功")
            return True
        else:
            logger.error(f"Git Clone 失败: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        logger.error("Git Clone 超时")
    except FileNotFoundError:
        logger.error("未找到 Git 命令，无法克隆")

    return False

# ==========================================
# 核心扫描引擎
# ==========================================
def scan_directory(target_dir):
    """纯文本静态扫描，绝不执行任何代码"""
    findings = []
    score = 100
    supported_exts = {'.py', '.js', '.ts', '.sh'}
    ignore_dirs = {'.git', 'tests', 'test', 'examples', 'docs', 'node_modules'}
    
    for root, dirs, files in os.walk(target_dir):
        # 原地修改 dirs 以跳过忽略的目录
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in supported_exts:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    for line_num, line in enumerate(lines, 1):
                        for rule_id, rule in SECURITY_RULES.items():
                            if re.search(rule["pattern"], line):
                                findings.append({
                                    "file": str(file_path.relative_to(target_dir)),
                                    "line": line_num,
                                    "risk": rule["desc"]
                                })
                                score -= rule["penalty"]
                except Exception as e:
                    logger.debug(f"跳过无法读取的文件 {file_path}: {e}")
                    
    return max(0, score), findings

def process_repo(repo_url):
    """端到端处理单个仓库：拉取 -> 扫描 -> 销毁"""
    print(f"\n" + "="*50)
    logger.info(f"📦 开始处理仓库: {repo_url}")
    temp_dir = tempfile.mkdtemp(prefix="xhs_skill_")
    
    try:
        success = clone_with_fallback(repo_url, temp_dir)
        if not success:
            print("   ⚠️ 获取源码失败，无法进行自动化扫描。请降级为纯文本人工浅层评估。")
            return
            
        logger.info("进行静态代码安全扫描...")
        score, findings = scan_directory(temp_dir)
        
        risk_level = "🟢 低风险" if score >= 80 else "🟡 中风险" if score >= 60 else "🔴 高风险"
        print(f"   => 最终安全得分: {score}/100 ({risk_level})")
        
        if findings:
            print("   => 发现以下风险点:")
            for f in findings[:5]: # 最多展示 5 个
                print(f"      - {f['file']}:{f['line']} -> {f['risk']}")
            if len(findings) > 5:
                print(f"      - ... 以及其他 {len(findings) - 5} 个风险点。")
        else:
            print("   => 扫描通过：未发现明显的硬编码高危漏洞。")
            
    finally:
        logger.info(f"🧹 强制清理临时目录: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)

# ==========================================
# 主入口
# ==========================================
def main():
    if len(sys.argv) < 2:
        print("用法: python xhs_analyzer_pipeline.py \"包含 GitHub 链接的文本\"")
        sys.exit(1)
        
    input_text = sys.argv[1]
    repos = extract_github_links(input_text)
    
    if not repos:
        logger.warning("❌ 在输入中未发现有效的 GitHub 链接。")
        sys.exit(0)
        
    logger.info(f"✅ 提取到 {len(repos)} 个仓库链接待扫描")
    for repo in repos:
        process_repo(repo)

if __name__ == "__main__":
    main()