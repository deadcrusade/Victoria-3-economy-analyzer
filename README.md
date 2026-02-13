# Victoria 3 Economic Analyzer

Real-time save game monitoring and economic analysis tool for Victoria 3. Perfect for mod developers tracking overproduction, price crashes, and market dynamics.

**Built for The Great Revision mod team** - now with **GUI and CLI** interfaces!

## ✨ Features

- 🔍 **Real-time monitoring** - Automatically processes new auto-saves and manual saves
- 📊 **Economic metrics** - Tracks goods prices, production, stockpiles, and building profitability
- 📈 **Visualizations** - Beautiful matplotlib charts showing trends over time
- 🔄 **Multi-playthrough** - Compare multiple campaigns side-by-side
- 🎯 **Overproduction detection** - Identifies goods with market crashes
- 💰 **Profitability analysis** - Tracks which buildings are losing money
- 🖥️ **Easy-to-use GUI** - Simple buttons for non-technical users
- ⌨️ **Powerful CLI** - Full command-line control for advanced users

## 📥 Installation

### Option A: Standalone Executable (Easiest!)

**No Python installation required!** Perfect for non-technical users.

**Windows:**
1. Download `Vic3_Analyzer.exe` from [Releases](../../releases)
2. Double-click to run
3. That's it!

**Building it yourself:**
```bash
build_exe.bat  # Creates standalone .exe
```

See [BUILD.md](docs/BUILD.md) for detailed instructions.

**File size:** ~50-100 MB (includes Python + all dependencies)

---

### Option B: Python Source (For Developers)

**Prerequisites:**
- Python 3.8 or higher
- Windows (fully tested) / Linux / macOS (should work)

**Quick Setup:**

1. **Clone or download** this repository

2. **Install dependencies:**
```bash
cd vic3_analyzer
pip install -r requirements.txt
```

That's it! Only needs matplotlib and numpy.

## 🚀 Usage

### 🖥️ GUI Mode (Recommended for Everyone)

**Easiest way to start - just double-click!**

**Windows:**
```
Double-click: run_gui.bat
```

**Or run manually:**
```bash
python gui.py
```

#### GUI Features:

The graphical interface provides simple buttons for all functions:

- **📊 Analyze Existing Saves** - Process all saves currently in your folder
- **▶️ Start/Stop Monitoring** - Real-time tracking while you play (checks every 60 seconds)
- **📈 Generate Charts** - Create visualizations from tracked data
- **ℹ️ Show Status** - See what playthroughs are being tracked
- **📁 Open Charts Folder** - Quick access to generated visualizations
- **🔄 Reset Data** - Clear all tracking and start fresh

**GUI shows live output** - see exactly what's happening in real-time!

---

### ⌨️ Command Line Mode (Advanced)

For advanced users who prefer command-line control:

#### Finding Your Save Directory

Your Victoria 3 saves are typically located at:
```
C:\Users\YourName\Documents\Paradox Interactive\Victoria 3\save games
```

Replace `YourName` with your Windows username.

#### Interactive CLI Mode

#### Interactive CLI Mode

Run the analyzer in interactive menu mode:

```bash
python main.py "C:\Users\YourName\Documents\Paradox Interactive\Victoria 3\save games"
```

This opens a text menu where you can select actions.

#### CLI Command Line Options

**Analyze existing saves:**
```bash
python main.py "C:\path\to\save games" --analyze
```

#### Start Real-Time Monitoring
Watch for new saves and process them automatically:
```bash
python main.py "C:\path\to\save games" --monitor
```

Check every 30 seconds instead of 60:
```bash
python main.py "C:\path\to\save games" --monitor --interval 30
```

Press `Ctrl+C` to stop monitoring and generate final visualizations.

#### Generate Visualizations Only
Create charts from existing tracked data:
```bash
python main.py "C:\path\to\save games" --visualize
```

#### Check Status
See what's currently tracked:
```bash
python main.py "C:\path\to\save games" --status
```

## What Gets Tracked

### Economic Metrics
- **Goods Prices** - Price of all goods across markets
- **Stockpiles** - Unsold goods piling up in markets
- **Production** - What's being produced vs consumed
- **Building Profitability** - Which buildings are making/losing money
- **Trade Routes** - Import/export patterns
- **Country GDP** - Economic performance by nation

### Visualizations Generated

1. **Goods Prices Over Time**
   - Tracks key goods (grain, steel, tools, etc.)
   - Shows price trends
   - Identifies crashes

2. **Price Crash Analysis**
   - Number of goods with crashed prices
   - Severity of crashes over time
   - Highlights problem periods

3. **Overproduction Heatmap**
   - Shows which goods are oversupplied
   - Color-coded by severity
   - Tracks progression through game

4. **Building Profitability**
   - Percentage of unprofitable buildings
   - Tracks economic health
   - Shows when industries become unsustainable

5. **Comparison Dashboard** (when multiple playthroughs exist)
   - Side-by-side comparison
   - See which changes improved economy
   - A/B test your mod tweaks

## Workflow for Mod Testing

### Recommended Process

1. **First playthrough - baseline:**
```bash
python main.py "C:\path\to\saves" --monitor --interval 30
```

2. **Play your game** - The analyzer runs in background, processing each auto-save

3. **Stop monitoring** - Press `Ctrl+C` when done (or when crashes occur)

