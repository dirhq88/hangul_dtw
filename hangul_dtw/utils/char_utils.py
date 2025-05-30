from jamo import is_jamo
from typing import List, Set, Union, Tuple

from ..exceptions import CharUtilsError
from .file_loaders import CV_TABLE

# --- 한글 자모 유니코드 블록 정의 ---
# 초성 (First Consonants)
FC_START_CODE = 0x1100
FC_END_CODE = 0x1112

# 중성 (Vowels)
V_START_CODE = 0x1161
V_END_CODE = 0x1175

# 종성 (Last Consonants)
LC_START_CODE = 0x11A8
LC_END_CODE = 0x11C2

# 겹받침 (Double Last Consonants)
DOUBLE_LAST_CONSONANT_CODES: Set[int] = {
    0x11AA,  # ㄳ
    0x11AC,  # ㄵ
    0x11AD,  # ᆭ
    0x11B0,  # ㄺ
    0x11B1,  # ㄻ
    0x11B2,  # ㄼ
    0x11B3,  # ㄽ
    0x11B4,  # ㄾ
    0x11B5,  # ㄿ
    0x11B6,  # ㅀ
    0x11B9   # ㅄ
}

INITIAL_EUNG_CHAR: str = '\u110b'  # 초성 'ㅇ'

def find_type(jamo_char: str) -> str:
    """주어진 한글 자모 문자의 타입을 반환합니다.

    Args:
        jamo_char (str): 타입을 판별할 한글 자모 문자 (한 글자)

    Returns:
        str: 자모 타입 ("FC", "V", "LC") 또는 "Not a jamo", "Unknown jamo type"

    Raises:
        CharUtilsError: 입력이 단일 문자가 아니거나 유니코드 변환에 실패할 경우
    """
    if not isinstance(jamo_char, str) or len(jamo_char) != 1:
        raise CharUtilsError(
            f"입력은 단일 문자여야 합니다. 입력값: '{jamo_char}' (타입: {type(jamo_char)})",
            function_name="find_type", char_input=str(jamo_char)
        )

    if not is_jamo(jamo_char):
        return "Not a jamo"
    
    try:
        jamo_code = ord(jamo_char)
    except TypeError:
        raise CharUtilsError(
            f"ord() 함수에 잘못된 타입이 입력되었습니다: {type(jamo_char)} (문자: '{jamo_char}')",
            function_name="find_type", char_input=str(jamo_char)
        )

    if FC_START_CODE <= jamo_code <= FC_END_CODE:
        return "FC"
    elif V_START_CODE <= jamo_code <= V_END_CODE:
        return "V"
    elif LC_START_CODE <= jamo_code <= LC_END_CODE:
        return "LC"
    else:
        return "Unknown jamo type"

def is_FC(jamo_char: str) -> bool:
    """주어진 문자가 한글 초성인지 확인합니다.

    Args:
        jamo_char (str): 확인할 문자

    Returns:
        bool: 초성이면 True, 아니면 False
    """
    if not isinstance(jamo_char, str) or len(jamo_char) != 1:
        return False
    try:
        jamo_code = ord(jamo_char)
        return FC_START_CODE <= jamo_code <= FC_END_CODE
    except TypeError:
        return False

def is_V(jamo_char: str) -> bool:
    """주어진 문자가 한글 중성인지 확인합니다.

    Args:
        jamo_char (str): 확인할 문자

    Returns:
        bool: 중성이면 True, 아니면 False
    """
    if not isinstance(jamo_char, str) or len(jamo_char) != 1:
        return False
    try:
        jamo_code = ord(jamo_char)
        return V_START_CODE <= jamo_code <= V_END_CODE
    except TypeError:
        return False

def is_LC(jamo_char: str) -> bool:
    """주어진 문자가 한글 종성인지 확인합니다.

    Args:
        jamo_char (str): 확인할 문자

    Returns:
        bool: 종성이면 True, 아니면 False
    """
    if not isinstance(jamo_char, str) or len(jamo_char) != 1:
        return False
    try:
        jamo_code = ord(jamo_char)
        return LC_START_CODE <= jamo_code <= LC_END_CODE
    except TypeError:
        return False

def is_space(jamo_char: str) -> bool:
    """주어진 문자가 공백인지 확인합니다.
    """
    return jamo_char == ' '

def is_DLC(jamo_char: str) -> bool:
    """주어진 문자가 한글 겹받침인지 확인합니다.

    Args:
        jamo_char (str): 확인할 문자

    Returns:
        bool: 겹받침이면 True, 아니면 False
    """
    if not isinstance(jamo_char, str) or len(jamo_char) != 1:
        return False
    try:
        jamo_code = ord(jamo_char)
        return jamo_code in DOUBLE_LAST_CONSONANT_CODES
    except TypeError:
        return False

def is_SLC(jamo_char: str) -> bool:
    """주어진 문자가 한글 단일받침인지 확인합니다.

    Args:
        jamo_char (str): 확인할 문자

    Returns:
        bool: 단일받침이면 True, 아니면 False
    """
    return is_LC(jamo_char) and not is_DLC(jamo_char)

