# 小红书产品经理技能分析器 (Xiaohongshu PM Skill Analyzer)

## 一、项目概述
本项目是一个基于 Web Coding (Trae/Cursor 等大模型 IDE) 的轻量级 Agent Skill。它的核心任务是：接收一个小红书「产品经理必备技能」图文笔记链接，自动提取、进行静态源码安全审计，并最终输出带有极强安全护栏的结构化评估报告和安装建议。

本工具融合了高级的安全审查协议（如 **Skill Vetter** 标准、红旗清单拦截、100/3 法则、纯套壳识别），能够帮助产品经理在探索新工具时避开恶意代码、数据泄露及低质营销工具的坑。

## 二、平台适配说明
- **首选宿主环境**：高度适配 **Trae (国内版 Trae CN)**。
- **推荐模型**：强烈建议在对话框中切换使用 **GLM-5V-Turbo** 或 **Gemini-3.1-Pro-Preview** 模型。这两种模型在中文小红书网页结构解析、图片原生理角能力及复杂的系统静态安全逻辑推理中表现最佳。
- **其他环境**：原则上支持所有遵循标准 Skill Vetter 安全审计协议的 MCP 终端或 Agent 平台，但未做特定 UI 和本地 API 拦截适配的测试。

## 三、核心依赖项与安装配置
为了满足“无复杂依赖”、“高速、低风险”的核心验收标准，本项目在代码安全审查环节**完全零第三方依赖**（仅使用 Python 标准库）。

但在社交媒体（如小红书）的数据获取上，为突破反爬限制，本 Skill 深度整合了 **[Agent Reach](https://github.com/Panniantong/agent-reach)** 作为后备抓取渠道。

- **运行环境**：Python 3.10+
- **核心脚本依赖**：`urllib`, `re`, `json`, `subprocess` (均为 Python 标准库)
- **社交媒体抓取依赖**：Agent Reach 及小红书配置

**配套环境一键配置指令**：
在使用本 Skill 之前，建议您（或让 AI 帮您）执行以下命令，完成 Agent Reach 的初始化，以确保在直连小红书失败时能顺利降级抓取：
```bash
# 1. 安装 Agent Reach
pipx install agent-reach || pip install agent-reach

# 2. 安装小红书支持并配置您的网页版 Cookie (请替换为您自己的 Header String)
agent-reach install --channels=xiaohongshu
agent-reach configure xhs-cookies "您的 Cookie 字符串"
```

## 四、核心功能与特性
- **渐进式数据获取 (Progressive Fetch)**：在读取小红书链接或 GitHub 仓库时，AI 会**首先尝试匿名直连/免授权读取**。只有当遭遇平台反爬（重定向至登录页）或私有权限拦截（404/403）时，才会降级调用 Agent Reach 或询问用户进行 `gh auth login` 授权。
- **防反爬与图文直提**：不使用脆弱的 DOM 解析，直接利用正则提取小红书底层 `__INITIAL_STATE__` 数据。
- **强制视频拦截**：严格判断 URL 或底层特征，一旦发现是视频立即阻断。
- **自动化安全流水线 (`xhs_analyzer_pipeline.py`)**：
  - **安全克隆与阅后即焚**：使用浅克隆拉取源码。无论扫描成功或失败，最后必然触发 `rm -rf` 强制销毁临时源码，杜绝环境污染。
  - **零执行扫描**：仅以纯文本形式静态扫描代码，匹配 30+ 种高危正则特征（RCE, 密钥泄露, 数据外发）。
- **广义产品定义与个性化需求打分**：打破传统“画原型写PRD”的职业刻板印象，将数据分析、前端审美、架构设计等均纳入高分范畴。同时支持接收用户的具体痛点（如“我是数据PM，需要做漏斗”），进行 0-100 分的精准需求匹配度量化打分。
- **用户绝对控制权**：Skill 仅输出分析报告与安装建议（✅ 已适配 / ⚠️ 有风险 / ❌ 不匹配），绝不在未经允许的情况下自动替用户运行安装命令。

## 五、安装方式一：通过压缩包本地安装（强烈推荐！🚀）

如果您已经下载了 `xhs_pm_skill_delivery.zip` 压缩包，这是最快、最稳定的安装方式，无需访问 GitHub！

### 为什么推荐压缩包安装？
- ✅ **速度快** - 无需网络，秒级安装
- ✅ **稳定可靠** - 不依赖 GitHub 访问
- ✅ **离线可用** - 没有网络也能安装使用
- ✅ **体积小** - 仅 39.9 KB

---

### 📦 完整安装步骤

#### macOS/Linux 用户：

1. **解压压缩包**
   ```bash
   unzip xhs_pm_skill_delivery.zip
   ```

2. **进入目录**
   ```bash
   cd xhs_pm_skill_delivery
   ```

3. **运行安装脚本** - 脚本会自动把 Skill 安装到 Trae
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

4. **完成！** 在 Trae 中刷新技能列表即可使用

---

#### Windows 用户：

1. **解压压缩包** - 使用解压工具解压 `xhs_pm_skill_delivery.zip`

2. **运行安装脚本** - 双击 `install.bat`

3. **完成！** 在 Trae 中刷新技能列表即可使用

---

### 🛠️ 手动运行安全扫描

如果需要单独运行安全扫描脚本分析 GitHub 仓库：

- **macOS/Linux**:
  ```bash
  ./run.sh "github.com/user/repo"
  ```

- **Windows**:
  ```cmd
  run.bat "github.com/user/repo"
  ```

---

### 📝 安装脚本包含的功能

- ✅ 自动检测 Python 环境
- ✅ 自动查找 Trae 技能目录
- ✅ 自动复制所有必要文件
- ✅ 无需任何用户输入，全自动安装
- ✅ 提供清晰的使用说明

## 六、安装方式二：在 Trae 中一键安装

我们也提供了一键安装脚本，您只需在 Trae 终端中运行以下命令即可将本 Skill 安装到您的 Trae 工作区中：

```bash
npx skills add Yixiao-Zhang1214/littleredbookskillreader --skill xhs-pm-analyzer -a trae -y
```
*(注：添加了 `-a trae -y` 参数，表示默认仅静默安装到 Trae 平台，跳过其他 Agent 平台的选择提示。)*

### 使用步骤：
1. 安装完成后，在 Trae 的对话框中，唤起本 Skill（或直接发送以下话术触发）。
2. 对 AI 助手说：“请帮我分析这个小红书产品经理技能笔记：[您的链接]”。
3. AI 会自动调用底层的 `xhs_analyzer_pipeline.py` 进行光速审查并输出极具深度的评估报告。



