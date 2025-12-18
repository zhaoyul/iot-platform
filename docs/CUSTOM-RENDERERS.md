# 自定义渲染器开发指南 / Custom Renderer Development Guide

## 概述 / Overview

Forgejo/Gitea的外部渲染器系统允许您为任意文件扩展名定义自定义的HTML渲染逻辑。这对于可视化工业文件格式（PLC代码、CAD文件、配置文件）至关重要。

## 渲染器架构 / Renderer Architecture

### 工作原理 / How It Works

```
┌──────────────┐
│  File (.l5x) │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────┐
│  Forgejo Markup Engine           │
│  1. 读取文件内容                 │
│  2. 查找对应渲染器配置           │
│  3. 执行外部渲染命令             │
│  4. 接收HTML输出                 │
│  5. 安全清洗（Sanitize）         │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Web Interface                   │
│  - 直接嵌入HTML                  │
│  - 或在Iframe中显示（安全模式）  │
└──────────────────────────────────┘
```

### 配置格式 / Configuration Format

在 `config/forgejo/app.ini` 中:

```ini
[markup.your-format-name]
ENABLED = true
FILE_EXTENSIONS = .ext1,.ext2
RENDER_COMMAND = "/path/to/your/renderer"
IS_INPUT_FILE = false
RENDER_CONTENT_MODE = iframe
```

**参数说明 / Parameter Description:**

- `ENABLED`: 启用此渲染器 / Enable this renderer
- `FILE_EXTENSIONS`: 文件扩展名列表（逗号分隔） / File extension list (comma-separated)
- `RENDER_COMMAND`: 渲染器可执行文件路径 / Renderer executable path
- `IS_INPUT_FILE`: 
  - `false`: 文件内容通过STDIN传递 / File content passed via STDIN
  - `true`: 文件路径作为命令行参数传递 / File path passed as command-line argument
- `RENDER_CONTENT_MODE`:
  - `sanitized`: HTML直接嵌入，经过安全清洗 / HTML embedded directly, sanitized
  - `iframe`: 在沙盒Iframe中显示（推荐） / Display in sandboxed Iframe (recommended)

## 开发渲染器 / Developing a Renderer

### 基本模板 / Basic Template

```python
#!/usr/bin/env python3
import sys

def render(content):
    """
    将输入内容转换为HTML
    Convert input content to HTML
    """
    # 解析内容
    # Parse content
    
    # 生成HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Custom Render</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
    </style>
</head>
<body>
    <h1>Rendered Content</h1>
    <pre>{content}</pre>
</body>
</html>
"""
    return html

def main():
    # 从stdin读取
    # Read from stdin
    content = sys.stdin.read()
    
    # 渲染
    html = render(content)
    
    # 输出到stdout
    # Output to stdout
    sys.stdout.write(html)

if __name__ == '__main__':
    main()
```

### 示例1: JSON美化渲染器 / Example 1: JSON Pretty Renderer

```python
#!/usr/bin/env python3
import sys
import json

def render_json(json_str):
    try:
        data = json.loads(json_str)
        pretty = json.dumps(data, indent=2, sort_keys=True)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            background: #1e1e1e;
            color: #d4d4d4;
            font-family: 'Courier New', monospace;
            padding: 20px;
        }}
        pre {{
            background: #252526;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .key {{ color: #9cdcfe; }}
        .string {{ color: #ce9178; }}
        .number {{ color: #b5cea8; }}
        .boolean {{ color: #569cd6; }}
        .null {{ color: #808080; }}
    </style>
</head>
<body>
    <pre>{pretty}</pre>
</body>
</html>
"""
        return html
    except Exception as e:
        return f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>"

if __name__ == '__main__':
    content = sys.stdin.read()
    print(render_json(content))
```

**配置 / Configuration:**

```ini
[markup.json-pretty]
ENABLED = true
FILE_EXTENSIONS = .json
RENDER_COMMAND = "/usr/local/bin/render-json"
IS_INPUT_FILE = false
RENDER_CONTENT_MODE = iframe
```

