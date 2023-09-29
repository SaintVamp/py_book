# -*- coding: utf-8 -*-
import os
import time

import requests
from bs4 import BeautifulSoup, NavigableString
import platform

# 两个小说网站
# base_urls = ['https://www.biqukun.com/77/77927/']
base_urls = ['https://www.xs386.com/24786/']
if platform.system() == 'Windows':
    book_path = os.getcwd() + '/out/'
else:
    book_path = '/usr/sv/out/'

# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    ts = time.time()
    print(ts)
    for base_url in base_urls:
        l_url = base_url.replace("//", "/")[:-1]
        l_url = l_url.split("/")
        r = requests.get(base_url)
        bs = BeautifulSoup(r.content, 'html.parser')
        # 两个网站容错
        book_name = bs.select("div#info>h1")
        flag = 1
        if len(book_name) == 0:
            book_name = bs.select("div.top>h1")
        book_name = book_name[0].text
        book_file = book_name + ".txt"
        log_name = book_name + ".log"
        arr_url = bs.select("dl>dt~dd>a")
        if len(arr_url) == 0:
            arr_url = bs.select("dd>a")
        i = 1
        for url in arr_url:
            print(i)
            if url.attrs["href"].find(l_url[2]):
                t_url = l_url[0] + "//" + l_url[1] + url.attrs["href"]
            else:
                t_url = l_url[0] + "//" + l_url[1] + "/" + l_url[2] + url.attrs["href"]
            tmp = requests.get(t_url)
            print(tmp.status_code)
            file = open(book_path + log_name, 'a', encoding='utf-8')
            file.write(str(i) + ":" + str(tmp.status_code) + "\n")
            file.close()
            tmp_html = BeautifulSoup(tmp.content, 'html.parser')
            title = tmp_html.select_one("h1").text
            contents = tmp_html.select_one("#content").contents
            # content = tmp_html.select_one("#content").text
            file = open(book_path + book_file, 'a', encoding='utf-8')
            file.write(str(title) + "\n")
            for content in contents:
                if isinstance(content, NavigableString):
                    file.write(str(content) + "\n")
            file.write("\n")
            file.close()
            i = i + 1
            time.sleep(2)
        requests.get("http://sv.svsoft.fun:8848/Serv/bookDownloadNotice?bookName=" + book_name)
    print(time.time() - ts)
