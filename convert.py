#!/usr/bin/env python3
"""
Day One to Obsidian Converter

Exports Day One journal entries and merges them into Obsidian daily notes.
Photos go to 06 Assets/DayOne/, entries merge into 00 Daily/YYYY/YYYYMMDD.md
"""

import os
import re
import sys
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


# Day One database path
DAYONE_DB = Path.home() / "Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOne.sqlite"
DAYONE_PHOTOS = Path.home() / "Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOnePhotos"
DAYONE_VIDEOS = Path.home() / "Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOneVideos"
DAYONE_AUDIOS = Path.home() / "Library/Group Containers/5U8NS4GX82.dayoneapp2/Data/Documents/DayOneAudios"


def get_journals(conn) -> dict:
    """Get all journals with their IDs and names."""
    cursor = conn.execute("SELECT Z_PK, ZNAME FROM ZJOURNAL")
    journals = {}
    for row in cursor:
        name = row[1] if row[1] else f"Journal-{row[0]}"
        if len(name) == 36 and name.count('-') == 4:
            name = "Unnamed Journal"
        journals[row[0]] = name
    return journals


def get_tags_for_entry(conn, entry_pk: int) -> list:
    """Get tags associated with an entry."""
    try:
        cursor = conn.execute("""
            SELECT t.ZNAME FROM ZTAG t
            JOIN Z_17TAGS et ON t.Z_PK = et.Z_62TAGS1
            WHERE et.Z_17ENTRIES = ?
        """, (entry_pk,))
        return [row[0] for row in cursor if row[0]]
    except Exception:
        return []


def get_location_for_entry(conn, location_pk: int) -> dict:
    """Get location data for an entry."""
    if not location_pk:
        return {}
    try:
        cursor = conn.execute("""
            SELECT ZPLACENAME, ZLOCALITYNAME, ZADMINISTRATIVEAREA, ZCOUNTRY, ZLATITUDE, ZLONGITUDE
            FROM ZLOCATION WHERE Z_PK = ?
        """, (location_pk,))
        row = cursor.fetchone()
        if row:
            return {
                'place': row[0],
                'locality': row[1],
                'region': row[2],
                'country': row[3],
                'latitude': row[4],
                'longitude': row[5]
            }
    except Exception:
        pass
    return {}


def get_weather_for_entry(conn, weather_pk: int) -> dict:
    """Get weather data for an entry."""
    if not weather_pk:
        return {}
    try:
        cursor = conn.execute("""
            SELECT ZCONDITIONSDESCRIPTION, ZTEMPERATURECELSIUS, ZRELATIVEHUMIDITY
            FROM ZWEATHER WHERE Z_PK = ?
        """, (weather_pk,))
        row = cursor.fetchone()
        if row:
            return {
                'conditions': row[0],
                'temperature': row[1],
                'humidity': row[2]
            }
    except Exception:
        pass
    return {}


def get_attachments_for_entry(conn, entry_pk: int) -> list:
    """Get photo/video/audio attachments for an entry."""
    try:
        cursor = conn.execute("""
            SELECT ZIDENTIFIER, ZTYPE, ZMD5 FROM ZATTACHMENT WHERE ZENTRY = ?
        """, (entry_pk,))
        attachments = []
        for row in cursor:
            attachments.append({
                'identifier': row[0],
                'type': row[1],
                'md5': row[2]
            })
        return attachments
    except Exception:
        return []


def copy_attachment(md5: str, assets_folder: Path) -> str | None:
    """Copy attachment to assets folder, return relative path or None."""
    for ext in ['.jpeg', '.jpg', '.png', '.gif', '.heic', '.mp4', '.mov', '.m4a', '.mp3']:
        for folder in [DAYONE_PHOTOS, DAYONE_VIDEOS, DAYONE_AUDIOS]:
            source = folder / f"{md5}{ext}"
            if source.exists():
                dest_name = f"{md5}{ext}"
                dest = assets_folder / dest_name
                if not dest.exists():
                    assets_folder.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
                return dest_name
    return None


