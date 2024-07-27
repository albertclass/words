import requests

uri = "https://dict.bing.com.cn/api/http/v2/4154AA7A1FC54ad7A84A0236AA4DCAF3/en-us/zh-cn/?q=address&format=application/json"
response = requests.get(uri, verify=False)
print(response.text)