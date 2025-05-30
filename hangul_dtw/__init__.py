"""한글 DTW 패키지.

이 패키지는 두 한글 문자열 간의 DTW(Dynamic Time Warping) 거리를 계산하고,
정렬 경로 및 자모/음절 단위 매핑을 분석하는 기능을 제공합니다.
주요 기능은 `hangul_DTW` 함수를 통해 접근할 수 있습니다.
"""

from .hangul_dtw import hangul_DTW
from .exceptions import (
    HangulDTWError,
    EmptyHangulInputError,
    DTWCalculationError,
    MappingError,
    CharUtilsError
)

__all__ = [
    'hangul_DTW',
    'HangulDTWError',
    'EmptyHangulInputError',
    'DTWCalculationError',
    'MappingError',
    'CharUtilsError'
]

__version__ = "0.1.0"
__author__ = "Jiwon Choi"  
__email__ = "dirhq88@gmail.com" 