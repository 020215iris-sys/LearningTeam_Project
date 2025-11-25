# 하드에서 수정

# ================================================================
#  📌 나연 v7_fixed_rev4
#     - A_normal: v4 완전 복원 (건들지 않음)
#     - B_hardcase: v4 (가장 진한 1픽셀 기반 대표색)
#     - PASS 내부 전체 재귀 스캔 (A_normal / B_hardcase)
# ================================================================

import os
import re
import csv
import uuid
from datetime import datetime

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from skimage.color import rgb2lab


# ================================================================
# 📌 0) 절대 경로 설정 (나연 폴더 그대로)
# ================================================================
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
CHIPS = os.path.join(DATA, "01_colorchips")

ORIGINAL = os.path.join(CHIPS, "01_colorchips_original")
FILTERED = os.path.join(CHIPS, "02_colorchips_filtered")

# 기본 PASS 경로
PASS = os.path.join(FILTERED, "pass")

# PASS 폴더 자동 탐색 (pass, PASS, Pass 등 대응)
if not os.path.exists(PASS):
    print("⚠ PASS 폴더 자동 탐색 중...")
    for name in os.listdir(FILTERED):
        p = os.path.join(FILTERED, name)
        if os.path.isdir(p) and name.lower().startswith("pass"):
            PASS = p
            print(f"👉 PASS 폴더 자동 설정: {PASS}")
            break

FAIL = os.path.join(FILTERED, "fail")

RESULT = os.path.join(CHIPS, "03_colorchips_result")
COMPARE = os.path.join(CHIPS, "04_auto_compare")
CSV_DIR = os.path.join(CHIPS, "05_csv_result")
CSV_PATH = os.path.join(CSV_DIR, "colorchips_data.csv")

LOG_DIR = os.path.join(ROOT, "logs")
LOG_PATH = os.path.join(LOG_DIR, "batch_log_v7_rev4.txt")

# 폴더 생성
for f in [DATA, CHIPS, ORIGINAL, FILTERED, PASS, FAIL, RESULT, COMPARE, CSV_DIR, LOG_DIR]:
    os.makedirs(f, exist_ok=True)


# ================================================================
# 📌 1) 로깅
# ================================================================
def log(msg: str):
    t = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{t} {msg}"
    print(line)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ================================================================
# 📌 2) 파일명 free-form 파싱
# ================================================================
def _clean(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]", "", text.strip())


def parse_filename_any(filename: str) -> dict:
    base, _ = os.path.splitext(filename)
    tokens = re.split(r"[_\s]+", base)
    tokens = [_clean(t) for t in tokens if t.strip()]

    category = "liptint"
    brand = "unknown"
    option = "unknown"

    if len(tokens) >= 2:
        brand = tokens[1]
    if len(tokens) >= 3:
        option = "".join(tokens[2:])

    temp_id = "TEMP" + str(uuid.uuid4().int)[-6:]

    meta = {
        "temp_id": temp_id,
        "product_id": temp_id,
        "category": category,
        "brand": brand,
        "option": option,
    }

    log(f"📦 파싱 → {meta}")
    return meta


# ================================================================
# 📌 3-1) A_normal — v4 완전 복원 (그대로 유지)
# ================================================================
def extract_color_normal_v4(path: str) -> dict:
    try:
        img = Image.open(path).convert("RGB").resize((160, 160))
        arr = np.array(img)
        h, w, _ = arr.shape

        # 중앙 crop 50%
        y1, y2 = int(h * 0.25), int(h * 0.75)
        x1, x2 = int(w * 0.25), int(w * 0.75)
        center = arr[y1:y2, x1:x2].reshape(-1, 3)

        # 밝기 필터
        brightness = 0.299*center[:,0] + 0.587*center[:,1] + 0.114*center[:,2]
        mask = (brightness > 30) & (brightness < 230)
        pixels = center[mask] if np.any(mask) else center

        # KMeans 4클러스터
        kmeans = KMeans(n_clusters=4, random_state=42, n_init="auto").fit(pixels)
        labels = kmeans.labels_
        centers = kmeans.cluster_centers_

        # 가장 넓은 클러스터
        best_idx = np.argmax([np.sum(labels == k) for k in range(4)])
        rgb = tuple(int(v) for v in centers[best_idx])

        # RGB → LAB + 밝기 보정(L*0.3)
        norm = np.array([[rgb]])/255.0
        L, a, b = rgb2lab(norm)[0][0]
        L_adj = L * 0.3

        lab = (round(L_adj, 4), round(float(a), 4), round(float(b), 4))
        hex_code = "#{:02X}{:02X}{:02X}".format(*rgb)

        result = {"rgb": rgb, "lab": lab, "hex": hex_code}
        log(f"🎨 [A_normal_v4] 색상 → {result}")
        return result

    except Exception as e:
        log(f"❌ [A_normal_v4] 실패: {e}")
        return {"rgb": (120,120,120), "lab": (20.0,0.0,0.0), "hex":"#777777"}


