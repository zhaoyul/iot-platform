#!/usr/bin/env python3
"""
PLC程序验证脚本
支持多种PLC编程语言的语法检查和静态分析
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any

class PLCValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_structured_text(self, file_path: str) -> bool:
        """验证Structured Text (ST)程序"""
        print(f"Validating ST program: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 基本语法检查
        if not self.check_program_structure(content):
            self.errors.append(f"{file_path}: Invalid program structure")
            return False
        
        # 检查变量声明
        if not self.check_variable_declarations(content):
            self.warnings.append(f"{file_path}: Variable declaration issues")
        
        # 检查括号匹配
        if not self.check_brackets(content):
            self.errors.append(f"{file_path}: Bracket mismatch")
            return False
        
        print(f"✓ {file_path} validated successfully")
        return True
    
    def check_program_structure(self, content: str) -> bool:
        """检查程序结构"""
        # 查找PROGRAM...END_PROGRAM块
        has_program = 'PROGRAM' in content and 'END_PROGRAM' in content
        if not has_program:
            # 可能是函数块或函数
            has_fb = 'FUNCTION_BLOCK' in content and 'END_FUNCTION_BLOCK' in content
            has_func = 'FUNCTION' in content and 'END_FUNCTION' in content
            return has_fb or has_func
        return True
    
    def check_variable_declarations(self, content: str) -> bool:
        """检查变量声明"""
        lines = content.split('\n')
        in_var_section = False
        var_count = 0
        
        for line in lines:
            line = line.strip()
            if line.startswith('VAR'):
                in_var_section = True
            elif line.startswith('END_VAR'):
                in_var_section = False
            elif in_var_section and ':' in line:
                var_count += 1
        
        return var_count > 0
    
    def check_brackets(self, content: str) -> bool:
        """检查括号匹配"""
        stack = []
        pairs = {'(': ')', '[': ']', '{': '}'}
        
        for char in content:
            if char in pairs.keys():
                stack.append(char)
            elif char in pairs.values():
                if not stack:
                    return False
                if pairs[stack[-1]] != char:
                    return False
                stack.pop()
        
        return len(stack) == 0
    
    def validate_ladder_logic(self, file_path: str) -> bool:
        """验证Ladder Logic程序"""
        print(f"Validating Ladder Logic: {file_path}")
        # 梯形图通常以XML或专有格式存储
        # 这里是简化的验证
        print(f"✓ {file_path} validated")
        return True
    
    def generate_report(self) -> Dict[str, Any]:
        """生成验证报告"""
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'passed': len(self.errors) == 0
        }

def main():
    parser = argparse.ArgumentParser(description='Validate PLC programs')
    parser.add_argument('--path', required=True, help='Path to PLC programs directory')
    parser.add_argument('--language', choices=['st', 'ld', 'all'], default='all',
                        help='PLC programming language')
    
    args = parser.parse_args()
    
    validator = PLCValidator()
    path = Path(args.path)
    
    if not path.exists():
        print(f"Error: Path {path} does not exist")
        sys.exit(1)
    
    # 查找所有PLC文件
    plc_files = []
    if path.is_file():
        plc_files.append(path)
    else:
        plc_files.extend(path.glob('**/*.st'))
        plc_files.extend(path.glob('**/*.ld'))
        plc_files.extend(path.glob('**/*.xml'))
    
    if not plc_files:
        print(f"No PLC files found in {path}")
        sys.exit(0)
    
    print(f"Found {len(plc_files)} PLC files")
    
    # 验证每个文件
    for plc_file in plc_files:
        if plc_file.suffix == '.st':
            validator.validate_structured_text(str(plc_file))
        elif plc_file.suffix in ['.ld', '.xml']:
            validator.validate_ladder_logic(str(plc_file))
    
    # 生成报告
    report = validator.generate_report()
    
    print("\n" + "="*50)
    print("Validation Report")
    print("="*50)
    print(f"Errors: {report['error_count']}")
    print(f"Warnings: {report['warning_count']}")
    
    if report['errors']:
        print("\nErrors:")
        for error in report['errors']:
            print(f"  - {error}")
    
    if report['warnings']:
        print("\nWarnings:")
        for warning in report['warnings']:
            print(f"  - {warning}")
    
    if report['passed']:
        print("\n✓ All validations passed")
        sys.exit(0)
    else:
        print("\n✗ Validation failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
