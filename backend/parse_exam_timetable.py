"""
Parses a DKUT-style exam timetable (.xlsx, one exam per row) into flat
sentence chunks suitable for RAG ingestion.

Expected raw shape:
- Row 0: title (university + "CS YEAR 2 SEMESTER 1 MAIN EXAMINATION TIMETABLE...")
- Row 1: real header — DAY, DATE, CODE, UNIT, TIME, COUNTER, VENUE,
  PR. INVIGILATOR, ASS. INVIGILATOR
- Data rows, with blank spacer rows scattered between entries
"""

import pandas as pd
import json


def parse_exam_timetable(path, sheet_name=0, year_label="Year 2"):
    df = pd.read_excel(path, sheet_name=sheet_name, header=1)
    df = df.dropna(subset=["DAY", "CODE", "UNIT"])  # drop spacer rows

    chunks = []
    for _, row in df.iterrows():
        day = str(row["DAY"]).strip()
        date = pd.to_datetime(row["DATE"]).strftime("%B %d, %Y") if pd.notna(row["DATE"]) else "an unspecified date"
        code = str(row["CODE"]).strip()
        unit = str(row["UNIT"]).strip()
        time_slot = str(row["TIME"]).strip() if pd.notna(row["TIME"]) else "an unspecified time"
        venue = str(row["VENUE"]).strip() if pd.notna(row["VENUE"]) else "an unspecified venue"

        sentence = (
            f"The {year_label} exam for {code} ({unit}) is on {day}, {date}, "
            f"from {time_slot} in {venue}."
        )

        chunks.append({
            "text": sentence,
            "source": "exam_timetable",
            "type": "exam",
            "year": year_label,
            "day": day,
            "date": date,
            "course_code": code,
            "unit_name": unit,
        })

    return chunks


if __name__ == "__main__":
    chunks = parse_exam_timetable(
        "/mnt/user-data/uploads/CS_2nd_Year_Main_Examination_Timetable_September_2026_07_09_2026.xlsx"
    )
    print(f"Parsed {len(chunks)} exam entries\n")
    for c in chunks:
        print(c["text"])

    with open("/home/claude/exam_timetable_chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)