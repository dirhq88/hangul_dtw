# Hangul DTW (한글 동적 시간 워핑)

한글 문자열 간의 자모 단위 정렬을 찾기 위한 Python 패키지입니다. 이 패키지는 원본 텍스트와 표준 맞춤법을 따르는 텍스트 간의 자모 단위 정렬을 동적 시간 워핑(DTW) 알고리즘을 사용하여 계산합니다.

## 주요 기능

- 한글 문자열 간의 DTW(Dynamic Time Warping) 계산
- 자모 단위 정렬 정보 추출
- 음절 매핑 정보 제공
- DTW 행렬 시각화
- 정렬 정보 시각화

## 설치 방법

### 소스 코드에서 설치

```bash
git clone https://github.com/dirhq88/hangul_dtw.git
cd hangul_dtw
pip install -e .
```

## 사용 예시

```python
from hangul_dtw import hangul_DTW

# 예시 텍스트
gt_text = "안녕하세요"  # 표준 맞춤법을 따르는 텍스트
raw_text = "안녕하세여"  # 정규화가 필요한 원본 텍스트

# DTW 계산 및 정렬 정보 추출
dtw_matrix, path, jamo_alignments, syllable_mapping = hangul_DTW(
    gt_text=gt_text,
    raw_text=raw_text,
    print_matrix=True,  # DTW 행렬 시각화
    print_align=True    # 정렬 정보 출력
)
```

## 의존성 패키지

- jamo
- pandas
- numpy
- matplotlib
- openpyxl

## 시스템 요구사항

- Python 3.7 이상

## 라이선스

MIT License

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다.

## 문의 및 버그 리포트

버그를 발견하거나 기능 요청이 있는 경우, GitHub Issues를 통해 알려주세요.
