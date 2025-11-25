"""
run.py
------------------------------------------
📌 컬러칩 파이프라인 내부 실행 모듈
"""

from colorchips_pipeline.utils.file_ops import ensure_directories, PASS_DIR
from colorchips_pipeline.watcher import start_watchdog
from colorchips_pipeline.logger import log_info


def run_colorchip_pipeline():
    log_info("🌸 나연의 컬러칩 자동 파이프라인 시작 🌸")

    ensure_directories()
    log_info("📁 폴더 구조 확인 및 생성 완료")

    log_info(f"📂 감시 대상 폴더: {PASS_DIR}")
    log_info("PASS 폴더에 이미지를 넣으면 자동 전처리가 시작됩니다.")

    start_watchdog()
