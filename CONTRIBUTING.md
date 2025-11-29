# Contributing to Day One to Obsidian

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/dayone-to-obsidian.git
   cd dayone-to-obsidian
   ```
3. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development

### Running

```bash
python convert.py /path/to/test/vault --dry-run
```

### Testing with a real vault

Create a test vault with the expected structure:

```bash
mkdir -p test_vault/00\ Daily/2024
mkdir -p test_vault/06\ Assets/DayOne
python convert.py test_vault
```

## Code Style

- Python 3.9+ compatible
- Use type hints where practical
- Keep the single-file structure (no external dependencies)
- Follow existing code patterns

## Submitting Changes

1. Test your changes with both existing and new daily notes
2. Update the README if adding new features
3. Update the CHANGELOG
4. Commit with a descriptive message
5. Push to your fork
6. Open a Pull Request

## Reporting Issues

When reporting issues, please include:
- Python version (`python --version`)
- macOS version
- Day One version
- Error messages (with any personal content redacted)
- Steps to reproduce

## Feature Ideas

Contributions welcome for:
- [ ] Configurable vault paths (not hardcoded `00 Daily/` and `06 Assets/`)
- [ ] Option to export to separate files instead of merging
- [ ] Date range filtering
- [ ] Journal name filtering
- [ ] Windows/Linux support (different database paths)

## Questions?

Open an issue for any questions about contributing.
