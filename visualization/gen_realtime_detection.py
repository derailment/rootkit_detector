import joblib
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import subprocess

# 載入模型
model = joblib.load('load_detector.pkl')
LOG_FILE = 'live_detection_log.csv'

def get_pid_cpu_sum():
    """使用 awk 累加 top 中所有 PID 的 CPU%"""
    # top -b (批次模式) -n 1 (更新一次)
    # awk 判斷第 9 欄是否為數字並累加
    cmd = "top -b -n 1 | awk 'NR>7 {sum += $9} END {print sum}'"
    result = subprocess.check_output(cmd, shell=True).decode().strip()
    try:
        return float(result)
    except:
        return 0.0

def plot_final_report():
    """從 CSV 讀取所有歷史資料並畫圖"""
    if not os.path.exists(LOG_FILE):
        return

    df_hist = pd.read_csv(LOG_FILE)
    if len(df_hist) < 2: return

    fig, ax1 = plt.subplots(figsize=(12, 6))
    time_axis = range(len(df_hist))

    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('PID CPU Sum (%)', color='tab:blue')
    ax1.plot(time_axis, df_hist['cpu_usage'], color='tab:blue', label='Reported CPU Sum', linewidth=2)

    ax2 = ax1.twinx()
    ax2.set_ylabel('System Load Average', color='tab:orange')
    ax2.plot(time_axis, df_hist['load_avg'], color='tab:orange', linestyle='--', label='Physical Load', linewidth=2)

    # 標註異常區間
    #in_anomaly = False
    #for i in range(len(df_hist)):
    #    if df_hist['prediction'][i] == 1:
    #        ax1.axvspan(i, i+1, color='red', alpha=0.3)

    # 標註異常區間與文字
    in_anomaly = False
    for i in range(len(df_hist)):
        if df_hist['prediction'][i] == 1:
            # 畫紅色背景
            ax1.axvspan(i, i+1, color='red', alpha=0.3)
            
            # 如果是異常區間的「剛開始」，就標註文字
            if not in_anomaly:
                ax1.text(i, ax1.get_ylim()[1] * 0.9, 'Rootkit Activated', 
                         color='red', fontweight='bold', fontsize=10,
                         bbox=dict(facecolor='white', alpha=0.7, edgecolor='red'))
                in_anomaly = True
        else:
            in_anomaly = False

    plt.title('Detection Timeline (Full History)')
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.savefig('live_timeline_report.png', dpi=300)
    print(f"\n✅ 報告已更新至: live_timeline_report.png")

# --- 主程式 ---
print(f"🛡️ 偵測啟動。資料將即時附加至 {LOG_FILE}")

try:
    while True:
        cpu_usage = get_pid_cpu_sum()
        load_avg = os.getloadavg()[0]
        pred = model.predict([[cpu_usage, load_avg]])[0]

        # 準備單筆數據
        new_data = pd.DataFrame([{
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'cpu_usage': cpu_usage,
            'load_avg': load_avg,
            'prediction': pred
        }])

        # 如果檔案不存在，則寫入 Header；否則只附加 Data
        file_exists = os.path.isfile(LOG_FILE)
        new_data.to_csv(LOG_FILE, mode='a', index=False, header=not file_exists)

        status = "🚨 ALERT" if pred == 1 else "🟢 OK"
        print(f"{status} | CPU: {cpu_usage:5.1f}% | Load: {load_avg:.2f}")

except KeyboardInterrupt:
    print("\n停止偵測中，正在產製最終圖表...")
    plot_final_report()
