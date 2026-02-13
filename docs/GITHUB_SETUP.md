# Setting Up on GitHub

Quick guide to get this project on GitHub for your team!

## Creating the Repository

### 1. Create New Repository on GitHub

1. Go to https://github.com/new
2. Name it: `vic3-economic-analyzer` (or whatever you prefer)
3. Description: `Economic analysis tool for Victoria 3 - Built for The Great Revision mod`
4. Choose **Public** (so team can access easily)
5. **Don't** add README, .gitignore, or license (we have them already)
6. Click "Create repository"

### 2. Push Your Code

In your `vic3_analyzer` folder, run:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# First commit
git commit -m "Initial release: Victoria 3 Economic Analyzer v1.0"

# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/vic3-economic-analyzer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Repository Structure

Your GitHub repo will have:

```
vic3-economic-analyzer/
├── .gitignore              # Ignores data/visualizations folders
├── LICENSE                 # MIT License
├── README.md              # Main documentation
├── CONTRIBUTING.md        # Contribution guidelines
├── CHANGELOG.md           # Version history
├── requirements.txt       # Python dependencies
├── vic3_parser.py         # Core modules
├── data_extractor.py
├── save_monitor.py
├── visualizer.py
├── gui.py                 # GUI application
├── main.py               # CLI application
├── examples.py           # Usage examples
├── run_gui.bat           # Windows GUI launcher
├── run_analyzer.bat      # Windows CLI launcher
└── docs/                 # Documentation
    ├── QUICKSTART.md     # 5-minute setup
    ├── GUI_GUIDE.md      # GUI walkthrough
    └── FOR_TGR_TEAM.md   # Team guide
```

## Sharing with Your Team

### Method 1: Share GitHub Link

1. Send them: `https://github.com/YOUR_USERNAME/vic3-economic-analyzer`
2. They click "Code" → "Download ZIP"
3. Extract and run `run_gui.bat`

### Method 2: Git Clone (for technical users)

They run:
```bash
git clone https://github.com/YOUR_USERNAME/vic3-economic-analyzer.git
cd vic3-economic-analyzer
pip install -r requirements.txt
```

## Recommended GitHub Settings

### 1. Add Topics

In your repo settings, add topics:
- `victoria-3`
- `mod-development`
- `economic-analysis`
- `save-parser`
- `python`

### 2. Create Discord Webhook (Optional)

Get notifications in Discord when issues are opened:
1. Discord → Server Settings → Integrations → Webhooks
2. Create webhook, copy URL
3. GitHub → Settings → Webhooks → Add webhook
4. Paste Discord URL (add `/github` at the end)

### 3. Enable Discussions (Optional)

For team Q&A:
- Settings → Features → Discussions → Enable

## Using GitHub Issues for Bug Reports

Teach your team to:

### Report Bugs:

```markdown
**Title:** Price crash not detected in save file

**Description:**
Playing as France in 1875, steel prices crashed to $2 but the analyzer 
didn't flag it as a crash.

**Steps to Reproduce:**
1. Load save: france_1875_1_1.v3
2. Run analyzer
3. Check price crashes report

**Expected:** Steel should appear in crashes
**Actual:** Not listed

**Files:**
- Save file: [link or attachment]
- Charts: [attach visualizations]

**Environment:**
- Python: 3.11
- Game version: 1.12.4
- Analyzer: v1.0
```

### Request Features:

```markdown
**Title:** Add export to Excel feature

**Description:**
Would be helpful to export price data to Excel for custom analysis.

**Use Case:**
I want to create pivot tables and custom charts in Excel.

**Proposed Solution:**
Add button in GUI: "Export to Excel"
```

## Updating the Tool

When you make improvements:

```bash
# Make your changes
git add .
git commit -m "Add: Excel export feature"
git push

# Create a new release (optional)
# Go to GitHub → Releases → Create new release
# Tag: v1.1.0
# Title: Version 1.1 - Excel Export
```

Your team can then:
```bash
git pull
```

Or download the new ZIP from GitHub.

## Repository Maintenance

### Good Practices:

1. **Update CHANGELOG.md** with each change
2. **Tag releases** (v1.0.0, v1.1.0, etc.)
3. **Use branches** for big features
4. **Review PRs** from team members
5. **Close fixed issues** with commit messages

### Commit Message Format:

```
Add: New feature
Fix: Bug description
Update: Changed functionality
Docs: Documentation updates
```

## Making the Repo Discoverable

### 1. Add to Steam Workshop Description

In your mod description, add:

```
📊 Economic Analyzer Tool:
https://github.com/YOUR_USERNAME/vic3-economic-analyzer

Track overproduction and market crashes while playing!
```

### 2. Share on Reddit

Post to r/victoria3 or r/victoria3mods with:
- Link to GitHub
- Screenshots of visualizations
- Brief description

### 3. Victoria 3 Modding Discord

Share in appropriate channels.

## Licensing

The project uses MIT License, which means:
- ✅ Anyone can use it
- ✅ Anyone can modify it
- ✅ Anyone can distribute it
- ✅ Commercial use allowed
- ⚠️ Must include original license
- ⚠️ No warranty

Perfect for open-source mod tools!

## Questions?

If your team has questions about GitHub:
- GitHub Docs: https://docs.github.com
- Git Tutorial: https://try.github.io
- Or just ask in your Discord!

---

**Ready to share your awesome tool with the world! 🚀**
