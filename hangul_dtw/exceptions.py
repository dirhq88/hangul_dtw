"""한글 DTW 패키지의 사용자 정의 예외 클래스들.

이 모듈은 hangul_dtw 패키지 내에서 사용되는 사용자 정의 예외 클래스들을 정의합니다.
"""
from typing import Any

class HangulDTWError(Exception):
    """한글 DTW 패키지의 기본 예외 클래스.

    다른 모든 패키지 관련 사용자 정의 예외는 이 클래스를 상속받습니다.
    이를 통해 사용자는 `except HangulDTWError:` 구문으로 패키지에서 발생 가능한
    모든 예외를 한 번에 처리할 수 있습니다.
    """
    pass

class EmptyHangulInputError(HangulDTWError):
    """한글 필터링 후 입력 문자열이 비어있을 때 발생하는 예외.

    한글 필터링 후 입력 문자열 (`gt_text` 또는 `raw_text`) 중 하나 또는 둘 모두가
    비어있을 경우 발생하는 예외입니다.

    Attributes:
        message (str): 에러에 대한 설명 메시지
        filename (str): 에러가 발생한 원본 파일명 또는 식별자
        error_code (str): 에러의 원인을 나타내는 간단한 코드 (예: "EMPTY_INPUT")
    """
    def __init__(self, message: str, filename: str, error_code: str = "EMPTY_INPUT"):
        """EmptyHangulInputError 초기화.

        Args:
            message (str): 에러에 대한 설명 메시지
            filename (str): 에러가 발생한 원본 파일명 또는 식별자
            error_code (str, optional): 에러의 원인을 나타내는 간단한 코드
                                      기본값은 "EMPTY_INPUT"입니다
        """
        super().__init__(message)
        self.filename = filename
        self.error_code = error_code

class DTWCalculationError(HangulDTWError):
    """DTW 계산 과정에서 발생하는 예외.

    DTW 행렬 계산 또는 경로 추적 중 예상치 못한 문제가 발생했을 때 사용됩니다.

    Attributes:
        message (str): 에러에 대한 설명 메시지
        details (Any, optional): 에러와 관련된 추가적인 상세 정보
    """
    def __init__(self, message: str, details: Any = None):
        super().__init__(message)
        self.details = details
        
class MappingError(HangulDTWError):
    """정렬 매핑 과정에서 발생하는 예외.

    자모 정렬, 음절 매핑 등 매핑 관련 로직에서 오류 발생 시 사용됩니다.

    Attributes:
        message (str): 에러에 대한 설명 메시지
        filename (str, optional): 에러가 발생한 원본 파일명 또는 식별자
        details (Any, optional): 에러와 관련된 추가적인 상세 정보
    """
    def __init__(self, message: str, filename: str = "", details: Any = None):
        super().__init__(message)
        self.filename = filename
        self.details = details
        
class CharUtilsError(HangulDTWError):
    """자모 유틸리티 함수에서 발생하는 예외.

    자모 변환, 타입 판별 등 자모 관련 유틸리티 함수에서 오류 발생 시 사용됩니다.

    Attributes:
        message (str): 에러에 대한 설명 메시지
        function_name (str, optional): 에러가 발생한 함수의 이름
        char_input (str, optional): 문제가 된 입력 문자
    """
    def __init__(self, message: str, function_name: str = "", char_input: str = ""):
        super().__init__(message)
        self.function_name = function_name
        self.char_input = char_input