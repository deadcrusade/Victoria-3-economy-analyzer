# GUI Usage Guide

This guide will walk you through using the Victoria 3 Economic Analyzer GUI - perfect for team members who aren't comfortable with command lines!

## Starting the GUI

### Windows (Easiest!)

1. Navigate to the `vic3_analyzer` folder
2. **Double-click `run_gui.bat`**
3. That's it! The GUI will open automatically

### Any Platform

1. Open terminal/command prompt
2. Navigate to `vic3_analyzer` folder:
   ```bash
   cd path/to/vic3_analyzer
   ```
3. Run:
   ```bash
   python gui.py
   ```

## First Time Setup

When the GUI opens for the first time:

### 1. Set Your Save Directory

The GUI tries to auto-detect your Victoria 3 save folder, but if it's wrong:

1. Click the **"Browse..."** button
2. Navigate to your save games folder (usually):
   ```
   C:\Users\YourName\Documents\Paradox Interactive\Victoria 3\save games
   ```
3. Select the folder
4. The path will appear in the text box

**Tip:** This setting is remembered between sessions!

## Main Functions

### 📊 Analyze Existing Saves

**What it does:** Processes all save files currently in your folder

**When to use:** 
- First time using the analyzer
- After playing without monitoring
- To catch up on saves you already have

**Steps:**
1. Make sure save directory is set
2. Click **"📊 Analyze Existing Saves"**
3. Watch the output console - you'll see each save being processed
4. Visualizations are generated automatically when done

**Output:** Charts appear in the `visualizations` folder

---

### ▶️ Start Monitoring / ⏸️ Stop Monitoring

**What it does:** Watches your save folder and processes new saves as they appear

**When to use:**
- While playing Victoria 3
- Testing your mod changes
- Long play sessions

**Steps:**
1. Click **"▶️ Start Monitoring"** BEFORE or WHILE playing
2. The button changes to **"⏸️ Stop Monitoring"**
3. Play Victoria 3 normally - auto-saves are processed automatically
4. You'll see new saves appear in the output console
5. Click **"⏸️ Stop Monitoring"** when done
6. Visualizations are generated automatically

**How it works:**
- Checks for new saves every 60 seconds
- Processes them automatically
- You can leave it running in the background

**Tip:** Set Victoria 3 to auto-save monthly or quarterly for best results!

---

### 📈 Generate Charts

**What it does:** Creates visualization charts from your tracked data

**When to use:**
- After analyzing or monitoring
- To regenerate charts with latest data
- To compare multiple playthroughs

**Steps:**
1. Click **"📈 Generate Charts"**
2. Wait for processing (shown in output)
3. Charts appear in `visualizations` folder

**Charts created:**
- Price trends over time
- Price crash analysis  
- Overproduction heatmap
- Building profitability
- Comparison dashboard (if multiple playthroughs)

---

### ℹ️ Show Status

**What it does:** Shows what's currently being tracked

**When to use:**
- Check if any playthroughs are tracked
- See how many saves have been processed
- View latest economic snapshot

**Output shows:**
- Number of playthroughs
- Data points per playthrough
- Date ranges
- Latest crash/overproduction stats

---

### 📁 Open Charts Folder

**What it does:** Opens the visualizations folder in your file explorer

**When to use:**
- Quickly view generated charts
- Share charts with team members
- Copy charts to documents

**Tip:** You can also just navigate to the `visualizations` folder manually!

---

### 🔄 Reset Data

**What it does:** Clears ALL tracked data and starts fresh

**When to use:**
- Starting a new mod version test
- Data got corrupted
- Want to start tracking from scratch

**Warning:** This deletes everything! You'll be asked to confirm.

---

## Understanding the Output Console

The console shows real-time information:

```
[Analyzing Existing Saves]
================================================================================
Processing: campaign_autosave_1870_5_1.v3
  Date: 1870.5.1
  Price crashes: 12
  Overproduction issues: 8
------------------------------------------------------------
Processing: campaign_autosave_1871_1_1.v3
  Date: 1871.1.1
  Price crashes: 15
  Overproduction issues: 11
------------------------------------------------------------
✓ Processed 2 save files
Generating visualizations...
✓ All visualizations generated!
```

**Key indicators:**
- **Price crashes** - Number of goods below $10
- **Overproduction issues** - Goods with severe oversupply

---

## Tips for Team Collaboration

### For The Great Revision Team:

1. **Name your test saves clearly:**
   - `test_trade_v1`, `test_trade_v2`, etc.
   - The analyzer groups saves by name automatically

2. **Share visualizations:**
   - Charts are PNG files - easy to share on Discord
   - Include in GitHub issues for bug reports

3. **Track multiple versions:**
   - Each test run is tracked separately
   - Use comparison dashboard to see improvements

4. **Regular monitoring:**
   - Run monitoring during longer test sessions
   - Helps catch exactly when crashes start

---

## Common Issues

### "Directory not found"
**Problem:** Can't find save directory  
**Solution:** Click Browse and manually select the folder

### "No data to plot"
**Problem:** Tried to generate charts with no data  
**Solution:** Run "Analyze Existing Saves" or "Start Monitoring" first

### Nothing happens when clicking buttons
**Problem:** Python or dependencies issue  
**Solution:** 
1. Close GUI
2. Run in terminal: `pip install -r requirements.txt`
3. Try again

### Charts look wrong/empty
**Problem:** Not enough data  
**Solution:** Need at least 2-3 saves for meaningful trends

---

## Where Files Are Stored

```
vic3_analyzer/
├── data/                      # Tracked data (JSON)
│   ├── campaign_1/
│   ├── campaign_2/
│   └── ...
├── visualizations/            # Generated charts (PNG)
│   ├── campaign_1_prices_over_time.png
│   ├── campaign_1_price_crashes.png
│   └── ...
└── monitor_state.json         # What's been processed
```

**You can delete these folders to start completely fresh!**

---

## Best Practices

### For Mod Testing:

1. **Before playing:**
   - Start the GUI
   - Set save directory
   - Click "Start Monitoring"

2. **While playing:**
   - Let Victoria 3 auto-save (monthly recommended)
   - Check GUI occasionally to see if saves are processing

3. **After playing:**
   - Click "Stop Monitoring"
   - Check visualizations folder
   - Review charts for problems

4. **For comparison:**
   - Make mod changes
   - Play again (new playthrough name)
   - GUI automatically tracks it separately
   - Use comparison dashboard to see difference

---

## Need Help?

- Check the main [README.md](../README.md) for detailed info
- Look at [examples.py](../examples.py) for custom usage
- Open an issue on GitHub if you find bugs

---

**Happy modding! May your markets never crash! 📊🎮**
