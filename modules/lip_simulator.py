import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path

mp_face_mesh = mp.solutions.face_mesh

class LipNotFoundError(Exception):
    pass

######## TEST LIP COLOR ########
TEST_LIP_COLORS = {
    "deep_red": (200, 30, 70),
    "pink": (220, 100, 150),
    "coral": (255, 90, 70)
}

# 정확한 상/하 입술 인덱스
UPPER_LIP = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409]
LOWER_LIP = [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]

def expand_polygon_adaptive(points, scales):
    """각 점별로 다른 scale 적용"""
    center = np.mean(points, axis=0)
    expanded = []
    for i, p in enumerate(points):
        direction = p - center
        s = scales[i] if i < len(scales) else 1.0
        expanded.append(center + direction * s)
    return np.array(expanded, dtype=np.int32)



def get_lip_mask(image):
    """배포용 안정화 + 완벽 입술 영역 확보"""
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as mesh:
        results = mesh.process(img_rgb)
        if not results.multi_face_landmarks:
            raise LipNotFoundError("입술을 인식하지 못했습니다.")

        h, w, _ = image.shape
        mask = np.zeros((h, w), dtype=np.uint8)

        for face in results.multi_face_landmarks:
            # Landmark 좌표
            upper = np.array([(int(face.landmark[i].x * w), int(face.landmark[i].y * h)) for i in UPPER_LIP], np.int32)
            lower = np.array([(int(face.landmark[i].x * w), int(face.landmark[i].y * h)) for i in LOWER_LIP], np.int32)

            # Polygon scale (안정화)
            upper_scales = [0.55, 0.56, 0.57, 0.57, 0.57, 0.55, 0.55, 0.55, 0.55, 0.55]
            lower_scales = [0.73] * len(lower)
            upper = expand_polygon_adaptive(upper, upper_scales)
            lower = expand_polygon_adaptive(lower, lower_scales)

            # 입술 채우기
            cv2.fillPoly(mask, [upper], 255)
            cv2.fillPoly(mask, [lower], 255)

        # Convex hull로 부족 영역 보강 (입꼬리/산 포함)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hull_mask = np.zeros_like(mask)
        for cnt in contours:
            hull = cv2.convexHull(cnt)
            cv2.drawContours(hull_mask, [hull], -1, 255, -1)

       

        return hull_mask



def apply_lip_color(image, lip_mask, color_rgb=(255,0,0)):
    overlay = image.copy()
    bgr = (color_rgb[2], color_rgb[1], color_rgb[0])

    # mask float normalization + 경계 색 농도 낮춰 번짐 최소화
    mask_float = lip_mask.astype(np.float32)/255.0 * 0.85

    for c in range(3):
        overlay[:,:,c] = overlay[:,:,c] * (1 - mask_float) + bgr[c] * mask_float

    blended = cv2.addWeighted(image, 0.6, overlay, 0.4, 0)
    return blended



def generate_before_after(image_path, color_rgb):
    """Before/After 합성 및 저장"""
    img_path = Path(image_path)
    image = cv2.imread(str(img_path))
    if image is None:
        raise FileNotFoundError(f"이미지를 찾을 수 없음: {image_path}")

    lip_mask = get_lip_mask(image)
    result_image = apply_lip_color(image, lip_mask, color_rgb=color_rgb)

    save_path = img_path.with_name(img_path.stem + "_lip.jpg")
    cv2.imwrite(str(save_path), result_image)
    
