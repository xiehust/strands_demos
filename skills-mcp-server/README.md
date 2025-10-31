# Skills MCP 服务器

一个基于模型上下文协议（MCP）的服务器，通过标准化的工具和资源提供对 Strands 技能的访问。

## 概述

此 MCP 服务器从目录结构中暴露技能，允许 AI 代理：
- 发现带有元数据的可用技能
- 调用技能以加载其指令
- 读取技能文件和支持文档
- 列出技能目录中的文件

## 🚀 快速开始

- **快速启动 MCP 服务器**
运行以下代码，您将在本地启动一个 HTTP MCP 服务器
```bash
uv run src/server.py
```

**快速示例：**
进入文件 [agent_with_mcp.py](../strands_skills_demo/agent_with_mcp.py) 所在的文件夹。
- 安装环境：

```bash
uv sync
uv pip install git+https://github.com/xiehust/sdk-python.git@c257c9238b1fa81b12b598855b0b1ae3e95a6e11
```

- 运行以下代码。
```bash
python main.py --prompt "research about Claude Code Agent Skills (https://docs.claude.com/en/docs/claude-code/skills), and create a ppt in Chinese to introduce it, save it as pptx file in working directory."
```


## 功能特性

### 工具

#### 1. **invoke_skill**
按名称加载并激活技能。返回完整的技能内容和指令，类似于 Strands Skill 工具。

```python
invoke_skill(skill_name="pdf")
```

**参数：**
- `skill_name` (str): 要调用的技能文件夹名称

**返回：** 包含元数据和指令的完整技能内容

---

#### 2. **read_skill_file**
从技能目录中读取任何文件。提供对示例、文档和参考资料等支持文件的访问。

```python
read_skill_file(skill_name="pdf", file_path="reference.md")
```

**参数：**
- `skill_name` (str): 技能文件夹名称
- `file_path` (str): 技能目录中文件的相对路径

**返回：** 请求文件的内容

**安全性：** 防止目录遍历攻击 - 只能访问技能目录内的文件。

---

#### 3. **list_skill_files**
列出技能文件夹或子文件夹中的所有文件和目录。

```python
list_skill_files(skill_name="pdf", subdirectory="examples")
```

**参数：**
- `skill_name` (str): 技能文件夹名称
- `subdirectory` (str, 可选): 技能内的子目录路径（默认：根目录）

**返回：** 带有大小的格式化文件和目录列表

---

### 资源

#### 1. **skills://list**
返回所有可用技能及其元数据的格式化列表。

**包含：**
- 技能名称
- 描述
- 文件夹名称
- 许可证信息（如果有）

---

#### 2. **skills://{skill_name}**
获取特定技能的完整内容。

**示例：** `skills://pdf`

**返回：** 包含元数据、基础目录和完整指令的完整技能

---



## 运行服务器

### 独立模式（HTTP）

```bash
uv run src/server.py
```

服务器将以 HTTP 模式启动，并通过标准输入/输出进行通信。

---


**重要提示：** 对于服务器脚本和技能目录都使用绝对路径。

---

### 与其他 MCP 客户端配合使用

服务器默认使用可流式 HTTP 传输，与任何支持模型上下文协议的 MCP 客户端兼容。

使用 MCP Python 客户端的示例：

```python
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("http://localhost:8000/mcp") as (read, write,_):
    async with ClientSession(read, write) as session:
        # 使用会话
        await session.initialize()

        # 调用工具
        result = await session.call_tool("invoke_skill", {"skill_name": "pdf"})
        print(result)
```

---

## 技能目录结构

技能必须遵循以下结构：

```
skills/
├── skill-name/
│   ├── SKILL.md          # 必需：带有前置元数据的主技能文件
│   ├── reference.md      # 可选：附加文档
│   ├── examples/         # 可选：示例文件
│   ├── forms.md          # 可选：特定指南
│   └── ...               # 其他支持文件
```

### SKILL.md 格式

每个 `SKILL.md` 文件必须有 YAML 前置元数据：

