# Day One to Obsidian

Export your Day One journal entries directly into Obsidian daily notes.

Unlike other exporters that require manual JSON exports, this tool reads directly from Day One's SQLite database and merges entries into your existing Obsidian daily notes structure.

## Features

- **Direct database access** - No manual export needed, reads from Day One's local database
- **Merges into daily notes** - Adds entries to existing notes or creates new ones in `YYYYMMDD.md` format
- **Preserves photos & media** - Copies attachments to your vault's assets folder with proper Obsidian embed links
- **Location & weather** - Includes metadata when available
- **Multiple journals** - Handles all your Day One journals including Instagram imports
- **Tags preserved** - Day One tags appear in the entry metadata
- **Idempotent** - Safe to run multiple times; skips dates already processed

## Requirements

- macOS (Day One stores data in `~/Library/Group Containers/`)
- Python 3.9+
- Day One app with local data (iCloud sync recommended to pull down all entries first)

## Installation

```bash
git clone https://github.com/yourusername/dayone-to-obsidian.git
cd dayone-to-obsidian
```

No dependencies required - uses Python standard library only.

## Usage

### Basic usage

```bash
python convert.py /path/to/your/obsidian/vault
```

This will:
1. Read all entries from Day One's database
2. Create/update daily notes in `00 Daily/YYYY/YYYYMMDD.md`
3. Copy photos to `06 Assets/DayOne/`
4. Skip Instagram entries by default

### Include Instagram entries

```bash
python convert.py /path/to/vault --include-instagram
```

### Example output

Existing daily note gets a new section appended:

```markdown
---

## Day One Journal

### Day One Entry

*📍 Valencia · 🌤 Partly Cloudy 22°C*

Today was a good day...

![[06 Assets/DayOne/abc123.jpeg]]
```

New daily notes are created with frontmatter:

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

## Vault Structure

The tool expects/creates this structure:

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

## How It Works

Day One stores entries in a SQLite database at:
```
~/Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOne.sqlite
```

Photos are stored separately in:
```
~/Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOnePhotos/
```

The script:
1. Queries the `ZENTRY` table for all journal entries
2. Joins with `ZLOCATION`, `ZWEATHER`, `ZTAG` for metadata
3. Maps `ZATTACHMENT` records to photo files via MD5 hash
4. Converts Day One's `dayone-moment://` links to Obsidian embeds
5. Groups entries by date and merges into daily notes

## Troubleshooting

### "Missing attachment" messages

Some photos may still be in iCloud and not downloaded locally. Open Day One and let it sync, then run again.

### Database locked

Make sure Day One isn't actively writing. Close the app or wait a moment.

### Wrong vault structure

The tool expects `00 Daily/` for daily notes and `06 Assets/` for media. Modify the paths in the script if your vault differs.

## License

MIT License - see [LICENSE](LICENSE)

## Author

Jim Christian ([@jimchristian](https://github.com/jimchristian))

## Related

- [Day One](https://dayoneapp.com/) - The journaling app
- [Obsidian](https://obsidian.md/) - The knowledge base
