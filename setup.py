# 파일 경로: setup.py
"""
hangul_dtw_pkg 패키지 설치 스크립트.

이 스크립트는 setuptools를 사용하여 패키지를 빌드, 배포, 설치합니다.
"""

import setuptools # find_packages를 사용하기 위해 setuptools를 직접 import
import pathlib

# 현재 디렉토리 경로
here = pathlib.Path(__file__).parent.resolve()

# README.md 파일 내용을 long_description으로 사용
# 인코딩 문제 발생 시 'utf-8' 지정
try:
    long_description = (here / "README.md").read_text(encoding="utf-8")
except FileNotFoundError:
    long_description = "A Python package for Dynamic Time Warping (DTW) between Hangul (Korean) strings."

# requirements.txt 파일에서 의존성 목록 읽기
try:
    with open(here / "requirements.txt", "r", encoding="utf-8") as f:
        install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # requirements.txt 파일이 없을 경우, 주요 의존성 직접 명시 (권장하지 않음)
    print("Warning: requirements.txt not found. Using default dependencies.")
    install_requires = [
        "jamo",
        "pandas",
        "numpy",
        "matplotlib",
        "openpyxl",
    ]

# 패키지 버전 정보 읽기 (hangul_dtw_pkg/__init__.py 에서)
# 이 방식은 setup.py 실행 시점에 hangul_dtw_pkg가 sys.path에 있어야 함.
# 또는, 정규표현식으로 __init__.py 파일에서 직접 읽어올 수도 있음.
version = {}
try:
    with open(here / "hangul_dtw_pkg" / "__init__.py", encoding="utf-8") as fp:
        # __version__ = "x.y.z" 형태의 라인을 찾음
        for line in fp:
            if line.startswith("__version__"):
                exec(line, version)
                break
except FileNotFoundError:
    print("Warning: hangul_dtw_pkg/__init__.py not found. Setting version to 0.0.1.")
    version["__version__"] = "0.0.1" # 기본값

if "__version__" not in version:
    print("Warning: __version__ not found in hangul_dtw_pkg/__init__.py. Setting version to 0.0.1.")
    version["__version__"] = "0.0.1"


setuptools.setup(
    name="hangul-dtw",  # PyPI에 표시될 패키지 이름 (하이픈 사용 가능)
    version=version["__version__"],
    author="JW Choi",  # 실제 작성자 정보로 변경
    author_email="jwchoi@example.com",  # 실제 이메일로 변경
    description="A Python package for DTW between Hangul (Korean) strings and alignment analysis.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jwchoi/hangul_dtw",  # 실제 프로젝트 URL로 변경
    
    # 패키지에 포함될 디렉토리 자동 검색
    packages=setuptools.find_packages(exclude=["tests*", "docs*", "examples*"]),
    
    # 패키지에 포함될 데이터 파일 지정 (중요!)
    package_data={
        "hangul_dtw": ["data/tables/*.csv", "data/tables/*.xlsx"],
    },
    # include_package_data=True와 MANIFEST.in을 사용하는 방법도 있습니다.
    # MANIFEST.in 예시:
    # recursive-include hangul_dtw_pkg/data/tables *

    # 설치 시 필요한 의존성 패키지 목록
    install_requires=install_requires,
    
    # Python 버전 요구사항 (선택 사항)
    python_requires=">=3.7",  # 예시: Python 3.7 이상 필요
    
    # PyPI에 표시될 추가 메타데이터 (선택 사항)
    classifiers=[
        "Development Status :: 3 - Alpha",  # 또는 "4 - Beta", "5 - Production/Stable"
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",  # 실제 라이선스에 맞게 수정
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering",
        "Natural Language :: Korean",
    ],
    
    # 콘솔 스크립트 진입점 (선택 사항, CLI 도구를 제공할 경우)
    # entry_points={
    #     "console_scripts": [
    #         "hangul-dtw=hangul_dtw_pkg.cli:main_cli_function", # 예시
    #     ],
    # },
    
    # 프로젝트 관련 URL (선택 사항)
    project_urls={
        "Bug Tracker": "https://github.com/jwchoi/hangul_dtw/issues", # 실제 URL로 변경
        "Source Code": "https://github.com/jwchoi/hangul_dtw",    # 실제 URL로 변경
        # "Documentation": "패키지_문서_URL",
    },
    # zip_safe=False 옵션은 C 확장이나 특정 리소스 접근 방식에 따라 필요할 수 있음
    # importlib.resources를 사용하므로 일반적으로 True여도 무방
    zip_safe=False,
)

