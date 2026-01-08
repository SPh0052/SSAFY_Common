from PIL import Image
import exifread

def _safe_str(value):
    try:
        return str(value)
    except Exception:
        return None

def _ratio_to_float(r):
    """
    exifread Ratio -> float
    분모가 0이면 None
    """
    try:
        den = float(r.den)
        if den == 0:
            return None
        return float(r.num) / den
    except Exception:
        return None

def extract_photo_metadata(image_path: str):
    """
    사진에서 EXIF 메타데이터 추출:
    - 촬영일시(DateTimeOriginal)
    - 카메라 제조사/모델(Make/Model)
    - GPS(있으면)
    """
    metadata = {
        "taken_date": None,
        "camera_make": None,
        "camera_model": None,
        "gps_lat": None,
        "gps_lon": None,
    }

    with open(image_path, "rb") as f:
        tags = exifread.process_file(f, details=False)

    # 촬영일시
    dt = tags.get("EXIF DateTimeOriginal") or tags.get("Image DateTime")
    if dt:
        metadata["taken_date"] = _safe_str(dt)

    # 카메라 정보
    mk = tags.get("Image Make")
    md = tags.get("Image Model")
    if mk:
        metadata["camera_make"] = _safe_str(mk)
    if md:
        metadata["camera_model"] = _safe_str(md)

    # GPS
    gps_lat = tags.get("GPS GPSLatitude")
    gps_lat_ref = tags.get("GPS GPSLatitudeRef")
    gps_lon = tags.get("GPS GPSLongitude")
    gps_lon_ref = tags.get("GPS GPSLongitudeRef")

    def _convert_to_degrees(values):
        # values는 [deg, min, sec] Ratio 리스트인 경우가 많음
        if not values or len(values) < 3:
            return None

        d = _ratio_to_float(values[0])
        m = _ratio_to_float(values[1])
        s = _ratio_to_float(values[2])

        # 하나라도 None이면 GPS 포기(깨진 EXIF)
        if d is None or m is None or s is None:
            return None

        return d + (m / 60.0) + (s / 3600.0)

    lat = None
    lon = None

    if gps_lat and gps_lat_ref and gps_lon and gps_lon_ref:
        lat = _convert_to_degrees(getattr(gps_lat, "values", None))
        lon = _convert_to_degrees(getattr(gps_lon, "values", None))

        if lat is not None and str(gps_lat_ref) == "S":
            lat = -lat
        if lon is not None and str(gps_lon_ref) == "W":
            lon = -lon

    # 최종 반영 (정상값일 때만)
    if lat is not None and lon is not None:
        metadata["gps_lat"] = lat
        metadata["gps_lon"] = lon
    else:
        metadata["gps_lat"] = None
        metadata["gps_lon"] = None

    return metadata

def is_photo_by_exif(metadata: dict):
    """
    EXIF 기준 '사진' 가능성 판단.
    - 촬영일시 또는 카메라 정보가 있으면 사진일 확률이 높음
    """
    return bool(metadata.get("taken_date") or metadata.get("camera_model") or metadata.get("camera_make"))

if __name__ == "__main__":
    image_path = input("테스트할 이미지 파일 경로를 붙여넣고 Enter: ").strip().strip('"')
    meta = extract_photo_metadata(image_path)

    print("\n[추출된 메타데이터]")
    for k, v in meta.items():
        print(f"- {k}: {v}")

    print("\n[판단]")
    if is_photo_by_exif(meta):
        print("✅ 일반 사진일 가능성이 높습니다 (EXIF 정보 존재).")
    else:
        print("⚠️ 문서/스캔/캡처일 가능성이 있습니다 (EXIF 정보 부족).")
