import os
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

lottery_data = pd.read_excel('大乐透开奖数据统计.xlsx')

def parse_number_string(num_str):
    return [x.zfill(2) for x in num_str.strip().split()]

front_numbers = []
back_numbers = []
for index, data_row in lottery_data.iterrows():
    front_numbers.extend(parse_number_string(data_row['前区号码']))
    back_numbers.extend(parse_number_string(data_row['后区号码']))

front_count = Counter(front_numbers)
back_count = Counter(back_numbers)

os.makedirs('result2', exist_ok=True)
front_number_labels = [str(i).zfill(2) for i in range(1, 36)]
back_number_labels = [str(i).zfill(2) for i in range(1, 13)]
front_frequency = [front_count.get(x, 0) for x in front_number_labels]
back_frequency = [back_count.get(x, 0) for x in back_number_labels]
plt.figure(figsize=(14, 6))
plt.bar(front_number_labels, front_frequency, color='orange')
plt.title('前区号码出现频率')
plt.xlabel('前区号码')
plt.ylabel('出现次数')
plt.xticks(rotation=90)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.tight_layout()
plt.savefig('result2/前区号码频率分布.png', dpi=200)
plt.close()

plt.figure(figsize=(8, 4))
plt.bar(back_number_labels, back_frequency)
plt.title('后区号码出现频率')
plt.xlabel('后区号码')
plt.ylabel('出现次数')
plt.xticks(rotation=0)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.tight_layout()
plt.savefig('result2/后区号码频率分布.png', dpi=200)
plt.close()

front_last_seen = {num: None for num in front_number_labels}
back_last_seen = {num: None for num in back_number_labels}
for idx, row in lottery_data.iterrows():
    date = pd.to_datetime(row['开奖日期'])
    for num in parse_number_string(row['前区号码']):
        front_last_seen[num] = date
    for num in parse_number_string(row['后区号码']):
        back_last_seen[num] = date

front_sorted = sorted(front_last_seen.items(), key=lambda x: (x[1] if x[1] is not None else pd.Timestamp.min))
back_sorted = sorted(back_last_seen.items(), key=lambda x: (x[1] if x[1] is not None else pd.Timestamp.min))
front_weights = {}
back_weights = {}
for i, (num, _) in enumerate(front_sorted):
    w = 3.0 - 2.0 * (i / (len(front_sorted)-1)) if len(front_sorted) > 1 else 1.0
    front_weights[num] = w
for i, (num, _) in enumerate(back_sorted):
    w = 3.0 - 2.0 * (i / (len(back_sorted)-1)) if len(back_sorted) > 1 else 1.0
    back_weights[num] = w

front_freq_array = np.array([front_count.get(x, 0) for x in front_number_labels], dtype=float)
back_freq_array = np.array([back_count.get(x, 0) for x in back_number_labels], dtype=float)
front_weight_array = np.array([front_weights[x] for x in front_number_labels], dtype=float)
back_weight_array = np.array([back_weights[x] for x in back_number_labels], dtype=float)
front_weighted_probs = front_freq_array * front_weight_array
back_weighted_probs = back_freq_array * back_weight_array
front_weighted_probs = front_weighted_probs / front_weighted_probs.sum()
back_weighted_probs = back_weighted_probs / back_weighted_probs.sum()

front_recommended = sorted(np.random.choice(front_number_labels, size=5, replace=False, p=front_weighted_probs))
back_recommended = sorted(np.random.choice(back_number_labels, size=2, replace=False, p=back_weighted_probs))

recommendation_df = pd.DataFrame({
    '日期': ['2025-07-02'],
    '前区推荐号码': [' '.join(front_recommended)],
    '后区推荐号码': [' '.join(back_recommended)]
})
recommendation_df.to_excel('result2/大乐透推荐号码20250702.xlsx', index=False)

print('频率统计图和推荐号码已输出到 result2 文件夹。')
