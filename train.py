import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.read_csv('output/training_data.csv')
X = df[['cpu_usage', 'load_avg']]
y = df['label']

model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

joblib.dump(model, 'output/rootkit_detector.pkl')
print("基於負載背離的模型訓練完成。")
