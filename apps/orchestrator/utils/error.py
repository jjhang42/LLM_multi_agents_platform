import traceback
from typing import Dict

def handle_exception(label: str, e: Exception) -> Dict[str, str]:
    """
    공통 예외 처리 유틸리티 함수
    - 예외 메시지를 콘솔에 출력하고 JSON 형태로 에러 응답 반환
    
    Args:
        label (str): 에러 위치 또는 태그
        e (Exception): 발생한 예외 객체

    Returns:
        Dict[str, str]: 상태 및 에러 메시지를 담은 딕셔너리
    """
    traceback.print_exc()
    return {
        "status": f"{label}_error",
        "error": str(e)
    }
