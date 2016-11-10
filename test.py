#!/usr/bin/env python
#coding: utf8

import time
from multiprocessing import Process

works = 2

def produce(symbol):
    timestamp = time.time()
    while 1:
        time.sleep(2)
        print "sleep 2 s - %s " % symbol
        if time.time() - timestamp > 10:
            break

if __name__ == '__main__':
    processes = []
    for i in range(works):
        process = Process(target=produce, args=(i,))
        processes.append(process)
    
    for process in processes:
        process.start()
    
    for process in processes:
        process.join()
    end = time.time()
    print "end..."