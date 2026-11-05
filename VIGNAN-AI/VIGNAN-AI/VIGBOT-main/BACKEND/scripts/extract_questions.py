import json
import re
import os

transcript_path = r"C:\Users\EVO GHOUL\.gemini\antigravity-ide\brain\79c343e3-5603-4af1-b209-1560eea786b0\.system_generated\logs\transcript_full.jsonl"
output_path = r"BACKEND\scripts\raw_questions.txt"

questions = []
pattern = re.compile(r'^\d+\.\s+(.*)')

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("type") == "USER_INPUT" and "1000 Common Questions Asked by Students" in data.get("content", ""):
                content = data["content"]
                for content_line in content.split('\n'):
                    content_line = content_line.strip()
                    if pattern.match(content_line):
                        questions.append(content_line)
        except Exception as e:
            pass

with open(output_path, "w", encoding="utf-8") as f:
    for q in questions:
        f.write(q + "\n")

print(f"Extracted {len(questions)} questions to {output_path}")
