import joblib
import os
import time
import subprocess

model = joblib.load('output/rootkit_detector.pkl')

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

def get_stats():
    
    cpu = get_pid_cpu_sum()
    load = os.getloadavg()[0]
    return [[cpu, load]]

print("🔍 啟動負載背離偵測器...")
try:
    while True:
        features = get_stats()
        pred = model.predict(features)[0]
        prob = model.predict_proba(features)[0][1]
        
        cpu, load = features[0]
        if pred == 1:
            print(f"🚨 [異常] 負載與 CPU 不符！ Load: {load}, CPU: {cpu}%")
        else:
            print(f"🟢 系統正常 - Load: {load}, CPU: {cpu}%")
        
        time.sleep(2)
except KeyboardInterrupt:
    pass
