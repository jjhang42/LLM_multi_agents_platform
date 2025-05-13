import re


def clean_json_like_block(text: str) -> str | None:
    """
    LLM 출력 중 JSON 블록을 정제
    """
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip("` \n")
    cleaned = re.sub(r"//.*?$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
    cleaned = cleaned.strip()

    # 루트 객체 또는 리스트만 추출
    if "{" in cleaned:
        start = cleaned.find("{")
        depth = 0
        for i in range(start, len(cleaned)):
            if cleaned[i] == "{":
                depth += 1
            elif cleaned[i] == "}":
                depth -= 1
                if depth == 0:
                    return cleaned[start:i+1].strip()

    if "[" in cleaned:
        start = cleaned.find("[")
        depth = 0
        for i in range(start, len(cleaned)):
            if cleaned[i] == "[":
                depth += 1
            elif cleaned[i] == "]":
                depth -= 1
                if depth == 0:
                    return cleaned[start:i+1].strip()

    return None