def is_FCE(jamo_char: str) -> bool:
    """주어진 문자가 초성 'ㅇ'인지 확인합니다.

    Args:
        jamo_char (str): 확인할 문자

    Returns:
        bool: 초성 'ㅇ'이면 True, 아니면 False
    """
    return jamo_char == INITIAL_EUNG_CHAR

def LC_to_FC(lc_char: str) -> str:
    """주어진 종성을 해당하는 대표 초성으로 변환합니다.

    Args:
        lc_char (str): 변환할 종성 문자

    Returns:
        str: 변환된 초성 문자

    Raises:
        CharUtilsError: 입력이 유효한 종성이 아니거나 변환 규칙이 없는 경우
    """
    pairs = {"ᆨ": "ᄀ", "ᆩ": "ᄁ", "ᆫ": "ᄂ", "ᆮ": "ᄃ", "ᆯ": "ᄅ", "ᆷ": "ᄆ", "ᆸ": "ᄇ",
             "ᆺ": "ᄉ", "ᆻ": "ᄊ", "ᆽ": "ᄌ", "ᆾ": "ᄎ", "ᆿ": "ᄏ", "ᇀ": "ᄐ", "ᇁ": "ᄑ",
             "ᆪ": "ᄊ", "ᆬ": "ᄌ", "ᆰ": "ᄀ", "ᆱ": "ᄆ", "ᆲ": "ᄇ", "ᆳ": "ᄊ", "ᆴ": "ᄐ",
             "ᆵ": "ᄑ", "ᆹ": "ᄊ", "ᆭ": "ᄂ", "ᆶ": "ᄅ", "ᆼ": "ᄋ", "ᇂ": "ᄋ"}

    if not is_LC(lc_char):
        raise CharUtilsError(
            f"입력 '{lc_char}'은(는) 유효한 종성이 아닙니다.",
            function_name="LC_to_FC", char_input=lc_char
        )
    try:
        return pairs[lc_char]
    except KeyError:
        raise CharUtilsError(
            f"종성 '{lc_char}'에 대한 초성 매핑이 없습니다.",
            function_name="LC_to_FC", char_input=lc_char
        )

def converted(
    lc_char: str,
    fc_char: str,
    return_type: str = 'Both'
) -> Union[List[str], Tuple[List[str], List[str]]]:
    """주어진 종성과 다음 초성의 조합에 따라 변환된 자모 집합을 반환합니다.

    Args:
        lc_char (str): 종성 문자
        fc_char (str): 다음 초성 문자
        return_type (str, optional): 반환할 결과 타입 ('LC', 'FC', 'Both'). 기본값은 'Both'

    Returns:
        Union[List[str], Tuple[List[str], List[str]]]: 변환된 자모 집합
            - 'LC': 변환된 종성 리스트
            - 'FC': 변환된 초성 리스트
            - 'Both': (변환된 종성 리스트, 변환된 초성 리스트)

    Raises:
        CharUtilsError: 입력이 유효하지 않거나 변환 규칙이 없는 경우
    """
    if not is_LC(lc_char):
        raise CharUtilsError(
            f"입력 '{lc_char}'은(는) 유효한 종성이 아닙니다.",
            function_name="converted", char_input=lc_char
        )
    if not is_FC(fc_char):
        raise CharUtilsError(
            f"입력 '{fc_char}'은(는) 유효한 초성이 아닙니다.",
            function_name="converted", char_input=fc_char
        )

    try:
        result_str: str = CV_TABLE.loc[lc_char, fc_char]
    except KeyError:
        raise CharUtilsError(
            f"종성='{lc_char}', 초성='{fc_char}'에 대한 변환 규칙이 없습니다.",
            function_name="converted", char_input=f"{lc_char}+{fc_char}"
        )
    except Exception as e:
        raise CharUtilsError(
            f"CV_TABLE 접근 중 오류 발생 (종성='{lc_char}', 초성='{fc_char}'): {e}",
            function_name="converted", char_input=f"{lc_char}+{fc_char}"
        )

    parts = result_str.split("/")
    if len(parts) != 2:
        raise CharUtilsError(
            f"CV_TABLE의 형식이 잘못되었습니다 (종성='{lc_char}', 초성='{fc_char}'). "
            f"예상: 'LCs/FCs', 실제: '{result_str}'",
            function_name="converted", char_input=f"{lc_char}+{fc_char}"
        )

    lc_set_str, fc_set_str = parts
    converted_lc_list = [s.strip() for s in lc_set_str.split(",") if s.strip()]
    converted_fc_list = [s.strip() for s in fc_set_str.split(",") if s.strip()]

    if return_type == 'LC':
        return converted_lc_list
    elif return_type == 'FC':
        return converted_fc_list
    elif return_type == 'Both':
        return converted_lc_list, converted_fc_list
    else:
        raise CharUtilsError(
            f"잘못된 return_type '{return_type}'입니다. 'LC', 'FC', 또는 'Both'여야 합니다.",
            function_name="converted"
        )