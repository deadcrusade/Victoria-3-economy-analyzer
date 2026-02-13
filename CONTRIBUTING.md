# Contributing to Victoria 3 Economic Analyzer

Thanks for your interest in contributing! This tool was built for The Great Revision mod team, but we welcome contributions from the Victoria 3 modding community.

## How to Contribute

### Reporting Issues

Found a bug or have a feature request? Please open an issue with:

- **Bug Reports:**
  - Your Python version
  - Your Victoria 3 game version
  - Steps to reproduce
  - Error messages (if any)
  - Save file (if you can share it)

- **Feature Requests:**
  - Clear description of the feature
  - Why it would be useful
  - Examples of how it would work

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Test thoroughly** (especially with different save files)
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/vic3_analyzer.git
cd vic3_analyzer

# Install dependencies
pip install -r requirements.txt

# Run tests (if we add them later)
# python -m pytest
```

## Code Style

- Follow PEP 8 style guidelines
- Add docstrings to functions
- Comment complex logic
- Keep functions focused and modular

## Areas for Contribution

### High Priority

- **Parser improvements** - Handle more save file formats
- **Custom goods tracking** - Make it easier to add custom goods
- **Performance optimization** - Speed up large save file parsing
- **Error handling** - Better error messages for users

### Medium Priority

- **Additional visualizations** - New chart types
- **Export formats** - CSV, Excel, JSON exports
- **GUI improvements** - More features, better UX
- **Cross-platform testing** - Linux/Mac support

### Low Priority (Nice to Have)

- **Unit tests** - Test coverage for core functions
- **Documentation** - More examples and tutorials
- **Themes** - Dark mode for GUI
- **Localization** - Support for other languages

## Architecture Overview

### Core Components

```
vic3_analyzer/
├── vic3_parser.py      # Parses Victoria 3 save format
├── data_extractor.py   # Extracts economic metrics
├── save_monitor.py     # Watches for new save files
├── visualizer.py       # Creates matplotlib charts
├── gui.py             # Tkinter GUI application
├── main.py            # CLI application
└── examples.py        # Usage examples
```

### Data Flow

```
Save File (.v3)
    ↓
vic3_parser.py (parse save structure)
    ↓
data_extractor.py (extract economic data)
    ↓
save_monitor.py (track and store data)
    ↓
visualizer.py (create charts)
```

### Adding New Features

#### Adding a New Metric

1. **Add extraction in `data_extractor.py`:**
```python
def _extract_your_metric(self, content: str):
    # Your parsing logic here
    return metric_data
```

2. **Add to `extract_all()` method:**
```python
data['your_metric'] = self._extract_your_metric(content)
```

3. **Add visualization in `visualizer.py`:**
```python
def plot_your_metric(self, playthrough_data, playthrough_name):
    # Your plotting logic here
```

4. **Add to GUI button (optional)** in `gui.py`

#### Adding a New Visualization

1. **Create function in `visualizer.py`:**
```python
def plot_custom_chart(self, data, name):
    fig, ax = plt.subplots(figsize=(14, 8))
    # Your plotting code
    plt.savefig(f"{name}_custom.png")
```

2. **Call from `generate_all_visualizations()`** or add as separate button

## Testing

Before submitting a PR:

1. **Test with multiple save files** - Different dates, different nations
2. **Test both GUI and CLI** - Make sure both work
3. **Check edge cases** - Empty saves, corrupted files, etc.
4. **Verify visualizations** - Charts render correctly

## Questions?

- Open an issue for questions
- Tag it with `question` label
- We'll respond as soon as we can!

## License

This project is open source and free to use for Victoria 3 modding purposes.

---

**Special thanks to The Great Revision mod team for inspiring this tool!**
