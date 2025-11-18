# 快速开始指南

## 安装

```bash
# 1. 克隆或下载代码
cd /path/to/code-mcp

# 2. 安装依赖
pip install -r requirements.txt
```

## 运行服务器

```bash
# 启动 MCP 服务器
python code_execution_mcp_server.py
```

## 查看示例

```bash
# 运行使用示例(无需启动服务器)
python example_usage.py
```

## 与 Claude Desktop 集成

在 Claude Desktop 的配置文件中添加:

### macOS
编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-execution": {
      "command": "python",
      "args": ["/path/to/code-mcp/code_execution_mcp_server.py"]
    }
  }
}
```

### Windows
编辑 `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-execution": {
      "command": "python",
      "args": ["C:\\path\\to\\code-mcp\\code_execution_mcp_server.py"]
    }
  }
}
```

### Linux
编辑 `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "code-execution": {
      "command": "python",
      "args": ["/path/to/code-mcp/code_execution_mcp_server.py"]
    }
  }
}
```

## 基本使用

启动 Claude Desktop 后,你可以这样使用:

### 1. 发现工具

```
User: 列出可用的工具类别

Claude 会调用: list_tool_categories()
```

### 2. 搜索特定工具

```
User: 搜索文件操作相关的工具

Claude 会调用: search_tools(query="file", detail_level="summary")
```

### 3. 执行代码

```
User: 读取 data.json 文件,过滤出 status=active 的项,
      然后统计每个类别的数量

Claude 会调用: execute_code(code='''
from tools.filesystem import read_file, write_file
from tools.data_processing import aggregate_data
import json

# 读取数据
data = json.loads(read_file('data.json'))

# 过滤
active = [item for item in data if item['status'] == 'active']

# 聚合
result = {}
for item in active:
    category = item['category']
    result[category] = result.get(category, 0) + 1

# 输出摘要
print(f"Total items: {len(data)}")
print(f"Active items: {len(active)}")
print(f"Categories: {result}")
''')
```

### 4. 保存技能

```
User: 刚才那个过滤和统计的逻辑很有用,帮我保存成一个技能

Claude 会:
1. 将代码封装成函数
2. 调用 save_skill() 保存
3. 之后可以通过 load_skill() 复用
```

## 常见使用场景

### 场景 1: 数据处理流水线

```python
# Agent 编写的代码
from tools.filesystem import read_file, write_file
import json

# 读取原始数据
raw_data = json.loads(read_file('raw_data.json'))

# 清洗
cleaned = [
    item for item in raw_data
    if item.get('valid') and item.get('amount') > 0
]

# 转换
transformed = [
    {
        'id': item['id'],
        'amount': item['amount'] * 1.1,  # 加10%
        'category': item['category'].upper()
    }
    for item in cleaned
]

# 保存
write_file('processed_data.json', json.dumps(transformed, indent=2))

print(f"Processed {len(raw_data)} → {len(cleaned)} → {len(transformed)}")
```

### 场景 2: 批量文件处理

```python
from tools.filesystem import list_directory, read_file, write_file
import json

# 获取所有 JSON 文件
files = [f for f in list_directory('.') if f.endswith('.json')]

results = []
for file in files:
    try:
        data = json.loads(read_file(file))
        # 提取需要的信息
        summary = {
            'file': file,
            'count': len(data),
            'total': sum(item.get('amount', 0) for item in data)
        }
        results.append(summary)
    except Exception as e:
        print(f"Error processing {file}: {e}")

# 生成报告
print(f"Processed {len(results)} files")
for r in results:
    print(f"  {r['file']}: {r['count']} items, total ${r['total']}")
```

### 场景 3: 条件轮询

```python
import time
from tools.filesystem import read_file

# 等待某个条件
for attempt in range(10):
    status = read_file('status.txt').strip()

    if status == 'ready':
        print("Ready!")
        break

    print(f"Attempt {attempt + 1}: Status is {status}")
    time.sleep(5)
