"""DTW 계산, 비용 함수, 매핑을 위한 핵심 서브패키지.

이 서브패키지는 DTW(Dynamic Time Warping) 알고리즘의 핵심 로직,
즉 비용 행렬 계산 함수, 다양한 비용 계산 함수들, 그리고 DTW 결과를
바탕으로 한 자모/음절 매핑 함수들을 포함합니다.
"""

# dtw_calculator 모듈에서 compute_dtw_matrix 함수 import
from .dtw_calculator import compute_dtw_matrix

# cost_calculator 모듈에서 주요 비용 계산 함수들 import
from .cost_calculator import (
    calculate_single_cost,
    calculate_multi_cost,
    find_max_offset,
    find_cost_in_table,
    find_similarity,
    find_max_vowel_offset
)

# mapper 모듈에서 주요 매핑 관련 함수들 import
from .mapper import (
    compute_character_mapping,
    normalize_jamo_alignments,
    find_syllable_index,
    check_inf_in_matrix
)

__all__ = [
    'compute_dtw_matrix',
    'calculate_single_cost',
    'calculate_multi_cost',
    'find_max_offset',
    'find_cost_in_table',
    'find_similarity',
    'find_max_vowel_offset',
    'compute_character_mapping',
    'normalize_jamo_alignments',
    'find_syllable_index',
    'check_inf_in_matrix'
]