```markdown
---
name: skill-name
description: 技能功能的简要描述
license: 可选的许可证信息
---

# 技能内容

技能的详细指令和文档...

## 快速开始

示例和使用说明...
```

**必需字段：**
- `name`: 技能的显示名称
- `description`: 技能用途的简要描述

**可选字段：**
- `license`: 许可证信息

---

## 使用示例

### 使用资源

```python
# 列出所有可用技能
skills_list = await session.read_resource("skills://list")
print(skills_list[0].text)

# 获取特定技能的内容
pdf_skill = await session.read_resource("skills://pdf")
print(pdf_skill[0].text)
```

### 使用工具

```python
# 调用技能
result = await session.call_tool("invoke_skill", {
    "skill_name": "pdf"
})

# 读取支持文件
reference = await session.call_tool("read_skill_file", {
    "skill_name": "pdf",
    "file_path": "reference.md"
})

# 列出技能目录中的文件
files = await session.call_tool("list_skill_files", {
    "skill_name": "pdf",
    "subdirectory": ""
})

# 从子目录读取文件
example = await session.call_tool("read_skill_file", {
    "skill_name": "pdf",
    "file_path": "examples/create_invoice.py"
})
```

---

## 安全性

服务器实现了多种安全措施：

- **目录遍历防护**：文件路径经过解析和验证，确保它们保持在技能目录内
- **路径清理**：所有文件路径都会针对基础技能目录进行检查
- **只读访问**：服务器仅提供对技能文件的读取访问
- **范围限制**：只能访问配置的技能目录中的文件

---

## 开发

### 项目结构

```
skills-mcp-server/
├── src/
│   └── server.py         # 主 MCP 服务器实现
├── tests/                # 测试文件（待添加）
├── .env.example          # 示例环境配置
├── .gitignore            # Git 忽略模式
├── pyproject.toml        # 项目配置和依赖项
└── README.md             # 本文件
```

## 故障排除

### 未找到技能

**问题：** 服务器报告"未找到技能"或技能未找到错误。

**解决方案：**
- 验证 `SKILLS_DIR` 环境变量指向正确的目录
- 确保技能目录包含有效的 `SKILL.md` 文件
- 检查 `SKILL.md` 文件是否具有正确的 YAML 前置元数据
- 验证文件权限允许读取

**调试：**
```bash
export SKILLS_DIR=/path/to/skills
python src/server.py
# 检查日志以查看正在扫描的目录
```

---

### 服务器无法启动

**问题：** 服务器启动失败或立即崩溃。

**解决方案：**
- 验证 Python 版本 >= 3.10: `python --version`
- 确保安装了所有依赖项: `pip list | grep mcp`
- 检查 `server.py` 中的语法错误
- 查看日志中的错误消息

---

### 无效的技能格式

**问题：** 初始化期间跳过技能。

**解决方案：** 确保 `SKILL.md` 具有正确的前置元数据：
```markdown
---
name: my-skill
description: 我的技能描述
---

内容在这里...
```

---

### 文件访问被拒绝

**问题：** 无法读取技能文件。

**解决方案：**
- 确保文件路径相对于技能目录
- 检查文件权限
- 验证文件是否存在：首先使用 `list_skill_files`
- 不要使用绝对路径或尝试逃逸技能目录

---

## 日志记录

服务器记录关键事件以帮助调试：

- 技能扫描和初始化
- 工具调用
- 文件读取操作
- 错误和警告

日志使用 Python 的标准日志模块，默认为 INFO 级别。

更改日志级别：
```python
# 在 server.py 中
logging.basicConfig(level=logging.DEBUG)  # 更详细
```

---

## 参考资料

- [模型上下文协议文档](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Strands Agent 文档](https://strands.dev)
- [FastMCP 文档](https://github.com/modelcontextprotocol/python-sdk#fastmcp)

---

## 更新日志

### v0.1.0 (2025-10-31)
- 初始版本发布
- 基本技能调用工具
- 文件读取功能
- 用于技能发现的资源端点
- 安全功能（目录遍历防护）
