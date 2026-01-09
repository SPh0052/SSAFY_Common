import streamlit as st
from PIL import Image
import numpy as np
import cv2


def pil_to_np_rgb(pil_image: Image.Image) -> np.ndarray:
    return np.array(pil_image.convert("RGB"))


def np_gray_to_pil(gray: np.ndarray) -> Image.Image:
    return Image.fromarray(gray)

def deskew(gray: np.ndarray) -> np.ndarray:
    """
    이미지의 기울기를 추정해서 자동으로 회전 보정
    입력: grayscale 이미지 (numpy)
    출력: 회전 보정된 grayscale 이미지
    """
    # 이진화 (윤곽 검출용)
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 글자 영역 좌표 추출
    coords = np.column_stack(np.where(bw > 0))
    if len(coords) == 0:
        return gray

    # 최소 사각형으로 각도 계산
    angle = cv2.minAreaRect(coords)[-1]

    # OpenCV 각도 보정
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = gray.shape
    center = (w // 2, h // 2)

    # 회전 행렬 생성
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        gray,
        M,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )

    return rotated

def preprocess_pipeline(
    pil_image: Image.Image,
    use_gray: bool = True,
    use_denoise: bool = True,
    denoise_strength: int = 5,
    use_contrast: bool = True,
    contrast_alpha: float = 1.5,
    contrast_beta: int = 0,
    use_binarize: bool = True,
    thresh: int = 160,
    use_deskew: bool = True,
) -> Image.Image:
    """
    실습과제1 전처리 파이프라인 (옵션형)
    - gray: 컬러 제거(밝기만 남김)
    - denoise: 잡음 제거(글자 주변 점/얼룩 감소)
    - contrast: 대비 향상(글자 더 진하게/배경 더 옅게)
    - binarize: 이진화(배경/글자 흑백 분리)
    """
    img = pil_to_np_rgb(pil_image)

    # 1) 그레이스케일
    if use_gray:
        x = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        # gray를 안 쓰면 이후 단계들이 애매해져서, 최소한 gray 형태로 맞춰준다
        x = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # 2) 노이즈 제거 (Median Blur)
    # denoise_strength는 홀수여야 함(3,5,7...)
    if use_denoise:
        k = denoise_strength if denoise_strength % 2 == 1 else denoise_strength + 1
        x = cv2.medianBlur(x, k)

    # 3) 대비 개선
    # x' = alpha*x + beta
    if use_contrast:
        x = cv2.convertScaleAbs(x, alpha=contrast_alpha, beta=contrast_beta)

    # 4) 이진화
    if use_binarize:
        # 고정 임계값 이진화 (원하는 값으로 조절)
        _, x = cv2.threshold(x, thresh, 255, cv2.THRESH_BINARY)

    if use_deskew:
        x = deskew(x)

    return np_gray_to_pil(x)


st.set_page_config(page_title="AI 아카이브 - 실습과제1", layout="wide")
st.title("실습과제1: 이미지 전처리 (2) - 노이즈/대비/이진화")

st.write(
    "이번 단계 목표: **OCR이 잘 읽도록** 문서 이미지를 더 깨끗하게 만듭니다.\n\n"
    "- 노이즈 제거: 자잘한 점/무늬 제거\n"
    "- 대비 개선: 글자와 배경 차이를 키움\n"
    "- 이진화: 배경(흰) / 글자(검)로 딱 분리"
)

uploaded = st.file_uploader("이미지 파일을 업로드하세요 (png/jpg)", type=["png", "jpg", "jpeg"])

# 전처리 옵션 UI
st.sidebar.header("전처리 옵션")

use_gray = st.sidebar.checkbox("1) 그레이스케일", value=True)

use_denoise = st.sidebar.checkbox("2) 노이즈 제거", value=True)
denoise_strength = st.sidebar.slider("노이즈 강도(커널 크기)", min_value=3, max_value=11, value=5, step=2)

use_contrast = st.sidebar.checkbox("3) 대비 개선", value=True)
contrast_alpha = st.sidebar.slider("대비(alpha)", min_value=1.0, max_value=3.0, value=1.5, step=0.1)
contrast_beta = st.sidebar.slider("밝기(beta)", min_value=-50, max_value=50, value=0, step=1)

use_binarize = st.sidebar.checkbox("4) 이진화", value=True)
thresh = st.sidebar.slider("이진화 임계값(threshold)", min_value=0, max_value=255, value=160, step=1)

use_deskew = st.sidebar.checkbox("5) 기울기(회전) 보정", value=True)

if uploaded is None:
    st.info("이미지를 업로드하면 전/후 비교가 나타납니다.")
    st.stop()

orig_pil = Image.open(uploaded).convert("RGB")

processed_pil = preprocess_pipeline(
    orig_pil,
    use_gray=use_gray,
    use_denoise=use_denoise,
    denoise_strength=denoise_strength,
    use_contrast=use_contrast,
    contrast_alpha=contrast_alpha,
    contrast_beta=contrast_beta,
    use_binarize=use_binarize,
    thresh=thresh,
    use_deskew=use_deskew,
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("원본 이미지")
    st.image(orig_pil, use_container_width=True)

with col2:
    st.subheader("전처리 결과")
    st.image(processed_pil, use_container_width=True)

st.divider()
st.write("✅ 다음 단계에서: **기울기(회전) 보정**을 추가해서 삐뚤어진 문서를 똑바로 세울 거예요.")
