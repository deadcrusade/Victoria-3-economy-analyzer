"""
Victoria 3 Economic Analyzer - Main Script
Real-time save game monitoring and economic analysis
"""

import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_extractor import EconomicExtractor
from save_monitor import SaveMonitor
from visualizer import EconomicVisualizer


class Vic3Analyzer:
    """Main analyzer orchestrating all components"""
    
    def __init__(self, save_directory: str):
        self.save_directory = save_directory
        self.monitor = SaveMonitor(save_directory, data_output_dir="./data")
        self.visualizer = EconomicVisualizer(output_dir="./visualizations")
        
        print("="*70)
        print("Victoria 3 Economic Analyzer")
        print("="*70)
        print(f"Save Directory: {save_directory}")
        print(f"Data Output: ./data")
        print(f"Visualizations: ./visualizations")
        print("="*70)
    
    def process_save_callback(self, save_file: Path, playthrough_id: str):
        """Callback for processing a single save file"""
        try:
            # Extract economic data
            extractor = EconomicExtractor(str(save_file))
            data = extractor.extract_all()
            
            # Print summary
            print("\n" + "-"*60)
            print(extractor.get_summary(data))
            print("-"*60)
            
            return data
            
        except Exception as e:
            print(f"Error extracting data: {e}")
            return None
    
    def analyze_existing_saves(self):
        """Analyze all existing save files"""
        print("\n[Analyzing Existing Saves]")
        print("Processing all saves in directory...")
        
        count = self.monitor.process_new_saves(self.process_save_callback)
        
        if count > 0:
            print(f"\nProcessed {count} save files")
            self.generate_visualizations()
        else:
            print("No new saves to process")
    
    def generate_visualizations(self):
        """Generate visualizations for all playthroughs"""
        print("\n[Generating Visualizations]")
        
        playthroughs = self.monitor.get_all_playthroughs()
        
        if not playthroughs:
            print("No playthrough data available yet")
            return
        
        # Generate for each playthrough
        for playthrough_id in playthroughs:
            data = self.monitor.load_playthrough_data(playthrough_id)
            
            if len(data) < 2:
                print(f"Skipping {playthrough_id}: need at least 2 data points")
                continue
            
            print(f"\nGenerating charts for: {playthrough_id}")
            self.visualizer.generate_all_visualizations(data, playthrough_id)
        
        # Generate comparison if multiple playthroughs
        if len(playthroughs) > 1:
            print("\nGenerating comparison dashboard...")
            comparison_data = {}
            for playthrough_id in playthroughs:
                data = self.monitor.load_playthrough_data(playthrough_id)
                if len(data) >= 2:
                    comparison_data[playthrough_id] = data
            
            if comparison_data:
                self.visualizer.plot_comparison_dashboard(comparison_data)
    
    def start_monitoring(self, interval: int = 60):
        """Start real-time monitoring"""
        print("\n[Starting Real-Time Monitoring]")
        print(f"Checking for new saves every {interval} seconds")
        print("Press Ctrl+C to stop and generate visualizations")
        print("-"*70)
        
        try:
            while True:
                count = self.monitor.process_new_saves(self.process_save_callback)
                
                if count > 0:
                    print(f"\n✓ Processed {count} new save(s)")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n[Monitoring Stopped]")
            print("Generating final visualizations...")
            self.generate_visualizations()
            print("\nDone! Check the ./visualizations folder for charts.")
    
    def show_status(self):
        """Show current status"""
        print("\n[Current Status]")
        print("-"*70)
        
        playthroughs = self.monitor.get_all_playthroughs()
        print(f"Playthroughs tracked: {len(playthroughs)}")
        
        for playthrough_id in playthroughs:
            data = self.monitor.load_playthrough_data(playthrough_id)
            print(f"\n  {playthrough_id}:")
            print(f"    - Data points: {len(data)}")
            
            if data:
                first_date = data[0].get('metadata', {}).get('date', 'Unknown')
                last_date = data[-1].get('metadata', {}).get('date', 'Unknown')
                print(f"    - Date range: {first_date} to {last_date}")
                
                # Latest economic snapshot
                latest = data[-1]
                crashes = latest.get('price_crashes', [])
                overproduction = latest.get('overproduction_ratio', {})
                
                print(f"    - Latest data:")
                print(f"      • Price crashes: {len(crashes)}")
                print(f"      • Overproduction issues: {len(overproduction)}")
        
        print("-"*70)
    
    def interactive_menu(self):
        """Interactive menu for analyzer"""
        while True:
            print("\n" + "="*70)
            print("VICTORIA 3 ECONOMIC ANALYZER - MENU")
            print("="*70)
            print("1. Analyze existing saves (process all saves in directory)")
            print("2. Start real-time monitoring (watches for new saves)")
            print("3. Generate visualizations (from existing data)")
            print("4. Show status (current tracking info)")
            print("5. Reset data (clear all tracking)")
            print("6. Exit")
            print("="*70)
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                self.analyze_existing_saves()
            elif choice == '2':
                interval = input("Check interval in seconds (default 60): ").strip()
                interval = int(interval) if interval else 60
                self.start_monitoring(interval)
            elif choice == '3':
                self.generate_visualizations()
            elif choice == '4':
                self.show_status()
            elif choice == '5':
                confirm = input("Are you sure? This will delete all tracking data (y/n): ")
                if confirm.lower() == 'y':
                    self.monitor.reset()
                    print("Data reset complete")
            elif choice == '6':
                print("\nExiting...")
                break
            else:
                print("Invalid option")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Victoria 3 Economic Analyzer - Track overproduction and market crashes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py "C:\\Users\\YourName\\Documents\\Paradox Interactive\\Victoria 3\\save games"
  
  # Analyze existing saves
  python main.py <save_dir> --analyze
  
  # Start monitoring
  python main.py <save_dir> --monitor --interval 30
  
  # Generate visualizations
  python main.py <save_dir> --visualize
        """
    )
    
    parser.add_argument('save_directory', 
                       help='Path to Victoria 3 save games directory')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze all existing saves')
    parser.add_argument('--monitor', action='store_true',
                       help='Start real-time monitoring')
    parser.add_argument('--visualize', action='store_true',
                       help='Generate visualizations only')
    parser.add_argument('--interval', type=int, default=60,
                       help='Monitoring interval in seconds (default: 60)')
    parser.add_argument('--status', action='store_true',
                       help='Show current status')
    
    args = parser.parse_args()
    
    # Validate save directory
    save_dir = Path(args.save_directory)
    if not save_dir.exists():
        print(f"Error: Directory not found: {save_dir}")
        print("\nTip: Your save directory is usually at:")
        print(r"  C:\Users\YourName\Documents\Paradox Interactive\Victoria 3\save games")
        sys.exit(1)
    
    # Create analyzer
    analyzer = Vic3Analyzer(str(save_dir))
    
    # Execute based on arguments
    if args.analyze:
        analyzer.analyze_existing_saves()
    elif args.monitor:
        analyzer.start_monitoring(args.interval)
    elif args.visualize:
        analyzer.generate_visualizations()
    elif args.status:
        analyzer.show_status()
    else:
        # Interactive mode
        analyzer.interactive_menu()


if __name__ == "__main__":
    main()
