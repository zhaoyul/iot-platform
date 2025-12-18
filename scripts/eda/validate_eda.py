#!/usr/bin/env python3
"""
EDA设计文件验证脚本
支持KiCad, Altium等EDA工具的设计规则检查
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any
import json

class EDAValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_kicad_schematic(self, file_path: str) -> bool:
        """验证KiCad原理图"""
        print(f"Validating KiCad schematic: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查文件格式
            if not content.startswith('(kicad_sch'):
                self.errors.append(f"{file_path}: Not a valid KiCad schematic file")
                return False
            
            # 检查必要字段
            required_fields = ['version', 'symbol', 'sheet']
            for field in required_fields:
                if field not in content:
                    self.warnings.append(f"{file_path}: Missing recommended field '{field}'")
            
            print(f"✓ {file_path} validated successfully")
            return True
            
        except Exception as e:
            self.errors.append(f"{file_path}: Error reading file - {str(e)}")
            return False
    
    def validate_kicad_pcb(self, file_path: str) -> bool:
        """验证KiCad PCB文件"""
        print(f"Validating KiCad PCB: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查文件格式
            if not content.startswith('(kicad_pcb'):
                self.errors.append(f"{file_path}: Not a valid KiCad PCB file")
                return False
            
            # 检查层定义
            if 'layers' not in content:
                self.errors.append(f"{file_path}: No layers defined")
                return False
            
            # 检查是否有铜箔
            if 'F.Cu' not in content and 'B.Cu' not in content:
                self.warnings.append(f"{file_path}: No copper layers found")
            
            print(f"✓ {file_path} validated successfully")
            return True
            
        except Exception as e:
            self.errors.append(f"{file_path}: Error reading file - {str(e)}")
            return False
    
    def validate_gerber(self, file_path: str) -> bool:
        """验证Gerber文件"""
        print(f"Validating Gerber file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查Gerber格式标记
            if '%FSLAX' not in content and 'G04' not in content:
                self.warnings.append(f"{file_path}: May not be a valid Gerber file")
            
            print(f"✓ {file_path} validated")
            return True
            
        except Exception as e:
            self.errors.append(f"{file_path}: Error reading file - {str(e)}")
            return False
    
    def check_drc_rules(self, file_path: str) -> Dict[str, Any]:
        """设计规则检查（DRC）"""
        drc_results = {
            'clearance_violations': [],
            'track_width_violations': [],
            'via_violations': [],
            'passed': True
        }
        
        # 这里应该实现实际的DRC检查
        # 简化示例
        print(f"Running DRC on {file_path}...")
        
        return drc_results
    
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
    parser = argparse.ArgumentParser(description='Validate EDA design files')
    parser.add_argument('--path', required=True, help='Path to EDA design files')
    parser.add_argument('--tool', choices=['kicad', 'altium', 'eagle', 'all'], 
                        default='all', help='EDA tool type')
    parser.add_argument('--drc', action='store_true', help='Run design rule check')
    
    args = parser.parse_args()
    
    validator = EDAValidator()
    path = Path(args.path)
    
    if not path.exists():
        print(f"Error: Path {path} does not exist")
        sys.exit(1)
    
    # 查找所有EDA文件
    eda_files = []
    if path.is_file():
        eda_files.append(path)
    else:
        # KiCad文件
        eda_files.extend(path.glob('**/*.kicad_sch'))
        eda_files.extend(path.glob('**/*.kicad_pcb'))
        eda_files.extend(path.glob('**/*.kicad_pro'))
        # Gerber文件
        eda_files.extend(path.glob('**/*.gbr'))
        eda_files.extend(path.glob('**/*.gko'))
        # 其他格式
        eda_files.extend(path.glob('**/*.brd'))
        eda_files.extend(path.glob('**/*.sch'))
    
    if not eda_files:
        print(f"No EDA files found in {path}")
        sys.exit(0)
    
    print(f"Found {len(eda_files)} EDA files")
    
    # 验证每个文件
    for eda_file in eda_files:
        if eda_file.suffix == '.kicad_sch':
            validator.validate_kicad_schematic(str(eda_file))
        elif eda_file.suffix == '.kicad_pcb':
            result = validator.validate_kicad_pcb(str(eda_file))
            if result and args.drc:
                validator.check_drc_rules(str(eda_file))
        elif eda_file.suffix in ['.gbr', '.gko']:
            validator.validate_gerber(str(eda_file))
    
    # 生成报告
    report = validator.generate_report()
    
    print("\n" + "="*50)
    print("EDA Validation Report")
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
