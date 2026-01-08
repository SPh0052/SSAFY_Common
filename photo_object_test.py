from ultralytics import YOLO
from PIL import Image
from collections import Counter

# YOLOv8n: 가벼워서 노트북에서 돌리기 좋음 (처음 실행 시 모델 다운로드됨)
model = YOLO("yolov8n.pt")

def detect_photo_objects(image_path: str, conf=0.25):
    """
    사진에서 객체 탐지 후, 객체 이름 리스트 반환
    """
    results = model.predict(image_path, conf=conf, verbose=False)
    r = results[0]

    names = model.names  # 클래스 id -> 이름
    objs = []

    if r.boxes is None:
        return objs

    for b in r.boxes:
        cls_id = int(b.cls[0].item())
        objs.append(names[cls_id])

    return objs

def summarize_objects(objs):
    """
    객체 리스트를 보기 좋게 요약(빈도)
    """
    if not objs:
        return []
    counter = Counter(objs)
    return counter.most_common(10)

if __name__ == "__main__":
    image_path = input("테스트할 사진 파일 경로를 붙여넣고 Enter: ").strip().strip('"')

    objs = detect_photo_objects(image_path, conf=0.25)

    print("\n[탐지된 객체 목록]")
    print(objs)

    print("\n[객체 요약(상위 10개)]")
    for name, cnt in summarize_objects(objs):
        print(f"- {name}: {cnt}")
