# ================================================================
# 📌 [필수 안내] 이 코드를 실행하기 전에 아래 라이브러리 설치 필요!!
#
# pip install beautifulsoup4
# pip install requests
#
# (파이썬 기본 내장: os, csv, re, datetime 은 따로 설치 불필요)
# ================================================================

import os
import csv
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup

# ============================================
# 1) 경로 자동 설정 (나연 폴더 구조 기준)
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

HTML_DIR = os.path.join(DATA_DIR, "html")
CSV_DIR = os.path.join(DATA_DIR, "csv")
IMG_DIR = os.path.join(DATA_DIR, "colorchips")

CSV_PATH = os.path.join(CSV_DIR, "lip_info.csv")

os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

# ============================================
# 파일명 정리 함수
# ============================================
def clean_filename(text):
    text = re.sub(r'[\\/:*?"<>|]', '', text)
    text = text.replace("\n", "").replace("\r", "")
    return text.strip()[:90]


# ============================================
# HTML 파싱
# ============================================
def parse_from_html(html_path):

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # 브랜드명
    brand_tag = soup.select_one(".TopUtils_btn-brand__tvEdp, .prd_brand, .tx_brand")
    brand = brand_tag.text.strip() if brand_tag else "UnknownBrand"

    # 제품명
    name_tag = soup.select_one(".prd_name, .product_tit, h3")
    product_name = name_tag.text.strip() if name_tag else "UnknownProduct"

    # 컬러칩
    chips = soup.select(".ColorChips_colorchip-item__PXPll img")
    color_list = []

    for img in chips:
        alt_name = img.get("alt", "UnknownColor").strip()
        img_url = img.get("src", "")

        # // 로 시작하면 https 붙여서 보정
        if img_url.startswith("//"):
            img_url = "https:" + img_url

        color_list.append((alt_name, img_url))

    return brand, product_name, color_list


# ============================================
# 이미지 저장
# ============================================
def save_image(img_url, brand, color_name):
    try:
        safe_brand = clean_filename(brand)
        safe_color = clean_filename(color_name)

        file_name = f"{safe_brand}_{safe_color}.jpg"
        save_path = os.path.join(IMG_DIR, file_name)

        response = requests.get(img_url, timeout=10)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(response.content)

        return file_name

    except Exception as e:
        print(f"이미지 저장 실패 ({color_name}): {e}")
        return None


# ============================================
# CSV 저장
# ============================================
def save_to_csv(rows):
    header = ["brand", "product_name", "color_name", "img_url", "img_file", "date", "time"]

    write_header = not os.path.exists(CSV_PATH)

    with open(CSV_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerows(rows)


# ============================================
# 단일 HTML 실행
# ============================================
def run_one_file(html_path):

    print(f"[파일 처리 중] → {html_path}")

    brand, product_name, color_list = parse_from_html(html_path)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    rows = []

    for color_name, img_url in color_list:
        img_file = save_image(img_url, brand, color_name)
        rows.append([
            brand, product_name, color_name, img_url, img_file, date_str, time_str
        ])

    save_to_csv(rows)
    print(f"  → 저장 완료 ✔")


# ============================================
# 폴더 전체 실행
# ============================================
def run_all():
    print("전체 HTML 크롤링 시작… 💜")

    html_files = [f for f in os.listdir(HTML_DIR) if f.endswith(".html")]

    if not html_files:
        print("⚠ html 폴더에 HTML 파일이 없습니다.")
        return

    for file in html_files:
        run_one_file(os.path.join(HTML_DIR, file))

    print("\n=== 전체 크롤링 완료! ===")
    print(f"CSV 저장 → {CSV_PATH}")
    print(f"이미지 저장 → {IMG_DIR}")


# ============================================
# 실행
# ============================================
if __name__ == "__main__":
    run_all()
