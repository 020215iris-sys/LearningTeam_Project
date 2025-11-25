"""
init_dirs.py
-----------------------------------------
📌 나연 프로젝트 폴더 구조 자동 생성 & 결과물 리셋 스크립트 (업그레이드)
- data/colorchips 내부 폴더 자동 생성
- pass / fail 자동 생성
- result / compare / csv 자동 생성
- logs 폴더 자동 생성 (logger.py와 일관성 유지)
- 결과물(03,04,05)만 싹 비우는 리셋 기능 포함
"""

import os
import shutil
from .utils.file_ops import (
    ORIGINAL_DIR,
    PASS_DIR,
    FAIL_DIR,
    RESULT_DIR,
    AUTO_COMPARE_DIR,
    CSV_DIR,
    CSV_PATH,
)

# 📌 추가: 로깅 폴더도 관리
LOG_DIR = "logs"


def make_dirs():
    """
    📌 파이프라인에 필요한 모든 폴더를 생성.
    이미 있으면 건너뛰고, 없으면 생성.
    """

    folders = [
        ORIGINAL_DIR,
        PASS_DIR,
        FAIL_DIR,
        RESULT_DIR,
        AUTO_COMPARE_DIR,
        CSV_DIR,
        LOG_DIR,   # ← 새로 추가됨
    ]

    for f in folders:
        os.makedirs(f, exist_ok=True)

    print("✨ 나연의 컬러칩 & 로깅 폴더 구조 자동 생성 완료!")


def reset_outputs():
    """
    📌 전처리 '결과물'만 리셋:
    - 03_colorchips_result → 내부 이미지 삭제
    - 04_auto_compare → 내부 이미지 삭제
    - 05_csv_result → CSV 삭제
    ✔ logs 폴더는 건드리지 않음 (로그는 중요한 기록!)
    """

    # 결과 이미지 폴더 비우기
    for target in [RESULT_DIR, AUTO_COMPARE_DIR]:
        if os.path.exists(target):
            for fname in os.listdir(target):
                fpath = os.path.join(target, fname)
                if os.path.isfile(fpath):
                    os.remove(fpath)

    # CSV 삭제 후 디렉토리 유지
    if os.path.exists(CSV_PATH):
        os.remove(CSV_PATH)
    os.makedirs(CSV_DIR, exist_ok=True)

    print("🧹 전처리 결과물 리셋 완료! (RESULT / AUTO_COMPARE / CSV — logs는 유지)")


if __name__ == "__main__":
    make_dirs()
    # reset_outputs()
