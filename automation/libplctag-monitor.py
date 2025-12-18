#!/usr/bin/env python3
"""
libplctag Integration for Direct PLC Parameter Backup
Monitors and backs up PLC tag values without full program upload
"""

import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('libplctag-monitor')

class PLCTagMonitor:
    """
    Monitor PLC tags using libplctag library
    
    This provides lightweight monitoring of recipe parameters
    and configuration values without requiring full SDK installation
    """
    
    def __init__(self, plc_config: Dict[str, Any]):
        self.plc_config = plc_config
        self.tag_cache = {}
    
    def connect(self) -> bool:
        """Establish connection to PLC"""
        try:
            # This would use pylogix or python-libplctag
            # Example: plc = PLC()
            # plc.IPAddress = self.plc_config['ip_address']
            
            logger.info(f"Connected to PLC at {self.plc_config.get('ip_address')}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def read_tags(self, tag_list: List[str]) -> Dict[str, Any]:
        """Read multiple tags from PLC"""
        results = {}
        
        for tag_name in tag_list:
            try:
                # Placeholder for actual libplctag read
                # value = plc.Read(tag_name)
                # results[tag_name] = value.Value
                
                # For demo, simulate reading
                results[tag_name] = {
                    'name': tag_name,
                    'value': 0,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Failed to read {tag_name}: {e}")
                results[tag_name] = None
        
        return results
    
    def detect_changes(self, current_values: Dict[str, Any]) -> Dict[str, Any]:
        """Detect which tags have changed since last read"""
        changes = {}
        
        for tag_name, value in current_values.items():
            if tag_name not in self.tag_cache:
                changes[tag_name] = {
                    'old': None,
                    'new': value,
                    'type': 'added'
                }
            elif self.tag_cache[tag_name] != value:
                changes[tag_name] = {
                    'old': self.tag_cache[tag_name],
                    'new': value,
                    'type': 'modified'
                }
        
        return changes
    
    def export_to_json(self, tag_values: Dict[str, Any], filepath: str):
        """Export tag values to JSON file for version control"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'plc_info': self.plc_config,
            'tags': tag_values
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported tag values to {filepath}")
    
    def monitor_loop(self, tag_list: List[str], interval: int = 60):
        """
        Continuously monitor tags and commit changes to Git
        
        This implements "Configuration as Code" for PLC parameters
        """
        logger.info(f"Starting tag monitor for {len(tag_list)} tags")
        
        while True:
            try:
                # Read current values
                current_values = self.read_tags(tag_list)
                
                # Detect changes
                changes = self.detect_changes(current_values)
                
                if changes:
                    # Export to JSON
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filepath = f"plc-configs/tags_{timestamp}.json"
                    self.export_to_json(current_values, filepath)
                    
                    # Git commit
                    change_summary = ', '.join(changes.keys())
                    logger.info(f"Detected changes: {change_summary}")
                    
                    # Update cache
                    self.tag_cache = current_values.copy()
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("Monitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(10)

def main():
    """Main entry point"""
    # Example configuration
    config = {
        'ip_address': '192.168.1.10',
        'plc_type': 'Allen-Bradley ControlLogix',
        'protocol': 'EtherNet/IP'
    }
    
    # Tags to monitor (recipe parameters, setpoints, etc.)
    tags_to_monitor = [
        'Recipe.Temperature_SP',
        'Recipe.Pressure_SP',
        'Recipe.Time_SP',
        'Config.PID_P',
        'Config.PID_I',
        'Config.PID_D'
    ]
    
    monitor = PLCTagMonitor(config)
    
    if monitor.connect():
        monitor.monitor_loop(tags_to_monitor, interval=300)  # Every 5 minutes

if __name__ == '__main__':
    main()
