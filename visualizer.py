"""
Matplotlib Visualizer for Victoria 3 Economic Data
Creates charts and graphs for economic analysis
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
from typing import Dict, List
from datetime import datetime
import json
from pathlib import Path
import numpy as np


class EconomicVisualizer:
    """Creates visualizations for Victoria 3 economic data"""
    
    def __init__(self, output_dir: str = "./visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def plot_goods_prices_over_time(self, playthrough_data: List[Dict], 
                                    goods_list: List[str] = None,
                                    playthrough_name: str = "default"):
        """Plot goods prices over time"""
        if not playthrough_data:
            print("No data to plot")
            return
        
        # Extract time series data
        game_days = []
        for idx, data_point in enumerate(playthrough_data):
            metadata = data_point.get('metadata', {})
            game_day = metadata.get('game_day')
            if game_day is None:
                game_day = idx
            game_days.append(game_day)

        # Build a complete per-goods series across all data points.
        all_goods = sorted({
            goods_name
            for data_point in playthrough_data
            for goods_name in data_point.get('goods_economy', {}).keys()
        })
        discovered_prices = {goods_name: [] for goods_name in all_goods}

        for data_point in playthrough_data:
            goods_economy = data_point.get('goods_economy', {})
            for goods_name in all_goods:
                goods_data = goods_economy.get(goods_name, {})
                discovered_prices[goods_name].append(self._extract_price(goods_data))

        # Default behavior: plot all detected goods with real price data.
        if goods_list is None:
            prices = {
                goods_name: series
                for goods_name, series in discovered_prices.items()
                if any(p > 0 for p in series)
            }
        else:
            prices = {}
            for goods_name in goods_list:
                series = discovered_prices.get(goods_name, [0.0] * len(playthrough_data))
                prices[goods_name] = series

            has_requested_data = any(any(p > 0 for p in series) for series in prices.values())
            if not has_requested_data:
                prices = {
                    goods_name: series
                    for goods_name, series in discovered_prices.items()
                    if any(p > 0 for p in series)
                }
                if prices:
                    print("Requested key goods missing; using all detected goods from data instead.")

        if not prices:
            print("No goods price data found to plot")
            return
        
        # Create plot
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for goods, price_list in prices.items():
            if any(p > 0 for p in price_list):  # Only plot if we have data
                ax.plot(game_days, price_list, marker='o', label=goods, linewidth=2)
        
        ax.set_xlabel('Game Day', fontsize=12)
        ax.set_ylabel('Price', fontsize=12)
        ax.set_title(f'Goods Prices Over Time - {playthrough_name}', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        
        # Save
        filename = self.output_dir / f"{playthrough_name}_prices_over_time.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Saved: {filename}")
        plt.close()

    @staticmethod
    def _extract_price(goods_data):
        """Extract numeric price value from goods record shape."""
        if isinstance(goods_data, dict):
            value = goods_data.get('price', 0)
        else:
            value = goods_data

        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    
    def plot_price_crashes(self, playthrough_data: List[Dict], 
                          playthrough_name: str = "default"):
        """Plot price crash severity over time"""
        if not playthrough_data:
            return
        
        game_days = []
        crash_counts = []
        avg_severity = []
        
        for data_point in playthrough_data:
            metadata = data_point.get('metadata', {})
            game_day = metadata.get('game_day', 0)
            game_days.append(game_day)
            
            crashes = data_point.get('price_crashes', [])
            crash_counts.append(len(crashes))
            
            if crashes:
                avg_sev = sum(c['severity'] for c in crashes) / len(crashes)
                avg_severity.append(avg_sev)
            else:
                avg_severity.append(0)
        
        # Create plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Crash count
        ax1.plot(game_days, crash_counts, marker='o', color='red', linewidth=2)
        ax1.fill_between(game_days, crash_counts, alpha=0.3, color='red')
        ax1.set_ylabel('Number of Price Crashes', fontsize=12)
        ax1.set_title(f'Price Crash Analysis - {playthrough_name}', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Average severity
        ax2.plot(game_days, avg_severity, marker='s', color='orange', linewidth=2)
        ax2.fill_between(game_days, avg_severity, alpha=0.3, color='orange')
        ax2.set_xlabel('Game Day', fontsize=12)
        ax2.set_ylabel('Average Crash Severity', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Save
        filename = self.output_dir / f"{playthrough_name}_price_crashes.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Saved: {filename}")
        plt.close()
    
    def plot_overproduction_heatmap(self, playthrough_data: List[Dict],
                                   playthrough_name: str = "default"):
        """Create heatmap of overproduction issues"""
        if not playthrough_data:
            return
        
        # Collect all goods that have overproduction
        all_goods = set()
        for data_point in playthrough_data:
            overproduction = data_point.get('overproduction_ratio', {})
            all_goods.update(overproduction.keys())
        
        if not all_goods:
            print("No overproduction data to plot")
            return
        
        # Sort goods by average overproduction
        goods_list = sorted(list(all_goods))[:20]  # Limit to top 20
        
        # Build matrix
        game_days = [dp.get('metadata', {}).get('game_day', 0) for dp in playthrough_data]
        matrix = []
        
        for goods in goods_list:
            row = []
            for data_point in playthrough_data:
                overproduction = data_point.get('overproduction_ratio', {})
                row.append(overproduction.get(goods, 0))
            matrix.append(row)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(14, 10))
        
        im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto', interpolation='nearest')
        
        # Labels
        ax.set_xticks(range(len(game_days)))
        ax.set_xticklabels([f"Day {d}" for d in game_days], rotation=45, ha='right')
        ax.set_yticks(range(len(goods_list)))
        ax.set_yticklabels(goods_list)
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Overproduction Ratio', rotation=270, labelpad=20)
        
        ax.set_title(f'Overproduction Heatmap - {playthrough_name}', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Game Progress', fontsize=12)
        ax.set_ylabel('Goods', fontsize=12)
        
        # Save
        filename = self.output_dir / f"{playthrough_name}_overproduction_heatmap.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Saved: {filename}")
        plt.close()
    
    def plot_building_profitability(self, playthrough_data: List[Dict],
                                   playthrough_name: str = "default"):
        """Plot building profitability trends"""
        if not playthrough_data:
            return
        
        # Track unprofitable building percentage over time
        game_days = []
        unprofitable_pct = []
        total_buildings = []
        
        for data_point in playthrough_data:
            metadata = data_point.get('metadata', {})
            game_day = metadata.get('game_day', 0)
            game_days.append(game_day)
            
            profitability = data_point.get('building_profitability', {})
            if profitability:
                total = len(profitability)
                unprofitable = sum(1 for v in profitability.values() if v.get('avg', 0) < 0)
                unprofitable_pct.append((unprofitable / total) * 100 if total > 0 else 0)
                total_buildings.append(total)
            else:
                unprofitable_pct.append(0)
                total_buildings.append(0)
        
        # Create plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Unprofitable percentage
        ax1.plot(game_days, unprofitable_pct, marker='o', color='crimson', linewidth=2)
        ax1.fill_between(game_days, unprofitable_pct, alpha=0.3, color='crimson')
        ax1.set_ylabel('Unprofitable Buildings (%)', fontsize=12)
        ax1.set_title(f'Building Profitability Trends - {playthrough_name}', 
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=50, color='red', linestyle='--', alpha=0.5, label='50% threshold')
        ax1.legend()
        
        # Total building types tracked
        ax2.plot(game_days, total_buildings, marker='s', color='steelblue', linewidth=2)
        ax2.set_xlabel('Game Day', fontsize=12)
        ax2.set_ylabel('Building Types Tracked', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Save
        filename = self.output_dir / f"{playthrough_name}_building_profitability.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Saved: {filename}")
        plt.close()
    
    def plot_comparison_dashboard(self, playthrough_data_dict: Dict[str, List[Dict]]):
        """Create comparison dashboard across multiple playthroughs"""
        if not playthrough_data_dict:
            return
        
        fig = plt.figure(figsize=(18, 12))
        gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. Price crashes comparison
        ax1 = fig.add_subplot(gs[0, :])
        for playthrough_name, data in playthrough_data_dict.items():
            game_days = [dp.get('metadata', {}).get('game_day', 0) for dp in data]
            crash_counts = [len(dp.get('price_crashes', [])) for dp in data]
            ax1.plot(game_days, crash_counts, marker='o', label=playthrough_name, linewidth=2)
        ax1.set_ylabel('Number of Price Crashes')
        ax1.set_title('Price Crashes Comparison', fontweight='bold', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Average goods prices
        ax2 = fig.add_subplot(gs[1, 0])
        for playthrough_name, data in playthrough_data_dict.items():
            game_days = [dp.get('metadata', {}).get('game_day', 0) for dp in data]
            avg_prices = []
            for dp in data:
                goods_economy = dp.get('goods_economy', {})
                if goods_economy:
                    prices = [g.get('price', 0) for g in goods_economy.values() if g.get('price', 0) > 0]
                    avg_prices.append(np.mean(prices) if prices else 0)
                else:
                    avg_prices.append(0)
            ax2.plot(game_days, avg_prices, marker='o', label=playthrough_name, linewidth=2)
        ax2.set_ylabel('Average Price')
        ax2.set_title('Average Goods Prices', fontweight='bold', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Unprofitable buildings
        ax3 = fig.add_subplot(gs[1, 1])
        for playthrough_name, data in playthrough_data_dict.items():
            game_days = [dp.get('metadata', {}).get('game_day', 0) for dp in data]
            unprofitable_pct = []
            for dp in data:
                profitability = dp.get('building_profitability', {})
                if profitability:
                    total = len(profitability)
                    unprofitable = sum(1 for v in profitability.values() if v.get('avg', 0) < 0)
                    unprofitable_pct.append((unprofitable / total) * 100 if total > 0 else 0)
                else:
                    unprofitable_pct.append(0)
            ax3.plot(game_days, unprofitable_pct, marker='o', label=playthrough_name, linewidth=2)
        ax3.set_ylabel('Unprofitable Buildings (%)')
        ax3.set_title('Building Profitability', fontweight='bold', fontsize=12)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Overproduction issues
        ax4 = fig.add_subplot(gs[2, :])
        for playthrough_name, data in playthrough_data_dict.items():
            game_days = [dp.get('metadata', {}).get('game_day', 0) for dp in data]
            overproduction_counts = [len(dp.get('overproduction_ratio', {})) for dp in data]
            ax4.plot(game_days, overproduction_counts, marker='o', label=playthrough_name, linewidth=2)
        ax4.set_xlabel('Game Day')
        ax4.set_ylabel('Goods with Overproduction')
        ax4.set_title('Overproduction Issues', fontweight='bold', fontsize=12)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Save
        filename = self.output_dir / "comparison_dashboard.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Saved: {filename}")
        plt.close()
    
    def generate_all_visualizations(self, playthrough_data: List[Dict],
                                   playthrough_name: str = "default",
                                   key_goods: List[str] = None):
        """Generate all standard visualizations"""
        print(f"\nGenerating visualizations for: {playthrough_name}")
        print("=" * 60)

        if key_goods is None:
            print("Plotting prices for all detected goods")
        else:
            print(f"Plotting prices for selected goods: {len(key_goods)}")

        self.plot_goods_prices_over_time(playthrough_data, key_goods, playthrough_name)
        self.plot_price_crashes(playthrough_data, playthrough_name)
        self.plot_overproduction_heatmap(playthrough_data, playthrough_name)
        self.plot_building_profitability(playthrough_data, playthrough_name)
        
        print("=" * 60)
        print(f"All visualizations saved to: {self.output_dir}")


if __name__ == "__main__":
    # Example test
    print("Visualizer module loaded successfully")
