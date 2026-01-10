import time
import pandas as pd
import os
import subprocess

def get_pid_cpu_sum():
    """使用 awk 累加 top 中所有 PID 的 CPU% (軟體回報視角)"""
    # top -b (批次模式) -n 1 (更新一次)
    cmd = "top -b -n 1 | awk 'NR>7 {sum += $9} END {print sum}'"
    try:
        result = subprocess.check_output(cmd, shell=True).decode().strip()
        return float(result)
    except:
        return 0.0

def get_cpu_idle():
    """從 vmstat 抓取實時物理 CPU 閒置率 (%) (硬體真實視角)"""
    # vmstat 1 2 取第二行實時數據的第 15 欄 (id)
    # 注意：在不同版本的 Linux 中，id 的位置可能略有不同，通常是倒數第 3 欄
    cmd = "vmstat 1 2 | tail -n 1 | awk '{print $(NF-2)}'" 
    try:
        result = subprocess.check_output(cmd, shell=True).decode().strip()
        return float(result)
    except:
        # 如果 NF-2 不對，嘗試第 15 欄（標準位置）
        try:
            cmd_alt = "vmstat 1 2 | tail -n 1 | awk '{print $15}'"
            result = subprocess.check_output(cmd_alt, shell=True).decode().strip()
            return float(result)
        except:
            return 100.0

def collect(is_anomaly, duration_seconds=60):
    data_list = []
    print(f"正在記錄 {'[異常]' if is_anomaly else '[正常]'} 狀態...")
    
    end_time = time.time() + duration_seconds
    while time.time() < end_time:
        # 獲取軟體回報 CPU 使用率與硬體真實閒置率
        cpu_usage_reported = get_pid_cpu_sum()
        cpu_idle_physical = get_cpu_idle()
          
        data_list.append({
            'cpu_usage': cpu_usage_reported,
            'cpu_idle': cpu_idle_physical,
            'label': 1 if is_anomaly else 0
        })
        
        # 打印即時狀態方便觀察背離現象
        # 正常時：cpu_usage + cpu_idle 應接近 100
        # 異常時：cpu_usage (低) + cpu_idle (低) -> 代表有 CPU 時間憑空消失了
        print(f"Reported CPU: {cpu_usage_reported:5.1f}% | Physical Idle: {cpu_idle_physical:5.1f}% | Label: {1 if is_anomaly else 0}", end='\r')
        
        time.sleep(1)
        
    print("\n採集完成！")
    return data_list

# --- 執行部分 ---
if not os.path.exists('output'):
    os.makedirs('output')

status = input("輸入類別 (0: 正常/高負載, 1: 模擬 Rootkit 隱藏): ")
# 建議採樣時間可以長一點，以獲取穩定的 vmstat 數值
new_data = collect(is_anomaly=(status == '1'), duration_seconds=800)
df = pd.DataFrame(new_data)

# 儲存至 CSV
csv_path = 'output/training_data.csv'
df.to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)
print(f"資料已成功附加至 {csv_path}")
