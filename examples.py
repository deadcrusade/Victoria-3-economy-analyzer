"""
Example: Custom Analysis Script
Shows how to use the analyzer components programmatically
"""

from pathlib import Path
from data_extractor import EconomicExtractor
from visualizer import EconomicVisualizer
from save_monitor import SaveMonitor


def example_single_save_analysis():
    """Analyze a single save file"""
    print("Example 1: Analyzing a single save file")
    print("-" * 60)
    
    # Point to your save file
    save_file = r"C:\path\to\your\save.v3"
    
    # Extract data
    extractor = EconomicExtractor(save_file)
    data = extractor.extract_all()
    
    # Print summary
    print(extractor.get_summary(data))
    
    # Access specific data
    print("\nTop 10 Price Crashes:")
    for crash in data['price_crashes'][:10]:
        print(f"  {crash['goods']}: ${crash['price']:.2f}")


def example_custom_goods_tracking():
    """Track specific goods you care about"""
    print("\nExample 2: Custom goods tracking")
    print("-" * 60)
    
    # Your custom goods list (e.g., goods affected by your mod)
    my_goods = ['steel', 'tools', 'engines', 'electricity']
    
    save_dir = r"C:\path\to\save games"
    monitor = SaveMonitor(save_dir)
    
    # Load a playthrough
    playthroughs = monitor.get_all_playthroughs()
    if playthroughs:
        data = monitor.load_playthrough_data(playthroughs[0])
        
        # Track your goods over time
        for point in data:
            date = point['metadata']['date']
            goods_economy = point['goods_economy']
            
            print(f"\nDate: {date}")
            for goods in my_goods:
                if goods in goods_economy:
                    price = goods_economy[goods].get('price', 0)
                    print(f"  {goods}: ${price:.2f}")


def example_custom_visualization():
    """Create custom visualization"""
    print("\nExample 3: Custom visualization")
    print("-" * 60)
    
    import matplotlib.pyplot as plt
    
    save_dir = r"C:\path\to\save games"
    monitor = SaveMonitor(save_dir)
    
    playthroughs = monitor.get_all_playthroughs()
    if not playthroughs:
        print("No data available")
        return
    
    data = monitor.load_playthrough_data(playthroughs[0])
    
    # Extract custom metric: Average building profitability
    game_days = []
    avg_profits = []
    
    for point in data:
        game_day = point['metadata']['game_day']
        profitability = point['building_profitability']
        
        if profitability:
            profits = [v['avg'] for v in profitability.values()]
            avg_profit = sum(profits) / len(profits)
            
            game_days.append(game_day)
            avg_profits.append(avg_profit)
    
    # Create custom chart
    plt.figure(figsize=(12, 6))
    plt.plot(game_days, avg_profits, marker='o', linewidth=2, color='steelblue')
    plt.axhline(y=0, color='red', linestyle='--', label='Break-even')
    plt.xlabel('Game Day')
    plt.ylabel('Average Building Profit')
    plt.title('Average Building Profitability Over Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('custom_analysis.png', dpi=150)
    print("Saved: custom_analysis.png")


def example_find_crash_pattern():
    """Detect when market crashes typically occur"""
    print("\nExample 4: Finding crash patterns")
    print("-" * 60)
    
    save_dir = r"C:\path\to\save games"
    monitor = SaveMonitor(save_dir)
    
    playthroughs = monitor.get_all_playthroughs()
    if not playthroughs:
        print("No data available")
        return
    
    # Analyze when crashes start occurring
    for playthrough in playthroughs:
        data = monitor.load_playthrough_data(playthrough)
        
        print(f"\nPlaythrough: {playthrough}")
        
        first_crash = None
        for point in data:
            crashes = point['price_crashes']
            if crashes and not first_crash:
                first_crash = point['metadata']
                print(f"  First crash at: {first_crash['date']} (Day {first_crash['game_day']})")
                print(f"  Crashed goods: {', '.join(c['goods'] for c in crashes[:5])}")
                break
        
        if not first_crash:
            print("  No crashes detected")


def example_compare_mod_versions():
    """Compare economic performance between mod versions"""
    print("\nExample 5: Comparing mod versions")
    print("-" * 60)
    
    save_dir = r"C:\path\to\save games"
    monitor = SaveMonitor(save_dir)
    
    # Assume you named your campaigns "mod_v1", "mod_v2", etc.
    versions = ["mod_v1", "mod_v2"]
    
    for version in versions:
        data = monitor.load_playthrough_data(version)
        
        if not data:
            print(f"{version}: No data")
            continue
        
        # Get final state
        final = data[-1]
        
        crashes = final['price_crashes']
        overproduction = final['overproduction_ratio']
        profitability = final['building_profitability']
        
        unprofitable_pct = 0
        if profitability:
            unprofitable = sum(1 for v in profitability.values() if v['avg'] < 0)
            unprofitable_pct = (unprofitable / len(profitability)) * 100
        
        print(f"\n{version}:")
        print(f"  Final date: {final['metadata']['date']}")
        print(f"  Price crashes: {len(crashes)}")
        print(f"  Overproduction issues: {len(overproduction)}")
        print(f"  Unprofitable buildings: {unprofitable_pct:.1f}%")


def example_export_to_csv():
    """Export data to CSV for external analysis"""
    print("\nExample 6: Export to CSV")
    print("-" * 60)
    
    import csv
    
    save_dir = r"C:\path\to\save games"
    monitor = SaveMonitor(save_dir)
    
    playthroughs = monitor.get_all_playthroughs()
    if not playthroughs:
        print("No data available")
        return
    
    data = monitor.load_playthrough_data(playthroughs[0])
    
    # Export goods prices over time
    with open('goods_prices.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        goods_names = set()
        for point in data:
            goods_names.update(point['goods_economy'].keys())
        
        header = ['date', 'game_day'] + sorted(goods_names)
        writer.writerow(header)
        
        # Data rows
        for point in data:
            row = [
                point['metadata']['date'],
                point['metadata']['game_day']
            ]
            
            goods_economy = point['goods_economy']
            for goods in sorted(goods_names):
                price = goods_economy.get(goods, {}).get('price', 0)
                row.append(price)
            
            writer.writerow(row)
    
    print("Exported to: goods_prices.csv")
    print("You can now open this in Excel or use with pandas!")


if __name__ == "__main__":
    print("="*60)
    print("VICTORIA 3 ANALYZER - CUSTOM EXAMPLES")
    print("="*60)
    print("\nThis file contains example code showing how to:")
    print("1. Analyze a single save file")
    print("2. Track custom goods")
    print("3. Create custom visualizations")
    print("4. Find crash patterns")
    print("5. Compare mod versions")
    print("6. Export to CSV")
    print("\nEdit this file and uncomment the examples you want to run.")
    print("="*60)
    
    # Uncomment the examples you want to run:
    
    # example_single_save_analysis()
    # example_custom_goods_tracking()
    # example_custom_visualization()
    # example_find_crash_pattern()
    # example_compare_mod_versions()
    # example_export_to_csv()
