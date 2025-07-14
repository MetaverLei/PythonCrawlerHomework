# Homework4 说明文档

## 1. 项目简介

本项目围绕大乐透彩票开奖数据的采集、分析、预测与专家信息挖掘，主要包括以下六个部分：

- **Crawl.py**：爬取大乐透开奖历史数据并保存为Excel。
- **MonPre.py**：基于历史销售额数据，进行时间序列建模与未来销售额预测。
- **NumPre.py**：统计号码出现频率并结合权重推荐新一期号码。
- **FeaAnaly.py**：对开奖数据进行分组统计、t检验和卡方检验，分析不同日期的销售额和号码分布特征。
- **ExpertCrawl.py**：爬取大乐透专家信息及其获奖情况。
- **ExpertAnaly.py**：对专家属性与中奖情况进行可视化和相关性分析。

---

## 2. 依赖库

- `requests`：网页请求，获取数据接口内容。
- `re`：正则表达式，解析文本。
- `json`：处理JSON数据。
- `datetime`：日期处理。
- `openpyxl`、`pandas`：Excel文件读写与数据分析。
- `matplotlib`、`seaborn`：数据可视化。
- `numpy`：数值计算。
- `statsmodels`、`scipy.stats`：时间序列建模与统计检验。
- `os`、`time`：文件与延时操作。
- `collections.Counter`：计数统计。

安装依赖：
```bash
pip install -r requirements.txt
```

---

## 3. 各模块核心说明

### 3.1 大乐透开奖数据爬取（Crawl.py）

**核心代码片段：**
```python
while True:
    url = f"https://jc.zhcw.com/port/client_json.php?...&pageNum={current_page}&pageSize=30..."
    response = requests.get(url, headers=headers)
    pattern_match = re.search(r"\((\{.*\})\)", response.text, re.S)
    if not pattern_match:
        break
    json_data = json.loads(pattern_match.group(1))
    for record in json_data.get("data", []):
        draw_time = record["openTime"]
        draw_date = datetime.datetime.strptime(draw_time, "%Y-%m-%d").date()
        if draw_date < date_begin:
            break
        if date_begin <= draw_date <= date_end:
            lottery_data.append({
                "开奖日期": draw_time,
                "星期": record["week"],
                "前区号码": record["frontWinningNum"],
                "后区号码": record["backWinningNum"],
                "总销售额": float(record["saleMoney"].replace(",", "")),
            })
        if len(lottery_data) >= 100:
            break
    if len(lottery_data) >= 100 or not json_data.get("data"):
        break
    current_page += 1

# 剔除2025-02-08的数据
lottery_data = [row for row in lottery_data if row['开奖日期'] != '2025-02-08']

workbook = openpyxl.Workbook()
worksheet = workbook.active
worksheet.append(["开奖日期", "星期", "前区号码", "后区号码", "总销售额"])
for data_row in lottery_data:
    worksheet.append([...])
workbook.save("大乐透开奖数据统计.xlsx")
```
**主要流程：**
1. 构造请求头和日期区间，分页请求API获取开奖数据。
2. 用正则和json解析返回内容，提取开奖日期、号码、销售额等。
3. 剔除特定日期数据，整理后写入Excel。

**关键库函数及其功能：**
- `requests.get`：发送HTTP请求。
- `re.search`：正则提取JSON。
- `json.loads`：解析JSON数据。
- `datetime`：日期处理。
- `openpyxl.Workbook`：写入Excel。

---

### 3.2 销售额时间序列预测（MonPre.py）

**核心代码片段：**
```python
lottery_df = pd.read_excel('大乐透开奖数据统计.xlsx')
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
prediction_df = pd.DataFrame({
    '开奖日期': [d.strftime('%Y-%m-%d') for d in future_dates],
    '预计总销售额': [float(x) for x in predicted_values],
    '预测方法': ['Holt-Winters季节性模型（周期=3）']*3
})
prediction_df.to_excel('result1/总销售额预测结果.xlsx', index=False)
```
**主要流程：**
1. 读取开奖数据，按日期排序，提取销售额序列。
2. 用Holt-Winters季节性模型拟合并预测未来三期销售额。
3. 整理预测结果保存为Excel。

