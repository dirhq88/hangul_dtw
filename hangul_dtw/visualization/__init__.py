"""DTW 결과 시각화 서브패키지.

이 서브패키지는 DTW(Dynamic Time Warping) 계산 결과, 정렬 경로,
자모 및 음절 매핑 등을 시각화하는 기능을 제공합니다.
주요 기능은 `visualization.py` 모듈에 구현되어 있습니다.
"""

# visualization.py 모듈에서 주요 시각화 함수들 import
from .visualization import (
    visualize_matrix_with_path,
    print_alignments,
    print_sylmap
)

# __all__ 변수를 정의하여 from .visualization import * 사용 시 노출할 이름들을 명시합니다.
# 이는 패키지의 공개 API를 명확히 하고, 의도치 않은 내부 요소의 노출을 방지합니다.
__all__ = [
    'visualize_matrix_with_path',
    'print_alignments',
    'print_sylmap'
]