# 1. 安装必要库
# !pip install pandas numpy matplotlib seaborn wordcloud sklearn statsmodels lxml

# 2. 导入所有库
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer
from statsmodels.tsa.arima.model import ARIMA
import re
import os
import warnings
warnings.filterwarnings('ignore')
plt.rcParams['font.family'] = 'SimHei'  # 中文显示

def fetch_dblp_data(conferences, years):
    """从DBLP爬取指定会议和年份的论文数据"""
    all_papers = []
    for conf_name, conf_code in conferences.items():
        for year in years:
            url = f"https://dblp.org/db/conf/{conf_code}/{conf_code}{year}.xml"
            print(f"正在爬取: {conf_name} {year} ({url})")
            
            try:
                response = requests.get(url, timeout=20)
                soup = BeautifulSoup(response.content, 'xml')
                
                # 提取论文信息
                for article in soup.find_all(['article', 'inproceedings']):
                    title = article.find('title').text.strip()
                    authors = [a.text.strip() for a in article.find_all('author')]
                    paper_url = article.find('ee').text if article.find('ee') else ""
                    
                    all_papers.append({
                        'title': title,
                        'authors': ', '.join(authors),
                        'year': year,
                        'conference': conf_name,
                        'url': paper_url
                    })
            except Exception as e:
                print(f"爬取出错: {conf_name}{year} - {str(e)}")
                if 'response' in locals():
                    print(f"响应状态码: {response.status_code}")
                    
    return pd.DataFrame(all_papers)

def preprocess_titles(df):
    """预处理论文标题"""
    def preprocess_title(title):
        # 移除非字母字符、转小写
        title = re.sub(r'[^a-zA-Z\s]', '', title).lower()
        # 移除常见停用词
        stop_words = {'for', 'and', 'with', 'using', 'based', 'via', 'towards', 
                      'toward', 'learning', 'approach', 'method', 'via', 'network',
                      'deep', 'model', 'models', 'neural', 'via', 'new', 'based'}
        words = [word for word in title.split() if len(word) > 2 and word not in stop_words]
        return ' '.join(words)
    
    df['clean_title'] = df['title'].apply(preprocess_title)
    return df

def plot_paper_trends(df):
    """绘制论文数量趋势图"""
    # 统计各会议年度论文数量
    conf_year_counts = df.groupby(['conference', 'year']).size().unstack().fillna(0)
    print("\n各会议年度论文数量:")
    print(conf_year_counts)
    
    # 绘制趋势图
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='year', y=df.index, hue='conference', 
                 estimator='count', errorbar=None, marker='o', linewidth=2.5)
    plt.title('顶级会议论文数量趋势 (2020-2025)', fontsize=15)
    plt.ylabel('论文数量', fontsize=12)
    plt.xlabel('年份', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='会议名称')
    plt.tight_layout()
    plt.savefig('charts/conference_trend.png', dpi=300)  # 修改路径
    plt.show()
    
def generate_combined_wordcloud(df):
    """生成五年合并的关键词词云"""
    # 合并所有年份的论文标题
    all_text = ' '.join(df['clean_title'])
    
    if not all_text.strip():
        print("没有可用的文本数据生成词云")
        return
    
    # 生成词云
    plt.figure(figsize=(12, 8))
    wc = WordCloud(
        width=1200, 
        height=800, 
        background_color='white',
        max_words=150,
        collocations=False,  # 避免重复词语
        stopwords=None,      # 使用自定义停用词
        colormap='viridis'   # 使用更鲜艳的配色
    ).generate(all_text)
    
    # 绘制词云
    plt.imshow(wc, interpolation='bilinear')
    plt.title('2020-2025年计算机科学领域研究热点', fontsize=20)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('charts/combined_wordcloud.png', dpi=300, bbox_inches='tight')  # 修改路径
    plt.show()
    
    # 提取高频关键词
    vectorizer = CountVectorizer(max_features=50, stop_words='english')
    X = vectorizer.fit_transform([all_text])
    word_freq = pd.Series(
        np.array(X.sum(axis=0))[0],
        index=vectorizer.get_feature_names_out()
    ).sort_values(ascending=False)
    
    print("\n2020-2025年高频关键词TOP 20:")
    print(word_freq.head(20))
    
    # 保存高频词到CSV
    word_freq_df = word_freq.reset_index()
    word_freq_df.columns = ['keyword', 'frequency']
    word_freq_df.to_csv('top_keywords.csv', index=False)  # 修改路径
    
    # 绘制关键词频率条形图
    plt.figure(figsize=(14, 8))
    top20 = word_freq.head(20)
    sns.barplot(x=top20.values, y=top20.index, palette='viridis')
    plt.title('2020-2025年TOP 20高频关键词', fontsize=16)
    plt.xlabel('出现频率', fontsize=12)
    plt.ylabel('关键词', fontsize=12)
    plt.tight_layout()
    plt.savefig('charts/top_keywords_bar.png', dpi=300)  # 修改路径
    plt.show()