4. **Review visualizations** - Check `./visualizations/` folder

5. **Make mod changes** based on what you found

6. **Start new playthrough** - Analyzer automatically tracks it separately

7. **Compare results:**
```bash
python main.py "C:\path\to\saves" --visualize
```

### Tips for Best Results

- **Use auto-saves:** Set auto-save frequency to monthly or quarterly
- **Name your saves:** Use descriptive names like "test_v1" vs "test_v2"
- **Let games run long:** Market crashes often appear in late game (1880+)
- **Multiple test runs:** Run 3-4 campaigns to identify patterns vs random variance
- **Check specific goods:** If you changed trade, track those goods specifically

## Output Structure

```
vic3_analyzer/
├── data/                          # Tracked data (JSON)
│   ├── campaign_1/
│   │   ├── data_20240213_143022.json
│   │   └── data_20240213_150033.json
│   └── campaign_2/
│       └── ...
├── visualizations/                # Generated charts
│   ├── campaign_1_prices_over_time.png
│   ├── campaign_1_price_crashes.png
│   ├── campaign_1_overproduction_heatmap.png
│   ├── campaign_1_building_profitability.png
│   └── comparison_dashboard.png   # Compares all campaigns
└── monitor_state.json             # Tracks processed files
```

## Interpreting Results

### Price Crashes (< $10)
- Normal price range: $20-40
- Below $15: Moderate oversupply
- Below $10: **Severe crash** - too much production
- Below $5: Market is completely flooded

### Overproduction Ratio
- Higher = worse oversupply
- Calculated as: `stockpile / (price + 0.1)`
- Ratio > 100: Major problem
- Ratio > 500: Critical issue

### Building Profitability
- Below 50% unprofitable: Healthy economy
- 50-70% unprofitable: Warning signs
- Above 70% unprofitable: **Economic collapse**

## Troubleshooting

### "Directory not found"
Double-check your save path. Common mistakes:
- Missing quotes around path with spaces
- Wrong username in path
- Game installed on different drive

### "No data to plot"
- Need at least 2 save files to show trends
- Make sure you ran `--analyze` or `--monitor` first
- Check `./data/` folder has JSON files

### Parser errors
Victoria 3 save format can vary between versions. If you get parsing errors:
1. Check you're using game version 1.12.x or similar
2. Open an issue with your game version

### Visualizations look wrong
- Need multiple data points (3+ saves recommended)
- Early game may not show issues (crashes happen late game)
- Try playing to 1880+ for better data

## Advanced Customization

### Track Specific Goods

Edit `data_extractor.py` and modify the `KEY_GOODS` list:

```python
KEY_GOODS = [
    'grain', 'meat', 'fish',      # Your food goods
    'steel', 'tools', 'engines',  # Industrial goods you care about
    # ... add your custom goods
]
```

### Adjust Price Crash Threshold

In `data_extractor.py`, find `_identify_price_crashes()`:

```python
if price > 0 and price < 10.0:  # Change this threshold
```

### Custom Visualizations

Add your own chart functions in `visualizer.py`. The data structure is:

```python
{
    'metadata': {'date': '1850.5.1', 'game_day': 5234},
    'goods_economy': {
        'grain': {'price': 18.5, 'buy_volume': 1200},
        'steel': {'price': 32.1, 'buy_volume': 850},
        # ...
    },
    'price_crashes': [
        {'goods': 'fabric', 'price': 4.2, 'severity': 5.8},
        # ...
    ],
    'overproduction_ratio': {
        'grain': 145.2,
        'steel': 67.3,
        # ...
    }
}
```

## For "The Great Revision" Mod

Since you're working on a comprehensive overhaul with:
- New taxation system
- Trade rework
- AI strategies
- Loan mechanics

This analyzer is perfect for:

1. **Testing AI trade behavior** - Are they using your import/export system?
2. **Loan system stress testing** - Do countries go bankrupt?
3. **Market crash detection** - Which goods crash most in late game?
4. **Building spam detection** - Are AIs over-building certain industries?
5. **Taxation impact** - How do different tax policies affect prices?

### Specific Metrics to Watch

For your mod specifically:

- **Trade routes** - Is your "import instead of build" mechanic working?
- **Building profitability** - Are buildings unprofitable because of your changes?
- **Price crashes** - Which industries collapse first?
- **Late game trends** - Do crashes accelerate after 1880?

## 📚 Documentation

Detailed guides for different users:

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get running in 5 minutes
- **[GUI User Guide](docs/GUI_GUIDE.md)** - Complete button-by-button walkthrough
- **[Building Executables](docs/BUILD.md)** - Create standalone .exe with no Python needed
- **[Distribution Guide](docs/DISTRIBUTION.md)** - Choose between .exe and source
- **[For TGR Team](docs/FOR_TGR_TEAM.md)** - Team-specific workflow and testing guide
- **[Contributing](CONTRIBUTING.md)** - How to contribute to this project
- **[Changelog](CHANGELOG.md)** - Version history and planned features

## Contributing

Found a bug? Have suggestions? Open an issue or submit a PR!

## License

Free to use and modify for Victoria 3 modding purposes.

---

**Pro Tip:** Run monitoring overnight while you sleep - let the game run on speed 5, and wake up to full analytics! 🎮📊
