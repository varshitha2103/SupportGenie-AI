import os
import re

INPUT_DIR = "isss_scraped_pages"
OUTPUT_DIR = "cleaned_pages"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define junk patterns to remove
REMOVE_PATTERNS = [
    r"Office of International Students.*",  # Repetitive headers
    r"University of Maryland, Baltimore County.*",
    r"Contact Us.*",
    r"MyUMBC.*",
    r"Instagram.*",
    r"Subscribe to UMBC.*",
    r"I am interested in:.*",
    r"^Hours.*",
    r"^Sun.*",
    r"^Mon.*",
    r"^Tue.*",
    r"^Wed.*",
    r"^Thu.*",
    r"^Fri.*",
    r"^Sat.*",
    r"Top Stories.*",
    r"Helpful Links.*",
    r"Location.*",
    r"Resources.*",
    r"Emergency Info.*",
    r"Consumer Information.*",
    r"Directions & Parking.*",
    r"Accreditation.*",
    r"Equal Opportunity.*",
    r"Privacy.*",
    r"Title IX.*",
    r"Web Accessibility.*",
    r"Online Directory.*",
    r"Sign Up for Text Alerts.*",
    r"UMBC Police.*"
    r"Center for Global Engagement.*",
    r"HomeImmigration Policy Updates.*",
    r"Immigration Policy Updates.*",
    r"About OISS.*",
    r"OISS Staff.*",
    r"Cultural Programming",
    r"Location",
    r"University CenterSecond Floor, 207A",
    r"Hours"
    r"SunClosed"
    r"Mon8:30 am – 4:30 pm",
    r"Tue8:30 am – 4:30 pm",
    r"Wed8:30 am – 4:30 pm",
    r"Thu8:30 am – 4:30 pm",
    r"Fri8:30 am – 4:30 pm",
    r"SatClosed",
    r"Contact",
    r"Contact Us",
    r"Alumni"
    r"Career Center"
    r"Events"
    r"Get Help"
    r"News"
    r"Visit Campus"
    r"Work at UMBC"
    r"Important s"
    r"UMBC"
    r"Request Support"
    r"UMBC Police:410-455-5555"
    r"Request Info"
    r"Apply"
    r"Enter email to subscribeGo"
]

def clean_text(text):
    for pattern in REMOVE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text.strip()

for file in os.listdir(INPUT_DIR):
    if file.endswith(".txt"):
        with open(os.path.join(INPUT_DIR, file), "r", encoding="utf-8") as f:
            lines = f.readlines()

        cleaned_lines = [clean_text(line) for line in lines if clean_text(line)]

        with open(os.path.join(OUTPUT_DIR, file), "w", encoding="utf-8") as out:
            out.write("\n".join(cleaned_lines))

print(f"✅ Cleaned {len(os.listdir(INPUT_DIR))} files and saved to '{OUTPUT_DIR}'")
