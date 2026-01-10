import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.read_csv('output/training_data.csv')
df = df[df['cpu_usage'] <= 130]
df = df[df['cpu_idle'] >= 90]

X = df[['cpu_usage', 'cpu_idle']]
y = df['label']

model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

joblib.dump(model, 'output/rootkit_detector.pkl')
print("基於負載背離的模型訓練完成。")
