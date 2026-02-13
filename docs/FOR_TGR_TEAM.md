# For The Great Revision Team

Hey team! This tool was built specifically to help us optimize The Great Revision mod's economy. Here's how to use it effectively for our mod development.

## 🎯 Why We Built This

We kept seeing late-game market crashes but didn't know:
- **Which goods** crash first?
- **When** crashes start happening?
- **Why** the AI builds too much?
- **What works** when we make changes?

This analyzer gives us the data to answer all these questions!

## 🚀 Getting Started (Super Simple!)

### First Time Setup

1. **Get Python** (if you don't have it)
   - Go to python.org
   - Download Python 3.8+
   - Install (check "Add Python to PATH")

2. **Get this tool**
   - Clone/download from GitHub
   - Or just grab the folder from Discord

3. **Install dependencies**
   - Open terminal in the folder
   - Run: `pip install -r requirements.txt`

### Using the GUI (Recommended!)

**Just double-click: `run_gui.bat`**

That's it! The GUI opens and you can click buttons.

## 📊 How to Help Test The Mod

### Testing Workflow:

1. **Before starting a test game:**
   ```
   - Open GUI (run_gui.bat)
   - Click "Browse" → select your save folder
   - Click "Start Monitoring"
   ```

2. **Play Victoria 3 normally**
   - Use our mod
   - Let auto-saves happen (I recommend monthly)
   - Play until 1880+ if possible (that's when crashes happen)
   - GUI tracks everything automatically

3. **When done / when crashes occur:**
   ```
   - Click "Stop Monitoring" in GUI
   - Click "Open Charts Folder"
   - Review the charts
   ```

4. **Share results:**
   - Screenshots of charts → Discord
   - Attach to GitHub issues
   - Mention specific problems you found

### What to Look For

When reviewing charts, look for:

#### ⚠️ Red Flags:
- **Prices below $10** - Market crash!
- **Prices below $5** - Critical failure
- **70%+ unprofitable buildings** - Economy is dead
- **Steep price drops** - Overproduction starting

#### ✅ Good Signs:
- **Prices $20-40** - Healthy market
- **Steady trends** - Stable economy
- **< 30% unprofitable** - Good profitability
- **No red zones in heatmap** - No oversupply

### Testing Different Versions

When we make mod changes:

1. **Name your test saves clearly:**
   ```
   Before: "test_baseline"
   After:  "test_trade_fix_v1"
   ```

2. **The analyzer automatically tracks them separately!**

3. **Use comparison dashboard** to see if changes helped:
   ```
   - Charts will show both versions
   - Compare crash counts
   - See if prices improved
   ```

## 🔍 What We're Looking For

### Our Mod-Specific Issues:

#### Trade System
- Are AIs importing instead of building?
- Do trade routes form efficiently?
- Which goods are most traded?

**What to check:** Trade routes data in status

#### AI Building Spam
- Which industries do AIs overbuild?
- What production methods are used?
- Do they adapt to prices?

**What to check:** Building profitability charts

#### Taxation Reform
- Do tax changes affect prices?
- Budget vs. market health?
- Which tax policies work best?

**What to check:** Correlate dates with price changes

#### Late Game Crashes
- What year do crashes start?
- Which goods crash first?
- Does it cascade to other goods?

**What to check:** Price crash analysis chart

## 📁 Sharing Data with Team

### Discord

Share these from the `visualizations` folder:
- `*_price_crashes.png` - Shows severity
- `*_overproduction_heatmap.png` - Visual overview
- `comparison_dashboard.png` - Version comparisons

### GitHub Issues

When reporting a bug:
1. Attach relevant charts
2. Include save file name and date
3. Mention which mod version
4. Describe what you saw in-game

Example:
```markdown
## Economy Crash at 1875

Playing with version 1.12.4, economy crashes around 1875.

**Save:** test_baseline_1875_1_1.v3

**Charts show:**
- Steel crashes to $3
- Tools follow shortly after
- 80% of factories unprofitable

See attached: baseline_price_crashes.png
```

## 🤝 Team Coordination

### Who Should Test What:

**SASCO (Lead Dev):**
- Baseline tests of each major version
- Comparison testing before releases
- Final validation

**Dingbat32:**
- AI behavior testing
- Trade system validation
- Building spam patterns

**Deacy:**
- Different nation playthroughs
- Varied starting conditions
- Edge case testing

**Everyone:**
- Report anything weird in charts
- Share interesting patterns
- Suggest improvements to analyzer

## 💡 Pro Tips for Testing

1. **Play on speed 5**
   - Get to late game faster
   - More auto-saves = more data

2. **Set auto-save to monthly**
   - Good balance of data points
   - Not too many files

3. **Test to 1880+**
   - Crashes happen late game
   - Early game looks fine

4. **Name saves clearly**
   - `test_trade_v1`, `test_trade_v2`
   - Analyzer groups automatically

5. **Take notes**
   - When you make mod changes
   - What you expected vs. what happened
   - Correlate with chart dates

## 🐛 If Something Goes Wrong

### GUI Issues:

**GUI won't start:**
- Check Python is installed
- Run: `pip install -r requirements.txt`
- Try running: `python gui.py`

**"Directory not found":**
- Click Browse button
- Manually select save folder

**Charts look empty:**
- Need 2+ saves minimum
- Play longer sessions
- Check `data` folder exists

### Ask for Help:

- Discord channel
- GitHub issues
- DM me (SASCO) or Dingbat32

## 📈 Understanding Our Data

### Quick Reference:

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Price | $20-40 | $10-20 | < $10 |
| Unprofitable % | < 30% | 30-50% | > 50% |
| Overproduction | < 50 | 50-100 | > 100 |
| Crashes | 0-5 | 5-15 | 15+ |

### Common Patterns We've Seen:

1. **The Fabric Cascade**
   - Fabric crashes first
   - Clothes follow
   - Luxury clothes last
   - **Why:** AI spam textile mills

2. **The Steel Death Spiral**
   - Iron oversupply
   - Steel prices drop
   - Tool factories close
   - Everything collapses
   - **Why:** Too many steel mills

3. **The Food Surplus**
   - Grain drops to $5
   - But this is actually OK!
   - People eat more
   - **Why:** Population growth slows late game

## 🎯 Our Testing Goals

### Version 1.12.4 Goals:

- [ ] Identify top 5 crashing goods
- [ ] Find when crashes typically start
- [ ] Test if trade changes help
- [ ] Validate AI building behavior
- [ ] Compare with vanilla behavior

### How You Can Help:

1. **Run at least one full playthrough to 1890**
2. **Test both major powers and small nations**
3. **Document anything unexpected**
4. **Share your visualizations**
5. **Suggest fixes based on data**

## 🚀 Let's Fix This Economy!

With this tool, we can finally see exactly what's breaking and when. Let's use the data to make The Great Revision the best economic overhaul mod for Victoria 3!

Questions? Ping me on Discord! 

— SASCO

---

**Remember:** The more we test, the better data we get, the better the mod becomes! 📊🎮
