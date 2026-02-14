"""
Victoria 3 Economic Analyzer - Main Script
Real-time save game monitoring and economic analysis
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_extractor import (
    BinarySaveParseError,
    EconomicExtractor,
    ParserRuntimeUnavailableError,
)
from save_monitor import SaveMonitor
from visualizer import EconomicVisualizer


class Vic3Analyzer:
    """Main analyzer orchestrating all components."""

    def __init__(self, save_directory: str):
        self.save_directory = save_directory
        self.monitor = SaveMonitor(save_directory, data_output_dir="./data")
        self.visualizer = EconomicVisualizer(output_dir="./visualizations")

        print("=" * 70)
        print("Victoria 3 Economic Analyzer")
        print("=" * 70)
        print(f"Save Directory: {save_directory}")
        print("Data Output: ./data")
        print("Visualizations: ./visualizations")
        print("=" * 70)

    def _format_run_stats(self) -> str:
        stats = self.monitor.get_run_stats_snapshot()
        backlog = self.monitor.get_queue_backlog_snapshot()
        return (
            f"Processed {stats.get('processed', 0)}, "
            f"captured {stats.get('captured', 0)}, "
            f"skipped duplicates {stats.get('duplicate_skipped', 0)}, "
            f"event duplicates {stats.get('event_duplicate_skipped', 0)}, "
            f"unsupported format {stats.get('unsupported_format', 0)}, "
            f"errors {stats.get('error', 0)}, "
            f"queue backlog events {backlog.get('event_queue', 0)} "
            f"processing {backlog.get('process_queue', 0)}"
        )

    @staticmethod
    def _warn_if_low_quality_data(playthrough_id: str, data: List[Dict[str, Any]]):
        if not data:
            return

        total = len(data)
        save_date_points = 0
        non_empty_goods_points = 0

        for data_point in data:
            metadata = data_point.get("metadata", {})
            if metadata.get("timeline_source") == "save_date":
                save_date_points += 1

            goods_economy = data_point.get("goods_economy", {})
            if isinstance(goods_economy, dict) and goods_economy:
                non_empty_goods_points += 1

        threshold = max(1, int(total * 0.5))
        if save_date_points < threshold or non_empty_goods_points < threshold:
            print(
                f"Warning: {playthrough_id} has low-quality historical data "
                f"(save-date points {save_date_points}/{total}, "
                f"goods snapshots {non_empty_goods_points}/{total})."
            )
            print(
                "Recommendation: legacy malformed snapshots may remain from older parser behavior. "
                "Use Reset Data and run a fresh tracking session for clean charts."
            )

    def process_save_callback(self, save_file: Path, playthrough_id: str):
        """Callback for processing a single save file."""
        try:
            extractor = EconomicExtractor(str(save_file))
            data = extractor.extract_all()

            print("\n" + "-" * 60)
            print(extractor.get_summary(data))
            print("-" * 60)

            return data

        except ParserRuntimeUnavailableError as e:
            print(f"Native parser runtime unavailable for {save_file.name}: {e}")
            print(
                "Action: reinstall/update analyzer build to restore bundled parser runtime."
            )
            raise
        except BinarySaveParseError as e:
            print(f"Save parse failed for {save_file.name}: {e}")
            print(
                "Action: this save is skipped and monitoring continues with future saves."
            )
            raise
        except Exception as e:
            print(f"Error extracting data from {save_file.name}: {e}")
            raise

    def analyze_existing_saves(self):
        """Analyze all existing save files."""
        print("\n[Analyzing Existing Saves]")
        print("Processing all saves in directory...")

        count = self.monitor.process_new_saves(self.process_save_callback)
        print(f"Run summary: {self._format_run_stats()}")

        if count > 0:
            print(f"\nProcessed {count} save files")
            self.generate_visualizations()
        else:
            print("No new saves to process")

    def generate_visualizations(self):
        """Generate visualizations for all playthroughs."""
        print("\n[Generating Visualizations]")

        playthroughs = self.monitor.get_all_playthroughs()

        if not playthroughs:
            print("No playthrough data available yet")
            return

        for playthrough_id in playthroughs:
            data = self.monitor.load_playthrough_data(playthrough_id)
            self._warn_if_low_quality_data(playthrough_id, data)

            if len(data) < 2:
                print(f"Skipping {playthrough_id}: need at least 2 data points")
                continue

            print(f"\nGenerating charts for: {playthrough_id}")
            self.visualizer.generate_all_visualizations(data, playthrough_id)

        if len(playthroughs) > 1:
            print("\nGenerating comparison dashboard...")
            comparison_data = {}
            for playthrough_id in playthroughs:
                data = self.monitor.load_playthrough_data(playthrough_id)
                if len(data) >= 2:
                    comparison_data[playthrough_id] = data

            if comparison_data:
                self.visualizer.plot_comparison_dashboard(comparison_data)

    def start_monitoring(self):
        """Start real-time monitoring."""
        print("\n[Starting Real-Time Monitoring]")
        print("Watching save folder continuously for changes")
        print("Capturing save snapshots and processing sequentially")
        print("Press Ctrl+C to stop and generate visualizations")
        print("-" * 70)

        watcher_started = False
        try:
            startup_count = self.monitor.start_monitoring(
                self.process_save_callback,
                process_existing=True,
                debounce_seconds=1.5,
            )
            watcher_started = True

            if startup_count > 0:
                print(f"\nProcessed {startup_count} save(s) at startup")
            print(f"Startup summary: {self._format_run_stats()}")

            while True:
                # Keep the process alive while watcher threads run.
                time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n\n[Monitoring Stopped]")
            print("Draining queued save snapshots before shutdown...")
        finally:
            if watcher_started:
                self.monitor.stop_monitoring()
                print(f"Monitoring summary: {self._format_run_stats()}")
                print("Generating final visualizations...")
                self.generate_visualizations()
                print("\nDone! Check the ./visualizations folder for charts.")

    def show_status(self):
        """Show current status."""
        print("\n[Current Status]")
        print("-" * 70)

        playthroughs = self.monitor.get_all_playthroughs()
        print(f"Playthroughs tracked: {len(playthroughs)}")

        for playthrough_id in playthroughs:
            data = self.monitor.load_playthrough_data(playthrough_id)
            print(f"\n  {playthrough_id}:")
            print(f"    - Data points: {len(data)}")

            if data:
                first_date = data[0].get("metadata", {}).get("date", "Unknown")
                last_date = data[-1].get("metadata", {}).get("date", "Unknown")
                print(f"    - Date range: {first_date} to {last_date}")

                latest = data[-1]
                crashes = latest.get("price_crashes", [])
                overproduction = latest.get("overproduction_ratio", {})

                print("    - Latest data:")
                print(f"      - Price crashes: {len(crashes)}")
                print(f"      - Overproduction issues: {len(overproduction)}")

        print("-" * 70)

    def interactive_menu(self):
        """Interactive menu for analyzer."""
        while True:
            print("\n" + "=" * 70)
            print("VICTORIA 3 ECONOMIC ANALYZER - MENU")
            print("=" * 70)
            print("1. Analyze existing saves (process all saves in directory)")
            print("2. Start real-time monitoring (watches for new saves)")
            print("3. Generate visualizations (from existing data)")
            print("4. Show status (current tracking info)")
            print("5. Reset data (clear all tracking)")
            print("6. Exit")
            print("=" * 70)

            choice = input("\nSelect option (1-6): ").strip()

            if choice == "1":
                self.analyze_existing_saves()
            elif choice == "2":
                self.start_monitoring()
            elif choice == "3":
                self.generate_visualizations()
            elif choice == "4":
                self.show_status()
            elif choice == "5":
                confirm = input("Are you sure? This will delete all tracking data (y/n): ")
                if confirm.lower() == "y":
                    self.monitor.reset()
                    print("Data reset complete")
            elif choice == "6":
                print("\nExiting...")
                break
            else:
                print("Invalid option")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Victoria 3 Economic Analyzer - Track overproduction and market crashes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py "C:\\Users\\YourName\\Documents\\Paradox Interactive\\Victoria 3\\save games"

  # Analyze existing saves
  python main.py <save_dir> --analyze

  # Start monitoring (continuous watch)
  python main.py <save_dir> --monitor

  # Generate visualizations
  python main.py <save_dir> --visualize
        """,
    )

    parser.add_argument("save_directory", help="Path to Victoria 3 save games directory")
    parser.add_argument("--analyze", action="store_true", help="Analyze all existing saves")
    parser.add_argument("--monitor", action="store_true", help="Start real-time monitoring")
    parser.add_argument("--visualize", action="store_true", help="Generate visualizations only")
    parser.add_argument("--status", action="store_true", help="Show current status")

    args = parser.parse_args()

    save_dir = Path(args.save_directory)
    if not save_dir.exists():
        print(f"Error: Directory not found: {save_dir}")
        print("\nTip: Your save directory is usually at:")
        print(r"  C:\Users\YourName\Documents\Paradox Interactive\Victoria 3\save games")
        sys.exit(1)

    analyzer = Vic3Analyzer(str(save_dir))

    if args.analyze:
        analyzer.analyze_existing_saves()
    elif args.monitor:
        analyzer.start_monitoring()
    elif args.visualize:
        analyzer.generate_visualizations()
    elif args.status:
        analyzer.show_status()
    else:
        analyzer.interactive_menu()


if __name__ == "__main__":
    main()
