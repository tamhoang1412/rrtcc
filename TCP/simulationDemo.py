# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 23:23:03 2016

import random
import functools

adist = functools.partial(random.expovariate, 0.5)
sdist = functools.partial(random.expovariate, 0.01)
samp_dist = functools.partial(random.expovariate, 1.0)
port_rate = 1000.0

"""
import time
from threading import Timer

def sender():
    print "send at time:", time.time()
    
def receiver():
    print "receive at time: ", time.time()

def simulate():
    seconds = 0
    while(seconds < 10):
        Timer(0, sender, ()).start()
        Timer(3, receiver, ()).start()
        seconds = seconds + 2
        time.sleep(2);
        
