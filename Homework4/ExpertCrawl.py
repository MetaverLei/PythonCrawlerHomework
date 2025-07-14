import requests
import time
import json
import os
import pandas as pd

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Host": "i.cmzj.net",
    "Origin": "https://www.cmzj.net",
    "Referer": "https://www.cmzj.net/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
}

expert_id_list = []
current_page = 1
while len(expert_id_list) < 25:
    api_url = f"https://i.cmzj.net/expert/queryExpert?limit=10&page={current_page}&sort=0"
    response = requests.get(api_url, headers=headers)
    try:
        response_text = response.content.decode('utf-8')
        response_data = json.loads(response_text)
    except Exception as decode_error:
        try:
            import brotli
            response_text = brotli.decompress(response.content).decode('utf-8')
            response_data = json.loads(response_text)
        except Exception as second_decode_error:
            print('两种方式都无法解码，内容如下：')
            print(response.content[:200])
            break
    for expert_item in response_data.get('data', []):
        expert_skills = [skill.strip() for skill in expert_item.get('skill', '').split(',')]
        if any('大乐透' in skill for skill in expert_skills):
            expert_id_list.append(expert_item['expertId'])
            if len(expert_id_list) >= 25:
                break
    current_page += 1
    time.sleep(0.2)  

print('大乐透专家expertId数组:', expert_id_list)

os.makedirs('result4', exist_ok=True)
expert_details = []
for expert_id in expert_id_list:
    detail_url = f'https://i.cmzj.net/expert/queryExpertById?expertId={expert_id}'
    detail_response = requests.get(detail_url, headers=headers)
    try:
        detail_text = detail_response.content.decode('utf-8')
        detail_data = json.loads(detail_text)
    except Exception as detail_decode_error:
        try:
            import brotli
            detail_text = brotli.decompress(detail_response.content).decode('utf-8')
            detail_data = json.loads(detail_text)
        except Exception as detail_second_error:
            print('两种方式都无法解码，内容如下：')
            print(detail_response.content[:200])
            continue
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
print('专家详情已写入 result4/大乐透专家详情统计.xlsx')
