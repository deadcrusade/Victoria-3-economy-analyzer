# Distribution Options - Which to Choose?

Two ways to distribute the Victoria 3 Economic Analyzer:

## Option 1: Standalone .exe (Recommended for Teams)

### ✅ Best For:
- Non-technical users (Dingbat32, Deacy)
- Quick distribution
- No Python knowledge needed
- "Just works" experience

### How to Create:

**Windows:**
```batch
build_exe.bat
```

**Result:** `releases/Vic3_Analyzer.exe` (~50-100 MB)

### How Users Run It:
1. Download `Vic3_Analyzer.exe`
2. Double-click
3. Done!

### Pros:
- ✅ Zero installation
- ✅ No Python needed
- ✅ No dependency issues
- ✅ One file = easy sharing

### Cons:
- ❌ Large file (~50-100 MB)
- ❌ May trigger antivirus warnings
- ❌ Need to rebuild for each platform
- ❌ Slower startup (~2-3 seconds)

---

## Option 2: Python Source (Recommended for Developers)

### ✅ Best For:
- Technical users (SASCO)
- Development and testing
- Modifying the code
- Version control

### How to Install:

```bash
pip install -r requirements.txt
python gui.py
```

**Result:** Runs directly from source

### How Users Run It:
1. Install Python 3.8+
2. Run: `pip install -r requirements.txt`
3. Double-click `run_gui.bat` or run `python gui.py`

### Pros:
- ✅ Tiny download (46 KB)
- ✅ Easy to modify
- ✅ Fast startup
- ✅ Cross-platform naturally

### Cons:
- ❌ Requires Python installation
- ❌ Dependency management needed
- ❌ More technical knowledge required

---

## Recommendation for TGR Team

### For Distribution:

**Dingbat32 & Deacy (Non-technical):**
→ Give them: `Vic3_Analyzer.exe`
→ They just double-click and go!

**SASCO (Technical lead):**
→ Keep: Python source
→ Modify and rebuild .exe when needed

### Hybrid Approach:

1. **Development:** Use Python source
2. **Testing:** Quick iterations with source
3. **Release:** Build .exe for team distribution
4. **GitHub:** Upload both source and .exe

```
Releases:
├── vic3_analyzer_v1.0_source.zip (46 KB)
└── vic3_analyzer_v1.0_standalone.zip (contains .exe, ~30 MB compressed)
```

---

## Building for Different Platforms

### Windows .exe
```batch
build_exe.bat
```
→ Produces: `Vic3_Analyzer.exe`

### Linux Binary
```bash
./build_exe.sh
```
→ Produces: `Vic3_Analyzer` (executable)

### macOS App
```bash
./build_exe.sh
```
→ Produces: `Vic3_Analyzer.app` (if using bundle config)

**Note:** Each platform needs its own build!

---

## Quick Comparison Table

| Feature | Standalone .exe | Python Source |
|---------|----------------|---------------|
| **Setup Time** | 0 minutes | 2-5 minutes |
| **File Size** | 50-100 MB | 46 KB |
| **Requires Python** | ❌ No | ✅ Yes |
| **Startup Speed** | ~2-3 sec | Instant |
| **Easy to Modify** | ❌ No | ✅ Yes |
| **Easy to Share** | ✅ Yes | ⚠️ Medium |
| **Antivirus Issues** | ⚠️ Possible | ❌ Rare |
| **Cross-Platform** | ❌ Need rebuild | ✅ Works everywhere |

---

## For Your Use Case

### If Your Team is Mostly Non-Technical:
→ **Build the .exe** and share it
→ They get zero-friction experience
→ You keep source for development

### If Your Team is Technical:
→ **Share the source** on GitHub
→ Everyone can modify and contribute
→ Smaller download, faster iteration

### If Mixed (Like TGR):
→ **Do both!**
→ Technical users clone the repo
→ Non-technical users get the .exe
→ Best of both worlds ✅

---

## Next Steps

### Ready to Build?

1. Read: [BUILD.md](BUILD.md) for detailed instructions
2. Run: `build_exe.bat` (Windows) or `./build_exe.sh` (Linux/Mac)
3. Test: `dist/Vic3_Analyzer.exe`
4. Share: Upload to Discord/GitHub/Google Drive

### Ready to Develop?

1. Read: [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Modify the code
3. Test with: `python gui.py`
4. When ready: Build .exe for distribution

---

**Bottom Line:** For **The Great Revision team**, build the .exe for easy sharing, but keep the source on GitHub for development! 🚀
