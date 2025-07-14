import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

temp_df = pd.read_excel('year_month_max_temp.xlsx')
real2025_df = pd.read_excel('2025_1-6_max_temp.xlsx')

temp_series = temp_df['平均最高气温'].values

def create_dataset(series, window=12):
    X, y = [], []
    for i in range(len(series) - window):
        X.append(series[i:i+window])
        y.append(series[i+window])
    return np.array(X), np.array(y)

X, y = create_dataset(temp_series, window=12)

model = LinearRegression()
model.fit(X, y)

# 预测2025年1-12月
test_input = temp_series[-12:]
preds = []
for i in range(12):
    pred = model.predict(test_input[-12:].reshape(1, -1))[0]
    preds.append(pred)
    test_input = np.append(test_input, pred)

y_true = real2025_df['平均最高温度'].values if '平均最高温度' in real2025_df.columns else real2025_df['平均最高气温'].values

# 可视化
os.makedirs('results', exist_ok=True)
months = [f'2025-{i:02d}' for i in range(1, 13)]
plt.figure(figsize=(10,6))
plt.plot(months, preds, marker='o', label='预测值')
plt.plot(months[:6], y_true, marker='o', label='真实值')
plt.xlabel('月份')
plt.ylabel('平均最高气温 (℃)')
plt.title('2025年1-12月平均最高气温预测与前6个月真实对比')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('results/pred_vs_real_2025_full.png')
plt.close()

print('2025年1-12月预测与前6个月真实对比折线图已保存到 results/pred_vs_real_2025_full.png')
