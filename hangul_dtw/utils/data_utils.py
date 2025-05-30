from typing import List, Set

from .char_utils import is_FCE

def is_PS(
    raw_jamo_seq: List[str],
    current_idx: int,
    target_vowel_set: Set[str]
) -> bool:
    """Prolonged Syllable (PS, 늘어난 음절) 패턴인지 확인합니다.

    raw 자모 시퀀스의 특정 위치에서 이전 자모가 초성 'ㅇ'이고
    현재 자모가 주어진 모음 집합에 속하는지 확인합니다.

    Args:
        raw_jamo_seq (List[str]): 검사할 raw 자모 시퀀스
        current_idx (int): raw 자모 시퀀스에서 현재 검사할 자모의 인덱스
        target_vowel_set (Set[str]): 현재 자모가 속해야 하는 모음 집합

    Returns:
        bool: PS 패턴이면 True, 아니면 False
    """
    if current_idx - 1 < 0:
        return False
    
    return is_FCE(raw_jamo_seq[current_idx - 1]) and raw_jamo_seq[current_idx] in target_vowel_set

def repeat_PS(
    raw_jamo_seq: List[str],
    check_len: int,
    current_idx: int,
    target_vowel_set: Set[str]
) -> bool:
    """Prolonged Syllable (PS, 늘어난 음절) 패턴이 지정된 길이만큼 반복되는지 확인합니다.

    Args:
        raw_jamo_seq (List[str]): 검사할 raw 자모 시퀀스
        check_len (int): 확인할 자모의 개수 (현재 위치 포함)
        current_idx (int): raw 자모 시퀀스에서 현재 검사의 끝 인덱스
        target_vowel_set (Set[str]): 반복되어야 하는 모음 집합

    Returns:
        bool: PS 패턴이 지정된 길이만큼 반복되면 True, 아니면 False
    """
    if check_len <= 1:
        return False

    num_ps_pairs = check_len // 2

    for i in range(num_ps_pairs):
        ps_vowel_idx = current_idx - (i * 2)
        if ps_vowel_idx < 1:
            return False
        
        if not is_PS(raw_jamo_seq, ps_vowel_idx, target_vowel_set):
            return False
            
    return True