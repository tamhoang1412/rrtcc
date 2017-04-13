import multiprocessing
import time

def worker():
    while True:
        print 'Worker'
        

if __name__ == '__main__':
        p = multiprocessing.Process(target=worker)
        p.start()