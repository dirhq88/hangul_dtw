import numpy as np
from typing import Tuple, List

# 패키지 내부 모듈 import (상대 경로 사용)
from ..utils.file_loaders import FC_TABLE, VW_TABLE, LC_TABLE
from ..utils.char_utils import *
from ..utils.data_utils import repeat_PS
from ..exceptions import CharUtilsError

# 모음 매핑 정의
vowel_set_map = {
    'ᅪ': {'ᅡ'}, 'ᅡ': {'ᅡ'}, 'ᅣ': {'ᅡ'}, 'ᅱ': {'ᅵ'}, 'ᅵ': {'ᅵ'},
    'ᅯ': {'ᅥ'}, 'ᅥ': {'ᅥ'}, 'ᅧ': {'ᅥ'}, 'ᅭ': {'ᅩ'}, 'ᅩ': {'ᅩ', 'ᅥ'},
    'ᅲ': {'ᅮ', 'ᅳ'}, 'ᅮ': {'ᅮ', 'ᅳ'}, 'ᅰ': {'ᅦ', 'ᅢ'}, 'ᅫ': {'ᅦ', 'ᅢ'}, 'ᅬ': {'ᅦ', 'ᅢ'},
    'ᅨ': {'ᅦ', 'ᅢ'}, 'ᅦ': {'ᅦ', 'ᅢ'}, 'ᅤ': {'ᅦ', 'ᅢ'}, 'ᅢ': {'ᅦ', 'ᅢ'},
    'ᅴ': {'ᅳ', 'ᅵ'}, 'ᅳ': {'ᅳ'}
}

# --- 비용 테이블 조회 및 유사도 관련 함수 ---

def find_cost_in_table(
    gt_jamo: str, 
    raw_jamo: str
) -> float:
    """두 자모 간의 비용을 미리 정의된 테이블에서 조회합니다.

    Args:
        gt_jamo (str): Ground Truth 자모
        raw_jamo (str): 원본 자모

    Returns:
        float: 두 자모 간의 비용. 매칭이 불가능한 경우 np.inf 반환
    """
    try:
        if is_V(gt_jamo) and is_V(raw_jamo):
            return float(VW_TABLE.loc[gt_jamo, raw_jamo])
        elif is_FC(gt_jamo) and is_FC(raw_jamo):
            return float(FC_TABLE.loc[gt_jamo, raw_jamo])
        elif is_LC(gt_jamo) and is_LC(raw_jamo):
            return float(LC_TABLE.loc[gt_jamo, raw_jamo])
        else:
            if (is_FC(gt_jamo) and is_LC(raw_jamo)) or (is_FC(raw_jamo) and is_LC(gt_jamo)):
                return 1.0
            else:
                return np.inf
    except (KeyError, CharUtilsError):
        return np.inf

def find_similarity(gt_jamo: str, raw_jamo: str) -> bool:
    """두 자모 간의 유사도를 비용 테이블과 임계값을 기준으로 판단합니다.

    Args:
        gt_jamo (str): Ground Truth 자모
        raw_jamo (str): 원본 자모

    Returns:
        bool: 두 자모가 유사하다고 판단되면 True, 그렇지 않으면 False
    """
    try:
        cost = find_cost_in_table(gt_jamo, raw_jamo)
        if cost == np.inf:
            return False

        if is_V(gt_jamo) and is_V(raw_jamo) and cost <= 0.3:
            return True
        elif is_FC(gt_jamo) and is_FC(raw_jamo) and cost <= 0.2:
            return True
        elif is_LC(gt_jamo) and is_LC(raw_jamo) and cost <= 0.2:
            return True
        else:
            return False
    except (KeyError, CharUtilsError):
        return False

