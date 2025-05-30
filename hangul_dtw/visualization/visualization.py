"""DTW 결과 시각화 유틸리티 모듈.

이 모듈은 DTW 비용 행렬, 최적 정렬 경로, 자모 및 음절 단위 정렬 결과를
matplotlib을 사용하여 시각화하는 함수들을 제공합니다.
"""

from jamo import h2j
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches 
import re 
from typing import List, Tuple, Dict, Any

try:
    # 한글 폰트 설정
    font_found = False
    font_families_to_try = ['NanumGothic', 'Malgun Gothic', 'AppleGothic', 'sans-serif']
    for font_family in font_families_to_try:
        try:
            plt.rcParams['font.family'] = font_family
            font_found = True
            break 
        except Exception:
            continue
    
    if not font_found:
        print("경고 (visualization): 한글 폰트를 설정할 수 없습니다. "
              "시스템의 sans-serif 폰트를 사용합니다. 한글이 올바르게 표시되지 않을 수 있습니다.")

    # 마이너스 부호 깨짐 방지 설정
    plt.rcParams['axes.unicode_minus'] = False

except Exception as e:
    print(f"경고 (visualization): 한글 폰트 설정 중 오류 발생: {e}. "
          "그래프에서 한글이 올바르게 표시되지 않을 수 있습니다.")

from ..utils.char_utils import find_type
from ..core.mapper import find_syllable_index

