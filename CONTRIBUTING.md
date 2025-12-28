# Contributing to Chronos

Thank you for considering contributing to Chronos! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/chronos.git
   cd chronos
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure they follow the project's coding standards

3. Format your code with Black:
   ```bash
   black .
   ```

4. Run the tests to ensure everything works:
   ```bash
   pytest
   ```

5. Commit your changes with a clear commit message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```

6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Open a Pull Request on GitHub

## Code Standards

- **Formatting**: All code must be formatted with [Black](https://github.com/psf/black)
- **Testing**: All new features should include tests
- **Documentation**: Update the README.md if you add new functionality
- **Type Hints**: Use type hints where appropriate

## Running Tests

Run all tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest test_sequences.py
```

## Code Formatting

Check if code needs formatting:
```bash
black --check .
```

Format all code:
```bash
black .
```

## Pull Request Guidelines

- Keep pull requests focused on a single feature or bugfix
- Write clear, descriptive commit messages
- Update documentation as needed
- Ensure all tests pass
- Ensure code is formatted with Black

## Reporting Issues

When reporting issues, please include:
- A clear description of the problem
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Python version and operating system

## Questions?

If you have questions, feel free to open an issue for discussion.

