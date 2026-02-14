# Building Standalone Executable

This guide shows you how to create a **single .exe file** (Windows) or executable (Linux/Mac) that includes Python and all dependencies - **no installation required**!

## Why Build an Executable?

**Pros:**
- ✅ No Python installation needed
- ✅ No dependency management
- ✅ Just double-click and run
- ✅ Perfect for non-technical users
- ✅ Easy distribution to team

**Cons:**
- ❌ Larger file size (~50-100 MB vs 46 KB source)
- ❌ One build per platform (Windows .exe, Mac app, Linux binary)
- ❌ Slower startup time (few seconds)

## Quick Build (Windows)

```batch
# Just double-click this:
build_exe.bat
```

The .exe will be in: `dist\Vic3_Analyzer.exe`

## Quick Build (Linux/Mac)

```bash
chmod +x build_exe.sh
./build_exe.sh
```

The executable will be in: `dist/Vic3_Analyzer`

---

## Detailed Instructions

### Prerequisites

1. **Python 3.8+** installed
2. **All dependencies** installed: `pip install -r requirements.txt`
3. **PyInstaller** (will be installed automatically by build script)

### Windows Build Process

#### Step 1: Run the Build Script

Open Command Prompt in the `vic3_analyzer` folder:

```batch
build_exe.bat
```

**What it does:**
1. Installs PyInstaller
2. Bundles GUI, all modules, and dependencies
3. Creates single executable: `dist\Vic3_Analyzer.exe`
4. Copies to `releases\` folder

#### Step 2: Test the Executable

```batch
dist\Vic3_Analyzer.exe
```

The GUI should open. Test all buttons!

#### Step 3: Distribute

Share `releases\Vic3_Analyzer.exe` with your team via:
- Discord
- Google Drive
- GitHub Releases
- Email

**File size:** ~50-100 MB (compressed: ~20-30 MB with zip)

### Linux/Mac Build Process

#### Step 1: Make Script Executable

```bash
chmod +x build_exe.sh
```

#### Step 2: Run Build

```bash
./build_exe.sh
```

#### Step 3: Test

```bash
dist/Vic3_Analyzer
```

#### Step 4: Distribute

Share `releases/Vic3_Analyzer` with your team.

---

## Advanced: Manual PyInstaller Command

If you want more control:

### Windows (Command Prompt)

```batch
pyinstaller --clean --onefile --windowed ^
    --name "Vic3_Analyzer" ^
    --add-data "docs;docs" ^
    --add-data "vendor;vendor" ^
    --hidden-import=matplotlib ^
    --hidden-import=numpy ^
    --hidden-import=watchdog ^
    --hidden-import=watchdog.observers.winapi ^
    gui.py
```

### Linux/Mac (Terminal)

```bash
pyinstaller --clean --onefile --windowed \
    --name "Vic3_Analyzer" \
    --add-data "docs:docs" \
    --add-data "vendor:vendor" \
    --hidden-import=matplotlib \
    --hidden-import=numpy \
    --hidden-import=watchdog \
    --hidden-import=watchdog.observers.inotify \
    gui.py
