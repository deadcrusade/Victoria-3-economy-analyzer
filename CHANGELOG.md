# Changelog

All notable changes to Victoria 3 Economic Analyzer will be documented in this file.

## [1.0.0] - 2025-02-13

### Added
- Initial release
- Real-time save game monitoring
- Economic data extraction (prices, production, stockpiles)
- Building profitability tracking
- Overproduction detection
- Price crash analysis
- Multi-playthrough comparison
- Matplotlib visualizations:
  - Goods prices over time
  - Price crash analysis
  - Overproduction heatmap
  - Building profitability trends
  - Comparison dashboard
- GUI application with tkinter
  - Simple button interface
  - Live output console
  - Browse for save directory
  - One-click monitoring
- CLI application with interactive menu
- Command-line options for advanced users
- **Standalone executable support** 🆕
  - Build scripts for creating .exe (Windows) / executables (Linux/Mac)
  - No Python installation required for end users
  - `build_exe.bat` / `build_exe.sh` for easy building
  - PyInstaller configuration included
- Comprehensive documentation
- Example scripts for custom analysis
- Windows batch launchers

### Supported
- Victoria 3 version 1.12.x
- Python 3.8+
- Windows (fully tested)
- Linux/macOS (should work, not fully tested)

---

## Future Plans

### Planned for v1.1
- [ ] Better save file format detection
- [ ] More robust error handling
- [ ] Additional chart types
- [ ] CSV/Excel export
- [ ] Dark mode for GUI
- [ ] Save presets for custom goods tracking

### Planned for v1.2
- [ ] Real-time graphs (updating while monitoring)
- [ ] Alert system for crashes
- [ ] Comparison mode improvements
- [ ] Performance optimizations for large saves

### Long-term Goals
- [ ] Web-based dashboard
- [ ] Steam Workshop integration
- [ ] Multiplayer save support
- [ ] Historical data database
- [ ] Community data sharing

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to this project!