**关键库函数及其功能：**
- `pandas.read_excel`：读取Excel数据。
- `statsmodels.tsa.holtwinters.ExponentialSmoothing`：季节性时间序列建模。
- `pandas.DataFrame.to_excel`：保存预测结果。

---

### 3.3 号码频率统计与推荐（NumPre.py）

**核心代码片段：**
```python
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

front_number_labels = [str(i).zfill(2) for i in range(1, 36)]
back_number_labels = [str(i).zfill(2) for i in range(1, 13)]
front_freq_array = np.array([front_count.get(x, 0) for x in front_number_labels], dtype=float)
back_freq_array = np.array([back_count.get(x, 0) for x in back_number_labels], dtype=float)
# ... 计算权重 ...
front_weighted_probs = front_freq_array * front_weight_array
front_weighted_probs = front_weighted_probs / front_weighted_probs.sum()
front_recommended = sorted(np.random.choice(front_number_labels, size=5, replace=False, p=front_weighted_probs))
back_recommended = sorted(np.random.choice(back_number_labels, size=2, replace=False, p=back_weighted_probs))

recommendation_df = pd.DataFrame({
    '日期': ['2025-07-02'],
    '前区推荐号码': [' '.join(front_recommended)],
    '后区推荐号码': [' '.join(back_recommended)]
})
recommendation_df.to_excel('result2/大乐透推荐号码20250702.xlsx', index=False)
```
**主要流程：**
1. 统计前区、后区号码出现频率。
2. 结合最近出现时间加权，计算推荐概率。
3. 随机抽取推荐号码，保存推荐结果。

**关键库函数及其功能：**
- `pandas.read_excel`：读取数据。
- `collections.Counter`：统计频率。
- `numpy.random.choice`：按概率抽样。
- `pandas.DataFrame.to_excel`：保存推荐结果。

---

### 3.4 开奖特征分析与统计检验（FeaAnaly.py）

**核心代码片段：**
```python
lottery_dataset = pd.read_excel('大乐透开奖数据统计.xlsx')
weekday_mapping = {'星期一': 'Mon', '星期三': 'Wed', '星期六': 'Sat'}
lottery_dataset['week_en'] = lottery_dataset['星期'].map(weekday_mapping)

monday_data = lottery_dataset[lottery_dataset['week_en'] == 'Mon']
wednesday_data = lottery_dataset[lottery_dataset['week_en'] == 'Wed']
saturday_data = lottery_dataset[lottery_dataset['week_en'] == 'Sat']

# t检验
monday_sales = monday_data['总销售额'].values
wednesday_sales = wednesday_data['总销售额'].values
saturday_sales = saturday_data[saturday_data['开奖日期'] != '2025-02-08']['总销售额'].values
_, p_value = ttest_ind(monday_sales, wednesday_sales, equal_var=False)

# 卡方检验
front_frequency_dict = {...}  # 见完整代码
contingency_table = np.vstack([front_frequency_dict['Mon'], front_frequency_dict['Wed']])
_, p_value, _, _ = chi2_contingency(contingency_table)
```
**主要流程：**
1. 按星期分组统计销售额和号码频率。
2. 对不同组间销售额做t检验，号码分布做卡方检验。
3. 生成热力图和分组统计图。

**关键库函数及其功能：**
- `pandas.read_excel`：读取数据。
- `scipy.stats.ttest_ind`：t检验。
- `scipy.stats.chi2_contingency`：卡方检验。
- `numpy.vstack`：构造列联表。

---

### 3.5 大乐透专家信息爬取（ExpertCrawl.py）

