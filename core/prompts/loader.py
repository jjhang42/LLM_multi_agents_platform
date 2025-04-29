import os

PROMPT_DIR = os.path.join(os.path.dirname(__file__))

def load_prompt(filename: str) -> str:
    """지정한 프롬프트 파일을 읽어 문자열로 반환"""
    path = os.path.join(PROMPT_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
