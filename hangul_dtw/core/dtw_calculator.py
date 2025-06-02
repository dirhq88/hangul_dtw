from jamo import h2j
import numpy as np
from typing import Tuple, List

from .cost_calculator import calculate_multi_cost, calculate_single_cost, find_max_offset
from ..exceptions import DTWCalculationError

def compute_dtw_matrix(
    gt_text: str,
    raw_text: str,
    raw_text_with_space: str,
    multi: bool = True,
    space: bool = True
) -> Tuple[np.ndarray, List[np.ndarray]]:
    """두 한글 문자열의 자모 시퀀스 간 DTW 비용 행렬과 최적 경로를 계산합니다.

    Args:
        gt_text (str): 표준 맞춤법을 따르는 한글 텍스트 (Ground Truth)
        raw_text (str): 정규화가 필요한 원본 한글 텍스트
        multi (bool, optional): 다중 자모 비용 계산 사용 여부. 기본값은 True

    Returns:
        Tuple[np.ndarray, List[np.ndarray]]: DTW 비용 행렬과 최적 경로

    Raises:
        DTWCalculationError: DTW 계산 과정에서 오류 발생 시
    """
    gt_jamo_seq: List[str] = h2j(gt_text)
    raw_jamo_seq: List[str] = h2j(raw_text)
    raw_jamo_seq_with_space: List[str] = h2j(raw_text_with_space)
    
    gt_jamo_len: int = len(gt_jamo_seq)
    raw_jamo_len: int = len(raw_jamo_seq)

    # DTW 행렬 초기화
    dtw_matrix: np.ndarray = np.full((gt_jamo_len + 1, raw_jamo_len + 1), np.inf)
    dtw_matrix[0, 0] = 0
    path_matrix: np.ndarray = np.empty((gt_jamo_len + 1, raw_jamo_len + 1), dtype=object)

    # DTW 행렬 계산
    for i in range(1, gt_jamo_len + 1):
        for j in range(1, raw_jamo_len + 1):
            current_gt_idx: int = i - 1
            current_raw_idx: int = j - 1

            max_gt_offset: int = 1
            max_raw_offset: int = 1
            
            _current_raw_idx = map_origin_index(current_raw_idx, raw_jamo_seq, raw_jamo_seq_with_space)

            if multi:
                if space:
                    max_gt_offset, max_raw_offset = find_max_offset(gt_jamo_seq, current_gt_idx, raw_jamo_seq_with_space, _current_raw_idx)
                else:
                    max_gt_offset, max_raw_offset = find_max_offset(gt_jamo_seq, current_gt_idx, raw_jamo_seq, current_raw_idx)
                        
            candidate_costs: List[float] = []
            candidate_prev_paths: List[Tuple[int, int]] = []

            # 이전 위치들의 비용 계산
            for gt_offset in range(max_gt_offset + 1):
                for raw_offset in range(max_raw_offset + 1):
                    if gt_offset == 0 and raw_offset == 0:
                        continue
                    
                    prev_i: int = i - gt_offset
                    prev_j: int = j - raw_offset

                    # 현재 위치로의 전이 비용 계산
                    current_transition_cost: float
                    if multi:
                        current_transition_cost = calculate_multi_cost(gt_jamo_seq, gt_offset, current_gt_idx, raw_jamo_seq, raw_offset, current_raw_idx)
                    else: 
                        current_transition_cost = calculate_single_cost(gt_jamo_seq, current_gt_idx, raw_jamo_seq, current_raw_idx)

                    accumulated_cost: float = float(dtw_matrix[prev_i, prev_j]) + current_transition_cost
                    
                    candidate_costs.append(accumulated_cost)
                    candidate_prev_paths.append((prev_i, prev_j))

            # 최적 경로 선택
            if not candidate_costs:
                dtw_matrix[i, j] = np.inf
                path_matrix[i, j] = (i - 1, j - 1) 
                continue
            
            candidate_costs_np = np.array(candidate_costs)[::-1]
            candidate_prev_paths_np = np.array(candidate_prev_paths)[::-1]
            
            min_cost_idx: int = candidate_costs_np.argmin()
            
            dtw_matrix[i, j] = candidate_costs_np[min_cost_idx]
            path_matrix[i, j] = tuple(candidate_prev_paths_np[min_cost_idx])

    # 최적 경로 추적
    optimal_path: List[np.ndarray] = []
    current_i: int = gt_jamo_len
    current_j: int = raw_jamo_len
    optimal_path.append(np.array([current_i, current_j]))
    
    while current_i > 0 or current_j > 0:
        if current_i == 0 and current_j == 0:
            break
        
        prev_coords = path_matrix[current_i, current_j]
        if prev_coords is None or not isinstance(prev_coords, tuple) or len(prev_coords) != 2:
            raise DTWCalculationError(
                f"gt_text: {gt_text}\n"
                f"raw_text: {raw_text}\n"
                f"DTW 행렬의 위치 [{current_i}, {current_j}]에서 잘못된 경로 정보를 발견했습니다. "
                f"2개의 정수로 구성된 튜플이 필요하지만, 다음을 받았습니다: {prev_coords}"
            )

        prev_i_typed, prev_j_typed = prev_coords
        
        if not (prev_i_typed <= current_i and prev_j_typed <= current_j and (prev_i_typed < current_i or prev_j_typed < current_j)):
            raise DTWCalculationError(
                f"경로 단계가 잘못되었습니다: ({current_i},{current_j})에서 ({prev_i_typed},{prev_j_typed})로의 이동. "
                f"경로는 반드시 (0,0)을 향해 이동해야 합니다."
            )
        
        if prev_i_typed == 0 and prev_j_typed == 0:
            break
        
        optimal_path.append(np.array([prev_i_typed, prev_j_typed]))
        current_i, current_j = prev_i_typed, prev_j_typed
    
    return dtw_matrix, optimal_path[::-1]

