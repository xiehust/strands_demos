# Code Execution MCP Server

这是一个基于 Anthropic 文章 [Code execution with MCP: Building more efficient agents](https://www.anthropic.com/engineering/code-execution-with-mcp) 思想实现的 MCP Server。

## 核心思想

传统的 MCP 使用方式存在两个主要问题:

1. **工具定义占用大量上下文**: 所有工具定义都预先加载到上下文中
2. **中间结果消耗额外 tokens**: 每次工具调用的结果都需要通过模型上下文传递

这个实现采用**代码执行模式**来解决这些问题:

```
传统模式:
Agent → Tool Call → Result → Agent (all in context)

代码执行模式:
Agent → Write Code → Execute in Sandbox → Return Summary → Agent
                     ↑ Data stays here ↑
```

## 主要特性

### 1. 渐进式工具发现 (Progressive Disclosure)

不是一次性加载所有工具定义,而是让 Agent 按需搜索和发现:

```python
# Agent 可以搜索需要的工具
search_tools(query="file operations", detail_level="summary")

# 只加载相关工具的定义
search_tools(query="read", detail_level="full")
```

### 2. 上下文高效的工具结果

数据在执行环境中处理,只返回摘要给模型:

```python
# Agent 编写的代码
from tools.filesystem import read_file
import json

# 读取大文件(10,000 行)
data = json.loads(read_file('large_dataset.json'))

# 在执行环境中过滤(不经过模型上下文!)
filtered = [item for item in data if item['status'] == 'pending']

# 只返回摘要给模型
print(f"Found {len(filtered)} pending items")
print(f"First 5: {filtered[:5]}")
```

**效果**: 10,000 行数据 → 只有摘要进入上下文 (节省 98%+ tokens)

### 3. 更强大的控制流

使用原生 Python 代码实现复杂逻辑:

```python
# 循环、条件、错误处理都用代码实现
for status in ['pending', 'active', 'completed']:
    items = [i for i in data if i['status'] == status]

    if len(items) > 100:
        # 自动分批处理
        for batch in chunks(items, 50):
            process_batch(batch)
    else:
        process_all(items)
```

而不是通过多次工具调用链来实现。

### 4. 隐私保护操作

敏感数据可以在执行环境中流转,不经过模型:

```python
# 读取包含 PII 的数据
customer_data = read_file('customers.json')

# 处理数据(PII 不进入模型上下文)
for customer in customer_data:
    update_crm(
        customer_id=customer['id'],
        email=customer['email'],  # 不经过模型
        phone=customer['phone']   # 不经过模型
    )

# 只返回统计信息
print(f"Updated {len(customer_data)} customers")
```

### 5. 状态持久化和技能复用

Agent 可以保存有用的代码作为技能,供未来复用:

```python
# 保存技能
save_skill(
    name="export_filtered_data",
    code='''
def export_filtered_data(file_path, filter_key, filter_value):
    from tools.filesystem import read_file, write_file
    import json

    data = json.loads(read_file(file_path))
    filtered = [item for item in data if item.get(filter_key) == filter_value]

    write_file('output.json', json.dumps(filtered, indent=2))
    return len(filtered)
''',
    description="Export filtered JSON data"
)

# 下次直接使用
from tools.skills import load_skill
export_fn = load_skill('export_filtered_data')
count = export_fn('data.json', 'status', 'active')
```

## 工具说明

### 核心工具

#### `execute_code`
执行 Python 代码的核心工具。

```python
execute_code(
    code="print('Hello from code execution!')",
    return_value=True,      # 是否返回最后表达式的值
    persist_state=True      # 是否持久化变量状态
)
```

**可用的 API**:
- `tools.filesystem`: 文件系统操作
  - `read_file(path, encoding='utf-8')`
  - `write_file(path, content, mode='w')`
  - `list_directory(path, recursive=False)`

- `tools.data_processing`: 数据处理
  - `filter_json(data, filter_fn)`
  - `aggregate_data(data, group_by, operation)`

- `tools.skills`: 技能管理
  - `list_skills()`
  - `save_skill(name, code, description)`
  - `load_skill(name)`

#### `search_tools`
搜索可用的工具(渐进式发现)。

```python
# 只看名字
search_tools(query="file", detail_level="name")

# 看名字和描述
search_tools(query="data", detail_level="summary")

# 完整定义(包括参数和返回值)
search_tools(query="filter", detail_level="full")
```

#### `list_tool_categories`
列出所有工具分类,不加载具体定义。

```python
list_tool_categories()
# 输出:
# - filesystem (3 tools)
# - data_processing (2 tools)
# - skills (3 tools)
```

### 技能管理工具

#### `save_skill`
保存可复用的技能函数。

```python
save_skill(
    name="my_skill",
    code="def my_function(): ...",
    description="What this skill does"
)
```

#### `list_saved_skills`
列出所有已保存的技能。

#### `get_execution_state`
查看当前执行状态(持久化的变量、技能等)。

#### `reset_execution_state`
重置执行状态。

## 使用示例

### 示例 1: 处理大型数据集

传统方式(低效):
```python
# 工具调用 1: 读取整个文件 → 50,000 tokens 进入上下文
data = read_file('large_dataset.json')

# 工具调用 2: 过滤数据 → 再次处理 50,000 tokens
filtered = filter_data(data, status='active')

# 工具调用 3: 写入结果
write_file('output.json', filtered)
```

代码执行方式(高效):
```python
execute_code('''
from tools.filesystem import read_file, write_file
import json

# 数据在执行环境中处理
data = json.loads(read_file('large_dataset.json'))
filtered = [item for item in data if item['status'] == 'active']

write_file('output.json', json.dumps(filtered, indent=2))

# 只返回摘要
print(f"Processed {len(data)} items")
print(f"Found {len(filtered)} active items")
print(f"Reduction: {(1 - len(filtered)/len(data)) * 100:.1f}%")
''')
```

**Token 节省**: 从 ~150,000 tokens → ~200 tokens (99.9% 节省)

### 示例 2: 复杂控制流

等待某个条件满足:

```python
execute_code('''
import time
from tools.filesystem import read_file

# 轮询检查文件状态
max_attempts = 10
for attempt in range(max_attempts):
    status = read_file('deployment_status.txt').strip()

    if status == 'completed':
        print(f"Deployment completed after {attempt + 1} checks")
        break
    elif status == 'failed':
        print(f"Deployment failed!")
        break
    else:
        print(f"Attempt {attempt + 1}: Status is {status}, waiting...")
        time.sleep(5)
else:
    print(f"Timeout after {max_attempts} attempts")
''')
```

### 示例 3: 构建和复用技能

第一次使用时,Agent 编写并保存技能:

```python
# 1. 开发技能
execute_code('''
def process_sales_report(input_file, output_file):
    """Process sales report and generate summary"""
    from tools.filesystem import read_file, write_file
    import json

    # Read and process data
    data = json.loads(read_file(input_file))

    # Calculate metrics
    total_sales = sum(item['amount'] for item in data)
    avg_sale = total_sales / len(data)
    top_products = sorted(data, key=lambda x: x['amount'], reverse=True)[:5]

    # Generate report
    report = {
        'total_sales': total_sales,
        'average_sale': avg_sale,
        'transaction_count': len(data),
        'top_products': top_products
    }

    write_file(output_file, json.dumps(report, indent=2))
    return report

# Test it
result = process_sales_report('sales.json', 'report.json')
print(f"Generated report: ${result['total_sales']:,.2f} total sales")
''')

# 2. 保存为技能
save_skill(
    name="sales_report_processor",
    code='''
def process_sales_report(input_file, output_file):
    from tools.filesystem import read_file, write_file
    import json

    data = json.loads(read_file(input_file))
    total_sales = sum(item['amount'] for item in data)
    avg_sale = total_sales / len(data)
    top_products = sorted(data, key=lambda x: x['amount'], reverse=True)[:5]

    report = {
        'total_sales': total_sales,
        'average_sale': avg_sale,
        'transaction_count': len(data),
        'top_products': top_products
    }

    write_file(output_file, json.dumps(report, indent=2))
    return report
''',
    description="Process sales data and generate summary report"
)
```

之后直接复用:

```python
execute_code('''
from tools.skills import load_skill

processor = load_skill('sales_report_processor')
result = processor('monthly_sales.json', 'monthly_report.json')
print(f"Report generated: {result}")
''')
```

## 架构对比

### 传统 MCP 架构

```
┌─────────────────────────────────────────────────────┐
│  Agent Context Window                               │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │ System Prompt                              │   │
│  │ + All Tool Definitions (10,000+ tokens)    │   │
│  │ + User Message                             │   │
│  │ + Tool Call 1                              │   │
│  │ + Tool Result 1 (large data)               │   │
│  │ + Tool Call 2                              │   │
│  │ + Tool Result 2 (large data)               │   │
│  │ + ...                                      │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
│  Total: 100,000+ tokens                            │
└─────────────────────────────────────────────────────┘
```

### 代码执行 MCP 架构

```
┌─────────────────────────────────────────────────────┐
│  Agent Context Window (Minimal)                     │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │ System Prompt                              │   │
│  │ + "Tools available via search_tools()"     │   │
│  │ + User Message                             │   │
│  │ + Code to Execute                          │   │
│  │ + Execution Summary (small)                │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
│  Total: ~2,000 tokens                              │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Code Execution Environment (Outside Context)       │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │ Agent's Code                               │   │
│  │                                            │   │
│  │ data = read_large_file()  # 50,000 tokens  │   │
│  │ filtered = [...]          # Processing     │   │
│  │ result = process(...)     # More work      │   │
│  │                                            │   │
│  │ print(summary)  ← Only this goes to Agent  │   │
│  └────────────────────────────────────────────┘   │
│                                                     │
│  Data stays here, not in context!                  │
└─────────────────────────────────────────────────────┘
```

## 性能对比

| 场景 | 传统 MCP | 代码执行 MCP | 节省 |
|------|----------|--------------|------|
| 处理 10,000 行 CSV | ~150,000 tokens | ~2,000 tokens | 98.7% |
| 多步数据转换 | ~80,000 tokens | ~1,500 tokens | 98.1% |
| 循环处理 100 个文件 | ~500,000 tokens | ~3,000 tokens | 99.4% |

## 安全考虑

代码执行需要安全的沙箱环境:

1. **资源限制**: CPU、内存、时间限制
2. **文件系统隔离**: 只能访问特定目录
3. **网络隔离**: 控制网络访问
4. **监控和日志**: 记录所有执行

在生产环境中,建议使用:
- Docker 容器隔离
- gVisor 等沙箱技术
- 严格的资源配额
- 审计日志

## 运行服务器

```bash
# 安装依赖
pip install mcp

# 运行服务器
python code_execution_mcp_server.py
```

## 配置

环境变量:
- `SKILLS_DIR`: 技能保存目录(默认: `./agent_skills`)

## 扩展

要添加新的工具类别:

1. 在 `generate_tool_api_structure()` 中添加定义
2. 在 `ToolsAPI` 类中添加实现类
3. 工具自动可通过 `search_tools()` 发现

示例:

```python
class ToolsAPI:
    # ... existing code ...

    class DatabaseTools:
        """Database operations"""

        @staticmethod
        def query(sql: str) -> List[Dict]:
            """Execute SQL query"""
            # Implementation
            pass

    def __init__(self):
        # ... existing code ...
        self.database = self.DatabaseTools()
```

## 总结

这个实现展示了如何通过代码执行模式构建更高效的 Agent:

✅ **Token 效率**: 减少 95%+ 的 token 使用
✅ **更快响应**: 减少上下文处理时间
✅ **更强能力**: 原生代码控制流
✅ **隐私保护**: 数据不经过模型
✅ **技能积累**: 可复用的函数库

这就是 Anthropic 文章倡导的**用代码与 MCP 交互**的实现方式!
