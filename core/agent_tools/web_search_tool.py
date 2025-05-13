# core/agent_tools/web_search_tool.py

import os
import logging
import requests
from crewai.tools import tool

logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CUSTOM_SEARCH_CX")
GOOGLE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"

@tool("WebSearchTool")
def web_search_tool(query: str) -> str:
    """
    Perform a Google Custom Search and return markdown-formatted top results.
    """
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        return "❌ Google API Key or Search Engine ID (CX) is missing."

    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": 5,
    }

    try:
        response = requests.get(GOOGLE_ENDPOINT, params=params)
        response.raise_for_status()
        results = response.json().get("items", [])
        if not results:
            return "❌ No search results found."

        markdown = ""
        for item in results:
            markdown += f"- **[{item['title']}]({item['link']})**\n  {item['snippet']}\n\n"
        return markdown.strip()
    except Exception as e:
        logger.error(f"[WebSearchTool] Google search failed: {e}")
        return f"❌ Web search error: {str(e)}"