def map_origin_index(origin_index: int, raw_jamo_seq: List[str], raw_jamo_seq_with_space: List[str]) -> int:
    """
    Maps an index from a sequence without spaces (raw_jamo_seq) to the corresponding
    index in a sequence with spaces (raw_jamo_seq_with_space).

    Args:
        origin_index: The index in raw_jamo_seq.
        raw_jamo_seq: A list of Jamo characters, without spaces.
        raw_jamo_seq_with_space: A list of Jamo characters, potentially including spaces.

    Returns:
        The corresponding index in raw_jamo_seq_with_space.

    Raises:
        IndexError: If origin_index is out of bounds for raw_jamo_seq.
        ValueError: If the corresponding element cannot be found (e.g., inconsistent sequences).
    """
    if not (0 <= origin_index < len(raw_jamo_seq)):
        raise IndexError(
            f"origin_index {origin_index} is out of bounds for raw_jamo_seq of length {len(raw_jamo_seq)}"
        )

    non_space_elements_encountered = 0
    for current_idx_in_spaced_seq, element in enumerate(raw_jamo_seq_with_space):
        if element != ' ':  # Assuming ' ' represents a space
            if non_space_elements_encountered == origin_index:
                # This non-space element in raw_jamo_seq_with_space corresponds to
                # raw_jamo_seq[origin_index].
                return current_idx_in_spaced_seq
            non_space_elements_encountered += 1
            
    # This part should ideally not be reached if raw_jamo_seq is consistently
    # derived from raw_jamo_seq_with_space by removing spaces.
    raise ValueError(
        f"Failed to map origin_index {origin_index}. "
        f"raw_jamo_seq_with_space may not have enough non-space elements "
        f"corresponding to raw_jamo_seq. "
        f"Expected at least {origin_index + 1} non-space elements in raw_jamo_seq_with_space, "
        f"but only {non_space_elements_encountered} were found before matching."
    )