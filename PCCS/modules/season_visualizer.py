import numpy as np
import matplotlib.pyplot as plt


def visualize_skin_position(palettes, skin_lab, save_path="skin_position.jpg"):
    """
    피부 Lab 값이 시즌 팔레트 Lab 좌표 안에서 어디에 위치하는지 시각화하는 함수.
    L / a 평면에서 표시.
    """

    plt.figure(figsize=(8, 8))

    # 시즌 컬러 테마
    season_colors = {
        "spring": "#FFB347",
        "summer": "#7EC8E3",
        "autumn": "#C97F3D",
        "winter": "#6A5ACD",
    }

    for season, df in palettes.items():
        plt.scatter(
            df["a*"],
            df["L*"],
            s=40,
            alpha=0.6,
            label=season,
            c=season_colors.get(season, "gray")
        )

    plt.scatter(
        skin_lab[1],
        skin_lab[0],
        s=250,
        c="red",
        edgecolors="black",
        label="SKIN",
        marker="X"
    )

    plt.title("Skin Lab Position inside Season Palettes (L vs a)", fontsize=13)
    plt.xlabel("a* (녹색  ← 0 →  빨강)", fontsize=11)
    plt.ylabel("L* (명도, 높을수록 밝음)", fontsize=11)

    plt.xlim(-60, 60)
    plt.ylim(100, 0)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    plt.savefig(save_path, dpi=250)
    plt.close()

    print(f"피부 Lab 위치 시각화 저장 완료 → {save_path}")
