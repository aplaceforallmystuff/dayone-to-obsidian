# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-29

### Added

- Initial release
- Direct SQLite database reading from Day One
- Merge entries into Obsidian daily notes (`00 Daily/YYYY/YYYYMMDD.md`)
- Photo/video/audio attachment copying to `06 Assets/DayOne/`
- Location and weather metadata preservation
- Tag extraction and display
- Instagram journal support (opt-in via `--include-instagram`)
- Multiple entries per day grouped with numbered headers
- Idempotent operation (skips already-processed dates)
- Proper frontmatter generation for new daily notes
- Obsidian wiki-link format for embedded media (`![[path]]`)
