import numpy as np
from sklearn.neighbors import KNeighborsClassifier


# ======================================================
# 순수 LAB 기반 Season KNN Classifier (최종 안정판)
# ======================================================
class SeasonKNNClassifier:
    def __init__(self, palettes, k=7):
        """
        palettes: dict {season: DataFrame(L*,a*,b*)}
        k: KNN 이웃 수
        """

        self.k = k
        self.palettes = palettes

        # ------------------------------------------------
        # 1) LAB 값을 그대로 KNN 데이터로 사용 (PCA 제거)
        # ------------------------------------------------
        self.X_lab = []
        self.y = []

        for season, df in palettes.items():
            for _, row in df.iterrows():
                self.X_lab.append([row["L*"], row["a*"], row["b*"]])
                self.y.append(season)

        self.X_lab = np.array(self.X_lab, dtype=np.float32)
        self.y = np.array(self.y)

        # ------------------------------------------------
        # 2) ΔE 기반 거리 metric = euclidean
        # ------------------------------------------------
        self.knn = KNeighborsClassifier(
            n_neighbors=k,
            metric="euclidean",  # ΔE76와 동일
            weights="distance"   # 가까운 색에 더 높은 가중치
        )

        self.knn.fit(self.X_lab, self.y)


    # ----------------------------------------------------
    # 시즌 예측 (ΔE 기반 KNN)
    # ----------------------------------------------------
    def predict_season(self, lab_input):
        lab_input = np.array(lab_input).reshape(1, -1)
        return self.knn.predict(lab_input)[0]