def visualize_matrix_with_path(
    matrix: np.ndarray,
    gt_text: str,
    raw_text: str,
    path: List[np.ndarray]
) -> None:
    """DTW 비용 행렬과 최적 정렬 경로를 시각화합니다.

    Args:
        matrix (np.ndarray): DTW 비용 행렬 (일반적으로 (N+1) x (M+1) 크기)
        gt_text (str): 첫 번째 한글 문자열 (Y축 레이블용)
        raw_text (str): 두 번째 한글 문자열 (X축 레이블용)
        path (List[np.ndarray]): 최적 정렬 경로
            경로의 각 요소는 [행 인덱스, 열 인덱스] 형태의 NumPy 배열입니다
    """
    if not isinstance(matrix, np.ndarray) or matrix.ndim != 2:
        print("오류 (visualize_matrix_with_path): 'matrix'는 2차원 NumPy 배열이어야 합니다.")
        return
    if not path:
        print("경고 (visualize_matrix_with_path): 경로가 비어있어 상세 경로 시각화를 건너뜁니다.")

    try:
        gt_jamo: List[str] = h2j(gt_text)
        raw_jamo: List[str] = h2j(raw_text)
    except Exception as e:
        print(f"오류 (visualize_matrix_with_path): 한글 문자열을 자모로 분해하는 데 실패했습니다: {e}")
        return

    trimmed_matrix: np.ndarray = matrix[1:, 1:]

    if trimmed_matrix.shape[0] == 0 or trimmed_matrix.shape[1] == 0:
        print("경고 (visualize_matrix_with_path): 잘린 행렬이 비어있어 시각화할 수 없습니다.")
        return
    if not gt_jamo or not raw_jamo:
        print("경고 (visualize_matrix_with_path): 하나 또는 두 자모 시퀀스가 비어있어 레이블을 올바르게 설정할 수 없습니다.")

    fig, ax = plt.subplots(figsize=(20, 14))
    
    im = ax.imshow(trimmed_matrix, cmap='Blues')
    
    for i in range(trimmed_matrix.shape[0]):
        for j in range(trimmed_matrix.shape[1]):
            ax.text(j, i, f'{trimmed_matrix[i, j]:.1f}',
                    ha='center', va='center', color='black', fontweight='bold')

    path_coords: List[Tuple[int, int]] = []
    if path:
        path_coords = [(int(point[0]) - 1, int(point[1]) - 1) for point in path
                       if int(point[0]) > 0 and int(point[1]) > 0 and
                          int(point[0]) -1 < trimmed_matrix.shape[0] and int(point[1]) -1 < trimmed_matrix.shape[1]]

    if path_coords:
        path_y, path_x = zip(*path_coords)
        ax.plot(path_x, path_y, color='gray', linewidth=2, zorder=1)

        for y_coord, x_coord in path_coords:
            rect = patches.Rectangle((x_coord - 0.5, y_coord - 0.5), 1, 1,
                                     linewidth=2,
                                     edgecolor='red',
                                     facecolor='none',
                                     zorder=2)
            ax.add_patch(rect)
    
    if raw_jamo:
        ax.set_xticks(np.arange(len(raw_jamo)))
        x_labels = [f'{jamo_char}' for jamo_char in raw_jamo]
        ax.set_xticklabels(x_labels, rotation=0, fontsize=12, fontweight='bold', va='top')
    else:
        ax.set_xticks([])
        ax.set_xticklabels([])

    if gt_jamo:
        ax.set_yticks(np.arange(len(gt_jamo)))
        y_labels = [f'{jamo_char}' for jamo_char in gt_jamo]
        ax.set_yticklabels(y_labels, fontsize=12, fontweight='bold')
    else:
        ax.set_yticks([])
        ax.set_yticklabels([])

    ax.xaxis.set_ticks_position('top')  
    ax.xaxis.set_label_position('top') 
    ax.xaxis.set_tick_params(pad=15)
    
    plt.title("DTW 행렬과 워핑 경로", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def print_alignments(
    gt_text: str,
    raw_text: str,
    syllable_mapping: Dict[int, List[int]],
    jamo_alignments: List[Tuple[Tuple[str, int], Tuple[str, int]]]
) -> None:
    """자모 단위 및 음절 단위 정렬 결과를 텍스트와 표 형태로 출력합니다.

    Args:
        gt_text (str): 첫 번째 한글 문자열
        raw_text (str): 두 번째 한글 문자열
        syllable_mapping (Dict[int, List[int]]): 음절 단위 매핑 결과
            gt 문자열의 음절 인덱스를 키로, 매핑된 raw 문자열의 음절 인덱스 리스트를 값으로 가짐
        jamo_alignments (List[Tuple[Tuple[str, int], Tuple[str, int]]]):
            자모 단위 정렬 결과. 각 요소는
            ((gt 자모, gt 자모 인덱스), (raw 자모, raw 자모 인덱스)) 형태의 튜플
    """
    try:
        gt_jamo_seq: List[str] = h2j(gt_text)
    except Exception as e:
        print(f"오류 (print_alignments): 한글 문자열을 자모로 분해하는 데 실패했습니다: {e}")
        return

    pre_jamo_char: str = ''
    pre_gt_jamo_at_idx: str = ''

    print("\n자모 정렬:")
    for (gt_jamo, gt_idx), (raw_jamo, raw_idx) in jamo_alignments:
        try:
            gt_syllable_char = gt_text[find_syllable_index(gt_idx, gt_text)]
            raw_syllable_char = raw_text[find_syllable_index(raw_idx, raw_text)]
        except Exception as e:
            print(f"  오류: 자모 정렬의 음절을 찾는 데 실패했습니다: gt_idx={gt_idx}, raw_idx={raw_idx}. 상세: {e}")
            continue

        if pre_jamo_char == gt_jamo and pre_gt_jamo_at_idx == gt_jamo_seq[gt_idx]:
            print(f"          -> '{raw_jamo}' ({raw_syllable_char})")
        else:
            pre_jamo_char = gt_jamo
            pre_gt_jamo_at_idx = gt_jamo_seq[gt_idx]
            print(f"'{gt_jamo}' ({gt_syllable_char}) -> '{raw_jamo}' ({raw_syllable_char})")
    
    fig, ax = plt.subplots(figsize=(5, max(1, len(syllable_mapping)) * 0.5))
    ax.axis('tight')
    ax.axis('off')
    
    table_data: List[List[str]] = []
    sorted_gt_syl_indices = sorted(syllable_mapping.keys())

    for gt_syl_idx in sorted_gt_syl_indices:
        raw_syl_indices = syllable_mapping.get(gt_syl_idx, [])
        
        gt_syllable_display = gt_text[gt_syl_idx] if 0 <= gt_syl_idx < len(gt_text) else f"GT_Syl[{gt_syl_idx}]?"
        
        raw_syllables_display_parts: List[str] = []
        for raw_syl_idx in sorted(list(set(raw_syl_indices))):
            if 0 <= raw_syl_idx < len(raw_text):
                raw_syllables_display_parts.append(raw_text[raw_syl_idx])
            else:
                raw_syllables_display_parts.append(f"Raw_Syl[{raw_syl_idx}]?")

        raw_syllables_display = "".join(raw_syllables_display_parts) if raw_syllables_display_parts else "-"
        
        table_data.append([gt_syllable_display, raw_syllables_display])
    
    if not table_data:
        print("\n음절 정렬 데이터가 비어있습니다.")
        plt.close(fig)
        return

    table = ax.table(cellText=table_data,
                    colLabels=['GT', 'Raw'],
                    cellLoc='center',
                    loc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(2, 2)
    
    plt.title("Syllable alignment", fontsize=14, pad=10)
    plt.show()


def print_sylmap(
    gt_text: str,
    raw_text: str,
    syllable_mapping: Dict[int, List[int]]
) -> None:
    """음절 단위 매핑 결과를 텍스트 형태로 간단히 출력합니다. (주로 디버깅용)

    Args:
        gt_text (str): 첫 번째 한글 문자열
        raw_text (str): 두 번째 한글 문자열
        syllable_mapping (Dict[int, List[int]]): 음절 단위 매핑 결과
            gt 문자열의 음절 인덱스를 키로, 매핑된 raw 문자열의 음절 인덱스 리스트를 값으로 가짐
    """
    # 입력 문자열에서 한글 및 자모/모음 외 다른 문자 제거
    processed_gt: str = re.sub(r'[^ㄱ-ㅎ가-힣]+', '', gt_text)
    processed_raw: str = re.sub(r'[^ㄱ-ㅎ가-힣]+', '', raw_text)
    
    print("\n음절 매핑 (간단):")
    sorted_gt_syl_indices = sorted(syllable_mapping.keys())

    for gt_syl_idx in sorted_gt_syl_indices:
        raw_syl_indices = syllable_mapping.get(gt_syl_idx, [])
        
        if not raw_syl_indices:
            print(f"{processed_gt[gt_syl_idx] if 0 <= gt_syl_idx < len(processed_gt) else f'GT_Syl[{gt_syl_idx}]?'}: - (매핑 없음)")
            continue
        
        gt_syllable_display = processed_gt[gt_syl_idx] if 0 <= gt_syl_idx < len(processed_gt) else f"GT_Syl[{gt_syl_idx}]?"

        raw_syllables_display_parts: List[str] = []
        for raw_syl_idx in sorted(list(set(raw_syl_indices))):
            if 0 <= raw_syl_idx < len(processed_raw):
                raw_syllables_display_parts.append(processed_raw[raw_syl_idx])
            else:
                raw_syllables_display_parts.append(f"Raw_Syl[{raw_syl_idx}]?")

        raw_syllables_display = "".join(raw_syllables_display_parts) if raw_syllables_display_parts else "-"

        print(f"{gt_syllable_display}: {raw_syllables_display}")
    print("-" * 30)