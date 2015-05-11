#!/usr/bin/python
import sys, re, urllib, urllib2, os, threading, Queue, time

basename = os.path.basename(sys.argv[0])
pathname = os.path.dirname(sys.argv[0])
title_re = re.compile(r'html5Config\s*:\s*{.*?title\s*:\s*[\'"](.+?)[\'"],', re.DOTALL)
src_re = re.compile(r'html5Config\s*:\s*{.*?video\s*:\s*{.*?src\s*:\s*[\'"](.+?)[\'"],', re.DOTALL)
embed_pref = 'http://www.pornhub.com/embed/'


def extract_title_and_src(link):
    embed_src = re.search(r'[0-9a-zA-Z]+$', link).group(0)
    embed_res = urllib2.urlopen(embed_pref + embed_src).read()
    title = title_re.search(embed_res).group(1)
    src = src_re.search(embed_res).group(1)
    return (title, src)


if len(sys.argv) < 2:
    print 'Usage: ' + basename + ' PATH/TO/SRC [PATH/TO/SAVE]'
    sys.exit(1)

if len(sys.argv) > 2:
    pathname = sys.argv[2]

worker_num = 4
queue = []
lock = threading.Lock()
main_signal = threading.Semaphore(0)


def worker(num):
    while True:
        lock.acquire()
        if len(queue) > 0:
            raw_src = queue.pop()
        else:
            lock.release()
            main_signal.release()
            return
        lock.release()

        start_time = time.time() * 1000
        try:
            v_title, v_src = extract_title_and_src(raw_src)
            filename, headers = urllib.urlretrieve(v_src, pathname + os.sep + v_title + ".mp4")
            print "Downloaded %s in %.2f seconds" % (os.path.basename(str(filename)), (time.time() * 1000 - start_time) / 1000)
        except Exception as e:
            print e

with open(sys.argv[1]) as src_f:
    for raw_src in src_f:
        queue.append(raw_src)

for i in xrange(worker_num):
    threading.Thread(target=worker, args=(i, )).start()

for w in xrange(worker_num):
    main_signal.acquire(True)