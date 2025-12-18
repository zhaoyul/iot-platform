#!/usr/bin/env python3
"""
L5X Ladder Logic Renderer
Converts Rockwell Automation L5X files to interactive HTML/SVG visualizations
"""

import sys
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any

class L5XParser:
    """Parser for Rockwell Automation L5X PLC files"""
    
    def __init__(self, xml_content: str):
        self.root = ET.fromstring(xml_content)
        self.namespaces = {'': 'http://www.rockwellautomation.com/schemas/l5x'}
    
    def extract_metadata(self) -> Dict[str, Any]:
        """Extract project metadata"""
        controller = self.root.find('.//Controller', self.namespaces)
        if controller is None:
            return {}
        
        return {
            'name': controller.get('Name', 'Unknown'),
            'processor_type': controller.get('ProcessorType', 'Unknown'),
            'revision': controller.get('MajorRev', '0') + '.' + controller.get('MinorRev', '0')
        }
    
    def extract_programs(self) -> List[Dict[str, Any]]:
        """Extract programs and routines"""
        programs = []
        
        for program in self.root.findall('.//Program', self.namespaces):
            program_data = {
                'name': program.get('Name', 'Unknown'),
                'type': program.get('Type', 'Normal'),
                'routines': []
            }
            
            routines = program.find('Routines', self.namespaces)
            if routines is not None:
                for routine in routines.findall('Routine', self.namespaces):
                    routine_data = {
                        'name': routine.get('Name', 'Unknown'),
                        'type': routine.get('Type', 'RLL'),  # Ladder Logic
                        'rungs': []
                    }
                    
                    # Extract ladder rungs if present
                    rll_content = routine.find('RLLContent', self.namespaces)
                    if rll_content is not None:
                        for rung in rll_content.findall('Rung', self.namespaces):
                            rung_data = {
                                'number': rung.get('Number', '0'),
                                'type': rung.get('Type', 'N'),
                                'comment': rung.find('Comment', self.namespaces).text if rung.find('Comment', self.namespaces) is not None else '',
                                'text': rung.find('Text', self.namespaces).text if rung.find('Text', self.namespaces) is not None else ''
                            }
                            routine_data['rungs'].append(rung_data)
                    
                    program_data['routines'].append(routine_data)
            
            programs.append(program_data)
        
        return programs
    
    def extract_tags(self) -> List[Dict[str, Any]]:
        """Extract controller tags"""
        tags = []
        
        controller = self.root.find('.//Controller', self.namespaces)
        if controller is None:
            return tags
        
        tag_container = controller.find('Tags', self.namespaces)
        if tag_container is not None:
            for tag in tag_container.findall('Tag', self.namespaces):
                tag_data = {
                    'name': tag.get('Name', 'Unknown'),
                    'tag_type': tag.get('TagType', 'Base'),
                    'data_type': tag.get('DataType', 'DINT'),
                    'radix': tag.get('Radix', 'Decimal')
                }
                tags.append(tag_data)
        
        return tags

def generate_html(metadata: Dict, programs: List[Dict], tags: List[Dict]) -> str:
    """Generate interactive HTML visualization"""
    
    # Generate JSON data for frontend rendering
    data = {
        'metadata': metadata,
        'programs': programs,
        'tags': tags
    }
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L5X Ladder Logic Visualization</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metadata {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .metadata h2 {{
            margin-top: 0;
            color: #1976d2;
        }}
        .program {{
            border: 1px solid #ddd;
            margin-bottom: 20px;
            border-radius: 4px;
        }}
        .program-header {{
            background: #2196f3;
            color: white;
            padding: 10px 15px;
            font-weight: bold;
            cursor: pointer;
        }}
        .program-header:hover {{
            background: #1976d2;
        }}
        .routine {{
            border-top: 1px solid #ddd;
            padding: 10px 15px;
        }}
        .routine-header {{
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        .rung {{
            background: #f9f9f9;
            border: 1px solid #e0e0e0;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }}
        .rung-number {{
            display: inline-block;
            background: #4caf50;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            margin-right: 10px;
            font-size: 12px;
        }}
        .rung-comment {{
            color: #666;
            font-style: italic;
            margin-bottom: 5px;
        }}
        .rung-logic {{
            color: #000;
            white-space: pre-wrap;
        }}
        .tags-section {{
            margin-top: 30px;
        }}
        .tag {{
            display: inline-block;
            background: #fff3e0;
            border: 1px solid #ffb74d;
            padding: 5px 10px;
            margin: 3px;
            border-radius: 3px;
            font-size: 13px;
        }}
        .collapsible {{
            display: none;
        }}
        .active + .collapsible {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="metadata">
            <h2>📊 Project Metadata</h2>
            <p><strong>Name:</strong> {metadata.get('name', 'Unknown')}</p>
            <p><strong>Processor:</strong> {metadata.get('processor_type', 'Unknown')}</p>
            <p><strong>Revision:</strong> {metadata.get('revision', 'Unknown')}</p>
        </div>
        
        <h2>🔧 Programs & Routines</h2>
        <div id="programs">
"""
    
    for program in programs:
        html += f"""
        <div class="program">
            <div class="program-header" onclick="this.classList.toggle('active')">
                {program['name']} ({program['type']})
            </div>
            <div class="collapsible">
"""
        for routine in program['routines']:
            html += f"""
                <div class="routine">
                    <div class="routine-header">
                        Routine: {routine['name']} (Type: {routine['type']})
                    </div>
"""
            for rung in routine['rungs']:
                html += f"""
                    <div class="rung">
                        <span class="rung-number">Rung {rung['number']}</span>
"""
                if rung['comment']:
                    html += f"""
                        <div class="rung-comment">{rung['comment']}</div>
"""
                html += f"""
                        <div class="rung-logic">{rung['text']}</div>
                    </div>
"""
            html += """
                </div>
"""
        html += """
            </div>
        </div>
"""
    
    html += """
        </div>
        
        <div class="tags-section">
            <h2>🏷️ Controller Tags</h2>
            <div id="tags">
"""
    
    for tag in tags[:50]:  # Limit display to first 50 tags
        html += f"""
                <span class="tag">
                    {tag['name']} ({tag['data_type']})
                </span>
"""
    
    if len(tags) > 50:
        html += f"""
                <p><em>... and {len(tags) - 50} more tags</em></p>
"""
    
    html += """
            </div>
        </div>
    </div>
    
    <script>
        // Store data for potential future interactions
        const plcData = """ + json.dumps(data) + """;
        console.log('PLC Data loaded:', plcData);
    </script>
</body>
</html>
"""
    
    return html

def main():
    """Main entry point for the renderer"""
    try:
        # Read L5X content from stdin
        xml_content = sys.stdin.read()
        
        # Parse the L5X file
        parser = L5XParser(xml_content)
        
        # Extract data
        metadata = parser.extract_metadata()
        programs = parser.extract_programs()
        tags = parser.extract_tags()
        
        # Generate HTML
        html_output = generate_html(metadata, programs, tags)
        
        # Write to stdout
        sys.stdout.write(html_output)
        
    except Exception as e:
        # Generate error page
        error_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>L5X Rendering Error</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .error {{ background: #ffebee; border: 1px solid #f44336; padding: 15px; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="error">
        <h2>⚠️ Error Rendering L5X File</h2>
        <p>{str(e)}</p>
    </div>
</body>
</html>
"""
        sys.stdout.write(error_html)
        sys.exit(1)

if __name__ == '__main__':
    main()
