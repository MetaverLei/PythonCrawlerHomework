import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from scipy.stats import ttest_ind, chi2_contingency
import seaborn as sns

lottery_dataset = pd.read_excel('大乐透开奖数据统计.xlsx')
weekday_mapping = {'星期一': 'Mon', '星期三': 'Wed', '星期六': 'Sat'}
lottery_dataset['week_en'] = lottery_dataset['星期'].map(weekday_mapping)

monday_data = lottery_dataset[lottery_dataset['week_en'] == 'Mon']
wednesday_data = lottery_dataset[lottery_dataset['week_en'] == 'Wed']
saturday_data = lottery_dataset[lottery_dataset['week_en'] == 'Sat']
weekday_groups = {'Mon': monday_data, 'Wed': wednesday_data, 'Sat': saturday_data}

os.makedirs('result3', exist_ok=True)

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

for weekday_key, group_data in weekday_groups.items():
    plt.figure(figsize=(10, 5))
    plt.plot(pd.to_datetime(group_data['开奖日期']), group_data['总销售额'], marker='o')
    plt.title(f'销售额走势_{weekday_key}')
    plt.xlabel('开奖日期')
    plt.ylabel('总销售额')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'result3/销售额走势_{weekday_key}.png', dpi=200)
    plt.close()

front_number_labels = [str(i).zfill(2) for i in range(1, 36)]
back_number_labels = [str(i).zfill(2) for i in range(1, 13)]
front_frequency_dict = {}
back_frequency_dict = {}
for weekday_key, group_data in weekday_groups.items():
    front_numbers_list = []
    back_numbers_list = []
    for index, data_row in group_data.iterrows():
        front_numbers_list.extend([x.zfill(2) for x in data_row['前区号码'].strip().split()])
        back_numbers_list.extend([x.zfill(2) for x in data_row['后区号码'].strip().split()])
    front_frequency_dict[weekday_key] = np.array([front_numbers_list.count(x) for x in front_number_labels])
    back_frequency_dict[weekday_key] = np.array([back_numbers_list.count(x) for x in back_number_labels])

for weekday_key in weekday_groups:
    plt.figure(figsize=(14, 6))
    plt.bar(front_number_labels, front_frequency_dict[weekday_key])
    plt.title(f'前区号码频率_{weekday_key}')
    plt.xlabel('前区号码')
    plt.ylabel('出现次数')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(f'result3/前区号码频率_{weekday_key}.png', dpi=200)
    plt.close()
    plt.figure(figsize=(8, 4))
    plt.bar(back_number_labels, back_frequency_dict[weekday_key], color='orange')
    plt.title(f'后区号码频率_{weekday_key}')
    plt.xlabel('后区号码')
    plt.ylabel('出现次数')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f'result3/后区号码频率_{weekday_key}.png', dpi=200)
    plt.close()

monday_sales = monday_data['总销售额'].values
wednesday_sales = wednesday_data['总销售额'].values
excluded_date = '2025-02-08'
saturday_sales = saturday_data[saturday_data['开奖日期'] != excluded_date]['总销售额'].values
sales_p_matrix = np.zeros((3, 3))
for i, sales_group_a in enumerate([monday_sales, wednesday_sales, saturday_sales]):
    for j, sales_group_b in enumerate([monday_sales, wednesday_sales, saturday_sales]):
        if i == j:
            sales_p_matrix[i, j] = 1
        else:
            _, p_value = ttest_ind(sales_group_a, sales_group_b, equal_var=False)
            sales_p_matrix[i, j] = p_value
plt.figure(figsize=(5, 4))
sns.heatmap(sales_p_matrix, annot=True, fmt='.3f', xticklabels=['Mon', 'Wed', 'Sat'], yticklabels=['Mon', 'Wed', 'Sat'])
plt.title('销售额两两t检验p值热力图')
plt.tight_layout()
plt.savefig('result3/销售额_t检验_p值热力图.png', dpi=200)
plt.close()

front_p_matrix = np.ones((3, 3))
for i, weekday_a in enumerate(['Mon', 'Wed', 'Sat']):
    for j, weekday_b in enumerate(['Mon', 'Wed', 'Sat']):
        if i < j:
            contingency_table = np.vstack([front_frequency_dict[weekday_a], front_frequency_dict[weekday_b]])
            _, p_value, _, _ = chi2_contingency(contingency_table)
            front_p_matrix[i, j] = p_value
            front_p_matrix[j, i] = p_value
plt.figure(figsize=(5, 4))
sns.heatmap(front_p_matrix, annot=True, fmt='.3f', xticklabels=['Mon', 'Wed', 'Sat'], yticklabels=['Mon', 'Wed', 'Sat'])
plt.title('前区号码频率卡方检验p值热力图')
plt.tight_layout()
plt.savefig('result3/前区号码_卡方_p值热力图.png', dpi=200)
plt.close()

back_p_matrix = np.ones((3, 3))
for i, weekday_a in enumerate(['Mon', 'Wed', 'Sat']):
    for j, weekday_b in enumerate(['Mon', 'Wed', 'Sat']):
        if i < j:
            contingency_table = np.vstack([back_frequency_dict[weekday_a], back_frequency_dict[weekday_b]])
            _, p_value, _, _ = chi2_contingency(contingency_table)
            back_p_matrix[i, j] = p_value
            back_p_matrix[j, i] = p_value
plt.figure(figsize=(5, 4))
sns.heatmap(back_p_matrix, annot=True, fmt='.3f', xticklabels=['Mon', 'Wed', 'Sat'], yticklabels=['Mon', 'Wed', 'Sat'])
plt.title('后区号码频率卡方检验p值热力图')
plt.tight_layout()
plt.savefig('result3/后区号码_卡方_p值热力图.png', dpi=200)
plt.close()

print('所有分析图表已输出到 result3 文件夹。')
