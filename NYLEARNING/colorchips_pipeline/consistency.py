"""
consistency.py
------------------------------------------
📌 데이터 일관성 체크 모듈 (나연 프로젝트 전용)

- PASS 폴더 이미지 개수
- RESULT 폴더 이미지 개수
- CSV 레코드 수

3개가 동일한지 확인하여 로그에 기록.
"""

import os
import csv

from colorchips_pipeline.utils.file_ops import PASS_DIR, RESULT_DIR, CSV_PATH
from logger import log_info


def _count_image_files(folder: str) -> int:
    """📌 jpg/png 이미지 개수 세기"""
    if not os.path.exists(folder):
        return 0

    return len([
        f for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ])


def _count_csv_rows(path: str) -> int:
    """📌 CSV 데이터 개수 세기 (header 제외)"""
    if not os.path.exists(path):
        return 0

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)
        return max(0, len(rows) - 1)  # header 제거


def run_consistency_check():
    """
    📌 PASS / RESULT / CSV의 개수를 비교.
       일치하면 OK, 다르면 WARNING 로그 출력.
    """
    n_pass = _count_image_files(PASS_DIR)
    n_result = _count_image_files(RESULT_DIR)
    n_csv = _count_csv_rows(CSV_PATH)

    log_info(f"[일관성 체크] PASS={n_pass} | RESULT={n_result} | CSV={n_csv}")

    if n_pass == n_result == n_csv:
        log_info("✅ 데이터 개수 일치 → 전처리 상태 정상입니다.")
    else:
        log_info("⚠️ WARNING: 데이터 불일치 → 확인 필요함.")