```

### PyInstaller Options Explained

- `--onefile` - Bundle everything into single executable
- `--windowed` - No console window (GUI only)
- `--name` - Name of the output file
- `--add-data` - Include docs and bundled native parser runtime
- `--hidden-import` - Force include these modules
- `--clean` - Clean cache before building
- `--icon` - Custom icon (optional, we don't have one)

---

## Custom Icon (Optional)

Want to add a custom icon?

### Step 1: Create/Get an Icon

Create a `icon.ico` file (256x256 recommended)

### Step 2: Add to Build Script

Edit `build_exe.bat` and change:

```batch
--icon=NONE
```

To:

```batch
--icon=icon.ico
```

### Step 3: Rebuild

Run `build_exe.bat` again.

---

## Troubleshooting

### "PyInstaller: command not found"

**Fix:**
```bash
pip install pyinstaller
```

### Build Fails with Import Errors

**Fix:** Add missing modules to hidden imports:

```batch
--hidden-import=missing_module_name
```

### .exe Won't Start / Crashes Immediately

**Debug mode:** Build without `--windowed` to see error messages:

```batch
pyinstaller --onefile --name "Vic3_Analyzer_Debug" gui.py
```

Run and check console output.

### Antivirus Blocks the .exe

**Common with PyInstaller!** The .exe is legitimate but may be flagged.

**Solutions:**
1. Add exception to antivirus
2. Build on a clean system
3. Use code signing (advanced, requires certificate)
4. Distribute source + instructions instead

### .exe is Too Large

**Reduce size:**

1. Use `--exclude-module` to remove unused imports:
```batch
--exclude-module=tkinter.test
--exclude-module=unittest
```

2. Compress with UPX:
```batch
pip install pyinstaller[encryption]
pyinstaller --upx-dir=C:\path\to\upx ...
```

3. Or just zip the .exe (usually 50-70% smaller)

---

## Distribution Options

### Option A: Direct Download

**Best for:** Small teams

1. Build the .exe
2. Upload to Google Drive / Dropbox
3. Share link

### Option B: GitHub Releases

**Best for:** Public distribution

1. Build the .exe
2. Go to GitHub → Releases → Create new release
3. Tag: `v1.0.0`
4. Upload: `Vic3_Analyzer.exe`
5. Users download from releases page

### Option C: Zip Archive

**Best for:** Keeping file size down

```batch
# Create vic3_analyzer_standalone.zip containing:
- Vic3_Analyzer.exe
- README.txt (quick instructions)
```

Compressed size: ~20-30 MB

### Option D: Installer (Advanced)

Use **Inno Setup** (Windows) or **InstallForge** to create a proper installer:

1. Download Inno Setup
2. Create installer script
3. Includes uninstaller, desktop shortcut, etc.

---

## File Size Comparison

| Distribution Method | Size | Pros | Cons |
|---------------------|------|------|------|
| Source (.zip) | 46 KB | Tiny, modifiable | Needs Python |
| Standalone .exe | 50-100 MB | No install needed | Large |
| .exe (zipped) | 20-30 MB | Smaller download | Needs unzip |
| Installer | 50-100 MB | Professional | Complex setup |

---

## For The Great Revision Team

### Recommended Distribution

**For Dingbat32 & Deacy (non-technical):**
- Give them: `Vic3_Analyzer.exe`
- Just double-click, no Python needed!

**For SASCO (technical):**
- Source code for modifying
- Can rebuild .exe after changes

### Quick Build Workflow

1. Make mod changes
2. Test with Python version
3. When ready to share: `build_exe.bat`
4. Upload `releases\Vic3_Analyzer.exe` to Discord
5. Team downloads and runs - done! ✅

---

## Building on GitHub Actions (Auto-Build)

Want automatic builds when you push to GitHub?

Create `.github/workflows/build.yml`:

```yaml
name: Build Executable

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build executable
      run: |
        pyinstaller --onefile --windowed gui.py
    
    - name: Upload artifact
      uses: actions/upload-artifact@v2
      with:
        name: Vic3_Analyzer.exe
        path: dist/Vic3_Analyzer.exe
```

Then: Push tag → GitHub builds → Download .exe from Actions

---

## FAQ

**Q: Can I customize what's included?**  
A: Yes! Edit `build_exe.bat` and add/remove modules.

**Q: Does it work on old Windows versions?**  
A: Tested on Windows 10+. Should work on Windows 7+ but untested.

**Q: Can users still see the code?**  
A: No, it's compiled. But it's not encryption - determined users can extract it.

**Q: Can I build for Mac on Windows?**  
A: No, you need to build on each platform separately.

**Q: Will antivirus flag it?**  
A: Possibly! PyInstaller executables are sometimes flagged. It's a false positive.

**Q: Can I update without rebuilding?**  
A: No, any code change requires a rebuild. Use semantic versioning (v1.0, v1.1, etc.).

---

## Next Steps

1. ✅ Run `build_exe.bat`
2. ✅ Test the .exe
3. ✅ Share with team
4. ✅ Get feedback
5. ✅ Iterate and rebuild as needed

**Happy distributing!** 🚀

---

**Note:** For most users, the **source distribution** (current method) is fine. Only build .exe if your team really needs it!
