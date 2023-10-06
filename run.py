# -*- coding: utf-8 -*-
import collections
import os
import platform
import sqlite3
import threading
import time

import requests
from bs4 import BeautifulSoup, NavigableString

# 两个网站
# base_urls = ['https://www.biqukun.com','https://www.xs386.com','https://www.tadu.com/']
if platform.system() == 'Windows':
    book_path = os.getcwd() + '/out/'
else:
    book_path = '/volume2/docker/reader/out/'


def check_book_exist(url):
    local_conn = sqlite3.connect("status.sqlite")
    local_cur = local_conn.cursor()
    op_sql = ('CREATE TABLE IF NOT EXISTS status(base_url TEXT PRIMARY KEY,book_name TEXT,sub_url TEXT,num INTEGER,'
              'timestamp INTEGER,count INTEGER)')
    local_cur.execute(op_sql)

    op_sql = "select count(*) from status where base_url='" + url + "'"
    local_cur.execute(op_sql)
    if local_cur.fetchone()[0] == 0:
        op_sql = "insert into status values ('" + base_url + "','','',0,0,0)"
        local_cur.execute(op_sql)
        local_conn.commit()
    local_conn.close()


def get_book_info(url):
    local_conn = sqlite3.connect("status.sqlite")
    local_cur = local_conn.cursor()
    op_sql = "select * from status where base_url='" + url + "'"
    local_cur.execute(op_sql)
    v_temp = local_cur.fetchone()
    local_conn.close()
    return v_temp


def update_book_info(url, book_name, sub_url, num):
    local_conn = sqlite3.connect("status.sqlite")
    local_cur = local_conn.cursor()
    op_sql = ("update status set book_name = '" + book_name + "',num = " + str(num) + ",sub_url = '" + sub_url +
              "',timestamp = " + str(int(time.time())) + ",count = 0 where base_url = '" + url + "'")
    local_cur.execute(op_sql)
    local_conn.commit()
    local_conn.close()


def update_book_count(url, count):
    local_conn = sqlite3.connect("status.sqlite")
    local_cur = local_conn.cursor()
    op_sql = "update status set count = " + str(count + 1) + " where base_url = '" + url + "'"
    local_cur.execute(op_sql)
    local_conn.commit()
    local_conn.close()


def parse_file():
    # 读取自定义格式的数组文件
    v_urls = []
    with open('book_urls.txt', 'r') as file:
        for line in file:
            # 解析每行数据，将字符串转换为数组
            v_urls.append(line.replace("\n", ""))
    file.close()
    return v_urls


def get_download_method(host):
    match host:
        case "www.biqukun.com":
            return ['div#info>h1', 'dd>a', 0, 1]
        case "www.xs386.com":
            return ['div#info>h1', 'dl>dt:nth-child(14)~dd>a', 1, 2]
        case "www.biqudd.org":
            return ['div#info>h1', 'center~dd>a', 0, 0]
        case "www.biqugeuu.com":
            return ['div#info>h1', 'dl>dt:nth-child(14)~dd>a', 1, 0]


def download_thread(main_url, main_info):
    try:
        s = requests.session()
        s.keep_alive = False
        l_url = main_url.replace("//", "/")[:-1]
        l_url = l_url.split("/")
        download_mothod = get_download_method(l_url[1])
        r = s.get(main_url)
        bs = BeautifulSoup(r.content, 'html.parser')
        # 两个网站容错
        book_name = bs.select(download_mothod[0])
        book_name = book_name[0].text
        book_file = book_name + ".txt"
        log_name = book_name + ".log"
        arr_url = bs.select(download_mothod[1])
        i = 1
        flag = True
        t_url = main_info['sub_url']
        for url in arr_url:
            if i > main_info['num']:
                flag = False
                print(i)
                match download_mothod[2]:
                    case 0:
                        t_url = main_url + url.attrs["href"]
                    case 1:
                        t_url = l_url[0] + "//" + l_url[1] + url.attrs["href"]
                    case 2:
                        t_url = url.attrs["href"]
                tmp = s.get(t_url)
                v_count = 0
                while v_count < 20 & tmp.status_code != 200:
                    time.sleep(1)
                    tmp = s.get(t_url)
                    v_count = v_count + 1
                print(tmp.status_code)
                file = open(book_path + log_name, 'a', encoding='utf-8')
                file.write(str(i) + ":" + str(tmp.status_code) + "\n")
                file.close()
                tmp_html = ""
                match download_mothod[3]:
                    case 0:
                        tmp_html = BeautifulSoup(tmp.text.replace("<br />", "<br>"), 'html.parser')
                    case 1:
                        tmp_html = BeautifulSoup(tmp.content.decode('utf-8').replace("<br />", "<br>"), 'html.parser')
                    case 2:
                        tmp_html = BeautifulSoup(tmp.content, 'html.parser')
                title = tmp_html.select_one("h1").text
                contents = tmp_html.select_one("#content").contents
                # content = tmp_html.select_one("#content").text
                file = open(book_path + book_file, 'a', encoding='utf-8')
                file.write(str(title) + "\n")
                for content in contents:
                    if isinstance(content, NavigableString):
                        if len(str(content).replace("\r", "").replace("\n", "")) > 0:
                            file.write(str(content).replace("\r", "").replace("\n", "") + "\n")
                file.write("\n")
                file.close()
                time.sleep(2)
                t_url = url.attrs["href"]
            i = i + 1
        if flag:
            update_book_count(main_url, main_info["count"])
        else:
            update_book_info(main_url, book_name, t_url, i - 1)
            s.get("http://4.0.4.51:8080/Serv/bookDownloadNotice?bookName=" + book_name)
    finally:
        file = open(book_path + log_name, 'a', encoding='utf-8')
        file.write(main_url + ":" + str(tmp.status_code) + "\n")
        file.close()


if __name__ == '__main__':
    ts = time.time()
    print(ts)
    base_urls = parse_file()
    for base_url in base_urls:
        _count = threading.active_count()
        while _count >= 5:
            print(f"等待中，线程个数：{_count}")
            _count = threading.active_count()
            time.sleep(60)
        check_book_exist(base_url)
        temp = get_book_info(base_url)

        book_info = collections.OrderedDict()
        book_info["base_url"] = temp[0]
        book_info["book_name"] = temp[1]
        book_info["sub_url"] = temp[2]
        book_info["num"] = temp[3]
        book_info["timestamp"] = temp[4]
        book_info["count"] = temp[5]
        if book_info['count'] == 5:
            requests.get("http://4.0.4.51:8080/Serv/bookFinish?bookName=" + book_info["book_name"])
        else:
            time.sleep(5)
            # download_thread(base_url, book_info)
            t = threading.Thread(target=download_thread, args=(base_url, book_info,))
            t.start()
        print(f"当前活跃的线程个数：{_count}")

    print(time.time() - ts)
