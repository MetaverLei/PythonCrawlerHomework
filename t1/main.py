import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import jieba
from wordcloud import WordCloud
from collections import Counter
import re
import os

# 创建保存图表的文件夹
if not os.path.exists('charts'):
    os.makedirs('charts')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示问题
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# 1. 爬取胡润百富榜数据
def fetch_hurun_data():
    url = "https://www.hurun.net/zh-CN/Rank/HsRankDetailsList?num=ODBYW2BI&search=&offset=0&limit=2000"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析JSON数据
        data = response.json()
        return data['rows']
    except Exception as e:
        print(f"数据获取失败: {e}")
        return None

# 2. 解析数据并创建DataFrame
def parse_data(data):
    parsed_data = []
    
    for row in data:
        # 提取基本信息
        char_info = row.get('hs_Character', [{}])[0]
        rank_info = row
        
        # 处理年龄字段
        age_str = char_info.get('hs_Character_Age', '')
        if age_str.isdigit():
            age = int(age_str)
        else:
            age = None
            
        # 处理财富字段
        wealth = rank_info.get('hs_Rank_Rich_Wealth', 0)
        if wealth is None:
            wealth = 0
            
        # 处理出生地
        birthplace = char_info.get('hs_Character_NativePlace_Cn', '未知')
        if birthplace != '未知':
            birthplace = birthplace.split('-')[-1]
        
        # 处理行业信息
        industry = rank_info.get('hs_Rank_Rich_Industry_Cn', '未知')
        if industry == '':
            industry = '未知'
        
        parsed_data.append({
            '姓名': char_info.get('hs_Character_Fullname_Cn', ''),
            '财富(亿)': wealth,
            '性别': char_info.get('hs_Character_Gender', '未知'),
            '年龄': age,
            '出生地': birthplace,
            '公司': rank_info.get('hs_Rank_Rich_ComName_Cn', ''),
            '行业': industry,
            '总部': rank_info.get('hs_Rank_Rich_ComHeadquarters_Cn', ''),
            '排名': rank_info.get('hs_Rank_Rich_Ranking', 0)
        })
    
    return pd.DataFrame(parsed_data)

# 3. 格式化打印数据 - 确保各列对齐
def print_formatted_data(df, num_rows=5):
    # 获取列名
    headers = df.columns.tolist()
    
    # 计算每列最大宽度
    col_widths = [max(len(str(col)), max(df[col].astype(str).apply(len).max(), 8)) for col in headers]
    
    # 打印表头
    header = " | ".join([str(headers[i]).ljust(col_widths[i]) for i in range(len(headers))])
    print(header)
    print("-" * len(header))
    
    # 打印数据行
    for i in range(min(num_rows, len(df))):
        row = df.iloc[i]
        row_str = " | ".join([str(row[col]).ljust(col_widths[j]) for j, col in enumerate(headers)])
        print(row_str)

# 4. 行业分析 - 独立图表
def industry_analysis(df):
    # 行业富豪数量统计
    industry_count = df['行业'].value_counts().head(10)
    
    # 行业财富总值统计
    industry_wealth = df.groupby('行业')['财富(亿)'].sum().sort_values(ascending=False).head(10)
    
    # 图表1：行业富豪数量TOP10
    plt.figure(figsize=(12, 8))
    industry_count.plot(kind='bar', color='skyblue')
    plt.title('各行业富豪数量TOP10', fontsize=15)
    plt.ylabel('人数', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('charts/行业富豪数量TOP10.png', dpi=300)
    plt.show()
    
    # 图表2：行业财富总值TOP10
    plt.figure(figsize=(12, 8))
    industry_wealth.plot(kind='bar', color='salmon')
    plt.title('各行业财富总值TOP10(亿)', fontsize=15)
    plt.ylabel('财富总值(亿)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('charts/行业财富总值TOP10.png', dpi=300)
    plt.show()
    
    # 返回分析结果
    return {
        'industry_count': industry_count,
        'industry_wealth': industry_wealth
    }

# 5. 性别分布 - 独立图表
def gender_distribution(df):
    plt.figure(figsize=(10, 8))
    gender_count = df['性别'].value_counts()
    gender_count.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=['lightblue', 'lightpink'])
    plt.title('富豪性别分布', fontsize=15)
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig('charts/富豪性别分布.png', dpi=300)
    plt.show()

# 6. 年龄分布 - 独立图表
def age_distribution(df):
    plt.figure(figsize=(12, 8))
    age_bins = [0, 30, 40, 50, 60, 70, 100]
    age_labels = ['30岁以下', '31-40岁', '41-50岁', '51-60岁', '61-70岁', '70岁以上']
    df['年龄段'] = pd.cut(df['年龄'], bins=age_bins, labels=age_labels, right=False)
    age_dist = df['年龄段'].value_counts().sort_index()
    age_dist.plot(kind='bar', color='teal')
    plt.title('富豪年龄分布', fontsize=15)
    plt.xlabel('年龄段')
    plt.ylabel('人数')
    plt.tight_layout()
    plt.savefig('charts/富豪年龄分布.png', dpi=300)
    plt.show()

# 7. 出生地分布 - 独立图表
def birthplace_distribution(df):
    plt.figure(figsize=(12, 8))
    birth_places = df[df['出生地'] != '未知']['出生地'].value_counts().head(10)
    birth_places.plot(kind='barh', color='orange')
    plt.title('富豪出生地TOP10', fontsize=15)
    plt.xlabel('人数')
    plt.tight_layout()
    plt.savefig('charts/富豪出生地TOP10.png', dpi=300)
    plt.show()

# 8. 财富-年龄关系 - 独立图表
def wealth_age_analysis(df):
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='年龄段', y='财富(亿)', data=df, palette='Set2')
    plt.title('不同年龄段财富分布', fontsize=15)
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig('charts/不同年龄段财富分布.png', dpi=300)
    plt.show()

