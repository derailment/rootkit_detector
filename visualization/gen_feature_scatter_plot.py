import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 載入資料
# 建議先檢查檔案是否存在
if os.path.exists('sys_metrics.csv'):
    df = pd.read_csv('sys_metrics.csv')
else:
    # 建立範例數據以防程式崩潰 (實際執行請確保有 csv)
    print("找不到 sys_metrics.csv，請確認路徑。")
    df = pd.DataFrame(columns=['cpu_usage', 'load_avg', 'label'])

def plot_scatter():
    plt.figure(figsize=(10, 6))
    
    # 1. 定義顏色映射字典 (確保 0 永遠是綠色，1 永遠是紅色)
    palette_colors = {0: 'green', 1: 'red'}
    
    # 2. 繪製散佈圖並取得 ax 物件
    # 將 hue_order 固定，確保圖例物件的抓取順序一致
    ax = sns.scatterplot(
        data=df, 
        x='cpu_usage', 
        y='load_avg', 
        hue='label', 
        palette=palette_colors,
        hue_order=[0, 1]  # 強制排序：先 Normal 後 Rootkit
    )
    
    # 3. 關鍵修正：抓取繪圖物件 (handles) 與其原始標籤 (labels)
    handles, labels = ax.get_legend_handles_labels()
    
    # 4. 建立標籤映射字典，將數據 '0' 轉為 'Normal'，'1' 轉為 'Rootkit'
    label_map = {'0': 'Normal', '1': 'Rootkit (Hidden)'}
    
    # 根據抓取到的 handles 順序來生成正確的名字
    new_labels = [label_map.get(l, l) for l in labels]
    
    # 5. 重新套用圖例，這會確保「物件」與「說明」正確綁定
    plt.legend(handles=handles, labels=new_labels, title='Status')

    plt.title('Detection Logic: CPU Usage vs System Load')
    plt.xlabel('Sum of PID CPU Usage (%)')
    plt.ylabel('System Load Average')
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # 存檔
    plt.savefig('detection_logic.png', dpi=300)
    print("✅ 已產製正確標籤的特徵散佈圖：detection_logic.png")
    plt.show()

# 呼叫函數
if __name__ == "__main__":
    plot_scatter()
