import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta

start_month = datetime(2022, 1, 1)
end_month = datetime(2024, 12, 1)
month_list = []
cur_month = start_month
while cur_month <= end_month:
    month_list.append(cur_month.strftime('%Y%m'))
    if cur_month.month == 12:
        cur_month = datetime(cur_month.year + 1, 1, 1)
    else:
        cur_month = datetime(cur_month.year, cur_month.month + 1, 1)

records = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

for month_str in month_list:
    url = f'https://www.tianqihoubao.com/lishi/dalian/month/{month_str}.html'
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        if resp.status_code != 200:
            print(f"Failed to get {url}, status: {resp.status_code}")
            time.sleep(1)
            continue
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'class': 'weather-table'})
        if not table:
            print(f"No table found for {month_str}")
            time.sleep(1)
            continue
        trs = table.find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            if len(tds) < 4:
                continue
            date = tds[0].get_text(strip=True)
            weather = tds[1].get_text(strip=True)
            temp = tds[2].get_text(strip=True)
            wind = tds[3].get_text(strip=True)
            if not date or not weather or not temp or not wind:
                continue
            try:
                day_weather, night_weather = [x.strip() for x in weather.split('/')]
            except:
                day_weather, night_weather = weather, ''
            try:
                high_temp, low_temp = [x.replace('℃','').strip() for x in temp.split('/')]
            except:
                high_temp, low_temp = '', ''
            try:
                day_wind, night_wind = [x.strip() for x in wind.split('/')]
            except:
                day_wind, night_wind = wind, ''
            record = {
                '日期': date,
                '白天天气': day_weather,
                '夜晚天气': night_weather,
                '最高温度': high_temp,
                '最低温度': low_temp,
                '白天风力': day_wind,
                '夜晚风力': night_wind,
            }
            records.append(record)
        print(f"Done: {month_str}")
    except Exception as e:
        print(f"Error on {month_str}: {e}")
    time.sleep(1)

# 爬取2025年1-6月数据
extra_months = [f'202501', f'202502', f'202503', f'202504', f'202505', f'202506']
extra_records = []
for month_str in extra_months:
    url = f'https://www.tianqihoubao.com/lishi/dalian/month/{month_str}.html'
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        if resp.status_code != 200:
            print(f"Failed to get {url}, status: {resp.status_code}")
            time.sleep(1)
            continue
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table', {'class': 'weather-table'})
        if not table:
            print(f"No table found for {month_str}")
            time.sleep(1)
            continue
        trs = table.find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            if len(tds) < 4:
                continue
            date = tds[0].get_text(strip=True)
            weather = tds[1].get_text(strip=True)
            temp = tds[2].get_text(strip=True)
            wind = tds[3].get_text(strip=True)
            if not date or not weather or not temp or not wind:
                continue
            try:
                day_weather, night_weather = [x.strip() for x in weather.split('/')]
            except:
                day_weather, night_weather = weather, ''
            try:
                high_temp, low_temp = [x.replace('℃','').strip() for x in temp.split('/')]
            except:
                high_temp, low_temp = '', ''
            try:
                day_wind, night_wind = [x.strip() for x in wind.split('/')]
            except:
                day_wind, night_wind = wind, ''
            record = {
                '日期': date,
                '白天天气': day_weather,
                '夜晚天气': night_weather,
                '最高温度': high_temp,
                '最低温度': low_temp,
                '白天风力': day_wind,
                '夜晚风力': night_wind,
                '月份': month_str
            }
            extra_records.append(record)
        print(f"Done: {month_str}")
    except Exception as e:
        print(f"Error on {month_str}: {e}")
    time.sleep(1)

if extra_records:
    extra_df = pd.DataFrame(extra_records)
    def to_num(x):
        try:
            return float(str(x).replace('℃','').replace(' ',''))
        except:
            return None
    extra_df['最高温度'] = extra_df['最高温度'].astype(str).apply(to_num)
    extra_df['month'] = extra_df['月份'].str[-2:].astype(int)
    avg_temp = extra_df.groupby('month')['最高温度'].mean().reset_index()
    avg_temp = avg_temp.rename(columns={'最高温度': '平均最高温度'})
    avg_temp.to_excel('2025_1-6_max_temp.xlsx', index=False)
    print('2025年1-6月每月平均最高气温已保存为 2025_1-6_max_temp.xlsx')
else:
    print('未获取到2025年1-6月数据')

if records:
    df = pd.DataFrame(records)
    df.to_excel('weather_dalian_2022_2024.xlsx', index=False)
    print('数据已保存为 weather_dalian_2022_2024.xlsx')
else:
    print('未获取到任何数据')