```

### 场景 4: 构建可复用技能

```python
# 第一次: 开发技能
def analyze_sales_data(file_path):
    from tools.filesystem import read_file
    import json

    data = json.loads(read_file(file_path))

    total = sum(item['amount'] for item in data)
    avg = total / len(data)
    top_5 = sorted(data, key=lambda x: x['amount'], reverse=True)[:5]

    return {
        'total': total,
        'average': avg,
        'count': len(data),
        'top_5': top_5
    }

# 测试
result = analyze_sales_data('sales.json')
print(result)
```

然后保存为技能:

```python
save_skill(
    name='analyze_sales_data',
    code='''<上面的函数代码>''',
    description='Analyze sales data and return summary'
)
```

之后复用:

```python
from tools.skills import load_skill

analyze = load_skill('analyze_sales_data')
result = analyze('monthly_sales.json')
print(result)
```

## 高级配置

### 自定义技能目录

```bash
export SKILLS_DIR=/custom/path/to/skills
python code_execution_mcp_server.py
```

### 安全限制 (生产环境推荐)

在生产环境中,建议使用 Docker 运行:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY code_execution_mcp_server.py .

# 创建非 root 用户
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# 资源限制
ENV PYTHONUNBUFFERED=1
ENV EXECUTION_TIMEOUT=300

CMD ["python", "code_execution_mcp_server.py"]
```

然后:

```bash
docker build -t code-execution-mcp .
docker run -p 8000:8000 \
  --memory=512m \
  --cpus=1.0 \
  code-execution-mcp
```

## 故障排除

### 问题 1: ModuleNotFoundError: No module named 'mcp'

**解决**: 安装 MCP 包

```bash
pip install mcp
```

### 问题 2: 代码执行超时

**解决**: 检查代码中是否有无限循环或长时间运行的操作

### 问题 3: 文件权限错误

**解决**: 确保执行用户有权限访问文件

```bash
chmod +r data.json  # 读权限
chmod +w output.json  # 写权限
```

### 问题 4: 技能保存失败

**解决**: 确保 SKILLS_DIR 存在且有写权限

```bash
mkdir -p agent_skills
chmod +w agent_skills
```

## 性能优化建议

### 1. 批量处理而非逐个处理

❌ 低效:
```python
for file in files:
    result = process_file(file)
    write_result(file, result)
```

✅ 高效:
```python
results = [process_file(f) for f in files]
write_all_results(results)
```

### 2. 在执行环境中过滤,不要返回大数据

❌ 低效:
```python
data = read_large_file()
return data  # 大量数据进入上下文
```

✅ 高效:
```python
data = read_large_file()
filtered = [item for item in data if condition(item)]
print(f"Found {len(filtered)} items")  # 只返回摘要
```

### 3. 复用技能而不是重写代码

❌ 低效:
```python
# 每次都重写相同的逻辑
def process_data():
    # ... 100 lines of code ...
```

✅ 高效:
```python
# 保存为技能,之后复用
from tools.skills import load_skill
process = load_skill('data_processor')
```

## 最佳实践

1. **渐进式发现工具**: 先用 `list_tool_categories()` 了解有什么,再用 `search_tools()` 获取具体工具

2. **数据留在执行环境**: 大数据处理都在代码中完成,只返回摘要给模型

3. **使用原生 Python**: 充分利用 Python 的循环、条件、函数等特性

4. **保存有用的模式**: 将常用的逻辑保存为技能,积累函数库

5. **错误处理**: 在代码中使用 try-except 处理错误,提供有意义的错误信息

6. **日志输出**: 使用 `print()` 输出执行进度和关键信息

## 下一步

- 阅读 [README.md](README.md) 了解详细设计理念
- 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解架构细节
- 运行 [example_usage.py](example_usage.py) 查看更多示例
- 查看 Anthropic 的原文: https://www.anthropic.com/engineering/code-execution-with-mcp

## 反馈

如有问题或建议,欢迎提 issue!
