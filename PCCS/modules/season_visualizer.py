import numpy as np
import matplotlib.pyplot as plt

def visualize_skin_position(palettes, skin_lab, classifier, save_path="skin_position.jpg"):
    """
    피부 Lab 값을 시즌 팔레트 위에 시각화 + 
    1) KNN 시즌 득표율 출력
    2) 시즌별 거리 상세(avg/min/sum) 출력
    """

    plt.figure(figsize=(8, 8))

    season_colors = {
        "spring": "#FFB347",
        "summer": "#7EC8E3",
        "autumn": "#C97F3D",
        "winter": "#6A5ACD",
    }

    # ------------------------------------------------
    # 1) KNN 득표율 얻기
    # ------------------------------------------------
    knn_percent = classifier.get_knn_votes(skin_lab)

    print("\n===== 시즌 KNN 득표율 =====")
    for s, p in knn_percent.items():
        print(f"{s:7s}: {p:5.2f}%")
    print("================================\n")

    # ------------------------------------------------
    # 2) 시즌별 거리 상세 정보 얻기
    # ------------------------------------------------
    detail = classifier.get_knn_detail(skin_lab)

    print("===== 시즌별 거리 정보(ΔE 기준) =====")
    for season in ["spring", "summer", "autumn", "winter"]:
        if season in detail:
            d = detail[season]
            print(f"{season:7s} | votes={d['votes']} | avg ΔE={d['avg']:.2f} | min ΔE={d['min']:.2f}")
        else:
            print(f"{season:7s} | votes=0 | avg ΔE= -   | min ΔE= -  ")
    print("====================================\n")

    # ------------------------------------------------
    # 3) 시각화 (기존 그대로)
    # ------------------------------------------------
    for season, df in palettes.items():
        plt.scatter(
            df["a*"], df["L*"],
            s=40,
            alpha=0.6,
            label=season,
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

    plt.savefig(save_path, dpi=250)
    plt.close()

    print(f"피부 Lab 위치 시각화 저장 완료 → {save_path}")

# def visualize_lip_position(palettes, lip_lab_list, save_path="lip_position.jpg"):
#     import matplotlib.pyplot as plt

#     plt.figure(figsize=(8, 8))

#     season_colors = {
#         "spring": "#FFB347",
#         "summer": "#7EC8E3",
#         "autumn": "#C97F3D",
#         "winter": "#6A5ACD",
#     }

#     # 시즌 팔레트 점들
#     for season, df in palettes.items():
#         plt.scatter(
#             df["a*"], df["L*"],
#             s=40,
#             alpha=0.6,
#             label=season,
#             c=season_colors.get(season, "gray")
#         )

#     # 립색 좌표 찍기
#     for i, (L, a, b) in enumerate(lip_lab_list, start=1):
#         plt.scatter(
#             a, L,
#             s=350,
#             c="red",
#             marker="X",
#             edgecolors="black",
#             linewidths=2,
#             label="LIP" if i == 1 else None
#         )
#         plt.text(a + 1, L + 1, f"#{i}", fontsize=12)

#     plt.gca().invert_yaxis()
#     plt.xlabel("a* (녹색 ← 0 → 빨강)")
#     plt.ylabel("L* (밝기)")
#     plt.title("Lip Color Lab Position inside Season Palettes (L vs a)")
#     plt.legend()
#     plt.grid(True, linestyle="--", alpha=0.3)

#     plt.savefig(save_path, dpi=250)
#     plt.close()

#     print(f"립 위치 시각화 저장 완료 → {save_path}")

