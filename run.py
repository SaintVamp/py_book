# -*- coding: utf-8 -*-
import collections
import os
import platform
import threading
import time

import pymysql
import requests
from bs4 import BeautifulSoup, NavigableString

linux_path = "/usr/sv/book/"
if platform.system() == 'Windows':
    book_path = os.getcwd() + '/out/'
    config_path = os.getcwd() + "/"
else:
    book_path = linux_path + 'out/'
    config_path = linux_path


def operate_mysql(op_sql):
    db = pymysql.connect(host="4.0.4.52", port=7848, user="sv", password="sv@8004", db="SV", charset='utf8')
    cursor = db.cursor()
    cursor.execute(op_sql)
    tmp = cursor.fetchone()
    db.commit()
    db.close()
    return tmp


def check_book_exist(url):
    op_sql = "select count(*) from BookInfo where base_url='" + url + "'"
    date = operate_mysql(op_sql)
    if date[0] == 0:
        op_sql = "insert into BookInfo values ('" + base_url + "','','',0,0,0,1)"
        operate_mysql(op_sql)


def get_book_info(url):
    op_sql = "select * from BookInfo where base_url='" + url + "'"
    return operate_mysql(op_sql)


def update_book_info(url, book_name, sub_url, num):
    op_sql = ("update BookInfo set book_name = '" + book_name + "',num = " + str(num) + ",sub_url = '" + sub_url +
              "',timestamp = " + str(int(time.time())) + ",count = 0 where base_url = '" + url + "'")
    operate_mysql(op_sql)


def update_book_count(url, count):
    op_sql = "update BookInfo set count = " + str(count + 1) + " where base_url = '" + url + "'"
    operate_mysql(op_sql)


def page_2_txt(s, url, method, nt_page):
    tmp = s.get(url)

    v_count = 0
    while v_count < 20 & tmp.status_code != 200:
        time.sleep(1)
        tmp = s.get(url)
        v_count = v_count + 1
    print(tmp.status_code)

    v_html = ""
    match method:
        case 0:
            v_html = BeautifulSoup(tmp.text.replace('id="articlecontent"', 'id="content"').replace("h3>", "h1>").replace("<br />", "<br>").replace("<br/>", "<br>").replace("<p>", "").replace("</p>", "<br>").replace('<p class="content_detail">', "<br>"), 'html.parser')
        case 1:
            try:
                v_html = BeautifulSoup(tmp.content.decode('gbk').replace("h3>", "h1>").replace("<br />", "<br>").replace("<br/>", "<br>").replace("<p>", "").replace("</p>", "<br>").replace('<p class="content_detail">', "<br>"), 'html.parser')
            except Exception as e:
                print(e)
                try:
                    v_html = BeautifulSoup(tmp.content.decode('UTF-8').replace("h3>", "h1>").replace("<br />", "<br>").replace("<br/>", "<br>").replace("<p>", "").replace("</p>", "<br>").replace('<p class="content_detail">', "<br>"), 'html.parser')
                except Exception as e:
                    print(e)
                    v_html = BeautifulSoup(tmp.content.replace("h3>", "h1>").replace("<br />", "<br>").replace("<br/>", "<br>").replace("<p>", "").replace("</p>", "<br>").replace('<p class="content_detail">', "<br>"), 'html.parser')
        case 2:
            v_html = BeautifulSoup(tmp.content.replace("h3>", "h1>").replace("<br />", "<br>").replace("<br/>", "<br>").replace("<p>", "").replace("</p>", "<br>").replace('<p class="content_detail">', "<br>"), 'html.parser')
    title = v_html.select_one("h1").text
    contents = v_html.select_one("#content").contents
    nt_page_tag = v_html.select_one(nt_page)
    nt_page_text = v_html.select_one(nt_page).text
    time.sleep(2)
    if nt_page_text.find("下一页") > -1:
        return [title, contents, True, nt_page_tag, tmp.status_code]
    else:
        return [title, contents, False, nt_page_tag, tmp.status_code]


def parse_file():
    # 读取自定义格式的数组文件
    v_urls = []
    with open(config_path + 'book_urls.txt', 'r') as file:
        for line in file:
            # 解析每行数据，将字符串转换为数组
            v_urls.append(line.replace("\n", ""))
    file.close()
    return v_urls


