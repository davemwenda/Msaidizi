import json
from extract import extract_handbook_text
from chunking import chunk_text, faqs_to_chunks
from parse_timetable import parse_timetable
from parse_exam_timetable import parse_exam_timetable
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))       # .../backend
PROJECT_ROOT = os.path.dirname(BASE_DIR)                     # .../Msaidizi
DATA_RAW = os.path.join(PROJECT_ROOT, "data", "raw")

handbook_text = extract_handbook_text()
handbook_chunks = chunk_text(handbook_text, source="handbook")

timetable_chunks = parse_timetable(
    os.path.join(DATA_RAW, "Timetable", "CS SEPT-DEC 2026 TEACHING TIMETABLE_DRAFT 3.xlsx")
)
exam_chunks = parse_exam_timetable(
    os.path.join(DATA_RAW, "Timetable", "CS_2nd Year_Main Examination_Timetable_September_2026_07.09.2026.xlsx")
)
# faq_chunks = faqs_to_chunks("data/raw/faqs.md")

all_chunks = handbook_chunks + timetable_chunks + exam_chunks 
# + faq_chunks

with open("data/processed/chunks.json", "w", encoding="utf-8") as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=2)

print(f"Saved {len(all_chunks)} chunks")
print(f"  handbook: {len(handbook_chunks)}")
print(f"  timetable: {len(timetable_chunks)}")
print(f"  exams: {len(exam_chunks)}")
# print(f"  faqs: {len(faq_chunks)}")