import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.holtwinters import Holt
import numpy as np

lottery_df = pd.read_excel('大乐透开奖数据统计.xlsx')

reversed_df = lottery_df.iloc[::-1].reset_index(drop=True)
plt.figure(figsize=(10, 5))
plt.plot(reversed_df['总销售额'].values, marker='o')
plt.title('大乐透总销售额走势')
plt.xlabel('期数')
plt.ylabel('总销售额')
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
os.makedirs('result1', exist_ok=True)
plt.savefig('result1/总销售额走势.png', dpi=200, bbox_inches='tight')
plt.close()

sorted_df = lottery_df.sort_values('开奖日期').reset_index(drop=True)
complete_sales = sorted_df['总销售额'].values

seasonal_model = ExponentialSmoothing(
    complete_sales, 
    seasonal_periods=3,  # 周期为3，对应周一、周三、周六
    trend='add',         
    seasonal='add'     
)
fitted_seasonal_model = seasonal_model.fit()
predicted_values = fitted_seasonal_model.forecast(3)

future_dates = [pd.to_datetime('2025-07-01'), pd.to_datetime('2025-07-03'), pd.to_datetime('2025-07-06')]

recent_10_records = lottery_df.head(10).copy()
recent_10_records = recent_10_records.iloc[::-1].reset_index(drop=True) 
plot_dates = pd.to_datetime(recent_10_records['开奖日期'])
plot_sales = recent_10_records['总销售额'].values
all_plot_dates = list(plot_dates) + future_dates
all_plot_sales = list(plot_sales) + [float(x) for x in predicted_values]

plt.figure(figsize=(12, 6))
plt.plot(plot_dates, plot_sales, 'bo-', label='原始数据')
plt.plot(all_plot_dates[-4:], all_plot_sales[-4:], 'ro-', label='预测数据')
plt.title('大乐透总销售额预测')
plt.xlabel('开奖日期')
plt.ylabel('总销售额')
plt.legend()
plt.xticks(all_plot_dates, [d.strftime('%Y-%m-%d') for d in all_plot_dates], rotation=45)
plt.tight_layout()
plt.savefig('result1/总销售额预测.png', dpi=200, bbox_inches='tight')
plt.close()

prediction_df = pd.DataFrame({
    '开奖日期': [d.strftime('%Y-%m-%d') for d in future_dates],
    '预计总销售额': [float(x) for x in predicted_values],
    '预测方法': ['Holt-Winters季节性模型（周期=3）']*3
})
prediction_df.to_excel('result1/总销售额预测结果.xlsx', index=False)

print('图表和预测表格已输出到 result1 文件夹。')
for d, v in zip(future_dates, predicted_values):
    print(f'预测{d.strftime("%Y-%m-%d")}的总销售额为: {float(v):.2f}')