def get_download_method(host):
    ### [名称,链接,拼接方式,替<BR>方式,下一页/下一章标志]
    match host:
        case "www.biqukun.com":
            return ['div#info>h1', 'dd>a', 0, 1]
        case "www.xs386.com":
            return ['div#info>h1', 'dl>dt:nth-child(14)~dd>a', 1, 2]
        case "www.biqudd.org":
            return ['div#info>h1', 'center~dd>a', 0, 0,"a#link-next"]
        case "www.biqugeuu.com":
            return ['div#info>h1', 'dl>dt:nth-child(14)~dd>a', 1, 1]
        case "www.aishangba4.com":
            return ['div#info>h1', 'dd>a', 1, 0]
        case "www.bqge.org":
            return ['div#info>h1', 'dl>dt:nth-child(7)~dd>a', 1, 0,"a.next"]
        case "www.yeduku.net":
            return ['div#info>h1', 'dl>dt:nth-child(14)~dd>a', 1, 0, "a#pager_next"]
        case "www.quanzhifashi.com":
            return ['div.introduce>h1', 'div.ml_list>ul>li>a', 1, 0, "div.nr_page:nth-child(2)>a:nth-child(5)"]


def download_thread(main_url, main_info):
    log_name = ""
    try:
        s = requests.session()
        s.keep_alive = False
        l_url = main_url.replace("//", "/")[:-1]
        l_url = l_url.split("/")
        download_method = get_download_method(l_url[1])
        r = s.get(main_url)
        bs = BeautifulSoup(r.content, 'html.parser')
        # 两个网站容错
        book_name = bs.select(download_method[0])
        book_name = book_name[0].text
        book_file = book_name + ".txt"
        log_name = book_name + ".log"
        arr_url = bs.select(download_method[1])
        i = 1
        flag = True
        t_url = main_info['sub_url']
        for url in arr_url:
            if i > main_info['num']:
                flag = False
                print(i)
                next_page = True
                title_flag = True
                v_url = url
                while next_page:
                    match download_method[2]:
                        case 0:
                            t_url = main_url + v_url.attrs["href"]
                        case 1:
                            t_url = l_url[0] + "//" + l_url[1] + v_url.attrs["href"]
                        case 2:
                            t_url = v_url.attrs["href"]
                    rt = page_2_txt(s, t_url, download_method[3], download_method[4])
                    next_page = rt[2]
                    v_url = rt[3]
                    file = open(book_path + log_name, 'a', encoding='utf-8')
                    file.write(str(i) + ":" + str(rt[4]) + "\n")
                    file.close()
                    file = open(book_path + book_file, 'a', encoding='utf-8')
                    if title_flag:
                        file.write(str(rt[0]) + "\n")
                        title_flag = False
                    for content in rt[1]:
                        if isinstance(content, NavigableString):
                            if len(str(content).replace("\r", "").replace("\n", "")) > 0:
                                file.write(str(content).replace("\r", "").replace("\n", "").replace("\t", "") + "\n")
                    file.write("\n")
                    file.close()
                t_url = url.attrs["href"]
                update_book_info(main_url, book_name, t_url, i)
            i = i + 1
        if flag:
            update_book_count(main_url, main_info["count"])
        else:
            s.get("http://4.0.4.51:8080/Serv/bookDownloadNotice?bookName=" + book_name)
    except Exception as e:
        file = open(book_path + log_name, 'a', encoding='utf-8')
        file.write(main_url + " : has error > " + str(e) + "\n")
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
        t_book_info = get_book_info(base_url)

        book_info = collections.OrderedDict()
        book_info["base_url"] = t_book_info[0]
        book_info["book_name"] = t_book_info[1]
        book_info["sub_url"] = t_book_info[2]
        book_info["num"] = t_book_info[3]
        book_info["timestamp"] = t_book_info[4]
        book_info["count"] = t_book_info[5]
        book_info["pass"] = t_book_info[6]
        if book_info["pass"] == 1:
            if book_info['count'] == 5:
                requests.get("http://4.0.4.51:8080/Serv/bookFinish?bookName=" + book_info["book_name"])
            else:
                time.sleep(5)
                download_thread(base_url, book_info)
                # t = threading.Thread(target=download_thread, args=(base_url, book_info,))
                # t.start()
            print(f"当前活跃的线程个数：{_count}")

    print(time.time() - ts)
