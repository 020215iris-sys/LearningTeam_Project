"""
parser.py
------------------------------------------
📌 파일명에서 메타데이터 추출하는 파서 (업그레이드 버전)
- 파일명 규칙 기반 metadata 추출
- 한글/영문 정규화(normalize_kor)
- parts 길이 검증(예외 방지)
- category를 메타데이터 최상단으로 배치
"""

import os
import re


def normalize_kor(text: str) -> str:
    """
    📌 한글/영문 정규화 함수
    - 공백 제거
    - 특수문자 제거
    - 초성 단독 제거
    """
    text = text.strip()

    # 1) 숫자/영문/한글 외 제거
    text = re.sub(r"[^0-9A-Za-z가-힣]", "", text)

    # 2) 공백 제거
    text = re.sub(r"\s+", "", text)

    # 3) 초성 단독 제거
    text = re.sub(r"[ㄱ-ㅎ]", "", text)

    return text


def extract_metadata(filepath: str) -> dict:
    """
    📌 파일명 규칙 기반 metadata 추출
    예) A000832921_lip_tint_romand_쥬시래스팅틴트_13말린복숭아.jpg
    """

    filename = os.path.basename(filepath)
    name, _ = os.path.splitext(filename)

    parts = name.split("_")

    # 🛡 안전성 체크
    if len(parts) < 5:
        raise ValueError(
            f"[ERROR] 파일명 형식이 잘못되었습니다: {filename}\n"
            f"예시 규칙: A000832921_lip_tint_romand_쥬시래스팅틴트_13말린복숭아.jpg"
        )

    category = normalize_kor(parts[1])
    product_id = parts[0]
    brand = normalize_kor(parts[2])
    product_name = normalize_kor(parts[3])
    option_name = normalize_kor(parts[4])

    meta = {
        "category": category,
        "product_id": product_id,
        "brand": brand,
        "product_name": product_name,
        "option_name": option_name,
        "product_url": (
            f"https://www.oliveyoung.co.kr/store/goods/"
            f"getGoodsDetail.do?goodsNo={product_id}"
        ),
    }

    return meta
