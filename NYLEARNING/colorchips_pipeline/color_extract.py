# colorchips_pipeline/color_extract.py
"""
color_extract.py
------------------------------------------
📌 나연 프로젝트 전용 색상 추출 모듈

- dominant color 추출 (KMeans)
- RGB → Lab 변환
- 밝기 L값 영향 최소화 (L*0.3 적용)
- RGB / Lab / Hex 모두 반환
- 에러 안정 처리 + 로그 기록
"""

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from .logger import log_info


def rgb_to_hex(rgb):
    """RGB 값을 HEX(#FFFFFF) 형태로 변환"""
    return "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])


def extract_color(filepath):
    """
    대표색 추출 함수
    - 이미지를 100×100으로 축소
    - KMeans로 dominant RGB 추출
    - RGB → LAB 변환
    - L값(밝기) 영향 최소화
    - RGB / LAB / HEX 반환
    """

    try:
        # 이미지 로드
        img = Image.open(filepath).convert("RGB")
        img = img.resize((100, 100))  # 연산 최적화

        pixels = np.array(img).reshape(-1, 3)

        # 대표색 추출
        kmeans = KMeans(n_clusters=1, random_state=42, n_init='auto').fit(pixels)
        rgb = kmeans.cluster_centers_[0].astype(int)

        # RGB → Lab 변환
        pil = Image.new("RGB", (1, 1), tuple(rgb))
        lab = pil.convert("LAB").getpixel((0, 0))

        # L값(밝기) 영향 줄이기
        L, a, b = lab
        L = int(L * 0.3)  # 조명 영향 최소화

        final_lab = (L, a, b)

        result = {
            "rgb": tuple(rgb),
            "lab": final_lab,
            "hex": rgb_to_hex(rgb),
        }

        log_info(f"🎨 색상 추출 완료 → RGB={result['rgb']} LAB={result['lab']} HEX={result['hex']}")
        return result

    except Exception as e:
        log_info(f"❌ 색상 추출 실패: {filepath} | 에러: {e}")
        return None
