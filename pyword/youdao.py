#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import requests
import time
import random
from hashlib import md5
 
headers = {
    'Cookie': 'OUTFOX_SEARCH_USER_ID=-690213934@10.108.162.139; OUTFOX_SEARCH_USER_ID_NCOO=1273672853.5782404; fanyi-ad-id=308216; fanyi-ad-closed=1; ___rl__test__cookies=1659506664755',
    'Host': 'fanyi.youdao.com',
    'Origin': 'https://fanyi.youdao.com',
    'Referer': 'https://fanyi.youdao.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
}
key = input("请输入你要翻译的单词：")
lts = str(int(time.time() * 100))
salt = lts + str(random.randint(0, 9))
sign_data = 'fanyideskweb' + key + salt +'Ygy_4c=r#e#4EX^NUGUc5'
sign = md5(sign_data.encode()).hexdigest()
data = {
    'i': key,
    'from': 'AUTO',
    'to': 'AUTO',
    'smartresult': 'dict',
    'client': 'fanyideskweb',
    # 时间戳  1970  秒
    'salt':salt,
    # 加密
    'sign': sign,
    # 时间戳
    'lts': lts,
    # 加密的数据
    'bv': 'f0819a82107e6150005e75ef5fddcc3b',
    'doctype': 'json',
    'version': '2.1',
    'keyfrom': 'fanyi.web',
    'action': 'FY_BY_REALTlME',
}
 
# 获取到资源地址
url = 'https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
response = requests.post(url, headers=headers, data=data)
print(response.text)