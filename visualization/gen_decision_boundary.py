import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
import joblib

def plot_decision_boundary(csv_file, model_file):
    # 1. 載入數據與模型
    df = pd.read_csv(csv_file)
    model = joblib.load(model_file)

    # 設定特徵與標籤 (請確保欄位名稱與訓練時一致)
    X = df[['cpu_usage', 'load_avg']].values
    y = df['label'].values

    # 2. 建立網格 (Meshgrid)
    # 定義範圍：取數據的最大最小值並稍微向外擴張
    x_min, x_max = X[:, 0].min() - 10, X[:, 0].max() + 10
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 1.0),
                         np.arange(y_min, y_max, 0.05))

    # 3. 預測網格中每個點的分類
    # 將網格攤平後進行預測，再轉回網格形狀
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # 4. 開始繪圖
    plt.figure(figsize=(10, 7))

    # 繪製背景顏色 (決策區域)
    # cmap 使用 RdYlGn (紅黃綠)，我們將 0 設為綠，1 設為紅
    from matplotlib.colors import ListedColormap
    cm_bright = ListedColormap(['#99ff99', '#ff9999']) # 淺綠與淺紅
    plt.contourf(xx, yy, Z, cmap=cm_bright, alpha=0.5)

    # 5. 繪製原始數據點
    plt.scatter(X[y == 0, 0], X[y == 0, 1], c='green', edgecolors='k', label='Normal', s=60)
    plt.scatter(X[y == 1, 0], X[y == 1, 1], c='red', edgecolors='k', label='Rootkit (Anomaly)', s=80)

    # 6. 圖表美化
    plt.title("Random Forest Decision Boundary for Rootkit Detection", fontsize=14)
    plt.xlabel("Sum of PID CPU Usage (%)", fontsize=12)
    plt.ylabel("System Load Average", fontsize=12)
    
    # 手動建立圖例，避免剛才討論的覆蓋問題
    plt.legend(title="System Status", loc='upper right')
    
    plt.grid(True, linestyle='--', alpha=0.3)
    
    # 存檔 (面試用紙本建議 300 DPI)
    output_path = 'decision_boundary_report.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()
    print(f"✅ 決策邊界圖已產製：{output_path}")

if __name__ == "__main__":
    # 請確保這兩個檔案在同目錄下
    plot_decision_boundary('sys_metrics.csv', 'load_detector.pkl')