# --- 매칭 범위 계산 함수 ---
# find_max_V_range, find_max_range 함수는 이전과 동일 (로깅 추가 없음)
def find_max_vowel_offset(
    gt_jamo_seq: List[str],
    gt_idx: int,
    raw_jamo_seq: List[str],
    raw_idx: int
) -> Tuple[int, int]:
    """모음 자모에 대한 최대 매칭 범위를 계산합니다.

    Args:
        gt_jamo_seq (List[str]): Ground Truth 자모 시퀀스
        gt_idx (int): Ground Truth 자모 인덱스
        raw_jamo_seq (List[str]): 원본 자모 시퀀스
        raw_idx (int): 원본 자모 인덱스

    Returns:
        Tuple[int, int]: (Ground Truth 방향 최대 오프셋, 원본 방향 최대 오프셋)
    """
    gt_offset, raw_offset = 1, 1
    
    current_raw_vowel = raw_jamo_seq[raw_idx]
    current_gt_vowel = gt_jamo_seq[gt_idx]
    
    # 모음 매칭 가능 여부 확인
    is_matching_vowel = (
        current_raw_vowel in ['ᅡ', 'ᅥ', 'ᅩ', 'ᅮ', 'ᅢ', 'ᅦ', 'ᅵ', 'ᅳ'] and
        (find_similarity(current_gt_vowel, current_raw_vowel) or
         (current_gt_vowel in vowel_set_map and current_raw_vowel in vowel_set_map[current_gt_vowel]))
    )
    
    if is_matching_vowel:
        current_raw_offset = 1
        while True:
            prev_raw_idx = raw_idx - current_raw_offset
            if prev_raw_idx < 0:
                raw_offset = current_raw_offset
                break
                
            prev_raw_vowel = raw_jamo_seq[prev_raw_idx]
            if prev_raw_vowel in vowel_set_map[current_gt_vowel] or is_FCE(prev_raw_vowel):
                current_raw_offset += 1
            else:
                if is_FC(prev_raw_vowel):
                    raw_offset = current_raw_offset
                elif is_V(prev_raw_vowel) and (
                    find_similarity(prev_raw_vowel, current_raw_vowel) or
                    (prev_raw_vowel in vowel_set_map.get(current_raw_vowel, set()))
                ):
                    raw_offset = current_raw_offset + 1
                elif is_LC(prev_raw_vowel) or is_V(prev_raw_vowel) or is_space(prev_raw_vowel):
                    if is_FCE(prev_raw_vowel):
                        raw_offset = current_raw_offset - 1
                    else:
                        raw_offset = current_raw_offset
                else:
                    raw_offset = 1
                break
                
    return gt_offset, raw_offset

def find_max_offset(
    gt_jamo_seq: List[str],
    gt_idx: int,
    raw_jamo_seq: List[str],
    raw_idx: int
) -> Tuple[int, int]:
    """두 자모 시퀀스 간의 최대 매칭 범위를 계산합니다.

    Args:
        gt_jamo_seq (List[str]): Ground Truth 자모 시퀀스
        gt_idx (int): Ground Truth 자모 인덱스
        raw_jamo_seq (List[str]): 원본 자모 시퀀스
        raw_idx (int): 원본 자모 인덱스

    Returns:
        Tuple[int, int]: (Ground Truth 방향 최대 오프셋, 원본 방향 최대 오프셋)
    """
    gt_offset, raw_offset = 1, 1
    if is_V(gt_jamo_seq[gt_idx]) and is_V(raw_jamo_seq[raw_idx]):
        gt_offset, raw_offset = find_max_vowel_offset(gt_jamo_seq, gt_idx, raw_jamo_seq, raw_idx)
    return gt_offset, raw_offset

# --- DTW 비용 계산 함수 ---

def calculate_single_cost(
    gt_jamo_seq: List[str],
    gt_idx: int,
    raw_jamo_seq: List[str],
    raw_idx: int
) -> float:
    """단일 자모 간의 비용을 계산합니다 (1:1 매칭).

    Args:
        gt_jamo_seq (List[str]): Ground Truth 자모 시퀀스
        gt_idx (int): Ground Truth 자모 인덱스
        raw_jamo_seq (List[str]): 원본 자모 시퀀스
        raw_idx (int): 원본 자모 인덱스

    Returns:
        float: 두 자모 간의 비용
    """
    return find_cost_in_table(gt_jamo_seq[gt_idx], raw_jamo_seq[raw_idx])

