import streamlit as st
from PIL import Image
import tempfile
from pathlib import Path
import pandas as pd

from db import init_db, insert_photo, search_items, list_photos_with_location
from photo_metadata_test import extract_photo_metadata, is_photo_by_exif
from photo_object_test import detect_photo_objects


def generate_photo_keywords(metadata: dict, objects: list):
    keywords = []

    if metadata.get("taken_date"):
        keywords.append(metadata["taken_date"])
    if metadata.get("camera_make"):
        keywords.append(metadata["camera_make"])
    if metadata.get("camera_model"):
        keywords.append(metadata["camera_model"])

    if metadata.get("gps_lat") is not None and metadata.get("gps_lon") is not None:
        keywords.append(f"GPS:{metadata['gps_lat']:.6f},{metadata['gps_lon']:.6f}")

    keywords.extend(objects)
    keywords = list(dict.fromkeys([str(k).strip() for k in keywords if k]))
    return keywords


st.set_page_config(page_title="AI 아카이브 - 실습과제3", layout="wide")
st.title("실습과제3: 사진 구분 및 메타데이터 검색")

init_db()

tab1, tab2, tab3 = st.tabs(["업로드/저장", "검색", "지도(위치 있는 사진)"])

with tab1:
    st.subheader("1) 사진 업로드 → EXIF/객체 탐지 → 키워드 생성 → DB 저장")

    uploaded = st.file_uploader("사진 파일 업로드 (jpg/png)", type=["jpg", "jpeg", "png"])
    if uploaded is None:
        st.info("사진을 업로드하면 분석 결과가 나오고 저장할 수 있어요.")
        st.stop()

    suffix = Path(uploaded.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getbuffer())
        tmp_path = tmp.name

    st.image(Image.open(uploaded), caption="업로드한 이미지", use_container_width=True)

    meta = extract_photo_metadata(tmp_path)
    objs = detect_photo_objects(tmp_path, conf=0.25)
    keywords = generate_photo_keywords(meta, objs)

    col1, col2 = st.columns(2)
    with col1:
        st.write("### EXIF 메타데이터")
        st.json(meta)

    with col2:
        st.write("### 객체 탐지 결과")
        st.write(objs if objs else "탐지된 객체가 없어요(사진에 따라 정상).")

    st.write("### 최종 키워드")
    st.write(keywords)

    is_photo = is_photo_by_exif(meta)
    st.write("### 사진 판별(EXIF 기준)")
    st.write("✅ 사진일 가능성 높음" if is_photo else "⚠️ EXIF가 부족해 애매함 (그래도 저장은 가능)")

    if st.button("DB에 저장"):
        insert_photo(
            file_name=uploaded.name,
            taken_date=meta.get("taken_date"),
            camera_make=meta.get("camera_make"),
            camera_model=meta.get("camera_model"),
            gps_lat=meta.get("gps_lat"),
            gps_lon=meta.get("gps_lon"),
            objects=objs,
            keywords=keywords,
        )
        st.success("저장 완료! 이제 [검색] 탭에서 찾아볼 수 있어요.")

with tab2:
    st.subheader("2) 사진 메타데이터/키워드 기반 검색")
    q = st.text_input("검색어 입력 (예: person / iPhone / 2026 / GPS / car)")
    if st.button("검색"):
        results = search_items(q)
        if not results:
            st.warning("검색 결과가 없어요.")
        else:
            st.write(f"총 {len(results)}개")
            for r in results:
                st.markdown(f"**#{r['id']} | {r['file_name']}**")
                st.write({
                    "type": r["item_type"],
                    "taken_date": r["taken_date"],
                    "camera": f"{r['camera_make']} {r['camera_model']}",
                    "gps": (r["gps_lat"], r["gps_lon"]),
                    "objects": r["objects"],
                    "keywords": r["keywords"],
                    "created_at": r["created_at"],
                })
                st.divider()

with tab3:
    st.subheader("3) GPS가 있는 사진만 지도에 표시 (있는 경우에만)")

    photos = list_photos_with_location()
    if not photos:
        st.info("GPS가 저장된 사진이 아직 없어요. (카메라 앱에서 위치 저장을 켜고 찍은 사진을 올리면 나와요.)")
        st.stop()

    # 지도 표시용 데이터프레임
    df_map = pd.DataFrame([
        {"lat": p["gps_lat"], "lon": p["gps_lon"]}
        for p in photos
    ])

    st.write("### 지도")
    st.map(df_map)

    # 보기 좋게 표 + 상세정보
    st.write("### GPS 사진 목록")
    df_list = pd.DataFrame([
        {
            "id": p["id"],
            "file_name": p["file_name"],
            "taken_date": p["taken_date"],
            "gps_lat": round(p["gps_lat"], 6),
            "gps_lon": round(p["gps_lon"], 6),
            "keywords": p["keywords"],
        }
        for p in photos
    ])
    st.dataframe(df_list, use_container_width=True)

    st.caption("※ GPS는 사진에 위치 정보(EXIF)가 저장된 경우에만 표시됩니다.")
