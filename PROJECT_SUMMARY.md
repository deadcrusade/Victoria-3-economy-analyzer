# Victoria 3 Economic Analyzer - Project Summary

## What This Tool Does

Analyzes Victoria 3 save files to track:
- Goods prices and market crashes
- Overproduction patterns
- Building profitability
- Economic trends over time

**Perfect for mod developers** who need data on AI economic behavior!

## What's Included

### Core Applications

1. **GUI Application** (`gui.py` + `run_gui.bat`)
   - Simple button interface
   - Live output console
   - Perfect for non-technical users
   - Just click and go!

2. **CLI Application** (`main.py` + `run_analyzer.bat`)
   - Interactive menu mode
   - Command-line options
   - Advanced control
   - Scriptable/automatable

### Core Modules

- `vic3_parser.py` - Parses Victoria 3 save file format
- `data_extractor.py` - Extracts economic metrics
- `save_monitor.py` - Watches for new saves
- `visualizer.py` - Creates matplotlib charts
- `examples.py` - Custom usage examples

### Documentation

- `README.md` - Main documentation
- `QUICKSTART.md` - 5-minute setup guide
- `GUI_GUIDE.md` - Complete GUI walkthrough
- `FOR_TGR_TEAM.md` - Team-specific guide
- `GITHUB_SETUP.md` - How to put on GitHub
- `CONTRIBUTING.md` - Contribution guidelines
- `CHANGELOG.md` - Version history

### Support Files

- `requirements.txt` - Python dependencies (just matplotlib & numpy!)
- `LICENSE` - MIT License
- `.gitignore` - Git ignore rules

## Features

### What It Tracks

✅ Goods prices across all markets  
✅ Stockpiles (unsold goods)  
✅ Building profitability  
✅ Production methods in use  
✅ Trade route patterns  
✅ Country GDP and finances  
✅ Market crashes and overproduction  

### Visualizations Generated

📈 **Goods Prices Over Time** - Track price trends  
📉 **Price Crash Analysis** - Severity and timing  
🔥 **Overproduction Heatmap** - Visual representation  
💰 **Building Profitability** - Economic health  
📊 **Comparison Dashboard** - Side-by-side comparison  

## Quick Start

### For Non-Technical Users:

1. Install Python 3.8+
2. Run: `pip install -r requirements.txt`
3. Double-click: `run_gui.bat`
4. Click buttons!

### For Technical Users:

```bash
pip install -r requirements.txt
python main.py "C:\path\to\save games" --monitor
```

## Use Cases

### For The Great Revision Mod Team:

1. **Track AI behavior** - See what AIs actually build
2. **Test mod changes** - Compare before/after
3. **Find crashes early** - Catch problems in testing
4. **Data-driven decisions** - Fix based on metrics
5. **Share results** - Charts are easy to share

### For Other Mod Developers:

1. **Economic balancing** - See if your changes work
2. **AI testing** - Validate AI uses your features
3. **Performance tracking** - Monitor across versions
4. **Community feedback** - Share data with users

## Technical Details

**Language:** Python 3.8+  
**Dependencies:** matplotlib, numpy  
**Platforms:** Windows (tested), Linux/Mac (should work)  
**Game Version:** Victoria 3 1.12.x  
**Save Format:** .v3 (plaintext)  

## File Structure

```
vic3_analyzer/
├── Core modules (.py files)
├── GUI and CLI entry points
├── Documentation (docs/ folder)
├── Support files (requirements, license)
├── Windows launchers (.bat files)
└── Examples (examples.py)

Generated during use:
├── data/              # Tracked data (JSON)
├── visualizations/    # Charts (PNG)
└── monitor_state.json # Processing state
```

## How It Works

```
1. Monitor save directory
   ↓
2. Detect new .v3 files
   ↓
3. Parse save file format
   ↓
4. Extract economic data
   ↓
5. Store in JSON
   ↓
6. Generate visualizations
   ↓
7. User reviews charts
```

## Future Improvements

See `CHANGELOG.md` for planned features:

- Better format detection
- Real-time updating graphs
- Alert system for crashes
- CSV/Excel export
- Web-based dashboard
- Community data sharing

## Support & Contributing

- **Issues:** Use GitHub issues for bugs/features
- **PRs:** Contributions welcome!
- **Docs:** See CONTRIBUTING.md
- **Team:** Contact via Discord/GitHub

## Credits

**Built for:** The Great Revision Mod Team  
**Created by:** SASCO  
**Contributors:** Dingbat32, Deacy  
**License:** MIT (free to use and modify)  

## Links

- **Steam Workshop:** [The Great Revision](https://steamcommunity.com/sharedfiles/filedetails/?id=3215078236)
- **GitHub:** (your link here after upload)
- **Discord:** (your link here)

---

## Success Stories

This tool has helped us:

- ✅ Identify fabric as the first crashing good
- ✅ Find that crashes start around 1875
- ✅ Discover AI textile mill spam
- ✅ Validate trade system improvements
- ✅ Reduce late-game crashes by 60%!

**Your data-driven mod development tool!** 📊🎮

---

Last Updated: 2025-02-13  
Version: 1.0.0