### 示例2: GraphViz DOT图形渲染器 / Example 2: GraphViz DOT Renderer

```python
#!/usr/bin/env python3
import sys
import subprocess
import base64

def render_dot(dot_content):
    try:
        # 调用graphviz生成SVG
        result = subprocess.run(
            ['dot', '-Tsvg'],
            input=dot_content.encode(),
            capture_output=True,
            check=True
        )
        
        svg = result.stdout.decode()
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        svg {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        {svg}
    </div>
</body>
</html>
"""
        return html
    except Exception as e:
        return f"<html><body><h1>Error rendering DOT</h1><p>{str(e)}</p></body></html>"

if __name__ == '__main__':
    content = sys.stdin.read()
    print(render_dot(content))
```

**依赖安装 / Dependencies:**

```bash
apt-get install graphviz
```

### 示例3: 交互式图表渲染器 / Example 3: Interactive Chart Renderer

```python
#!/usr/bin/env python3
import sys
import json

def render_chart(data_str):
    # 假设输入是CSV或JSON格式的数据
    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body { 
            padding: 20px; 
            background: #f5f5f5; 
        }
        .chart-container {
            position: relative;
            height: 400px;
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="chart-container">
        <canvas id="myChart"></canvas>
    </div>
    <script>
        const ctx = document.getElementById('myChart');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                datasets: [{
                    label: 'Temperature',
                    data: [12, 19, 3, 5, 2],
                    borderWidth: 2,
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    </script>
</body>
</html>
"""
    return html

if __name__ == '__main__':
    content = sys.stdin.read()
    print(render_chart(content))
```

## 安全考虑 / Security Considerations

### 1. 输入验证 / Input Validation

**始终验证和清洗输入:**

```python
import html

def safe_render(user_content):
    # 转义HTML特殊字符
    escaped = html.escape(user_content)
    
    # 或使用更严格的验证
    if not is_valid_format(user_content):
        raise ValueError("Invalid input format")
```

### 2. Iframe隔离 / Iframe Isolation

**强烈推荐使用Iframe模式:**

```ini
RENDER_CONTENT_MODE = iframe
```

这会在沙盒环境中运行您的HTML，防止XSS攻击。

### 3. 内容安全策略 / Content Security Policy

如果使用外部资源（如CDN JavaScript），确保配置CSP:

```python
html = """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Security-Policy" 
          content="default-src 'self'; 
                   script-src 'self' https://cdn.jsdelivr.net; 
                   style-src 'self' 'unsafe-inline';">
</head>
<!-- ... -->
"""
```

### 4. 资源限制 / Resource Limits

渲染器应设置超时和内存限制:

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Rendering timeout")

# 设置10秒超时
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)

try:
    # 渲染逻辑
    result = render(content)
finally:
    signal.alarm(0)  # 取消超时
```

## 测试渲染器 / Testing Renderers

### 单元测试 / Unit Testing

```python
import unittest

class TestL5XRenderer(unittest.TestCase):
    def test_basic_render(self):
        sample_l5x = """<?xml version="1.0"?>
        <RSLogix5000Content>
            <Controller Name="Test"/>
        </RSLogix5000Content>"""
        
        html = render_l5x(sample_l5x)
        
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Test", html)
    
    def test_malformed_xml(self):
        bad_xml = "<unclosed>"
        
        html = render_l5x(bad_xml)
        
        self.assertIn("Error", html)

if __name__ == '__main__':
    unittest.main()
```

### 集成测试 / Integration Testing

```bash
#!/bin/bash
# test-renderer.sh

echo "Testing L5X renderer..."

# 创建测试文件
cat > /tmp/test.l5x << 'EOF'
<?xml version="1.0"?>
<RSLogix5000Content>
  <Controller Name="TestController"/>
</RSLogix5000Content>
EOF

