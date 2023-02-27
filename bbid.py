#!/usr/bin/env python3
import hashlib
import os
import pickle
import re
import signal
import socket
import threading
import time
import urllib.parse
import urllib.request

# config
output_dir = './bing'  # default output dir
adult_filter = True  # Do not disable adult filter by default
socket.setdefaulttimeout(2)

tried_urls = []
image_md5s = {}
in_progress = 0
urlopenheader = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}

def download(pool_sema: threading.Semaphore, img_sema: threading.Semaphore, url: str, output_dir: str, tried_urls, image_md5s, filename_):
    global in_progress

    state = 0
    a = 0
    
    while state != 1:

        pool_sema.acquire()
        in_progress += 1
        filename = filename_ + '.jpg'

        try:
            request = urllib.request.Request(url, None, urlopenheader)
            image = urllib.request.urlopen(request).read()

            md5_key = hashlib.md5(image).hexdigest()

            image_md5s[md5_key] = filename

            img_sema.acquire()

            imagefile = open(os.path.join(output_dir, filename), 'wb')
            imagefile.write(image)
            imagefile.close()
            print(" OK : " + filename)

            state = 1
            return
        except :
            a = a + 1


def fetch_images_from_keyword(pool_sema: threading.Semaphore, img_sema: threading.Semaphore, keyword: str,
                              output_dir: str, tried_urls, image_md5s, filename_):
    current = 0
    last = ''
    while True:
        time.sleep(0.1)

        if in_progress > 10:
            continue

        request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(keyword) + '&first=' + str(
            current) + '&count=35&adlt=' + '' + '&qft=' + ''
        request = urllib.request.Request(request_url, None, headers=urlopenheader)

        response = urllib.request.urlopen(request, timeout = 15)

        global Max_Num
        Max_Num = 6
        for i in range(Max_Num):
            try:
                html = urllib.request.urlopen(request, timeout = 15).read().decode('utf8')
                break
            except:
                if i < Max_Num - 1:
                    continue
                else:
                    print('Error')            

        links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
        
        try:
            if links[-1] == last:
                return
            for index, link in enumerate(links):
                download(pool_sema, img_sema, link, output_dir, tried_urls, image_md5s, filename_)
                return
            last = links[-1]
        except IndexError:
            print('FAIL: No search results for "{0}"'.format(keyword))
            return


def backup_history(*args):
    download_history = open(os.path.join(output_dir, 'download_history.pickle'), 'wb')
    pickle.dump(tried_urls, download_history)
    copied_image_md5s = dict(image_md5s)  
    pickle.dump(copied_image_md5s, download_history)
    download_history.close()
    print('history_dumped')
    if args:
        exit(0)


def use(search_string_, output_, filename_):

    search_string = search_string_
    output_dir = output_
    threads = 20

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    signal.signal(signal.SIGINT, backup_history)

    try:
        download_history = open(os.path.join(output_dir, 'download_history.pickle'), 'rb')
        tried_urls = pickle.load(download_history)
        global image_md5s 
        image_md5s = pickle.load(download_history)
        download_history.close()
    except (OSError, IOError):
        tried_urls = []

    pool_sema = threading.BoundedSemaphore(threads)
    img_sema = threading.Semaphore()

    if search_string:
        fetch_images_from_keyword(pool_sema, img_sema, search_string, output_dir, tried_urls, image_md5s, filename_)
        print('Done')