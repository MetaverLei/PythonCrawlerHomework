import requests
import re
import json
import datetime
import openpyxl

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Host": "jc.zhcw.com",
    "Referer": "https://www.zhcw.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
}

date_begin = datetime.date(2024, 10, 30)
date_end = datetime.date(2025, 7, 1)

lottery_data = []
current_page = 1

while True:
    url = (
        f"https://jc.zhcw.com/port/client_json.php?"
        f"callback=jQuery112209220184727154788_1751885800538"
        f"&transactionType=10001001&lotteryId=281&issueCount=1000"
        f"&startIssue=&endIssue=&startDate=&endDate=&type=0"
        f"&pageNum={current_page}&pageSize=30&tt=0.7861486523735369"
        f"&_=1751885800551"
    )
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
    worksheet.append([
        data_row["开奖日期"],
        data_row["星期"],
        data_row["前区号码"],
        data_row["后区号码"],
        data_row["总销售额"],
    ])
workbook.save("大乐透开奖数据统计.xlsx")
print("数据已保存到 大乐透开奖数据统计.xlsx")