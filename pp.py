# Author:zmd
# Date:2019/8/20 14:56
# desc:

import requests
import time
from lxml import etree
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
import json

test_url="https://www.baidu.com/"
head={"User-Agent":UserAgent().random}
apiurl='http://127.0.0.1:8000/api'
req=requests.get(apiurl,headers=head)
p=json.loads(req.text)
print(p)
html=requests.get(test_url,proxies=p,headers=head,timeout=10)
print(html.status_code)
