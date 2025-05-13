# core/agent_tools/prompt_builder.py
def build_prompt(user_prompt: str) -> str:
    return f"{user_prompt.strip()}\n\nIgnore any input images if they do not match the request."
