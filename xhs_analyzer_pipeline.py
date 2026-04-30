import sys
import urllib.request
import re
import json
import subprocess
import tempfile
import shutil
import os
from pathlib import Path

# ==========================================
# 内置安全审查规则 (复用之前的低依赖扫描器)
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
# 1. 帖子读取与提取模块 (零外部依赖)
# ==========================================
def fetch_xhs_content(url):
    print(f"🔄 正在尝试读取小红书链接: {url}")
    # 使用基础的 User-Agent 模拟浏览器，避免被直接 403
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    try:
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        
        # 拦截视频判定
        if 'video' in url or '"type":"video"' in html:
            print("❌ 拦截：该链接包含视频内容，MVP版本仅支持图文。")
            return None
            
        # 尝试从 window.__INITIAL_STATE__ 中提取文本
        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});</script>', html)
        text_content = html # 默认 fallback 为整个 html
        if match:
            try:
                state = json.loads(match.group(1))
                # 简化提取逻辑，直接将 state 序列化为字符串进行后续正则匹配
                text_content = json.dumps(state, ensure_ascii=False)
                print("✅ 成功提取小红书底层数据状态。")
            except json.JSONDecodeError:
                pass
        return text_content
    except Exception as e:
        print(f"⚠️ 读取小红书页面失败 (可能触发反爬): {e}")
        print("💡 提示：在实际 Trae 环境中，可直接让 AI 助手通过自带工具或 OCR 提取文本传入。")
        return None

def extract_github_links(text):
    print("🔍 正在从文本中提取 Skill (GitHub) 链接...")
    repos = set()
    # 匹配 https://github.com/foo/bar
    for match in re.findall(r'github\.com/([\w-]+/[\w-]+)', text):
        repos.add(f"https://github.com/{match}")
    # 匹配 npx skills add foo/bar 这种常见的 skill 安装命令
    for match in re.findall(r'npx\s+skills\s+add\s+([\w-]+/[\w-]+)', text):
        repos.add(f"https://github.com/{match}")
        
    return list(repos)

# ==========================================
# 2. 安全克隆与扫描模块 (核心安全护栏)
# ==========================================
def scan_directory(target_dir):
    findings = []
    score = 100
    # 移除 .md 和 .json 等文档配置文件的扫描，避免说明文档中的 curl/wget 被误报为高危操作
    supported_exts = {'.py', '.js', '.ts', '.sh'}
    
    for root, _, files in os.walk(target_dir):
        # 过滤掉 .git 目录、测试目录、示例目录等，减少合理调用的误报
        if any(ignore in root for ignore in ['.git', 'tests', 'test', 'examples', 'docs']):
            continue
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
                except Exception:
                    pass
    return max(0, score), findings

def process_repo(repo_url):
    print(f"\n📦 开始处理仓库: {repo_url}")
    # 强制安全护栏：创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="xhs_skill_")
    
    try:
        # 安全护栏 1: 浅克隆 --depth 1 防止磁盘耗尽
        print("   -> 正在执行安全克隆 (--depth 1)...")
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, temp_dir],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print("   ⚠️ 克隆失败或仓库不存在。")
            return
            
        # 安全护栏 2: 纯文本扫描 (禁止执行)
        print("   -> 正在进行静态代码安全扫描...")
        score, findings = scan_directory(temp_dir)
        
        # 打印简易报告
        risk_level = "🟢 低风险" if score >= 80 else "🟡 中风险" if score >= 60 else "🔴 高风险"
        print(f"   => 扫描得分: {score}/100 ({risk_level})")
        if findings:
            print("   => 发现以下风险点:")
            for f in findings[:3]: # 只显示前 3 个
                print(f"      - {f['file']}:{f['line']} -> {f['risk']}")
            if len(findings) > 3:
                print(f"      - ... 以及其他 {len(findings) - 3} 个风险点。")
        else:
            print("   => 未发现明显的硬编码高危漏洞。")
            
    finally:
        # 安全护栏 3: 强制清理，销毁现场
        print(f"   🧹 扫描结束，强制销毁临时目录: {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)

# ==========================================
# 主流水线
# ==========================================
def main():
    if len(sys.argv) < 2:
        print("用法: python xhs_analyzer_pipeline.py <小红书链接或文本内容>")
        sys.exit(1)
        
    input_data = sys.argv[1]
    
    if input_data.startswith("http"):
        text = fetch_xhs_content(input_data)
        if not text:
            print("未能提取有效内容，流程终止。")
            sys.exit(1)
    else:
        text = input_data # 支持直接传入提取好的文本
        
    repos = extract_github_links(text)
    if not repos:
        print("❌ 在提供的内容中未发现有效的 GitHub Skill 链接。")
        sys.exit(0)
        
    print(f"\n✅ 提取到 {len(repos)} 个潜在的 Skill 仓库:")
    for repo in repos:
        print(f"  - {repo}")
        
    for repo in repos:
        process_repo(repo)

if __name__ == "__main__":
    main()