# 代码执行 MCP Server - 项目索引

## 📚 文档导航

### 🚀 开始使用
- **[QUICKSTART.md](QUICKSTART.md)** - 快速开始指南
  - 安装和配置
  - 基本使用示例
  - 常见问题解决

### 📖 核心文档
- **[README.md](README.md)** - 项目概述和核心思想
  - Anthropic 文章核心理念
  - 主要特性说明
  - 使用示例和场景

### 🏗️ 架构设计
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 详细架构设计
  - 组件架构图
  - 数据流分析
  - 性能指标
  - 安全设计

### 📊 对比分析
- **[COMPARISON.md](COMPARISON.md)** - 传统 vs 代码执行模式对比
  - 详细场景对比
  - 性能数据对比
  - 适用场景分析
  - 迁移建议

## 🔧 代码文件

### 核心服务器
- **[code_execution_mcp_server.py](code_execution_mcp_server.py)** - MCP 服务器实现
  - 工具发现 API
  - 代码执行引擎
  - 工具 API 层
  - 技能管理系统

### 示例代码
- **[example_usage.py](example_usage.py)** - 使用示例演示
  - 6 个详细示例场景
  - 对比演示
  - 最佳实践展示

### 配置文件
- **[requirements.txt](requirements.txt)** - Python 依赖

## 📂 目录结构

```
code-mcp/
├── README.md                          # 项目概述
├── QUICKSTART.md                      # 快速开始
├── ARCHITECTURE.md                    # 架构设计
├── COMPARISON.md                      # 对比分析
├── INDEX.md                           # 本文档
├── requirements.txt                   # 依赖配置
├── code_execution_mcp_server.py      # 服务器实现
├── example_usage.py                   # 使用示例
└── agent_skills/                      # 技能保存目录(运行时创建)
    ├── skill1.py
    ├── skill2.py
    └── ...
```

## 🎯 阅读路径建议

### 快速了解(15 分钟)
1. [README.md](README.md) - 了解核心思想
2. [example_usage.py](example_usage.py) - 运行示例看效果
3. [QUICKSTART.md](QUICKSTART.md) - 动手试用