**核心代码片段：**
```python
expert_id_list = []
current_page = 1
while len(expert_id_list) < 25:
    api_url = f"https://i.cmzj.net/expert/queryExpert?limit=10&page={current_page}&sort=0"
    response = requests.get(api_url, headers=headers)
    response_data = json.loads(response.content.decode('utf-8'))
    for expert_item in response_data.get('data', []):
        expert_skills = [skill.strip() for skill in expert_item.get('skill', '').split(',')]
        if any('大乐透' in skill for skill in expert_skills):
            expert_id_list.append(expert_item['expertId'])
            if len(expert_id_list) >= 25:
                break
    current_page += 1
    time.sleep(0.2)

expert_details = []
for expert_id in expert_id_list:
    detail_url = f'https://i.cmzj.net/expert/queryExpertById?expertId={expert_id}'
    detail_response = requests.get(detail_url, headers=headers)
    detail_data = json.loads(detail_response.content.decode('utf-8'))
    expert_detail = detail_data.get('data', {})
    expert_info = {
        '专家Id': expert_id,
        '昵称': expert_detail.get('name', ''),
        '彩龄': expert_detail.get('age', ''),
        '发文量': expert_detail.get('articles', ''),
        '大乐透一等奖': expert_detail.get('dltOne', ''),
        '大乐透二等奖': expert_detail.get('dltTwo', ''),
        '大乐透三等奖': expert_detail.get('dltThree', ''),
    }
    if expert_info['大乐透一等奖'] != '' and expert_info['大乐透一等奖'] is not None:
        expert_details.append(expert_info)
    time.sleep(0.2)

pd.DataFrame(expert_details).to_excel('result4/大乐透专家详情统计.xlsx', index=False)
```
**主要流程：**
1. 分页请求专家列表，筛选大乐透专家ID。
2. 逐个请求专家详情，提取属性与获奖信息。
3. 保存为Excel。

**关键库函数及其功能：**
- `requests.get`：请求API。
- `json.loads`：解析JSON。
- `pandas.DataFrame.to_excel`：保存专家信息。
- `time.sleep`：请求间隔。

---

### 3.6 专家属性与中奖分析（ExpertAnaly.py）

**核心代码片段：**
```python
expert_dataset = pd.read_excel('result4/大乐透专家详情统计.xlsx')

plt.figure(figsize=(16, 6))
primary_axis = plt.gca()
secondary_axis = primary_axis.twinx()
x_positions = np.arange(len(expert_dataset['昵称']))
primary_axis.plot(x_positions, expert_dataset['彩龄'], 'b-o', label='彩龄')
secondary_axis.plot(x_positions, expert_dataset['发文量'], 'r-s', label='发文量')

correlation_dataset = expert_dataset[['彩龄', '发文量', '大乐透一等奖', '大乐透二等奖', '大乐透三等奖']].copy()
for column_name in correlation_dataset.columns:
    correlation_dataset[column_name] = pd.to_numeric(correlation_dataset[column_name], errors='coerce')
correlation_matrix = np.zeros((2, 3))
for i, x_column in enumerate(['彩龄', '发文量']):
    for j, y_column in enumerate(['大乐透一等奖', '大乐透二等奖', '大乐透三等奖']):
        correlation_matrix[i, j] = correlation_dataset[x_column].corr(correlation_dataset[y_column])
sns.heatmap(correlation_matrix, annot=True, fmt='.2f', xticklabels=['一等奖', '二等奖', '三等奖'], yticklabels=['彩龄', '发文量'])
```
**主要流程：**
1. 读取专家详情数据，绘制彩龄与发文量对比图。
2. 计算专家属性与中奖次数的相关性，绘制热力图。

**关键库函数及其功能：**
- `pandas.read_excel`：读取专家数据。
- `matplotlib.pyplot`、`seaborn.heatmap`：可视化。
- `pandas.DataFrame.corr`：相关性分析。
- `numpy`：数值计算。

---

## 4. 总结

本项目实现了大乐透开奖数据的自动化采集、统计分析、预测建模与专家信息挖掘，涵盖数据工程与数据分析的完整流程，适合数据科学与彩票数据分析相关学习参考。
