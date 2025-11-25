"""
save_chip.py
------------------------------------------
📌 나연 프로젝트 전용 대표 컬러칩 저장 모듈
- 200×200 단색 칩 이미지 생성
- 파일명 규칙: [product_id]_[category]_[brand]_[product]_[option].jpg
- 저장 위치: data/colorchips/03_colorchips_result/
"""

from PIL import Image
import os
from utils.file_ops import (
    generate_filename,
    CHIPS_DIR,
)

def save_color_chip(meta: dict, color_info: dict):
    """
    meta = {
        'product_id': ...,
        'category': ...,
        'brand': ...,
        'product_name': ...,
        'option_name': ...,
        'product_url': ...
    }

    color_info = {
        'rgb': (120, 60, 80),
        'lab': (50, 30, 20),
        'hex': '#783C50'
    }
    """

    # RGB 값
    r, g, b = color_info["rgb"]

    # 단색 이미지 생성 (200x200)
    chip = Image.new("RGB", (200, 200), (r, g, b))

    # 저장 파일명 생성
    filename = generate_filename(meta)

    # 저장 경로
    save_path = os.path.join(
        CHIPS_DIR, "03_colorchips_result", filename
    )

    # 저장
    chip.save(save_path)

    print(f"🎨 대표 컬러칩 저장 완료 → {save_path}")
    return save_path
