import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties
import re

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_excel('weather_dalian_2022_2024.xlsx')

if '日期' in df.columns:
    df = df[df['日期'].notnull()]
    def parse_date(s):
        s = str(s)
        s = re.sub(r'[年月]', '-', s)
        s = re.sub(r'[日.]', '', s)
        s = s.strip('-')
        try:
            return pd.to_datetime(s, format='%Y-%m-%d', errors='coerce')
        except:
            return pd.to_datetime(s, errors='coerce')
    df['日期'] = df['日期'].apply(parse_date)
    df = df[df['日期'].notnull()]
    df['year'] = df['日期'].dt.year
    df['month'] = df['日期'].dt.month
else:
    raise ValueError('数据表缺少"日期"列')

# 任务2
def to_num(x):
    try:
        return float(str(x).replace('℃','').replace(' ',''))
    except:
        return None

df['最高温度'] = df['最高温度'].astype(str).apply(to_num)
df['最低温度'] = df['最低温度'].astype(str).apply(to_num)

os.makedirs('results', exist_ok=True)

monthly_temp = df.groupby('month').agg({'最高温度':'mean', '最低温度':'mean'}).reset_index()
if not monthly_temp.empty:
    plt.figure(figsize=(10,6))
    plt.plot(monthly_temp['month'], monthly_temp['最高温度'], marker='o', label='平均最高温度')
    plt.plot(monthly_temp['month'], monthly_temp['最低温度'], marker='o', label='平均最低温度')
    plt.xticks(range(1,13))
    plt.xlabel('月份')
    plt.ylabel('温度 (℃)')
    plt.title('大连市近三年月平均气温变化')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('results/monthly_temp_trend.png')
    plt.close()
else:
    print('月平均气温数据为空，未生成气温变化图。')

year_month_temp = df.groupby(['year', 'month'])['最高温度'].mean().reset_index()
year_month_temp = year_month_temp.rename(columns={'最高温度': '平均最高气温'})
year_month_temp.to_excel('year_month_max_temp.xlsx', index=False)

# 任务3
def extract_wind_level(w):
    match = re.search(r'(\d+\s*[-~]\s*\d+级|\d+级)', str(w))
    return match.group(1).replace(' ', '') if match else None

for col in ['白天风力', '夜晚风力']:
    df[col] = df[col].astype(str).apply(extract_wind_level)

for m in range(1, 13):
    month_df = df[df['month'] == m]
    wind_levels = pd.concat([
        month_df['白天风力'].dropna(),
        month_df['夜晚风力'].dropna()
    ])
    wind_counts = wind_levels.value_counts().sort_index()
    if not wind_counts.empty:
        plt.figure(figsize=(6,6))
        plt.pie(wind_counts, labels=wind_counts.index, autopct='%1.1f%%', startangle=90, counterclock=False)
        plt.title(f'{m}月风力等级分布')
        plt.tight_layout()
        plt.savefig(f'results/wind_pie_{m:02d}.png')
        plt.close()
    else:
        print(f'{m}月风力数据为空，未生成饼图。')

# 任务4
weather_df = pd.DataFrame()
weather_df['month'] = df['month']
weather_df['白天天气'] = df['白天天气'].astype(str).str.strip()
weather_df['夜晚天气'] = df['夜晚天气'].astype(str).str.strip()
weather_long = pd.melt(weather_df, id_vars=['month'], value_vars=['白天天气','夜晚天气'], var_name='时段', value_name='天气')
weather_long = weather_long[weather_long['天气'].notnull() & (weather_long['天气'] != '')]
weather_count = weather_long.groupby(['month','天气']).size().reset_index(name='天数')
weather_count['平均天数'] = weather_count['天数'] / 3
weather_count['平均天数'] = weather_count['平均天数'].apply(lambda x: round(x, 1))

for i, months in enumerate([range(1,5), range(5,9), range(9,13)], 1):
    plt.figure(figsize=(12,7))
    subset = weather_count[weather_count['month'].isin(months)]
    if not subset.empty:
        sns.barplot(data=subset, x='month', y='平均天数', hue='天气')
        plt.xlabel('月份')
        plt.ylabel('平均天数')
        plt.title(f'大连市近三年天气状况分布（{min(months)}-{max(months)}月）')
        plt.legend(title='天气状况', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(f'results/weather_bar_{i}.png')
        plt.close()
    else:
        print(f'{min(months)}-{max(months)}月天气状况数据为空，未生成柱状图。')

print('所有可视化结果已保存到 results 文件夹。')
print('每年每月平均最高气温已保存为 year_month_max_temp.xlsx。')
