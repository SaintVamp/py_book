hostname=$(uci get system.@system[0].hostname)
if [ "$hostname" = "R404" ]; then
    mkdir /usr/sv/book/out
    curl -o /usr/sv/book/py_book.py https://gitee.com/saintvamp/py_book/raw/master/run.py
    curl -o /usr/sv/book/book_urls.txt https://gitee.com/saintvamp/py_book/raw/master/book_urls.txt
    nohup python /usr/sv/book/py_book.py > /usr/sv/out/book/run.log 2>&1 &
elif [ "$hostname" = "R2804" ]; then
    echo 'pass'
fi