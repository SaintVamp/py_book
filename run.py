# -*- coding: utf-8 -*-
import os
import time

import requests
from bs4 import BeautifulSoup, NavigableString

# base_url = 'https://www.biqukun.com/77/77927/'
base_url = 'https://www.biqukun.com/88/88855/'
base_file = os.getcwd() + '/out/'

# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    ts = time.time()
    print(ts)
    r = requests.get(base_url)
    bs = BeautifulSoup(r.content, 'html.parser')
    book_name = bs.find_all("h1")[0].text + ".txt"
    log_name = bs.find_all("h1")[0].text + ".log"
    arr_url = bs.select("dd>a")
    i = 1
    for url in arr_url:
        print(i)
        t_url = base_url + url.attrs["href"]
        tmp = requests.get(t_url)
        print(tmp.status_code)
        file = open(base_file + log_name, 'a', encoding='utf-8')
        file.write(str(i) + ":" + str(tmp.status_code) + "\n")
        file.close()
        tmp_html = BeautifulSoup(tmp.content, 'html.parser')
        title = tmp_html.select_one("h1").text
        contents = tmp_html.select_one("#content").contents
        # content = tmp_html.select_one("#content").text
        file = open(base_file + book_name, 'a', encoding='utf-8')
        file.write(str(title) + "\n")
        for content in contents:
            if isinstance(content, NavigableString):
                file.write(str(content) + "\n")
        file.write("\n")
        file.close()
        i = i + 1
        time.sleep(2)

    print(time.time() - ts)