# --- setup.py 코드 설명 ---
"""
### 파일의 목적

`setup.py`는 파이썬 패키지를 빌드, 배포, 설치하기 위한 `setuptools`의 설정 파일입니다.
이 파일을 통해 패키지의 이름, 버전, 작성자, 의존성, 포함될 파일 등 다양한 메타데이터와
설치 옵션을 정의할 수 있습니다. `pip install .` 또는 `python setup.py install` 명령을
사용하여 패키지를 설치할 때 이 파일이 사용됩니다.

### 주요 내용

1.  **Import**:
    -   `setuptools`의 `setup` 함수와 `find_packages` 함수를 import 합니다.
    -   `pathlib`을 사용하여 파일 경로를 안전하게 처리합니다.

2.  **`long_description`**:
    -   패키지에 대한 상세 설명을 `README.md` 파일에서 읽어와 사용합니다.

3.  **`install_requires`**:
    -   `requirements.txt` 파일에서 설치 의존성 목록을 읽어옵니다.

4.  **버전 정보 읽기**:
    -   `hangul_dtw_pkg/__init__.py` 파일 내의 `__version__` 변수 값을 읽어와 `setup()` 함수의
        `version` 인자로 사용합니다. 이렇게 하면 버전 정보를 한 곳에서 관리할 수 있습니다.

5.  **`setuptools.setup()` 함수 호출**:
    -   **`name`**: PyPI(Python Package Index)에 등록될 패키지의 이름입니다. 일반적으로 하이픈(-)을 사용합니다.
    -   **`version`**: 패키지의 버전입니다. (`__init__.py`에서 읽어옴)
    -   **`author`, `author_email`**: 패키지 작성자 정보. (실제 정보로 수정 필요)
    -   **`description`**: 패키지에 대한 짧은 설명입니다.
    -   **`long_description`, `long_description_content_type`**: 상세 설명 및 형식.
    -   **`url`**: 패키지 웹사이트 또는 소스 코드 저장소 URL. (실제 정보로 수정 필요)
    -   **`packages=setuptools.find_packages(...)`**: 패키지에 포함될 모든 파이썬 패키지를
        자동으로 찾아줍니다. `hangul_dtw_pkg`와 그 하위 패키지들(`core`, `utils` 등)이 포함됩니다.
    -   **`package_data`**: 파이썬 코드가 아닌 데이터 파일(예: CSV, Excel)을 패키지에
        포함시키기 위한 설정입니다. `hangul_dtw_pkg` 패키지 내의 `data/tables/`
        디렉토리에 있는 모든 `.csv`와 `.xlsx` 파일을 포함하도록 지정했습니다.
        이 설정이 있어야 `file_loaders.py`에서 `importlib.resources`를 통해 데이터 파일에
        안정적으로 접근할 수 있습니다.
    -   **`install_requires`**: 패키지 설치 시 함께 설치되어야 하는 다른 파이썬 패키지들의
        목록입니다. (`requirements.txt`에서 읽어옴)
    -   **`python_requires`**: 패키지가 호환되는 파이썬 버전을 명시합니다.
    -   **`classifiers`**: PyPI에 패키지를 분류하기 위한 메타데이터입니다.
    -   **`entry_points`**: 콘솔 스크립트 진입점을 정의합니다. (선택 사항)
    -   **`project_urls`**: 버그 리포트, 소스 코드 등 프로젝트 관련 추가 URL을 제공합니다. (실제 정보로 수정 필요)
    -   **`zip_safe=False`**: `importlib.resources` (특히 `as_file` 사용 시) 또는 다른 파일 접근 방식이
        압축된 egg 파일 내에서 제대로 작동하지 않을 수 있는 경우를 대비하여 `False`로 설정하는 것이
        더 안전할 수 있습니다. 필수는 아니지만, 리소스 파일 접근 시 문제를 줄여줄 수 있습니다.

### 사용 방법

1.  **정보 업데이트**: `author`, `author_email`, `url`, `project_urls` 등의 필드를
    실제 프로젝트 정보로 업데이트합니다. `name` 필드도 PyPI에 배포할 이름으로 적절히 수정합니다.
2.  **패키지 빌드**:
    ```bash
    python setup.py sdist bdist_wheel
    ```
3.  **로컬 환경에 설치**:
    ```bash
    pip install .
    ```
    또는 (개발 모드):
    ```bash
    pip install -e .
    ```

이 `setup.py` 파일은 `hangul_dtw_pkg`를 다른 사람들이 쉽게 설치하고 사용할 수 있도록
만드는 데 중요한 역할을 합니다.
"""
