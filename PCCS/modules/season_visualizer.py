import numpy as np
import matplotlib.pyplot as plt

def visualize_skin_position(palettes, skin_lab, save_path="skin_position.jpg"):
    """
    피부 Lab 값의 시즌 팔레트 위치 시각화 + 시즌별 거리 기반 비율 출력까지 포함
    """

    plt.figure(figsize=(8, 8))

    season_colors = {
        "spring": "#FFB347",
        "summer": "#7EC8E3",
        "autumn": "#C97F3D",
        "winter": "#6A5ACD",
    }

    # 시즌별 평균 ΔE 거리 계산
    season_distances = {}

    for season, df in palettes.items():
        labs = df[["L*", "a*", "b*"]].values
        dists = np.linalg.norm(labs - skin_lab, axis=1)
        season_distances[season] = dists.mean()

    # 퍼센트 산출
    inv_score = {s: 1 / (d + 1e-6) for s, d in season_distances.items()}
    total_inv = sum(inv_score.values())
    season_percent = {s: round((v / total_inv) * 100, 2) for s, v in inv_score.items()}

    # 출력
    print("\n===== 시즌별 피부색 근접 비율 (%) =====")
    for s, p in season_percent.items():
        print(f"{s:7s}: {p:5.2f}%")
    print("=====================================\n")

    # 시각화 
    for season, df in palettes.items():
        plt.scatter(
            df["a*"], df["L*"],
            s=40,
            alpha=0.6,
            label=f"{season} ({season_percent[season]}%)",
            c=season_colors.get(season, "gray")
        )

    plt.scatter(
        skin_lab[1], skin_lab[0],
        s=250,
        c="red",
        edgecolors="black",
        marker="X",
        label="SKIN"
    )

    plt.title("Skin Lab Position inside Season Palettes (L vs a)", fontsize=13)
    plt.xlabel("a* (녹색  ← 0 →  빨강)", fontsize=11)
    plt.ylabel("L* (명도)", fontsize=11)

    plt.xlim(-60, 60)
    plt.ylim(100, 0)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()

    # 이미지 저장 
    plt.savefig(save_path, dpi=250)
    plt.close()

    print(f"피부 Lab 위치 시각화 저장 완료 → {save_path}")
