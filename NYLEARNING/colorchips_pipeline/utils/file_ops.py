"""
file_ops.py
---------------------------------------
📌 공통 파일/폴더 경로 관리 & 자동 생성 모듈
   (나연 컬러칩 프로젝트 전용)

폴더 구조 (data 기준):

data/
 └ 01_colorchips/
      ├ 01_colorchips_original/
      ├ 02_colorchips_filtered/
      │      ├ pass/
      │      └ fail/
      ├ 03_colorchips_result/
      ├ 04_auto_compare/
      └ 05_csv_result/
"""

import os
from datetime import datetime

# -------------------------------------------------------
# 📌 1) 프로젝트 루트 경로
# -------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# -------------------------------------------------------
# 📌 2) 컬러칩 디렉토리 구조
# -------------------------------------------------------
CHIPS_DIR = os.path.join(DATA_DIR, "01_colorchips")

ORIGINAL_DIR = os.path.join(CHIPS_DIR, "01_colorchips_original")

FILTERED_DIR = os.path.join(CHIPS_DIR, "02_colorchips_filtered")
PASS_DIR = os.path.join(FILTERED_DIR, "pass")
FAIL_DIR = os.path.join(FILTERED_DIR, "fail")

RESULT_DIR = os.path.join(CHIPS_DIR, "03_colorchips_result")
AUTO_COMPARE_DIR = os.path.join(CHIPS_DIR, "04_auto_compare")

CSV_DIR = os.path.join(CHIPS_DIR, "05_csv_result")
CSV_PATH = os.path.join(CSV_DIR, "colorchips_data.csv")

# -------------------------------------------------------
# 📌 3) 폴더 생성 함수
# -------------------------------------------------------
def ensure_directories():
    """
    📌 컬러칩 파이프라인 실행에 필요한 모든 폴더 생성
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CHIPS_DIR, exist_ok=True)

    os.makedirs(ORIGINAL_DIR, exist_ok=True)

    os.makedirs(FILTERED_DIR, exist_ok=True)
    os.makedirs(PASS_DIR, exist_ok=True)
    os.makedirs(FAIL_DIR, exist_ok=True)

    os.makedirs(RESULT_DIR, exist_ok=True)
    os.makedirs(AUTO_COMPARE_DIR, exist_ok=True)

    os.makedirs(CSV_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

# -------------------------------------------------------
# 📌 4) 파일명 생성
# -------------------------------------------------------
def generate_filename(meta: dict) -> str:
    """
    meta 예시:
    {
        'product_id': 'A000123456',
        'category': 'lip_tint',
        'brand': 'romand',
        'product_name': '쥬시래스팅틴트',
        'option_name': '13말린복숭아'
    }
    """
    file_name = (
        f"{meta['product_id']}_"
        f"{meta['category']}_"
        f"{meta['brand']}_"
        f"{meta['product_name']}_"
        f"{meta['option_name']}.jpg"
    )
    return file_name

# -------------------------------------------------------
# 📌 5) timestamp
# -------------------------------------------------------
def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
