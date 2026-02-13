"""
Save File Monitor for Victoria 3
Watches save game directory and processes new saves
"""

import time
import json
import re
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
import threading


class SaveMonitor:
    """Monitors Victoria 3 save directory for new files"""
    
    def __init__(self, save_directory: str, data_output_dir: str = "./data"):
        self.save_directory = Path(save_directory)
        self.data_output_dir = Path(data_output_dir)
        self.data_output_dir.mkdir(exist_ok=True)
        
        self.processed_files: Set[str] = set()
        self.tracking_data: Dict[str, List] = {}  # playthrough_id -> [data_points]
        self.running = False
        
        # Load previously processed files
        self._load_state()
        
    def _load_state(self):
        """Load previously processed files from state file"""
        state_file = self.data_output_dir / "monitor_state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
                self.processed_files = set(state.get('processed_files', []))
                print(f"Loaded state: {len(self.processed_files)} files already processed")
    
    def _save_state(self):
        """Save processed files to state file"""
        state_file = self.data_output_dir / "monitor_state.json"
        with open(state_file, 'w') as f:
            json.dump({
                'processed_files': list(self.processed_files),
                'last_update': datetime.now().isoformat()
            }, f, indent=2)
    
    def get_save_files(self) -> List[Path]:
        """Get all .v3 save files in directory"""
        if not self.save_directory.exists():
            print(f"Warning: Save directory not found: {self.save_directory}")
            return []
        
        return sorted(self.save_directory.glob("*.v3"), key=lambda p: p.stat().st_mtime)
    
    def identify_playthrough(self, save_file: Path) -> str:
        """Identify which playthrough a save belongs to"""
        # Use the base name without date/time suffixes
        # e.g., "Belgium_1850_5_1_autosave.v3" -> "Belgium"
        name = save_file.stem
        
        # Remove common suffixes (case insensitive)
        for suffix in ['_autosave', '_backup', '_Autosave', '_Backup', 'autosave', 'backup']:
            name = name.replace(suffix, '')
        
        # Remove all date patterns: _YYYY_MM_DD or _YYYY_M_D
        # Remove patterns like _1850_5_1 or _2024_12_25
        name = re.sub(r'_\d{4}_\d{1,2}_\d{1,2}', '', name)
        # Remove patterns like _1850 or _20XX (year only)
        name = re.sub(r'_\d{4}', '', name)
        # Remove trailing numbers like _1, _2, _3
        name = re.sub(r'_\d+$', '', name)
        
        # Clean up any double underscores or trailing underscores
        name = re.sub(r'_+', '_', name).strip('_')
        
        # If nothing left, use "campaign" as default
        return name if name else "campaign"
    
    def process_new_saves(self, callback):
        """Process any new save files"""
        save_files = self.get_save_files()
        new_files = [f for f in save_files if str(f) not in self.processed_files]
        
        if new_files:
            print(f"\nFound {len(new_files)} new save file(s) to process")
        
        for save_file in new_files:
            try:
                print(f"Processing: {save_file.name}")
                
                # Identify playthrough
                playthrough_id = self.identify_playthrough(save_file)
                
                # Process the save file
                result = callback(save_file, playthrough_id)
                
                if result:
                    # Track data
                    if playthrough_id not in self.tracking_data:
                        self.tracking_data[playthrough_id] = []
                    self.tracking_data[playthrough_id].append(result)
                    
                    # Save data point
                    self._save_data_point(playthrough_id, result)
                
                # Mark as processed
                self.processed_files.add(str(save_file))
                self._save_state()
                
            except Exception as e:
                print(f"Error processing {save_file.name}: {e}")
        
        return len(new_files)
    
    def _save_data_point(self, playthrough_id: str, data: Dict):
        """Save individual data point to JSON"""
        playthrough_dir = self.data_output_dir / playthrough_id
        playthrough_dir.mkdir(exist_ok=True)
        
        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = playthrough_dir / f"data_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_playthrough_data(self, playthrough_id: str) -> List[Dict]:
        """Load all data for a specific playthrough"""
        playthrough_dir = self.data_output_dir / playthrough_id
        if not playthrough_dir.exists():
            return []
        
        data_points = []
        for json_file in sorted(playthrough_dir.glob("data_*.json")):
            with open(json_file, 'r') as f:
                data_points.append(json.load(f))
        
        return data_points
    
    def get_all_playthroughs(self) -> List[str]:
        """Get list of all tracked playthroughs"""
        if not self.data_output_dir.exists():
            return []
        
        return [d.name for d in self.data_output_dir.iterdir() if d.is_dir()]
    
    def start_monitoring(self, callback, interval: int = 60):
        """Start monitoring in background thread"""
        self.running = True
        
        def monitor_loop():
            print(f"Started monitoring: {self.save_directory}")
            print(f"Checking for new saves every {interval} seconds...")
            print("Press Ctrl+C to stop")
            
            while self.running:
                try:
                    self.process_new_saves(callback)
                    time.sleep(interval)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Monitor error: {e}")
                    time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
    
    def reset(self):
        """Reset all tracking data"""
        self.processed_files.clear()
        self.tracking_data.clear()
        self._save_state()
        print("Monitoring state reset")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python save_monitor.py <save_directory>")
        print("\nExample:")
        print(r'python save_monitor.py "C:\Users\YourName\Documents\Paradox Interactive\Victoria 3\save games"')
        sys.exit(1)
    
    monitor = SaveMonitor(sys.argv[1])
    print(f"Monitoring: {monitor.save_directory}")
    print(f"Found {len(monitor.get_save_files())} save files")
    print(f"Playthroughs: {monitor.get_all_playthroughs()}")
