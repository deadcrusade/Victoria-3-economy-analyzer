# Quick Start Guide

Get started with Victoria 3 Economic Analyzer in 5 minutes!

## Installation (One Time)

### 1. Install Python

Download Python 3.8 or higher from [python.org](https://www.python.org/downloads/)

**Important:** During installation, check "Add Python to PATH"

### 2. Get the Analyzer

**Option A: Download ZIP**
1. Click the green "Code" button on GitHub
2. Click "Download ZIP"
3. Extract somewhere (e.g., Desktop)

**Option B: Git Clone**
```bash
git clone https://github.com/yourusername/vic3_analyzer.git
cd vic3_analyzer
```

### 3. Install Dependencies

Open terminal/command prompt in the `vic3_analyzer` folder and run:

```bash
pip install -r requirements.txt
```

That's it! Installation complete.

`requirements.txt` includes `matplotlib`, `numpy`, and `watchdog` (continuous file watching).

Binary Victoria 3 `.v3` saves are parsed through bundled native runtime (`vendor/librakaly/win-x64/rakaly.dll`).

---

## Using the Analyzer

### For Non-Technical Users (GUI)

**Windows:**
1. Double-click `run_gui.bat`
2. Click "Browse" and select your save folder
3. Click buttons to analyze!

**Mac/Linux:**
```bash
python gui.py
```

See [GUI Guide](docs/GUI_GUIDE.md) for detailed instructions.

---

### For Technical Users (CLI)

**Interactive menu:**
```bash
python main.py "C:\path\to\save games"
```

**Direct commands:**
```bash
# Analyze all saves
python main.py "C:\path\to\save games" --analyze

# Start monitoring
python main.py "C:\path\to\save games" --monitor

# Generate visualizations
python main.py "C:\path\to\save games" --visualize
```

See [README.md](README.md) for all CLI options.

---

## Your First Analysis

### Step 1: Find Your Saves

Victoria 3 saves are usually here:
```
C:\Users\YourName\Documents\Paradox Interactive\Victoria 3\save games
```

### Step 2: Run Analysis

**GUI:** Click "📊 Analyze Existing Saves"

**CLI:** `python main.py "<save_path>" --analyze`

### Step 3: View Results

Charts appear in the `visualizations` folder!

**GUI:** Click "📁 Open Charts Folder"

---

## What You Get

After analysis, you'll have charts showing:

- **Price trends** - See when goods crash
- **Overproduction** - Which goods are oversupplied
- **Building profitability** - Economic health
- **Comparisons** - Multiple playthroughs side-by-side

---

## Typical Workflow

### Testing Mod Changes:

1. **Start monitoring** before playing
2. **Play Victoria 3** with your mod
   - Monitoring is continuous and event-driven (no timer polling)
   - Overwritten autosave slots are still captured as new data when game day changes
   - New saves are queued as immutable snapshots while parsing is busy
   - Duplicate filesystem events are deduped per playthrough/game day
3. **Stop monitoring** when done
   - Queued snapshots are drained before final visualization generation
4. **Review charts** - find problems
5. **Make mod changes**
6. **Repeat** - compare results!

---

## Common Issues

### "Python not found"
→ Install Python from python.org  
→ Make sure to check "Add Python to PATH" during installation

### "pip: command not found"  
→ Try `python -m pip install -r requirements.txt` instead

### "Directory not found"
→ Check your save path - use quotes if path has spaces  
→ Make sure you're using the right path for your OS

### Charts are empty
→ Need at least 2-3 save files  
→ Play the game longer and let auto-saves accumulate

### "Native parser runtime unavailable"
→ Bundled parser runtime is missing/invalid  
→ Reinstall/update analyzer build so `vendor/librakaly/win-x64/rakaly.dll` is restored

### "Save parse failed"
→ A specific save is corrupt or unsupported  
→ That save is skipped; monitoring continues for next autosave

### Charts still look wrong after fixes
→ Older malformed JSON snapshots may still exist from previous runs  
→ Use Reset Data, then re-track with current parser build

---

## Next Steps

- Read the [full README](README.md) for detailed features
- Check [GUI Guide](docs/GUI_GUIDE.md) for button-by-button instructions
- Look at [examples.py](examples.py) for custom analysis
- See [CONTRIBUTING.md](CONTRIBUTING.md) to help improve the tool

---

## Need Help?

- Open an issue on GitHub
- Tag it appropriately (`bug`, `question`, `help wanted`)
- Include your Python version and OS

---

**Ready to track those market crashes! 📊**
