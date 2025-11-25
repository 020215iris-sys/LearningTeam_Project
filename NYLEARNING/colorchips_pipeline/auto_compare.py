"""
auto_compare.py
------------------------------------------
📌 나연 프로젝트 전용 비교 이미지 생성 모듈

- 원본 옵션 이미지 200×200
- 대표 컬러칩 200×200
- 두 이미지를 가로로 합쳐 400×200 비교 이미지 저장

파일명 규칙:
compare_[product_id]_[category]_[brand]_[product]_[option].jpg

저장 위치:
data/01_colorchips/04_auto_compare/
"""

import os
from PIL import Image

from utils.file_ops import generate_filename, AUTO_COMPARE_DIR
from logger import log_info


# 폴더 자동 생성 (안전성)
os.makedirs(AUTO_COMPARE_DIR, exist_ok=True)


def make_compare_image(original_path, meta, color_info):
    """
    원본 이미지 + 대표 컬러칩 이미지를 비교 이미지(400×200)로 생성하여 저장.
    """

    # --- 1) 원본 이미지 로드 ---
    try:
        original = Image.open(original_path).convert("RGB")
        original = original.resize((200, 200))
    except Exception as e:
        log_info(f"❌ 원본 이미지 로드 실패: {original_path} | 에러: {e}")
        return None

    # --- 2) 대표 색 칩 생성 (200×200) ---
    try:
        r, g, b = color_info["rgb"]
        chip = Image.new("RGB", (200, 200), (r, g, b))
    except Exception as e:
        log_info(f"❌ 대표 색 칩 생성 실패: {color_info} | 에러: {e}")
        return None

    # --- 3) 400×200 비교 캔버스 생성 ---
    canvas = Image.new("RGB", (400, 200), (255, 255, 255))
    canvas.paste(original, (0, 0))
    canvas.paste(chip, (200, 0))

    # --- 4) 저장 파일명 생성 ---
    base = generate_filename(meta).replace(".jpg", "")
    filename = f"compare_{base}.jpg"

    save_path = os.path.join(AUTO_COMPARE_DIR, filename)

    # --- 5) 저장 ---
    try:
        canvas.save(save_path)
        log_info(f"🖼 비교이미지 저장 완료 → {save_path}")
        return save_path
    except Exception as e:
        log_info(f"❌ 비교이미지 저장 실패 → {save_path} | 에러: {e}")
        return None
