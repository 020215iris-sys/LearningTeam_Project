from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time

from colorchips_pipeline.consistency import run_consistency_check
from colorchips_pipeline.parser import extract_metadata
from colorchips_pipeline.color_extract import extract_color
from colorchips_pipeline.save_chip import save_color_chip
from colorchips_pipeline.auto_compare import make_compare_image
from colorchips_pipeline.update_csv import update_csv
from colorchips_pipeline.logger import log_info
from colorchips_pipeline.utils.file_ops import PASS_DIR


class PassFolderHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path

        if not filepath.lower().endswith((".jpg", ".jpeg", ".png")):
            return

        log_info(f"🆕 새 파일 감지 → {filepath}")

        try:
            meta = extract_metadata(filepath)
            log_info(f"ℹ️ 메타데이터: {meta}")

            color_info = extract_color(filepath)
            log_info(f"🎨 대표색 정보: {color_info}")

            save_chip_path = save_color_chip(meta, color_info)

            compare_path = make_compare_image(filepath, meta, color_info)

            update_csv(meta, color_info)

            run_consistency_check()

            log_info(
                f"✅ 전처리 완료 → chip: {save_chip_path}, compare: {compare_path}"
            )

        except Exception as e:
            log_info(f"❌ 에러 발생: {e}")


def start_watchdog():
    os.makedirs(PASS_DIR, exist_ok=True)
    log_info(f"👀 감시 시작 → {PASS_DIR}")

    event_handler = PassFolderHandler()
    observer = Observer()
    observer.schedule(event_handler, PASS_DIR, recursive=False)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_info("🛑 감시 중단 (KeyboardInterrupt)")
        observer.stop()
    observer.join()
