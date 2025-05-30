import re
from typing import Tuple, List, Dict, Any
import numpy as np
from .core.dtw_calculator import compute_dtw_matrix
from .core.mapper import compute_character_mapping
from .visualization.visualization import visualize_matrix_with_path, print_alignments
from .exceptions import EmptyHangulInputError, DTWCalculationError, MappingError, CharUtilsError

def hangul_DTW(
    gt_text: str,
    raw_text: str,
    print_matrix: bool = False,
    print_align: bool = False,
    multi: bool = True
) -> Tuple[np.ndarray, List[np.ndarray], List[Tuple[Tuple[str, int], Tuple[str, int]]], Dict[int, List[int]]]:
    """
    두 한글 문자열 간의 DTW(Dynamic Time Warping)를 계산하고 정렬 정보를 반환합니다.
    
    Args:
        gt_text (str): 표준 맞춤법을 따르는 한글 텍스트 (Ground Truth)
        raw_text (str): 정규화가 필요한 원본 한글 텍스트
        print_matrix (bool): DTW 행렬 시각화 여부
        print_align (bool): 정렬 정보 출력 여부
        multi (bool): 다중 문자 DTW 사용 여부
        
    Returns:
        Tuple containing:
        - DTW 행렬
        - DTW 경로
        - 자모 정렬 정보
        - 음절 매핑 정보
        
    Raises:
        EmptyHangulInputError: 입력 문자열에 한글이 없는 경우
        DTWCalculationError: DTW 계산 실패 시
        MappingError: 문자 매핑 실패 시
        CharUtilsError: 문자 유틸리티 작업 실패 시
    """
    # 한글 문자만 추출
    processed_gt: str = re.sub(r'[^ㄱ-ㅎ가-힣]+', '', gt_text)
    processed_raw: str = re.sub(r'[^ㄱ-ㅎ가-힣]+', '', raw_text)
    processed_raw_with_space: str = re.sub(r'[^\sㄱ-ㅎ가-힣]+', '', raw_text)
    
    # 한글이 없는 경우 예외 발생
    if not processed_gt or not processed_raw:
        raise EmptyHangulInputError(
            message=f"한글 필터링 후 하나 또는 두 입력 문자열이 비어있습니다.\n"
                   f"GT 텍스트: '{gt_text}' -> 필터링: '{processed_gt}'\n"
                   f"원본 텍스트: '{raw_text}' -> 필터링: '{processed_raw}'"
        )
    
    try:
        # DTW 행렬과 경로 계산
        dtw_matrix, path = compute_dtw_matrix(processed_gt, processed_raw, processed_raw_with_space, multi=multi)

        # 자모 정렬과 음절 매핑 계산
        jamo_alignments, syllable_mapping = compute_character_mapping(processed_gt, processed_raw, dtw_matrix, path)
    except (EmptyHangulInputError, DTWCalculationError, MappingError, CharUtilsError):
        raise
    except Exception as e:
        raise DTWCalculationError(
            message=f"DTW 계산 중 예기치 않은 오류 발생: {str(e)}\n"
                   f"GT 텍스트: '{gt_text}'\n"
                   f"원본 텍스트: '{raw_text}'"
        )

    # DTW 행렬 시각화
    if print_matrix:
        visualize_matrix_with_path(dtw_matrix, processed_gt, processed_raw, path)

    # 정렬 정보 출력
    if print_align:
        print_alignments(processed_gt, processed_raw, syllable_mapping, jamo_alignments)

    return dtw_matrix, path, jamo_alignments, syllable_mapping