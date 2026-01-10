import joblib
import os
import time
import subprocess

# 載入模型 (請確保你的模型是用 [cpu_usage, cpu_idle] 訓練的)
model = joblib.load('output/rootkit_detector.pkl')

def get_pid_cpu_sum():
    """使用 awk 累加 top 中所有 PID 的 CPU% (軟體視角)"""
    # top -b (批次模式) -n 1 (更新一次)
    cmd = "top -b -n 1 | awk 'NR>7 {sum += $9} END {print sum}'"
    try:
        result = subprocess.check_output(cmd, shell=True).decode().strip()
        return float(result)
    except:
        return 0.0

def get_cpu_idle():
    """從 vmstat 抓取實時物理 CPU 閒置率 (%) (硬體/核心視角)"""
    # vmstat 1 2 取第二行實時數據的 id 欄位 (通常是第 15 欄或倒數第 3 欄)
    cmd = "vmstat 1 2 | tail -n 1 | awk '{print $(NF-2)}'"
    try:
        result = subprocess.check_output(cmd, shell=True).decode().strip()
        return float(result)
    except:
        # 如果 NF-2 不適用，嘗試標準的第 15 欄
        try:
            cmd_alt = "vmstat 1 2 | tail -n 1 | awk '{print $15}'"
            result = subprocess.check_output(cmd_alt, shell=True).decode().strip()
            return float(result)
        except:
            return 100.0

def get_stats():
    cpu_reported = get_pid_cpu_sum()
    cpu_idle = get_cpu_idle()
    return [[cpu_reported, cpu_idle]]

print("🔍 啟動「CPU 指標背離」偵測器...")
print("偵測邏輯：當 Reported CPU 低且 Physical Idle 也低時，判定為 Rootkit 隱匿行為。")
print("-" * 60)

try:
    while True:
        features = get_stats()
        pred = model.predict(features)[0]
        # 獲取異常機率（Label 1 的機率）
        prob = model.predict_proba(features)[0][1]
        
        cpu_reported, cpu_idle = features[0]
        
        # 顯示當前數值
        status_msg = f"Reported: {cpu_reported:5.1f}% | Physical Idle: {cpu_idle:5.1f}% | Confidence: {prob:.2%}"
        
        if pred == 1:
            print(f"🚨 [異常] 偵測到指標背離！ {status_msg}")
        else:
            print(f"🟢 系統正常 - {status_msg}")
        
        # 由於 vmstat 1 2 本身會耗時約 1 秒，這裡 sleep 1 秒即可達到約 2 秒一次的循環
        time.sleep(1)
except KeyboardInterrupt:
    print("\n偵測器已停止。")
    pass
