# core/agent_tools/ref_image.py
import base64
from io import BytesIO
from PIL import Image
from core.server_components.cache.in_memory_cache import InMemoryCache

def get_reference_image(session_id: str, artifact_file_id: str = None):
    cache = InMemoryCache()
    session_data = cache.get(session_id)
    ref_image_data = None

    if not session_data:
        return None

    if artifact_file_id and artifact_file_id in session_data:
        ref_image_data = session_data[artifact_file_id]
    else:
        try:
            latest_key = list(session_data.keys())[-1]
            ref_image_data = session_data.get(latest_key)
        except IndexError:
            return None

    try:
        ref_bytes = base64.b64decode(ref_image_data.bytes)
        return Image.open(BytesIO(ref_bytes))
    except Exception:
        return None
