# core/agent_tools/image_tool.py

import base64
import logging
from uuid import uuid4
from crewai.tools import tool
from typing import Optional
from core.agent_tools.client import get_gemini_client
from core.agent_tools.prompt_builder import build_prompt
from core.agent_tools.ref_image import get_reference_image
from core.system.formats.image_data import Imagedata
from core.server_components.cache.in_memory_cache import InMemoryCache
from google.generativeai import types

logger = logging.getLogger(__name__)

@tool("ImageGenerationTool")
def generate_image_tool(prompt: str, session_id: str, artifact_file_id: Optional[str] = None) -> Optional[str]:
    """
    Image generation tool that generates images or modifies a given image based on a prompt.
    Uses Gemini multimodal API to produce an image from a textual prompt with optional image context.
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty")

    client = get_gemini_client()
    cache = InMemoryCache()

    text_input = build_prompt(prompt)
    ref_image = get_reference_image(session_id, artifact_file_id)

    contents = [text_input, ref_image] if ref_image else text_input

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(response_modalities=["Text", "Image"]),
        )
    except Exception as e:
        logger.error(f"[ImageGenerationTool] Gemini API error: {e}")
        return None

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            try:
                data = Imagedata(
                    bytes=base64.b64encode(part.inline_data.data).decode("utf-8"),
                    mime_type=part.inline_data.mime_type,
                    name="generated_image.png",
                    id=uuid4().hex,
                )

                session_data = cache.get(session_id)
                if session_data is None:
                    cache.set(session_id, {data.id: data})
                else:
                    session_data[data.id] = data

                logger.info(f"[ImageGenerationTool] Image generated: {data.id}")
                return data.id
            except Exception as e:
                logger.error(f"[ImageGenerationTool] Image unpack error: {e}")
    return None
