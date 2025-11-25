"""
logger.py
------------------------------------------
📌 나연 프로젝트 전용 로깅 시스템 (업그레이드)
- 콘솔 출력 + logs/pipeline_log.txt 기록
- logs 폴더 자동 생성
- timestamp 포함
"""

import os
from datetime import datetime

# 📌 logs 폴더 자동 생성
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_PATH = os.path.join(LOG_DIR, "pipeline_log.txt")


def log_info(msg: str):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{timestamp} {msg}"

    # 콘솔 출력
    print(line)

    # 파일 기록
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")
