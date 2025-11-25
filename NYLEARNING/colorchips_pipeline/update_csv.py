"""
update_csv.py
------------------------------------------
📌 나연 프로젝트 전용 CSV 업데이트 모듈
- meta + color_info를 CSV로 저장
- UTF-8-SIG (Excel 호환)
- 헤더 자동 생성
- 파일 없으면 자동 생성
"""

import os
import csv
from utils.file_ops import CSV_PATH
from logger import log_info


# CSV 컬럼 순서 (나연 요청 반영: category 최상단)
FIELDNAMES = [
    "category",
    "product_id",
    "brand",
    "product_name",
    "option_name",
    "product_url",
    "rgb",
    "lab",
    "hex",
]


def update_csv(meta: dict, color_info: dict):
    """
    meta: parser.extract_metadata() 결과
    color_info: color_extract.extract_color() 결과
    """

    try:
        row = {
            "category": meta["category"],
            "product_id": meta["product_id"],
            "brand": meta["brand"],
            "product_name": meta["product_name"],
            "option_name": meta["option_name"],
            "product_url": meta["product_url"],
            "rgb": str(color_info["rgb"]),
            "lab": str(color_info["lab"]),
            "hex": color_info["hex"],
        }

        file_exists = os.path.exists(CSV_PATH)

        with open(CSV_PATH, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)

            # 처음 만들 때만 헤더 생성
            if not file_exists:
                writer.writeheader()

            writer.writerow(row)

        log_info(f"📝 CSV 업데이트 완료 → {CSV_PATH}")

    except Exception as e:
        log_info(f"❌ CSV 업데이트 실패: {e}")
