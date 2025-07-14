# Homework2 说明文档

## 1. 项目简介

本项目主要包括三个部分：

- **天气数据爬取（crawl.py）**：自动爬取大连市2022-2025年上半年逐日天气数据，并整理为Excel文件。
- **气温预测分析（prediction.py）**：基于历史月平均最高气温数据，利用线性回归模型预测2025年全年气温，并与真实数据对比。
- **数据可视化与统计分析（visual.py）**：对爬取的天气数据进行统计分析和多种可视化展示。

---

## 2. 依赖库

- `requests`：用于网页请求，获取天气数据页面内容。
- `bs4`（BeautifulSoup）：解析HTML页面，提取表格数据。
- `pandas`：数据整理与存储，读写Excel文件。
- `numpy`：数值计算，数据处理。
- `scikit-learn`（sklearn）：机器学习库，线性回归建模。
- `matplotlib`：数据可视化。
- `seaborn`：高级数据可视化。
- `re`：正则表达式，文本处理。

安装依赖：
```bash
pip install -r requirements.txt
```

---

## 3. 核心代码与思路

### 3.1 天气数据爬取（crawl.py）

**关键代码片段：**
```python
# 构造月份列表
month_list = []
cur_month = start_month
while cur_month <= end_month:
    month_list.append(cur_month.strftime('%Y%m'))
    # ...月份递增...

# 爬取每月数据
for month_str in month_list:
    url = f'https://www.tianqihoubao.com/lishi/dalian/month/{month_str}.html'
    resp = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'html.parser')
    table = soup.find('table', {'class': 'weather-table'})
    # 解析表格，提取数据
    for tr in trs[1:]:
        tds = tr.find_all('td')
        # ...提取日期、天气、温度、风力...
        record = {...}
        records.append(record)
# 保存为Excel
df = pd.DataFrame(records)
df.to_excel('weather_dalian_2022_2024.xlsx', index=False)
```

**主要流程：**
1. **构造月份列表**：遍历2022年1月至2024年12月的每个月份，生成对应的字符串（如`202201`）。
2. **循环爬取每月数据**：
   - 构造目标URL，发送HTTP请求获取网页内容。
   - 用BeautifulSoup解析HTML，定位天气数据表格。
   - 提取每一天的日期、天气、温度、风力等信息，整理为字典，加入记录列表。
3. **额外爬取2025年1-6月数据**，并计算每月平均最高气温，保存为Excel。
4. **数据保存**：将所有数据保存为`weather_dalian_2022_2024.xlsx`和`2025_1-6_max_temp.xlsx`。

**关键库函数及其功能：**
- `requests.get`：发送HTTP请求，获取网页内容。
- `BeautifulSoup`：解析HTML文档，便于提取表格和标签内容。
- `find`/`find_all`（BeautifulSoup方法）：定位HTML中的表格和行。
- `pandas.DataFrame`：将字典列表转换为结构化表格数据。
- `DataFrame.to_excel`：将数据保存为Excel文件。

---

### 3.2 数据可视化与统计分析（visual.py）

**关键代码片段：**
```python
# 读取和预处理数据
df = pd.read_excel('weather_dalian_2022_2024.xlsx')
df['日期'] = df['日期'].apply(parse_date)
df['year'] = df['日期'].dt.year
df['month'] = df['日期'].dt.month

def to_num(x):
    try:
        return float(str(x).replace('℃','').replace(' ',''))
    except:
        return None

df['最高温度'] = df['最高温度'].astype(str).apply(to_num)
df['最低温度'] = df['最低温度'].astype(str).apply(to_num)

# 气温统计与保存
year_month_temp = df.groupby(['year', 'month'])['最高温度'].mean().reset_index()
year_month_temp = year_month_temp.rename(columns={'最高温度': '平均最高气温'})
year_month_temp.to_excel('year_month_max_temp.xlsx', index=False)

# 风力分布分析
def extract_wind_level(w):
    match = re.search(r'(\d+\s*[-~]\s*\d+级|\d+级)', str(w))
    return match.group(1).replace(' ', '') if match else None

df['白天风力'] = df['白天风力'].astype(str).apply(extract_wind_level)
df['夜晚风力'] = df['夜晚风力'].astype(str).apply(extract_wind_level)

# 天气状况分布分析
weather_long = pd.melt(weather_df, id_vars=['month'], value_vars=['白天天气','夜晚天气'], var_name='时段', value_name='天气')
weather_count = weather_long.groupby(['month','天气']).size().reset_index(name='天数')
```

**主要流程：**
1. **数据预处理**：读取天气数据，解析日期，补全年份和月份信息。
2. **气温统计与可视化**：统计每月平均最高/最低气温，保存折线图，并输出每年每月平均最高气温到Excel。
3. **风力分布分析**：提取风力等级，统计每月风力分布，生成饼图。
4. **天气状况分布分析**：统计每月不同天气类型的天数，分季度生成柱状图。

**关键库函数及其功能：**
- `pandas.read_excel`、`pandas.DataFrame`、`groupby`、`melt`：数据读取、整理与透视。
- `matplotlib.pyplot`、`plt.plot`、`plt.pie`、`plt.savefig`：绘制折线图、饼图并保存。
- `seaborn.barplot`：绘制分组柱状图。
- `re.search`：正则表达式提取风力等级。
- `os.makedirs`：创建结果文件夹。

---

### 3.3 气温预测分析（prediction.py）

**关键代码片段：**
```python
# 构造时序数据集
def create_dataset(series, window=12):
    X, y = [], []
    for i in range(len(series) - window):
        X.append(series[i:i+window])
        y.append(series[i+window])
    return np.array(X), np.array(y)

X, y = create_dataset(temp_series, window=12)

# 线性回归建模
model = LinearRegression()
model.fit(X, y)

# 递推预测未来12个月
test_input = temp_series[-12:]
preds = []
for i in range(12):
    pred = model.predict(test_input[-12:].reshape(1, -1))[0]
    preds.append(pred)
    test_input = np.append(test_input, pred)
```

**主要流程：**
1. **读取数据**：加载历史月平均最高气温和2025年1-6月真实气温数据。
2. **构造时序数据集**：用前12个月的气温预测下一个月，形成训练集。
3. **线性回归建模**：用`sklearn`的`LinearRegression`模型拟合数据。
4. **递推预测**：用最近12个月的气温递推预测2025年1-12月的气温。
5. **结果保存与对比**：将预测结果与真实数据对比（可视化部分略）。

**关键库函数及其功能：**
- `pandas.read_excel`：读取Excel文件，获取历史气温数据。
- `numpy.array`：高效存储和处理数值型数据。
- `sklearn.linear_model.LinearRegression`：线性回归模型，用于拟合和预测。
- `model.fit`：训练线性回归模型。
- `model.predict`：用训练好的模型进行预测。
- `numpy.append`：在数组末尾添加新预测值，实现递推。

---

## 4. 总结

本项目实现了大连市近年天气数据的自动化爬取与整理，并基于历史数据进行气温预测和多维度可视化分析。核心流程包括数据采集、清洗、特征构造、建模、统计与可视化。

---

如需运行，确保已安装依赖库，并在`Homework2`目录下依次运行`crawl.py`、`visual.py`和`prediction.py`即可。



