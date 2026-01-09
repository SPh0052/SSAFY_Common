# AI Document Archive (실습과제 1·2·3)

문서 이미지와 사진을 분석하여  
전처리, 키워드 추출, 메타데이터 기반 검색까지 수행하는  
**AI 문서·사진 아카이브 실습 프로젝트**입니다.

본 프로젝트는 다음 3가지 실습과제로 구성되어 있습니다.

---

## 📌 실습과제 구성

### 🟦 실습과제 1 — 문서 이미지 전처리
- 문서 이미지를 OCR이 잘 인식할 수 있도록 전처리
- 그레이스케일 변환
- 노이즈 제거
- 대비 개선
- 이진화
- 기울기(회전) 보정
- Streamlit UI로 전/후 비교 제공

실행 파일:
- `app.py`

---

### 🟩 실습과제 2 — 키워드 추출
- KoNLPy(Okt) 기반 형태소 분석
- 명사 추출
- 연속 명사 결합을 통한 **복합명사 생성**
- TF-IDF 기반 키워드 중요도 계산
- 문서 수가 부족한 경우를 대비한 **TF fallback 로직 적용**

실행 파일:
- `keyword_test.py`
- `user_dict.txt` (사용자 정의 단어 사전)

---

### 🟨 실습과제 3 — 사진 메타데이터 & 검색
- 사진 vs 문서 구분
- 사진의 EXIF 메타데이터 추출
  - 촬영일시
  - 카메라 제조사 / 모델
  - GPS (존재하는 경우에만 사용)
- YOLOv8 기반 객체 탐지 → 사진 키워드 생성
- SQLite DB에 메타데이터 + 키워드 저장
- 키워드 기반 검색 기능
- GPS가 있는 사진만 지도에 시각화
- 깨진/없는 GPS 정보에 대한 예외 처리 적용

실행 파일:
- `app_archive.py`

---

## 📂 프로젝트 파일 구조

```text
ai_document_archive/
├─ app.py                  # 실습과제1 (전처리 UI)
├─ keyword_test.py         # 실습과제2 (키워드 추출)
├─ user_dict.txt           # 실습과제2 (사용자 사전)
├─ photo_metadata_test.py  # 실습과제3 (EXIF 처리)
├─ photo_object_test.py    # 실습과제3 (객체 탐지)
├─ db.py                   # 실습과제3 (DB 저장/검색)
├─ app_archive.py          # 실습과제3 (최종 Streamlit 앱)
├─ requirements.txt        # Python 패키지 목록
├─ .gitignore
└─ README.md
```



## PyTorch 설치 안내

본 프로젝트는 PyTorch를 사용합니다.
PyTorch는 실행 환경(CPU/GPU, CUDA 버전)에 따라 설치 방법이 다르므로
아래 공식 사이트를 참고하여 별도로 설치하세요.

https://pytorch.org/