def convert_dayone_moment_links(text: str, attachments: list, assets_folder: Path, assets_rel_path: str) -> str:
    """Convert Day One moment:// links to Obsidian image embeds."""
    if not text:
        return ""

    # Build lookup from identifier to md5
    attachment_map = {}
    for att in attachments:
        if att['md5']:
            attachment_map[att['identifier'].upper()] = att['md5']

    def replace_moment(match):
        identifier = match.group(1).upper()
        if identifier in attachment_map:
            md5 = attachment_map[identifier]
            filename = copy_attachment(md5, assets_folder)
            if filename:
                return f"![[{assets_rel_path}/{filename}]]"
        return f"[Missing attachment: {identifier}]"

    # Replace dayone-moment:// links
    text = re.sub(r'!\[\]\(dayone-moment://([A-Fa-f0-9]+)\)', replace_moment, text)

    # Clean up escaped characters from Day One
    text = text.replace('\\. ', '. ')
    text = text.replace('\\.', '.')
    text = text.replace('\\!', '!')
    text = text.replace('\\-', '-')
    text = text.replace('\\*', '*')
    text = text.replace('\\#', '#')
    text = text.replace('\\[', '[')
    text = text.replace('\\]', ']')
    text = text.replace('\\(', '(')
    text = text.replace('\\)', ')')

    return text


def format_entry_block(entry: dict, entry_num: int = None, total_entries: int = 1) -> str:
    """Format a single Day One entry as a markdown block."""
    lines = []

    # Header - only show entry number if multiple entries that day
    if total_entries > 1 and entry_num:
        journal_label = f" ({entry['journal']})" if entry['journal'] not in ['Journal', None] else ""
        lines.append(f"### Day One Entry {entry_num}{journal_label}")
    else:
        journal_label = f" *({entry['journal']})*" if entry['journal'] not in ['Journal', None] else ""
        lines.append(f"### Day One Entry{journal_label}")

    lines.append("")

    # Metadata line
    metadata = []
    loc = entry.get('location', {})
    if loc.get('locality'):
        location_parts = [loc.get('locality')]
        if loc.get('country') and loc.get('country') != 'Spain':
            location_parts.append(loc.get('country'))
        metadata.append(f"📍 {', '.join(location_parts)}")

    weather = entry.get('weather', {})
    if weather.get('conditions'):
        weather_str = weather['conditions']
        if weather.get('temperature'):
            weather_str += f" {int(weather['temperature'])}°C"
        metadata.append(f"🌤 {weather_str}")

    if entry.get('tags'):
        metadata.append(f"🏷 {', '.join(entry['tags'])}")

    if metadata:
        lines.append(f"*{' · '.join(metadata)}*")
        lines.append("")

    # Content
    lines.append(entry['text'])

    return '\n'.join(lines)


