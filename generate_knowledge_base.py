import os
import json
import re
import random
from faker import Faker
from datetime import datetime, timedelta

# --- Config
INPUT_DIR = 'cleaned_pages'
OUTPUT_DIR = 'knowledge_base'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Create policies.json
def generate_policies():
    policies = []
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith('.txt'):
            filepath = os.path.join(INPUT_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip().replace('\n', ' ')
                title = filename.replace(".txt", "").replace("_", " ").title()
                if content:
                    policies.append({
                        "title": title,
                        "content": content[:2000]
                    })
    with open(os.path.join(OUTPUT_DIR, 'policies.json'), 'w', encoding='utf-8') as f:
        json.dump(policies, f, indent=2)
    print(f"✅ Created policies.json with {len(policies)} entries.")

# --- Create faqs.json (if any Q/A format exists)
def generate_faqs():
    faqs = []
    for filename in os.listdir(INPUT_DIR):
        with open(os.path.join(INPUT_DIR, filename), 'r', encoding='utf-8') as f:
            lines = f.readlines()
            question = None
            for line in lines:
                line = line.strip()
                if re.match(r'^(Q|Question)[:\-]', line, re.IGNORECASE):
                    question = line.split(':', 1)[-1].strip()
                elif re.match(r'^(A|Answer)[:\-]', line, re.IGNORECASE) and question:
                    answer = line.split(':', 1)[-1].strip()
                    faqs.append({
                        "category": filename.split("-")[0].upper(),
                        "question": question,
                        "answer": answer
                    })
                    question = None
    if faqs:
        with open(os.path.join(OUTPUT_DIR, 'faqs.json'), 'w', encoding='utf-8') as f:
            json.dump(faqs, f, indent=2)
        print(f"✅ Created faqs.json with {len(faqs)} Q&A pairs.")
    else:
        print("⚠️ No Q/A format found for faqs.json")

# --- Create student_profiles.json (synthetic)
def generate_students():
    fake = Faker()
    majors = ["Computer Science", "Data Science", "Cybersecurity", "Biology", "Business Analytics"]
    requests = ["I-20 Extension", "OPT Application", "CPT Request", "Visa Renewal", "Travel Signature"]
    profiles = []

    for i in range(15):
        name = fake.name()
        student_id = f"S{1000 + i}"
        nationality = fake.country()
        major = random.choice(majors)
        req_type = random.choice(requests)
        req_date = fake.date_between(start_date="-60d", end_date="today")
        profiles.append({
            "name": name,
            "student_id": student_id,
            "nationality": nationality,
            "visa_type": "F1",
            "major": major,
            "academic_status": "Full-time",
            "requests": [
                {
                    "type": req_type,
                    "status": "Submitted",
                    "date": req_date.strftime("%Y-%m-%d")
                }
            ]
        })

    with open(os.path.join(OUTPUT_DIR, 'student_profiles.json'), 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2)
    print(f"✅ Created student_profiles.json with {len(profiles)} mock students.")

# --- Run All
if __name__ == "__main__":
    generate_policies()
    generate_faqs()
    generate_students()
    print("\n🎉 All JSON files generated in 'knowledge_base/' folder.")
