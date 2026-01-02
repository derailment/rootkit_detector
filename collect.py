import time
import pandas as pd
import os
import subprocess
import sklearn


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


def collect(is_anomaly, duration_seconds=60):
    data_list = []
    print(f"正在記錄 {'[異常]' if is_anomaly else '[正常]'} 狀態...")
    
    end_time = time.time() + duration_seconds
    while time.time() < end_time:
        # 獲取 CPU 使用率與核心負載
        cpu_usage = get_pid_cpu_sum()
        load_1min, _, _ = os.getloadavg()
          
        data_list.append({
            'cpu_usage': cpu_usage,
            'load_avg': load_1min,
            'label': 1 if is_anomaly else 0
        })
    return data_list

status = input("輸入類別 (0: 正常/高負載, 1: 模擬 Rootkit 隱藏): ")
new_data = collect(is_anomaly=(status == '1'), duration_seconds=60)
df = pd.DataFrame(new_data)
df.to_csv('output/training_data.csv', mode='a', header=not os.path.exists('output/training_data.csv'), index=False)