def calculate_multi_cost(
    gt_jamo_seq: List[str],
    gt_offset: int,
    gt_idx: int,
    raw_jamo_seq: List[str],
    raw_offset: int,
    raw_idx: int
) -> float:
    """다중 자모 간의 비용을 계산합니다 (n:m 매칭).

    Args:
        gt_jamo_seq (List[str]): Ground Truth 자모 시퀀스
        gt_offset (int): Ground Truth 방향 오프셋
        gt_idx (int): Ground Truth 자모 인덱스
        raw_jamo_seq (List[str]): 원본 자모 시퀀스
        raw_offset (int): 원본 방향 오프셋
        raw_idx (int): 원본 자모 인덱스

    Returns:
        float: 다중 자모 간의 비용
    """
    current_gt_char = gt_jamo_seq[gt_idx]
    current_raw_char = raw_jamo_seq[raw_idx]

    if raw_offset > 1 and (raw_idx - 1 >= 0) and is_FCE(raw_jamo_seq[raw_idx - 1]) and current_raw_char in ['ᅡ','ᅵ','ᅥ','ᅩ','ᅮ','ᅦ','ᅢ','ᅳ']:
        target_vowel_set = vowel_set_map.get(current_gt_char)
        if target_vowel_set:
            if repeat_PS(raw_jamo_seq, raw_offset, raw_idx, target_vowel_set):
                return find_cost_in_table(current_gt_char, raw_jamo_seq[raw_idx - raw_offset + 1])
            else: 
                return np.inf
        else: 
            return np.inf

    elif gt_offset == 1 and raw_offset == 1:
        if (gt_idx - 1 >= 0) and is_DLC(gt_jamo_seq[gt_idx - 1]) and is_FC(current_gt_char):
            prev_gt_char_dlc = gt_jamo_seq[gt_idx - 1]
            if not (raw_idx - 1 >= 0 and find_similarity(prev_gt_char_dlc, raw_jamo_seq[raw_idx - 1])):
                return np.inf
            lc_cost = find_cost_in_table(prev_gt_char_dlc, raw_jamo_seq[raw_idx - 1])
            try:
                fc_set_from_dlc = converted(prev_gt_char_dlc, current_gt_char, 'FC')
            except CharUtilsError:
                return np.inf
            if current_raw_char in fc_set_from_dlc:
                fc_cost_candidates = [find_cost_in_table(current_raw_char, fc_cand) for fc_cand in fc_set_from_dlc if fc_cand != '.']
                fc_cost = min(fc_cost_candidates) if fc_cost_candidates else np.inf
            else: 
                fc_cost = np.inf
            return lc_cost + fc_cost if lc_cost != np.inf and fc_cost != np.inf else np.inf

        elif (gt_idx - 1 >= 0) and is_SLC(gt_jamo_seq[gt_idx - 1]) and is_FC(current_gt_char):
            prev_gt_char_slc = gt_jamo_seq[gt_idx - 1]
            try:
                fc_set_from_slc = converted(prev_gt_char_slc, current_gt_char, 'FC')
            except CharUtilsError:
                return np.inf
            if (raw_idx - 1 >= 0) and find_similarity(prev_gt_char_slc, raw_jamo_seq[raw_idx - 1]) and \
               current_raw_char in fc_set_from_slc:
                fc_cost_candidates = [find_cost_in_table(current_raw_char, fc_cand) for fc_cand in fc_set_from_slc if fc_cand != '.']
                return min(fc_cost_candidates) if fc_cost_candidates else np.inf
            else: 
                return find_cost_in_table(current_gt_char, current_raw_char)
        else: 
            return find_cost_in_table(current_gt_char, current_raw_char)
            
    elif gt_offset == 1 and raw_offset == 0:  # u == 1 and v == 0 케이스 추가
        if (gt_idx - 1 >= 0) and is_FCE(current_gt_char) and is_FC(current_raw_char) and \
           is_LC(gt_jamo_seq[gt_idx - 1]) and find_similarity(LC_to_FC(gt_jamo_seq[gt_idx - 1]), current_raw_char):
            return find_cost_in_table(LC_to_FC(gt_jamo_seq[gt_idx - 1]), current_raw_char)
            
        elif (gt_idx - 1 >= 0) and is_LC(gt_jamo_seq[gt_idx - 1]) and is_FC(current_gt_char) and is_FC(current_raw_char):
            try:
                fc_set = converted(gt_jamo_seq[gt_idx - 1], current_gt_char, 'FC')
                fc_cost_candidates = [find_cost_in_table(current_raw_char, fc) for fc in fc_set if fc != '.']
                return min(fc_cost_candidates) if fc_cost_candidates else np.inf
            except CharUtilsError:
                return np.inf
        else:
            return find_cost_in_table(current_gt_char, current_raw_char)
            
    elif gt_offset <= 1 and raw_offset <= 1:
        return find_cost_in_table(current_gt_char, current_raw_char)
        
    else:
        return np.inf