def get_existing_daily_note(daily_path: Path) -> str | None:
    """Read existing daily note content if it exists."""
    if daily_path.exists():
        with open(daily_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def merge_into_daily_note(daily_path: Path, dayone_content: str, date_str: str):
    """Merge Day One content into existing or new daily note."""
    existing = get_existing_daily_note(daily_path)

    # Check if we already added Day One content
    if existing and '## Day One Journal' in existing:
        print(f"  Skipping {daily_path.name} - Day One content already present")
        return False

    daily_path.parent.mkdir(parents=True, exist_ok=True)

    if existing:
        # Append Day One section to existing note
        with open(daily_path, 'a', encoding='utf-8') as f:
            f.write("\n\n---\n\n")
            f.write("## Day One Journal\n\n")
            f.write(dayone_content)
    else:
        # Create new daily note with Day One content
        weekday = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        month_day = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")

        with open(daily_path, 'w', encoding='utf-8') as f:
            f.write("---\n")
            f.write(f"date: {date_str}\n")
            f.write("tags: [Daily, DayOne]\n")
            f.write(f"cssclasses: [daily, {weekday}]\n")
            f.write("---\n\n")
            f.write(f"# {weekday}, {month_day}\n\n")
            f.write("## Day One Journal\n\n")
            f.write(dayone_content)

    return True


def convert_to_daily_notes(vault_path: str, include_instagram: bool = False):
    """
    Convert Day One entries and merge into Obsidian daily notes structure.

    Args:
        vault_path: Path to Obsidian vault root
        include_instagram: Whether to include Instagram journal entries
    """
    vault = Path(vault_path)
    daily_folder = vault / "00 Daily"
    assets_folder = vault / "06 Assets" / "DayOne"
    assets_rel_path = "06 Assets/DayOne"

    if not daily_folder.exists():
        print(f"Error: Daily folder not found: {daily_folder}")
        sys.exit(1)

    conn = sqlite3.connect(DAYONE_DB)
    journals = get_journals(conn)

    print(f"Found journals: {journals}")
    print(f"Vault: {vault}")
    print(f"Daily notes: {daily_folder}")
    print(f"Assets: {assets_folder}")
    print()

    # Query all entries
    query = """
        SELECT
            e.Z_PK,
            e.ZGREGORIANYEAR,
            e.ZGREGORIANMONTH,
            e.ZGREGORIANDAY,
            e.ZCREATIONDATE,
            e.ZMARKDOWNTEXT,
            e.ZSTARRED,
            e.ZJOURNAL,
            e.ZLOCATION,
            e.ZWEATHER,
            e.ZUUID
        FROM ZENTRY e
        ORDER BY e.ZCREATIONDATE ASC
    """

    cursor = conn.execute(query)

    # Group entries by date
    entries_by_date = defaultdict(list)
    skipped_instagram = 0
    skipped_empty = 0

    for row in cursor:
        pk, year, month, day, creation_ts, text, starred, journal_pk, location_pk, weather_pk, uuid = row

        journal_name = journals.get(journal_pk, 'Unknown')

        # Skip Instagram if not requested
        if journal_name == 'Instagram' and not include_instagram:
            skipped_instagram += 1
            continue

        # Skip empty entries
        if not text or not text.strip():
            skipped_empty += 1
            continue

        # Build date
        if year and month and day:
            date_key = f"{year:04d}{month:02d}{day:02d}"
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            year_str = str(year)
        elif creation_ts:
            dt = datetime(2001, 1, 1) + timedelta(seconds=creation_ts)
            date_key = dt.strftime("%Y%m%d")
            date_str = dt.strftime("%Y-%m-%d")
            year_str = dt.strftime("%Y")
        else:
            continue

        # Get metadata
        tags = get_tags_for_entry(conn, pk)
        location = get_location_for_entry(conn, location_pk)
        weather = get_weather_for_entry(conn, weather_pk)
        attachments = get_attachments_for_entry(conn, pk)

        # Convert content
        converted_text = convert_dayone_moment_links(text, attachments, assets_folder, assets_rel_path)

        entries_by_date[(year_str, date_key, date_str)].append({
            'text': converted_text,
            'tags': tags,
            'location': location,
            'weather': weather,
            'journal': journal_name,
            'starred': starred,
            'uuid': uuid
        })

    conn.close()

    # Process each date
    created = 0
    updated = 0
    skipped = 0

    print(f"Processing {len(entries_by_date)} dates...")

    for (year_str, date_key, date_str), entries in sorted(entries_by_date.items()):
        daily_path = daily_folder / year_str / f"{date_key}.md"

        # Format all entries for this date
        if len(entries) == 1:
            content = format_entry_block(entries[0])
        else:
            blocks = []
            for i, entry in enumerate(entries, 1):
                blocks.append(format_entry_block(entry, i, len(entries)))
            content = "\n\n---\n\n".join(blocks)

        # Merge into daily note
        if daily_path.exists():
            if merge_into_daily_note(daily_path, content, date_str):
                updated += 1
                print(f"  Updated: {daily_path.name}")
            else:
                skipped += 1
        else:
            if merge_into_daily_note(daily_path, content, date_str):
                created += 1
                print(f"  Created: {daily_path.name}")

    # Count assets
    asset_count = len(list(assets_folder.glob('*'))) if assets_folder.exists() else 0

    print()
    print("=" * 50)
    print("Conversion complete!")
    print(f"  Daily notes created: {created}")
    print(f"  Daily notes updated: {updated}")
    print(f"  Daily notes skipped (already had DayOne): {skipped}")
    print(f"  Instagram entries skipped: {skipped_instagram}")
    print(f"  Empty entries skipped: {skipped_empty}")
    print(f"  Photos/videos copied to assets: {asset_count}")
    print()
    if not include_instagram and skipped_instagram > 0:
        print(f"  (Run with --include-instagram to include {skipped_instagram} Instagram entries)")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Export Day One journal entries to Obsidian daily notes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s ~/Documents/MyVault
  %(prog)s ~/Documents/MyVault --include-instagram
  %(prog)s ~/Documents/MyVault --dry-run

The tool expects this vault structure:
  - Daily notes: 00 Daily/YYYY/YYYYMMDD.md
  - Assets: 06 Assets/DayOne/
        '''
    )
    parser.add_argument('vault_path', help='Path to Obsidian vault root')
    parser.add_argument('--include-instagram', action='store_true',
                        help='Include Instagram journal entries (excluded by default)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')

    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN - No changes will be made\n")

    convert_to_daily_notes(args.vault_path, args.include_instagram)