# ================================================================
# 📌 3-2) B_hardcase — v4 (가장 진한 1픽셀 기반)
# ================================================================
def extract_color_hardcase(path: str) -> dict:
    """
    하드케이스:
      - 이미지 전체에서 Lab 채도가 가장 높은 1픽셀을 찾고
      - 그 픽셀의 RGB를 그대로 대표색으로 사용
      - 평균 NO, 군집 NO → '가장 진한 색' 1점만 사용
    """
    try:
        img = Image.open(path).convert("RGB").resize((200, 200))
        arr = np.array(img)
        h, w, _ = arr.shape

        # RGB → Lab
        rgb_norm = arr / 255.0
        lab_img = rgb2lab(rgb_norm)
        L_channel = lab_img[:, :, 0]
        a_channel = lab_img[:, :, 1]
        b_channel = lab_img[:, :, 2]

        # 채도(chroma) 계산
        chroma = np.sqrt(a_channel**2 + b_channel**2)

        # 고채도 + 적당한 밝기 영역만 남기기
        #  - chroma > 25 : 꽤 진한 색만
        #  - 15 < L < 90 : 너무 어둡거나 너무 밝은 영역 제거
        mask = (chroma > 25) & (L_channel > 15) & (L_channel < 90)

        # 유효 픽셀이 너무 적으면 → fallback 사용
        if np.count_nonzero(mask) < 10:
            log("⚠ [B_hardcase_v4] 고채도 픽셀 부족 → fallback 사용")
            return _extract_color_hardcase_fallback(arr)

        # 마스크 외 영역은 채도 0으로 처리하고, 최고 채도 픽셀 찾기
        masked_chroma = np.where(mask, chroma, 0.0)
        flat_idx = int(np.argmax(masked_chroma))
        y, x = np.unravel_index(flat_idx, (h, w))

        rgb = tuple(int(v) for v in arr[y, x, :])

        # 선택된 1픽셀 RGB를 Lab으로 변환
        norm = np.array([[rgb]]) / 255.0
        L, a, b = rgb2lab(norm)[0][0]
        L_adj = L * 0.3

        lab = (round(L_adj, 4), round(float(a), 4), round(float(b), 4))
        hex_code = "#{:02X}{:02X}{:02X}".format(*rgb)

        result = {"rgb": rgb, "lab": lab, "hex": hex_code}
        log(f"🎨 [B_hardcase_v4] 색상(가장 진한 1픽셀) → {result}")
        return result

    except Exception as e:
        log(f"❌ [B_hardcase_v4] 실패 → fallback 사용: {e}")
        return _extract_color_hardcase_fallback(arr)