# 9. 行业热力图 - 独立图表
def industry_heatmap(df):
    plt.figure(figsize=(14, 10))
    # 选择前15个行业
    top_industries = df['行业'].value_counts().head(15).index
    industry_age = pd.crosstab(df[df['行业'].isin(top_industries)]['行业'], 
                              df['年龄段'], normalize='index')
    sns.heatmap(industry_age, cmap='YlGnBu', annot=True, fmt='.1%')
    plt.title('行业与年龄段热力图', fontsize=15)
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig('charts/行业与年龄段热力图.png', dpi=300)
    plt.show()

# 10. 财富排名分析 - 独立图表
def wealth_rank_analysis(df):
    # 图表1：财富分布直方图
    plt.figure(figsize=(12, 6))
    plt.hist(df['财富(亿)'], bins=30, color='steelblue', alpha=0.7)
    plt.title('财富分布直方图', fontsize=15)
    plt.xlabel('财富(亿)')
    plt.ylabel('人数')
    plt.tight_layout()
    plt.savefig('charts/财富分布直方图.png', dpi=300)
    plt.show()
    
    # 图表2：排名与财富关系
    plt.figure(figsize=(12, 6))
    plt.scatter(df['排名'], df['财富(亿)'], alpha=0.6, color='darkorange')
    plt.title('排名与财富关系', fontsize=15)
    plt.xlabel('排名')
    plt.ylabel('财富(亿)')
    plt.gca().invert_xaxis()  # 反转x轴，排名1在最左边
    plt.tight_layout()
    plt.savefig('charts/排名与财富关系.png', dpi=300)
    plt.show()

# 11. 生成词云 - 独立图表
def generate_wordcloud(df):
    plt.figure(figsize=(14, 10))
    # 提取公司名称
    companies = ' '.join(df['公司'].dropna().astype(str))
    
    # 使用jieba分词
    words = jieba.lcut(companies)
    word_count = Counter(words)
    
    # 过滤单字
    filtered_words = {word: count for word, count in word_count.items() if len(word) > 1}
    
    # 生成词云
    wc = WordCloud(
        font_path='simhei.ttf',
        background_color='white',
        max_words=200,
        width=1200,
        height=800
    ).generate_from_frequencies(filtered_words)
    
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title('公司名称词云', fontsize=16)
    plt.tight_layout()
    plt.savefig('charts/公司名称词云.png', dpi=300)
    plt.show()

# 12. 富豪地理分布 - 新增图表
def geographic_distribution(df):
    plt.figure(figsize=(14, 10))
    # 提取总部所在省份
    df['省份'] = df['总部'].apply(lambda x: x.split(' ')[0] if isinstance(x, str) else '未知')
    
    # 统计各省富豪数量
    province_count = df[df['省份'] != '未知']['省份'].value_counts().head(15)
    
    # 绘制地图式分布
    province_count.plot(kind='bar', color='purple')
    plt.title('富豪地理分布TOP15', fontsize=15)
    plt.ylabel('人数')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('charts/富豪地理分布.png', dpi=300)
    plt.show()

# 主函数
def main():
    # 爬取数据
    print("正在爬取胡润百富榜数据...")
    raw_data = fetch_hurun_data()
    
    if raw_data is None:
        print("数据获取失败，程序终止")
        return
    
    # 解析数据
    print("解析数据...")
    df = parse_data(raw_data)
    
    # 显示基本信息
    print(f"\n共爬取 {len(df)} 位富豪数据")
    print("\n数据示例:")
    print_formatted_data(df.head())
    
    # 行业分析
    print("\n正在进行行业分析...")
    industry_analysis(df)
    
    # 性别分布
    print("\n分析性别分布...")
    gender_distribution(df)
    
    # 年龄分布
    print("\n分析年龄分布...")
    age_distribution(df)
    
    # 出生地分布
    print("\n分析出生地分布...")
    birthplace_distribution(df)
    
    # 财富-年龄关系
    print("\n分析财富与年龄关系...")
    wealth_age_analysis(df)
    
    # 行业热力图
    print("\n分析行业与年龄关系...")
    industry_heatmap(df)
    
    # 财富排名分析
    print("\n进行财富排名分析...")
    wealth_rank_analysis(df)
    
    # 地理分布
    print("\n分析地理分布...")
    geographic_distribution(df)
    
    # 生成词云
    print("\n生成公司名称词云...")
    generate_wordcloud(df)
    
    # 保存数据
    df.to_csv('胡润百富榜2024.csv', index=False, encoding='utf_8_sig')
    print("\n数据已保存为 '胡润百富榜2024.csv'")
    print("所有图表已保存到 'charts' 文件夹")

if __name__ == "__main__":
    main()