# utils.py
from typing import List

def are_modalities_compatible(accepted_modes: List[str], supported_modes: List[str]) -> bool:
    return any(mode in supported_modes for mode in accepted_modes)

def new_incompatible_types_error(request_id: str):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32602,
            "message": "Incompatible input/output modalities",
        },
    }