# 🔹 v4에서 고채도 픽셀이 너무 적거나 에러 날 때 쓰는 안전용 fallback
def _extract_color_hardcase_fallback(arr: np.ndarray) -> dict:
    try:
        h, w, _ = arr.shape

        # 하단 30% 사용
        y1 = int(h * 0.7)
        band = arr[y1:h].reshape(-1, 3)

        brightness = 0.299*band[:,0] + 0.587*band[:,1] + 0.114*band[:,2]
        mask = (brightness > 10) & (brightness < 200)
        pixels = band[mask] if np.any(mask) else band

        # KMeans 3개 + 가장 채도 높은 클러스터 중심
        kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto").fit(pixels)
        centers = kmeans.cluster_centers_

        centers_norm = centers / 255.0
        centers_lab = rgb2lab(centers_norm.reshape(1, -1, 3))[0]
        chroma_sq = centers_lab[:, 1]**2 + centers_lab[:, 2]**2
        best_idx = int(np.argmax(chroma_sq))

        rgb = tuple(int(v) for v in centers[best_idx])

        norm = np.array([[rgb]]) / 255.0
        L, a, b = rgb2lab(norm)[0][0]
        L_adj = L * 0.3

        lab = (round(L_adj,4), round(float(a),4), round(float(b),4))
        hex_code = "#{:02X}{:02X}{:02X}".format(*rgb)

        result = {"rgb": rgb, "lab": lab, "hex": hex_code}
        log(f"🎨 [B_hardcase_fallback_v4] 색상 → {result}")
        return result

    except Exception as e:
        log(f"❌ [B_hardcase_fallback_v4] 최종 실패: {e}")
        return {"rgb": (120,120,120), "lab": (20.0,0.0,0.0), "hex":"#777777"}


# ================================================================
# 📌 4) 칩 저장 / 비교 저장
# ================================================================
def build_filename(meta):
    return f"{meta['category']}_{meta['brand']}_{meta['option']}_{meta['temp_id']}.jpg"


def save_chip(meta, color):
    name = build_filename(meta)
    path = os.path.join(RESULT, name)
    img = Image.new("RGB", (200, 200), color["rgb"])
    img.save(path)
    log(f"🎨 칩 저장 → {path}")
    return path


def save_compare(original, meta, color):
    name = build_filename(meta)
    save_path = os.path.join(COMPARE, "compare_" + name)

    try:
        ori = Image.open(original).convert("RGB").resize((200, 200))
    except Exception:
        ori = Image.new("RGB", (200,200), (255,255,255))

    chip = Image.new("RGB", (200,200), color["rgb"])
    canvas = Image.new("RGB", (400,200), (255,255,255))
    canvas.paste(ori, (0,0))
    canvas.paste(chip, (200,0))
    canvas.save(save_path)

    log(f"🖼 비교 저장 → {save_path}")
    return save_path


# ================================================================
# 📌 5) CSV 재생성
# ================================================================
def rebuild_csv(records):
    log("📝 CSV 전체 재생성 시작")

    header = [
        "product_id","category","brand","option",
        "r","g","b",
        "L","a","b",
        "hex","case_type","timestamp"
    ]

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for rec in records:
            r,g,bb = rec["color"]["rgb"]
            L,a,b = rec["color"]["lab"]

            w.writerow([
                rec["meta"]["product_id"],
                rec["meta"]["category"],
                rec["meta"]["brand"],
                rec["meta"]["option"],
                r, g, bb,
                L, a, b,
                rec["color"]["hex"],
                rec["case_type"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

    log("📝 CSV 재생성 완료")


# ================================================================
# 📌 6) 메인 — PASS 내부 전체 재귀 스캔
# ================================================================
def main():
    log("🌸 Batch v7_fixed_rev4 시작 — A_normal(v4) + B_hardcase_v4 (전체 스캔)")

    record_map = {}

    # PASS 전체 재귀 탐색 (A_normal / B_hardcase 모두 포함)
    for root, dirs, files in os.walk(PASS):
        for fname in files:
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            path = os.path.join(root, fname)

            # 케이스 자동 판별
            lower_root = root.replace("\\", "/").lower()
            if "b_hardcase" in lower_root:
                case_type = "B_hardcase"
            else:
                case_type = "A_normal"

            log(f"📂 처리 중 ({case_type}) → {path}")

            meta = parse_filename_any(fname)

            if case_type == "B_hardcase":
                color = extract_color_hardcase(path)
            else:
                color = extract_color_normal_v4(path)

            save_chip(meta, color)
            save_compare(path, meta, color)

            key = (meta["brand"], meta["option"])
            if key not in record_map:
                record_map[key] = {
                    "meta": meta,
                    "color": color,
                    "case_type": case_type
                }
            else:
                if record_map[key]["case_type"] == "B_hardcase" and case_type == "A_normal":
                    record_map[key] = {
                        "meta": meta,
                        "color": color,
                        "case_type": case_type
                    }

    rebuild_csv(record_map.values())

    log("🎉 Batch v7_fixed_rev4 전체 처리 완료!")


if __name__ == "__main__":
    main()
