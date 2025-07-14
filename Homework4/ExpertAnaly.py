import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

expert_dataset = pd.read_excel('result4/大乐透专家详情统计.xlsx')

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

plt.figure(figsize=(16, 6))
primary_axis = plt.gca()
secondary_axis = primary_axis.twinx()

x_positions = np.arange(len(expert_dataset['昵称']))
primary_axis.plot(x_positions, expert_dataset['彩龄'], 'b-o', label='彩龄')
secondary_axis.plot(x_positions, expert_dataset['发文量'], 'r-s', label='发文量')

primary_axis.set_xlabel('专家')
primary_axis.set_ylabel('彩龄', color='b')
secondary_axis.set_ylabel('发文量', color='r')
plt.xticks(x_positions, expert_dataset['昵称'], rotation=45, ha='right')
primary_axis.legend(loc='upper left')
secondary_axis.legend(loc='upper right')
plt.title('专家彩龄与发文量对比')
plt.tight_layout()
plt.savefig('result4/专家彩龄与发文量对比.png', dpi=200)
plt.close()

correlation_dataset = expert_dataset[['彩龄', '发文量', '大乐透一等奖', '大乐透二等奖', '大乐透三等奖']].copy()
for column_name in correlation_dataset.columns:
    correlation_dataset[column_name] = pd.to_numeric(correlation_dataset[column_name], errors='coerce')
correlation_matrix = np.zeros((2, 3))
for i, x_column in enumerate(['彩龄', '发文量']):
    for j, y_column in enumerate(['大乐透一等奖', '大乐透二等奖', '大乐透三等奖']):
        correlation_matrix[i, j] = correlation_dataset[x_column].corr(correlation_dataset[y_column])

plt.figure(figsize=(8, 4))
sns.heatmap(correlation_matrix, annot=True, fmt='.2f', xticklabels=['一等奖', '二等奖', '三等奖'], yticklabels=['彩龄', '发文量'], cmap='coolwarm', vmin=-1, vmax=1)
plt.title('彩龄/发文量与大乐透中奖次数相关性热力图')
plt.tight_layout()
plt.savefig('result4/专家属性与中奖次数相关性热力图.png', dpi=200)
plt.close()

print('分析图表已输出到 result4 文件夹。')
