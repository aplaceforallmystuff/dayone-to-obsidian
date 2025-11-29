# Day One to Obsidian

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Export Day One journal entries directly into Obsidian daily notes.

## Why Use This?

- **No manual export** - Reads directly from Day One's SQLite database
- **Merges into daily notes** - Adds entries to existing notes or creates new ones
- **Preserves everything** - Photos, location, weather, and tags come along
- **Handles multiple journals** - Including Instagram imports
- **Safe to re-run** - Skips dates already processed

Unlike other exporters that require you to manually export JSON from Day One, this tool reads the local database directly and integrates entries into your existing Obsidian daily notes structure.

## Features

| Feature | Description |
|---------|-------------|
| **Direct database access** | No manual export needed |
| **Daily note merging** | Appends to existing notes in `YYYYMMDD.md` format |
| **Photo/video copying** | Copies media to vault assets with Obsidian embed links |
| **Metadata preservation** | Location, weather, and tags included when available |
| **Multiple journals** | Handles all Day One journals including Instagram |
| **Idempotent** | Safe to run multiple times |

## Requirements

- macOS (Day One stores data in `~/Library/Group Containers/`)
- Python 3.9+
- Day One app with local data

**Tip:** Open Day One and let it sync before running to ensure all entries and photos are downloaded from iCloud.

## Installation

```bash
git clone https://github.com/aplaceforallmystuff/dayone-to-obsidian.git
cd dayone-to-obsidian
```

No dependencies required - uses Python standard library only.

## Usage

### Basic

```bash
python convert.py /path/to/your/obsidian/vault
```

### Include Instagram entries

```bash
python convert.py /path/to/vault --include-instagram
```

### Dry run

```bash
python convert.py /path/to/vault --dry-run
```

### Help

```bash
python convert.py --help
```

## Vault Structure

The tool expects this structure (common for PARA-based vaults):

```
Your Vault/
├── 00 Daily/
│   ├── 2024/
│   │   ├── 20240315.md
│   │   └── ...
│   └── 2025/
│       └── ...
└── 06 Assets/
    └── DayOne/
        ├── abc123.jpeg
        └── ...
```

## Output Format

### Existing daily notes

A `## Day One Journal` section is appended:

```markdown
---

## Day One Journal

### Day One Entry

*📍 Valencia · 🌤 Partly Cloudy 22°C*

Today was a good day...

![[06 Assets/DayOne/abc123.jpeg]]
```

### New daily notes

Created with frontmatter:

```markdown
---
date: 2024-03-15
tags: [Daily, DayOne]
cssclasses: [daily, Friday]
---

# Friday, March 15, 2024

## Day One Journal

### Day One Entry

Your journal content here...
```

### Multiple entries per day

Numbered with journal labels:

```markdown
### Day One Entry 1

First entry of the day...

---

### Day One Entry 2 (Instagram)

Second entry from Instagram...
```

## How It Works

Day One stores entries in a SQLite database at:
```
~/Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOne.sqlite
```

Photos are stored in:
```
~/Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOnePhotos/
```

The script:
1. Queries the `ZENTRY` table for all journal entries
2. Joins with `ZLOCATION`, `ZWEATHER`, `ZTAG` for metadata
3. Maps `ZATTACHMENT` records to photo files via MD5 hash
4. Converts `dayone-moment://` links to Obsidian embeds
5. Groups entries by date and merges into daily notes

## Troubleshooting

### Missing attachments

Some photos may still be in iCloud. Open Day One, wait for sync to complete, then run again.

### Database locked

Close Day One or wait a moment before running.

### Different vault structure

Modify the paths at the top of `convert.py` if your vault uses different folder names.

## License

MIT License - see [LICENSE](LICENSE)

## Author

Jim Christian ([@aplaceforallmystuff](https://github.com/aplaceforallmystuff))
