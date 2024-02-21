hostname=$(hostname)
if [ "$hostname" = "R404" ]; then
    mkdir /usr/sv/book/out
    curl -o /usr/sv/book/py_book.py https://gitee.com/saintvamp/py_book/raw/master/run.py
    curl -o /usr/sv/book/book_urls.txt https://gitee.com/saintvamp/py_book/raw/master/book_urls.txt
    nohup python3 /usr/sv/book/py_book.py >> /usr/sv/book/out/run.log 2>&1 &
elif [ "$hostname" = "R2804" ]; then
    echo 'pass'
elif [ "$hostname" = "NASDown" ]; then
    mkdir /data/book/out
    curl -o /data/book/py_book.py https://gitee.com/saintvamp/py_book/raw/master/run.py
    curl -o /data/book/book_urls.txt https://gitee.com/saintvamp/py_book/raw/master/book_urls.txt
    nohup python3 /data/book/py_book.py >> /data/book/out/run.log 2>&1 &
fi