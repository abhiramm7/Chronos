# Chronos v0.0.0 - Release Checklist

This document summarizes the open source package setup for Chronos.

### Core Package Files
- `__init__.py` - Package initialization with version 0.0.0
- `core.py` - Core shingling functionality (Black formatted)
- `test_core.py` - Test suite (Black formatted)
- `pyproject.toml` - Package configuration with full metadata

### Documentation
- `README.md` - Comprehensive README with usage examples and version 0.0.0
- `LICENSE` - MIT License
- `CONTRIBUTING.md` - Contribution guidelines
- `.gitignore` - Python gitignore template

### Testing & CI/CD
- `pytest.ini` - Pytest configuration
- `.github/workflows/test.yml` - GitHub Actions for automated testing
- `.github/workflows/black.yml` - GitHub Actions for code formatting checks

### Build Configuration
- `MANIFEST.in` - Package distribution manifest
- `pyproject.toml` - Build system using Hatchling

## Package Information

**Name:** chronos  
**Version:** 0.0.0  
**Description:** A Python package for time series preprocessing, forecasting, classification, and analysis  
**License:** MIT  
**Python Version:** >= 3.14  

## Dependencies

### Production
- matplotlib >= 3.10.8
- numpy >= 2.4.0
- pandas >= 2.3.3

### Development
- pytest >= 7.0.0
- black >= 23.0.0

## Current Features

### Time Series Preprocessing
- **Shingling**: Create sliding window features from uniformly sampled time series data
  - Supports both `pd.Timedelta` and integer window sizes
  - Automatically handles column naming (t-0, t-1, etc.)
  - Validates uniform sampling

## Test Results

All tests passing (1/1)  
All code formatted with Black  

## Next Steps for Release

1. **Update GitHub URLs** in `pyproject.toml` and `README.md` with your actual repository
2. **Create GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - v0.0.0"
   git branch -M main
   git remote add origin https://github.com/yourusername/chronos.git
   git push -u origin main
   ```

3. **Enable GitHub Actions** - Workflows are ready to run automatically

4. **Optional: Publish to PyPI**
   ```bash
   # Build the package
   python -m build
   
   # Upload to PyPI (requires twine and PyPI account)
   python -m twine upload dist/*
   ```

## Development Commands

```bash
# Run tests
pytest -v

# Check code formatting
black --check .

# Format code
black .

# Install in development mode
pip install -e ".[dev]"
```

## GitHub Actions Workflows

Both workflows run on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### test.yml
- Tests on Python 3.14
- Runs full pytest suite

### black.yml
- Checks code formatting
- Ensures all code follows Black style guide

---

**Status:** Ready for initial release