def predict_paper_counts(df):
    """预测下一届会议论文数量"""
    plt.figure(figsize=(12, 8))
    
    conferences = df['conference'].unique()
    next_year = df['year'].max() + 1
    
    for i, conf in enumerate(conferences):
        # 获取历史数据
        conf_data = df[df['conference'] == conf]
        yearly_counts = conf_data['year'].value_counts().sort_index()
        
        # 转换为时间序列（确保包含所有年份）
        all_years = range(df['year'].min(), next_year)
        ts_data = yearly_counts.reindex(all_years, fill_value=0)
        
        # 训练ARIMA模型
        try:
            model = ARIMA(ts_data, order=(1, 1, 1))
            model_fit = model.fit()
            
            # 预测下一年
            forecast = model_fit.forecast(steps=1)
            predicted_next = int(round(forecast.iloc[0]))
        except Exception as e:
            print(f"预测失败 {conf}: {str(e)}")
            predicted_next = ts_data.iloc[-1]  # 使用最近一年的数据作为预测
        # 动态调整行数
        rows = (len(conferences) + 1) // 2 
        # 绘制历史趋势和预测
        plt.subplot(rows, 2, i+1)
        sns.lineplot(x=ts_data.index, y=ts_data.values, marker='o', label='历史数据')
        plt.plot([ts_data.index[-1], next_year], 
                 [ts_data.iloc[-1], predicted_next], 
                 'r--', marker='o', label='预测')
        
        plt.title(f'{conf}论文数量预测', fontsize=14)
        plt.xlabel('年份', fontsize=12)
        plt.ylabel('论文数量', fontsize=12)
        plt.xticks(list(ts_data.index) + [next_year])
        plt.legend()
        plt.grid(alpha=0.3)
        
        print(f"{conf} {next_year}年预测论文数: {predicted_next} (最近一年实际: {ts_data.iloc[-1]})")
    
    plt.tight_layout()
    plt.savefig('charts/prediction.png', dpi=300)  # 修改路径
    plt.show()

def main():
    """主函数，执行整个分析流程"""
    # 创建 charts 文件夹（如果不存在）
    charts_dir = 'charts'
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
        print(f"创建文件夹: {charts_dir}")
    
    # 定义会议列表和年份范围 (2020-2025)
    conferences = {
        'AAAI': 'aaai',
        'CVPR': 'cvpr',
        'NeurIPS': 'nips',
        'ICML': 'icml',
        'IJCAI': 'ijcai',
        'KDD': 'kdd'
    }
    years = range(2020, 2026)  # 2020-2025
    
    # 获取数据
    data_file = 'dblp_papers_2020-2025.csv'
    if os.path.exists(data_file):
        print("加载本地数据文件...")
        df = pd.read_csv(data_file)
    else:
        print("从DBLP爬取数据...")
        df = fetch_dblp_data(conferences, years)
        df.to_csv(data_file, index=False)
    
    print(f"总论文数: {len(df)}")
    print("数据年份范围:", df['year'].min(), "至", df['year'].max())
    
    # 预处理标题
    df = preprocess_titles(df)
    
    # 分析任务
    plot_paper_trends(df)         # 任务2：论文数量趋势
    generate_combined_wordcloud(df) # 任务3：五年合并关键词分析
    predict_paper_counts(df)       # 任务4：论文数量预测
    
    print("\n分析完成！结果已保存到 charts 文件夹中。")  # 更新提示信息

if __name__ == "__main__":
    main()