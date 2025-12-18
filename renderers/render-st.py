#!/usr/bin/env python3
"""
Structured Text (ST) Renderer
Converts IEC 61131-3 Structured Text to syntax-highlighted HTML
"""

import sys
import re
from typing import List, Tuple

class STRenderer:
    """Renderer for IEC 61131-3 Structured Text"""
    
    # Keywords for syntax highlighting
    KEYWORDS = {
        'IF', 'THEN', 'ELSE', 'ELSIF', 'END_IF',
        'CASE', 'OF', 'END_CASE',
        'FOR', 'TO', 'BY', 'DO', 'END_FOR',
        'WHILE', 'END_WHILE',
        'REPEAT', 'UNTIL', 'END_REPEAT',
        'FUNCTION', 'END_FUNCTION',
        'FUNCTION_BLOCK', 'END_FUNCTION_BLOCK',
        'PROGRAM', 'END_PROGRAM',
        'VAR', 'VAR_INPUT', 'VAR_OUTPUT', 'VAR_IN_OUT', 'VAR_TEMP', 'END_VAR',
        'RETURN', 'EXIT',
        'AND', 'OR', 'NOT', 'XOR', 'MOD',
        'TRUE', 'FALSE'
    }
    
    DATA_TYPES = {
        'BOOL', 'BYTE', 'WORD', 'DWORD', 'LWORD',
        'SINT', 'USINT', 'INT', 'UINT', 'DINT', 'UDINT', 'LINT', 'ULINT',
        'REAL', 'LREAL',
        'TIME', 'DATE', 'TIME_OF_DAY', 'TOD', 'DATE_AND_TIME', 'DT',
        'STRING', 'WSTRING',
        'ARRAY', 'STRUCT'
    }
    
    def __init__(self, code: str):
        self.code = code
        self.lines = code.split('\n')
    
    def highlight_line(self, line: str) -> str:
        """Apply syntax highlighting to a single line"""
        # Escape HTML
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Comments
        if '(*' in line or '//' in line:
            # Block comment
            line = re.sub(r'\(\*(.*?)\*\)', r'<span class="comment">(*\1*)</span>', line)
            # Line comment
            line = re.sub(r'//(.*?)$', r'<span class="comment">//\1</span>', line)
        
        # Keywords
        for keyword in self.KEYWORDS:
            pattern = r'\b(' + keyword + r')\b'
            line = re.sub(pattern, r'<span class="keyword">\1</span>', line, flags=re.IGNORECASE)
        
        # Data types
        for dtype in self.DATA_TYPES:
            pattern = r'\b(' + dtype + r')\b'
            line = re.sub(pattern, r'<span class="datatype">\1</span>', line, flags=re.IGNORECASE)
        
        # Numbers
        line = re.sub(r'\b(\d+\.?\d*)\b', r'<span class="number">\1</span>', line)
        
        # Strings
        line = re.sub(r"'([^']*)'", r"<span class=\"string\">'\\1'</span>", line)
        
        return line
    
    def generate_html(self) -> str:
        """Generate syntax-highlighted HTML"""
        
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Structured Text Viewer</title>
    <style>
        body {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            margin: 0;
            padding: 20px;
            background-color: #1e1e1e;
            color: #d4d4d4;
            font-size: 14px;
            line-height: 1.6;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: #252526;
            padding: 20px;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .header {
            background: #2d2d30;
            padding: 10px 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            color: #cccccc;
        }
        .code-container {
            background: #1e1e1e;
            border: 1px solid #3c3c3c;
            border-radius: 4px;
            overflow-x: auto;
        }
        .line {
            padding: 2px 10px;
            border-left: 3px solid transparent;
        }
        .line:hover {
            background: #2a2d2e;
            border-left-color: #007acc;
        }
        .line-number {
            display: inline-block;
            width: 40px;
            color: #858585;
            text-align: right;
            margin-right: 20px;
            user-select: none;
        }
        .keyword {
            color: #569cd6;
            font-weight: bold;
        }
        .datatype {
            color: #4ec9b0;
        }
        .comment {
            color: #6a9955;
            font-style: italic;
        }
        .string {
            color: #ce9178;
        }
        .number {
            color: #b5cea8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <strong>📝 Structured Text (IEC 61131-3)</strong>
        </div>
        <div class="code-container">
"""
        
        for i, line in enumerate(self.lines, 1):
            highlighted = self.highlight_line(line)
            html += f'            <div class="line"><span class="line-number">{i}</span>{highlighted}</div>\n'
        
        html += """
        </div>
    </div>
</body>
</html>
"""
        return html

def main():
    """Main entry point"""
    try:
        # Read ST code from stdin
        st_code = sys.stdin.read()
        
        # Create renderer
        renderer = STRenderer(st_code)
        
        # Generate and output HTML
        html_output = renderer.generate_html()
        sys.stdout.write(html_output)
        
    except Exception as e:
        error_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ST Rendering Error</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #1e1e1e; color: #d4d4d4; }}
        .error {{ background: #5a1d1d; border: 1px solid #f44336; padding: 15px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="error">
        <h2>⚠️ Error Rendering Structured Text</h2>
        <p>{str(e)}</p>
    </div>
</body>
</html>
"""
        sys.stdout.write(error_html)
        sys.exit(1)

if __name__ == '__main__':
    main()
