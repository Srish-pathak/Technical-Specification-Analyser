import os
import pypdf

pdf_path = "TechSpecAnalyser_BTech_Project_Report.pdf"
reader = pypdf.PdfReader(pdf_path)
total_pages = len(reader.pages)
print(f"Total Pages in PDF: {total_pages}")

placeholders = [
    "<STUDENT_NAME>",
    "<ENROLMENT_NUMBER>",
    "<SUPERVISOR_NAME>",
    "<HOD_NAME>",
    "<DEPARTMENT_NAME>",
    "<INSTITUTE_NAME>",
    "<DATE>"
]

found_placeholders = {p: 0 for p in placeholders}

for idx, page in enumerate(reader.pages):
    text = page.extract_text() or ""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    first_line = lines[0] if lines else "EMPTY"
    last_line = lines[-1] if lines else "EMPTY"
    
    # Check placeholders
    for p in placeholders:
        if p in text:
            found_placeholders[p] += 1
            
    # Print sample pages
    if idx in [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 20, 30, total_pages - 1]:
        print(f"Page {idx+1}: First line: '{first_line[:40]}' | Last line (Footer): '{last_line}'")

print("\n--- Placeholder Occurrences across Document ---")
for p, count in found_placeholders.items():
    print(f"{p}: found on {count} pages")
