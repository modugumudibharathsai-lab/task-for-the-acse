nlu_path = r'BACKEND\app\agent\nlu_engine.py'
with open(nlu_path, 'r', encoding='utf-8') as f:
    code = f.read()

old_extract = '''    @classmethod
    def extract_subject(cls, text: str) -> Optional[str]:
        if cls.has_any_word(text, ["digital electronics", "cs302", "de"]):
            return "Digital Electronics"
        if cls.has_any_word(text, ["data structures", "cs301", "ds"]):
            return "Data Structures"
        if cls.has_any_word(text, ["discrete mathematics", "cs303", "dm"]):
            return "Discrete Mathematics"
        return None'''

new_extract = '''    @classmethod
    def extract_subject(cls, text: str) -> Optional[str]:
        if cls.has_any_word(text, ["digital logic", "dld", "digital electronics", "25cs205"]):
            return "Digital Logic design"
        if cls.has_any_word(text, ["data structures", "ds", "25cs201"]):
            return "Data Structures"
        if cls.has_any_word(text, ["discrete", "dms", "discrete mathematical", "25mt202"]):
            return "Discrete Mathematical Structures"
        if cls.has_any_word(text, ["dbms", "database", "25cs203"]):
            return "Database Management System"
        if cls.has_any_word(text, ["oops", "java", "oop", "25cs204"]):
            return "Object Oriented Programming Through Java"
        if cls.has_any_word(text, ["ai", "artificial intelligence", "24cs302"]):
            return "Artificial Intelligence"
        if cls.has_any_word(text, ["data wrangling", "dw", "visualization", "25cs202"]):
            return "Data Wrangling and Visualization"
        return None'''

if old_extract in code:
    code = code.replace(old_extract, new_extract)
    print("Replaced extract_subject in nlu_engine.py")

code = code.replace("active_subject or 'Digital Electronics'", "active_subject or 'Digital Logic design'")
code = code.replace("How do I recover my attendance in Digital Electronics?", "How do I recover my attendance in Digital Logic design?")

with open(nlu_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated nlu_engine.py successfully!")
