import joblib
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import subprocess

# 載入模型 (請確保模型是用 [cpu_usage, cpu_idle] 訓練的)
model = joblib.load('output/rootkit_detector.pkl')
LOG_FILE = 'output/realtime_data.csv'
REPORT_PATH = 'demo/live_monitoring_detection.png'

def get_pid_cpu_sum():
    """使用 awk 累加 top 中所有 PID 的 CPU% (軟體視角)"""
    cmd = "top -b -n 1 | awk 'NR>7 {sum += $9} END {print sum}'"
    try:
        result = subprocess.check_output(cmd, shell=True).decode().strip()
        return float(result)
    except:
        return 0.0

def get_cpu_idle():
    """從 vmstat 抓取實時物理 CPU 閒置率 (%) (硬體視角)"""
    # vmstat 1 2 取第二行實時數據的 id 欄位 (通常是第 15 欄)
    cmd = "vmstat 1 2 | tail -n 1 | awk '{print $(NF-2)}'"
    try:
        result = subprocess.check_output(cmd, shell=True).decode().strip()
        return float(result)
    except:
        # 備用方案：直接指定第 15 欄
        try:
            cmd_alt = "vmstat 1 2 | tail -n 1 | awk '{print $15}'"
            result = subprocess.check_output(cmd_alt, shell=True).decode().strip()
            return float(result)
        except:
            return 100.0

def plot_final_report():
    """從 CSV 讀取所有歷史資料並畫圖"""
    if not os.path.exists(LOG_FILE):
        return

    df_hist = pd.read_csv(LOG_FILE)
    if len(df_hist) < 2: return

    # 建立畫布
    fig, ax1 = plt.subplots(figsize=(12, 6))

    time_axis = range(len(df_hist))

    # 第一軸：Reported CPU Usage (左)
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Reported Process CPU Sum (%)', color='tab:blue', fontsize=10)
    line1 = ax1.plot(time_axis, df_hist['cpu_usage'], color='tab:blue', label='Reported CPU', linewidth=2)
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_ylim(-5, 105) # 固定百分比範圍

    # 第二軸：Physical CPU Idle (右)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Physical CPU Idle (%)', color='tab:red', fontsize=10)
    line2 = ax2.plot(time_axis, df_hist['cpu_idle'], color='tab:red', linestyle='--', label='Physical Idle', linewidth=2)
    ax2.tick_params(axis='y', labelcolor='tab:red')
    ax2.set_ylim(-5, 105) # 固定百分比範圍

    # 標註異常區間
    in_anomaly = False
    for i in range(len(df_hist)):
        if df_hist['prediction'][i] == 1:
            ax1.axvspan(i, i+1, color='red', alpha=0.15)
            if not in_anomaly:
                ax1.text(i, 90, 'Rootkit Activated', 
                         color='white', fontweight='bold', fontsize=10,
                         bbox=dict(facecolor='red', alpha=0.8, edgecolor='none'))
                in_anomaly = True
        else:
            in_anomaly = False

    plt.title('Real-time Rootkit Detection', fontsize=14)
    
    # 合併 Legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center left')

    plt.grid(True, axis='y', alpha=0.2)
    plt.savefig(REPORT_PATH, dpi=300)
    print(f"\n✅ 最終分析報告已產製: {REPORT_PATH}")

# --- 主程式 ---
print(f"🛡️ 偵測系統啟動。監控目標：Reported CPU vs. Physical Idle...")
print(f"數據即時存儲中: {LOG_FILE}")

try:
    while True:
        cpu_reported = get_pid_cpu_sum()
        cpu_idle = get_cpu_idle()
        
        # 核心預測：[軟體回報使用率, 物理真實閒置率]
        pred = model.predict([[cpu_reported, cpu_idle]])[0]

        new_data = pd.DataFrame([{
            'timestamp': time.strftime("%H:%M:%S"),
            'cpu_usage': cpu_reported,
            'cpu_idle': cpu_idle,
            'prediction': pred
        }])

        file_exists = os.path.isfile(LOG_FILE)
        new_data.to_csv(LOG_FILE, mode='a', index=False, header=not file_exists)

        status = "🚨 ALERT" if pred == 1 else "🟢 OK"
        # 邏輯說明：正常時 Reported + Idle 應接近 100；Rootkit 時 Reported(低) + Idle(低) << 100
        print(f"{status} | Reported: {cpu_reported:5.1f}% | Physical Idle: {cpu_idle:5.1f}% | Total: {cpu_reported+cpu_idle:5.1f}%")
        
        time.sleep(1)

except KeyboardInterrupt:
    print("\n停止偵測，正在生成最終圖表...")
    plot_final_report()