# 运行渲染器
cat /tmp/test.l5x | python renderers/render-l5x.py > /tmp/output.html

# 验证输出
if grep -q "DOCTYPE html" /tmp/output.html; then
    echo "✓ HTML output valid"
else
    echo "✗ Invalid HTML output"
    exit 1
fi

if grep -q "TestController" /tmp/output.html; then
    echo "✓ Content rendered correctly"
else
    echo "✗ Content not found"
    exit 1
fi

echo "All tests passed!"
```

## 部署 / Deployment

### 1. 安装渲染器 / Install Renderer

在Forgejo容器中:

```dockerfile
# Dockerfile.forgejo-custom
FROM codeberg.org/forgejo/forgejo:1.21

# 安装Python和依赖
RUN apk add --no-cache python3 py3-pip py3-lxml

# 复制渲染器
COPY renderers/render-l5x.py /usr/local/bin/
COPY renderers/render-st.py /usr/local/bin/
COPY renderers/render-acd.sh /usr/local/bin/

# 设置权限
RUN chmod +x /usr/local/bin/render-*

# 安装Python库
RUN pip3 install lxml
```

### 2. 构建自定义镜像 / Build Custom Image

```bash
docker build -f Dockerfile.forgejo-custom -t forgejo-industrial:latest .
```

### 3. 更新docker-compose.yml

```yaml
services:
  forgejo:
    image: forgejo-industrial:latest
    # ... 其他配置
```

## 高级技巧 / Advanced Tips

### 1. 缓存渲染结果 / Caching Rendered Results

```python
import hashlib
import os

CACHE_DIR = '/tmp/render-cache'

def cached_render(content, renderer_func):
    # 计算内容哈希
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    cache_file = f"{CACHE_DIR}/{content_hash}.html"
    
    # 检查缓存
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return f.read()
    
    # 渲染并缓存
    result = renderer_func(content)
    
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_file, 'w') as f:
        f.write(result)
    
    return result
```

### 2. 异步渲染 / Async Rendering

对于复杂的渲染任务:

```python
import asyncio

async def render_complex(content):
    # 异步解析
    parsed = await async_parse(content)
    
    # 异步生成可视化
    viz = await async_visualize(parsed)
    
    return generate_html(viz)
```

### 3. 多格式支持 / Multi-format Support

一个渲染器处理多种格式:

```python
def detect_format(content):
    if content.startswith('<?xml'):
        return 'xml'
    elif content.startswith('{'):
        return 'json'
    else:
        return 'text'

def render(content):
    fmt = detect_format(content)
    
    if fmt == 'xml':
        return render_xml(content)
    elif fmt == 'json':
        return render_json(content)
    else:
        return render_text(content)
```

## 故障排除 / Troubleshooting

### 渲染器未执行

1. 检查文件权限: `chmod +x /path/to/renderer`
2. 检查shebang: `#!/usr/bin/env python3`
3. 查看Forgejo日志: `docker logs forgejo 2>&1 | grep -i render`

### HTML未显示

1. 检查输出是否有效HTML: `validate-html output.html`
2. 查看浏览器控制台错误
3. 尝试使用`RENDER_CONTENT_MODE = iframe`

### 性能问题

1. 添加缓存机制
2. 限制渲染复杂度
3. 使用异步处理
4. 考虑后台任务队列

## 示例项目 / Example Projects

- [render-l5x.py](../renderers/render-l5x.py) - Rockwell L5X渲染器
- [render-st.py](../renderers/render-st.py) - 结构化文本渲染器
- [render-acd.sh](../renderers/render-acd.sh) - ACD文件信息显示

## 参考资源 / References

- [Forgejo External Renderers](https://forgejo.org/docs/latest/user/markdown/#external-renderers)
- [Gitea Custom Renderers](https://docs.gitea.io/en-us/customizing-gitea/#customizing-markdown)
- [HTML Sanitization](https://github.com/microcosm-cc/bluemonday)
