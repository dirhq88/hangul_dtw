import pandas as pd
import importlib.resources
import os
from typing import Callable, Any

try:
    from .. import data as data_files_anchor
except ImportError as e:
    raise ImportError(
        "'hangul_dtw.utils'에서 'data' 서브패키지를 가져올 수 없습니다. "
        "'hangul_dtw/data/__init__.py' 파일이 존재하는지 확인하고 "
        "패키지 구조가 올바르게 설정되어 있는지 확인하세요."
    ) from e

def _load_table(
    filename: str,
    loader_func: Callable[[Any], pd.DataFrame],
    **kwargs: Any
) -> pd.DataFrame:
    """패키지 내 데이터 파일을 로드하는 내부 헬퍼 함수입니다.

    Args:
        filename (str): 로드할 데이터 파일의 이름
        loader_func (Callable): 파일을 로드하는 함수 (예: pd.read_csv, pd.read_excel)
        **kwargs: loader_func에 전달할 추가 인자

    Returns:
        pd.DataFrame: 로드된 데이터 테이블

    Raises:
        ImportError: 데이터 파일을 찾을 수 없거나 로드하는 데 실패한 경우
    """
    actual_file_path_str: str = ""
    resource_ref_str: str = "N/A"
    candidate_path_os: str = "N/A"

    try:
        if data_files_anchor is None:
            raise ImportError("'data' 패키지 앵커를 찾을 수 없습니다.")
        
        # --- 시도 1: os.path 기반 경로 탐색 (패키지가 설치되지 않은 개발 환경 우선) ---
        if hasattr(data_files_anchor, '__file__') and data_files_anchor.__file__ is not None:
            anchor_dir = os.path.dirname(os.path.abspath(data_files_anchor.__file__))
            candidate_path_os = os.path.join(anchor_dir, "tables", filename)
            if os.path.exists(candidate_path_os):
                actual_file_path_str = candidate_path_os
                return loader_func(actual_file_path_str, **kwargs)

        # --- 시도 2: importlib.resources (주로 설치된 패키지 환경) ---
        try:
            resource_ref = importlib.resources.files(data_files_anchor) / "tables" / filename
            resource_ref_str = str(resource_ref)
            with importlib.resources.as_file(resource_ref) as temp_path:
                actual_file_path_str = str(temp_path)
                if os.path.exists(actual_file_path_str):
                    return loader_func(actual_file_path_str, **kwargs)
        except AttributeError:  # importlib.resources.files()가 없는 경우 (Python < 3.9)
            try:
                with importlib.resources.path(data_files_anchor, os.path.join("tables", filename)) as temp_path:
                    actual_file_path_str = str(temp_path)
                    if os.path.exists(actual_file_path_str):
                        return loader_func(actual_file_path_str, **kwargs)
            except Exception:
                pass
        except Exception:
            pass
        
        # 모든 시도 실패
        err_msg = (
            f"'{filename}' 파일을 찾을 수 없습니다. "
            f"시도한 경로: os.path='{candidate_path_os}', "
            f"importlib.resources='{resource_ref_str}'. "
            "데이터 파일이 'hangul_dtw/data/tables/'에 존재하는지 확인하세요."
        )
        print(f"치명적 오류 (file_loaders): {err_msg}")
        raise FileNotFoundError(err_msg)
            
    except FileNotFoundError as e:
        raise ImportError(str(e)) from e
    except Exception as e:
        error_message = (
            f"'{filename}' 파일을 로드하는 데 실패했습니다. "
            f"오류 유형: {type(e).__name__} - {e}"
        )
        print(f"오류 (file_loaders): {error_message}")
        raise ImportError(error_message) from e

# --- 전역 데이터 테이블 로드 ---
try:
    FC_TABLE: pd.DataFrame = _load_table("FC_Table.csv", pd.read_csv, index_col=0)
    VW_TABLE: pd.DataFrame = _load_table("VW_Table.xlsx", pd.read_excel, index_col=0)
    LC_TABLE: pd.DataFrame = _load_table("LC_Table.xlsx", pd.read_excel, index_col=0)
    CV_TABLE: pd.DataFrame = _load_table("converted_AIHub.csv", pd.read_csv, index_col=0)
except ImportError as e:
    print(f"치명적 오류 (file_loaders): 필수 데이터 테이블 로드 실패. 오류: {e}")
    raise
