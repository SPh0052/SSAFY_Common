from photo_metadata_test import extract_photo_metadata, is_photo_by_exif
from photo_object_test import detect_photo_objects
from datetime import datetime

def generate_photo_keywords(metadata: dict, objects: list):
    keywords = []

    # 날짜 키워드
    if metadata.get("taken_date"):
        keywords.append(metadata["taken_date"])

    # 카메라 키워드
    if metadata.get("camera_make"):
        keywords.append(metadata["camera_make"])
    if metadata.get("camera_model"):
        keywords.append(metadata["camera_model"])

    # GPS 키워드(있으면)
    if metadata.get("gps_lat") and metadata.get("gps_lon"):
        keywords.append(f"GPS:{metadata['gps_lat']:.6f},{metadata['gps_lon']:.6f}")

    # 객체 키워드
    keywords.extend(objects)

    # 중복 제거 + 정리
    keywords = list(dict.fromkeys([str(k).strip() for k in keywords if k]))
    return keywords

if __name__ == "__main__":
    image_path = input("테스트할 사진 파일 경로를 붙여넣고 Enter: ").strip().strip('"')

    meta = extract_photo_metadata(image_path)
    print("\n[메타데이터]")
    print(meta)

    if not is_photo_by_exif(meta):
        print("\n⚠️ EXIF 기준 사진 판별이 애매합니다. 그래도 객체 탐지를 실행합니다.")

    objs = detect_photo_objects(image_path, conf=0.25)
    print("\n[객체]")
    print(objs)

    keywords = generate_photo_keywords(meta, objs)
    print("\n[최종 키워드]")
    print(keywords)