### 深入理解(1 小时)
1. [README.md](README.md) - 核心理念
2. [COMPARISON.md](COMPARISON.md) - 对比分析
3. [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计
4. [code_execution_mcp_server.py](code_execution_mcp_server.py) - 代码实现

### 实战应用(按需)
1. [QUICKSTART.md](QUICKSTART.md) - 配置和启动
2. [example_usage.py](example_usage.py) - 参考示例
3. [code_execution_mcp_server.py](code_execution_mcp_server.py) - 根据需求修改

## 🌟 核心特性快速查找

### 渐进式工具发现
- 代码: `code_execution_mcp_server.py:136-162` (search_tools)
- 文档: [README.md#渐进式工具发现](README.md)
- 示例: [example_usage.py:12-70](example_usage.py) (Example 1)

### 代码执行引擎
- 代码: `code_execution_mcp_server.py:243-315` (execute_code)
- 文档: [ARCHITECTURE.md#代码执行层](ARCHITECTURE.md)
- 示例: [example_usage.py:73-145](example_usage.py) (Example 2)

### 工具 API
- 代码: `code_execution_mcp_server.py:318-430` (ToolsAPI)
- 文档: [README.md#工具说明](README.md)
- 示例: 所有 example_usage.py 中的示例

### 技能管理
- 代码: `code_execution_mcp_server.py:433-503` (save_skill, list_saved_skills)
- 文档: [README.md#状态持久化和技能复用](README.md)
- 示例: [example_usage.py:285-370](example_usage.py) (Example 5)

## 💡 常见使用场景快速查找

| 场景 | 示例位置 | 对比数据 |
|------|---------|---------|
| 数据处理流水线 | [example_usage.py:73](example_usage.py) | [COMPARISON.md#场景2](COMPARISON.md) |
| 批量文件处理 | [QUICKSTART.md#场景2](QUICKSTART.md) | [COMPARISON.md#场景4](COMPARISON.md) |
| 轮询等待 | [example_usage.py:148](example_usage.py) | [COMPARISON.md#场景3](COMPARISON.md) |
| 隐私保护 | [example_usage.py:222](example_usage.py) | [README.md#隐私保护操作](README.md) |
| 技能构建 | [example_usage.py:285](example_usage.py) | [QUICKSTART.md#场景4](QUICKSTART.md) |

## 📈 性能数据快速查找

### Token 节省
- **多步处理**: 98.7% 节省 - [COMPARISON.md#场景2](COMPARISON.md)
- **批量操作**: 99.5% 节省 - [COMPARISON.md#场景4](COMPARISON.md)
- **复杂流水线**: 98.2% 节省 - [COMPARISON.md#场景5](COMPARISON.md)

### 时间节省
- **多步处理**: 66.7% 节省 - [COMPARISON.md#场景2](COMPARISON.md)
- **批量操作**: 98.5% 节省 - [COMPARISON.md#场景4](COMPARISON.md)
- **复杂流水线**: 78.6% 节省 - [COMPARISON.md#场景5](COMPARISON.md)

### 成本节省
- **月度运营**: 97.5% 节省 ($2,400 → $60) - [ARCHITECTURE.md#成本对比](ARCHITECTURE.md)

## 🔍 技术细节快速查找

### 工具发现机制
- 实现: [code_execution_mcp_server.py:27-125](code_execution_mcp_server.py)
- 原理: [ARCHITECTURE.md#工具发现层](ARCHITECTURE.md)

### 执行环境
- 实现: [code_execution_mcp_server.py:243-315](code_execution_mcp_server.py)
- 原理: [ARCHITECTURE.md#代码执行层](ARCHITECTURE.md)

### 安全机制
- 原理: [ARCHITECTURE.md#安全架构](ARCHITECTURE.md)
- 配置: [QUICKSTART.md#安全限制](QUICKSTART.md)

### 扩展性
- 添加工具: [ARCHITECTURE.md#添加新工具类别](ARCHITECTURE.md)
- 集成服务: [ARCHITECTURE.md#集成外部服务](ARCHITECTURE.md)

## 📝 文档大小参考

| 文件 | 大小 | 预计阅读时间 |
|------|------|-------------|
| QUICKSTART.md | 7.9 KB | 10 分钟 |
| README.md | 15 KB | 20 分钟 |
| ARCHITECTURE.md | 32 KB | 40 分钟 |
| COMPARISON.md | 9.5 KB | 15 分钟 |
| code_execution_mcp_server.py | 22 KB | 30 分钟 |
| example_usage.py | 14 KB | 15 分钟 |
| **总计** | **~100 KB** | **~2 小时** |

## 🎓 学习路径

### 初学者 (1 天)
```
上午:
1. 阅读 README.md 了解概念
2. 运行 example_usage.py 看效果
3. 阅读 QUICKSTART.md 并动手试用

下午:
4. 尝试修改示例代码
5. 创建自己的第一个技能
6. 阅读 COMPARISON.md 理解优势
```

### 中级用户 (3 天)
```
第1天: 基础掌握(同初学者)

第2天: 深入理解
1. 研读 ARCHITECTURE.md
2. 分析 code_execution_mcp_server.py 源码
3. 理解各组件交互

第3天: 实战应用
1. 集成到自己的项目
2. 添加自定义工具类别
3. 构建技能库
```

### 高级用户 (1 周)
```
第1-3天: 掌握所有内容(同中级用户)

第4-5天: 定制开发
1. 根据需求修改源码
2. 添加新功能
3. 性能优化

第6-7天: 生产部署
1. Docker 容器化
2. 安全加固
3. 监控和日志
```

## 🔗 相关资源

### Anthropic 官方
- [Code execution with MCP 原文](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP SDK](https://modelcontextprotocol.io/docs/sdk)

### 社区资源
- [MCP Servers 仓库](https://github.com/modelcontextprotocol/servers)
- [MCP 社区](https://modelcontextprotocol.io/community/communication)

## 🤝 贡献

欢迎贡献代码、文档或建议! 请遵循以下步骤:

1. Fork 项目
2. 创建特性分支
3. 提交修改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目为教育和演示目的创建,遵循 MIT 许可证。

## ✨ 致谢

本项目基于 Anthropic 的文章 [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) 的思想实现。

---

**最后更新**: 2025-11-14
**版本**: 1.0.0
