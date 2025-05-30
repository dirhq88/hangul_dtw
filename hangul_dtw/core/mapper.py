from jamo import h2j
import numpy as np
from typing import List, Tuple, Dict, Any

from ..utils.char_utils import is_V
from ..exceptions import MappingError

def check_inf_in_matrix(
    dtw_matrix: np.ndarray,
    path: List[np.ndarray]
) -> bool:
    """주어진 경로(path) 상에 DTW 행렬(dtw_matrix)의 무한대(inf) 값이 있는지 확인합니다.

    Args:
        dtw_matrix (np.ndarray): DTW 비용 행렬
        path (List[np.ndarray]): 최적 정렬 경로

    Returns:
        bool: 경로 상에 무한대 값이 있으면 True, 그렇지 않으면 False
    """
    for i, j in path:
        if i < dtw_matrix.shape[0] and j < dtw_matrix.shape[1]:
            if dtw_matrix[i, j] == np.inf:
                return True
    return False

def find_syllable_index(
    jamo_index: int,
    hangul_str: str
) -> int:
    """주어진 한글 문자열에서 특정 자모 인덱스에 해당하는 음절 인덱스를 찾습니다.

    Args:
        jamo_index (int): 찾고자 하는 자모의 인덱스 (전체 자모 시퀀스 기준)
        hangul_str (str): 원본 한글 문자열

    Returns:
        int: 해당 자모가 속한 음절의 인덱스 (hangul_str 기준)

    Raises:
        MappingError: jamo_index가 유효한 범위를 벗어나는 경우
    """
    cumulative_len: int = 0
    for i, syllable in enumerate(hangul_str):
        try:
            decomposed_jamos: List[str] = list(h2j(syllable))
        except Exception as e:
            raise MappingError(
                message=f"한글 문자열을 자모로 분해하는 중 오류 발생: '{syllable}' at index {i} in '{hangul_str}': {str(e)}"
            ) from e

        syllable_jamo_len = len(decomposed_jamos)
        if cumulative_len <= jamo_index < cumulative_len + syllable_jamo_len:
            return i
        cumulative_len += syllable_jamo_len

    raise MappingError(
        message=f"자모 인덱스 {jamo_index}가 한글 문자열 '{hangul_str}'의 범위를 벗어났습니다. (전체 자모 길이: {cumulative_len})"
    )

def normalize_jamo_alignments(
    jamo_alignments: List[Tuple[Tuple[str, int], Tuple[str, int]]],
    raw_jamo_seq: List[str]
) -> List[Tuple[Tuple[str, int], Tuple[str, int]]]:
    """자모 정렬 결과를 정규화합니다.

    raw_jamo_seq 기준으로 정렬을 보정하여 누락된 부분을 채워 넣습니다.

    Args:
        jamo_alignments (List[Tuple[Tuple[str, int], Tuple[str, int]]]): 원본 자모 정렬 결과
        raw_jamo_seq (List[str]): 원본 문자열의 전체 자모 시퀀스

    Returns:
        List[Tuple[Tuple[str, int], Tuple[str, int]]]: 정규화된 자모 정렬 결과
    """
    if not jamo_alignments:
        return []

    check_idx: int = 0
    normalized_align: List[Tuple[Tuple[str, int], Tuple[str, int]]] = []

    for (gt_jamo, gt_idx), (raw_jamo, raw_idx) in jamo_alignments:
        if check_idx == raw_idx:
            normalized_align.append(((gt_jamo, gt_idx), (raw_jamo, raw_idx)))
            check_idx += 1
        elif check_idx < raw_idx:
            while check_idx < raw_idx:
                if check_idx < len(raw_jamo_seq):
                    normalized_align.append(((gt_jamo, gt_idx), (raw_jamo_seq[check_idx], check_idx)))
                else:
                    break
                check_idx += 1
            if raw_idx < len(raw_jamo_seq):
                normalized_align.append(((gt_jamo, gt_idx), (raw_jamo_seq[raw_idx], raw_idx)))
            check_idx += 1
        elif check_idx > raw_idx:
            normalized_align.append(((gt_jamo, gt_idx), (raw_jamo, raw_idx)))
            check_idx = raw_idx + 1

    return normalized_align

def compute_character_mapping(
    gt_text: str,
    raw_text: str,
    dtw_matrix: np.ndarray,
    path: List[np.ndarray]
) -> Tuple[List[Tuple[Tuple[str, int], Tuple[str, int]]], Dict[int, List[int]]]:
    """DTW 경로를 기반으로 자모 정렬 및 음절 매핑을 수행합니다.

    Args:
        gt_text (str): 표준 맞춤법을 따르는 한글 텍스트 (Ground Truth)
        raw_text (str): 정규화가 필요한 원본 한글 텍스트
        dtw_matrix (np.ndarray): DTW 비용 행렬
        path (List[np.ndarray]): 최적 정렬 경로

    Returns:
        Tuple[List[Tuple[Tuple[str, int], Tuple[str, int]]], Dict[int, List[int]]]:
        - jamo_alignments: 자모 단위 정렬 결과
        - syllable_mapping: 음절 단위 매핑 결과

    Raises:
        MappingError: 매핑 과정 중 오류 발생 시
    """
    try:
        gt_jamo_seq: List[str] = h2j(gt_text)
        raw_jamo_seq: List[str] = h2j(raw_text)
    except Exception as e:
        raise MappingError(
            message=f"한글 문자열을 자모로 분해하는 중 오류 발생: GT='{gt_text}', 원본='{raw_text}'. 상세: {str(e)}"
        ) from e

    jamo_alignments: List[Tuple[Tuple[str, int], Tuple[str, int]]] = []
    if not path or len(path) <= 1:
        return [], {}

    try:
        for r_idx, c_idx in path:
            if r_idx == 0 and c_idx == 0:
                continue
            if r_idx > 0 and c_idx > 0:
                if r_idx-1 < len(gt_jamo_seq) and c_idx-1 < len(raw_jamo_seq):
                    jamo_alignments.append(((gt_jamo_seq[r_idx - 1], r_idx - 1), (raw_jamo_seq[c_idx - 1], c_idx - 1)))
                else:
                    raise MappingError(
                        message=f"경로 인덱스가 범위를 벗어났습니다. 경로 포인트: ({r_idx},{c_idx}). "
                               f"GT 자모 길이: {len(gt_jamo_seq)}, 원본 자모 길이: {len(raw_jamo_seq)}"
                    )

        normalized_alignments = normalize_jamo_alignments(jamo_alignments, raw_jamo_seq)

        syllable_mapping: Dict[int, List[int]] = {}
        for (gt_jamo, gt_idx), (raw_jamo, raw_idx) in normalized_alignments:
            # 모음이 매칭된 경우에만 음절 매핑
            if is_V(gt_jamo) and is_V(raw_jamo):
                gt_syl_idx = find_syllable_index(gt_idx, gt_text)
                raw_syl_idx = find_syllable_index(raw_idx, raw_text)
                if gt_syl_idx not in syllable_mapping:
                    syllable_mapping[gt_syl_idx] = []
                if raw_syl_idx not in syllable_mapping[gt_syl_idx]:
                    syllable_mapping[gt_syl_idx].append(raw_syl_idx)

        return normalized_alignments, syllable_mapping

    except Exception as e:
        raise MappingError(
            message=f"문자 매핑 중 오류 발생: {str(e)}"
        ) from e