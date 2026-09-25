"""
Parses a DKUT-style weekly teaching timetable Excel file (day x time-slot grid)
into flat sentence chunks suitable for RAG ingestion.

Expected raw shape:
- A few junk rows at the top (draft label, university/department name, title)
- A header row: DAY, GROUP, <time slot columns...>
- Data rows: DAY is only filled on the first row of each day's block
  (blank on subsequent rows = "same day as above")
- Blank rows separate each day's block
- Each time-slot cell (when filled) looks like "CCS 4204 RC 18" or
  "CCS 2211- RCL 1" — course code followed by venue, format not fully
  consistent (sometimes a hyphen, sometimes not, sometimes extra notes).
"""

import pandas as pd
import re
import json


def find_header_row(raw_path, sheet_name=0):
    """Locate the row index where the real header (DAY, GROUP, ...) lives."""
    df = pd.read_excel(raw_path, sheet_name=sheet_name, header=None)
    for i, row in df.iterrows():
        if str(row[0]).strip().upper() == "DAY" and str(row[1]).strip().upper() == "GROUP":
            return i
    raise ValueError("Could not find header row containing DAY, GROUP")


def parse_timetable(raw_path, sheet_name=0, semester_label="September - December 2026"):
    header_idx = find_header_row(raw_path, sheet_name=sheet_name)
    df = pd.read_excel(raw_path, sheet_name=sheet_name, header=header_idx)

    df = df.dropna(how="all")  # drop fully blank separator rows
    df["DAY"] = df["DAY"].ffill()  # forward-fill the merged day cells

    time_cols = [c for c in df.columns if c not in ("DAY", "GROUP") and "Unnamed" not in str(c)]

    chunks = []
    for _, row in df.iterrows():
        day = str(row["DAY"]).strip()
        group = str(row["GROUP"]).strip() if pd.notna(row["GROUP"]) else None
        if not group or group.lower() == "nan":
            continue

        for slot in time_cols:
            cell = row.get(slot)
            if pd.isna(cell) or not str(cell).strip():
                continue
            entry = str(cell).strip()

            course_match = re.match(r"([A-Z]{2,4}\s?\d{3,4})\s*[-]?\s*(.*)", entry)
            if course_match:
                course_code = course_match.group(1).strip()
                venue_or_note = course_match.group(2).strip(" -")
            else:
                course_code = entry
                venue_or_note = ""

            sentence = f"On {day}s during {slot}, {group} has {course_code}"
            if venue_or_note:
                sentence += f" in {venue_or_note}"
            sentence += f" ({semester_label} semester)."

            chunks.append({
                "text": sentence,
                "source": "timetable",
                "type": "timetable",
                "day": day,
                "group": group,
                "time_slot": slot,
                "course_code": course_code,
            })

    return chunks


if __name__ == "__main__":
    chunks = parse_timetable("/mnt/user-data/uploads/CS SEPT-DEC 2026 TEACHING TIMETABLE_DRAFT 3.xlsx")
    print(f"Parsed {len(chunks)} timetable entries\n")
    for c in chunks[:8]:
        print(c["text"])

    with open("/home/claude/timetable_chunks_sample.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)