# -*- coding: utf-8 -*-
"""
Created on Tue Oct 04 23:30:34 2016

@author: tamho
"""


import time
from threading import Thread
from queuelib import FifoDiskQueue

class packetTam:
    def __init__(self, source, destination, payload, sendTime):
        self.source = source
        self.destination = destination
        self.payload = payload
        self.sendTime = sendTime

#scheduler = queue.PriorityQueue()

class host:
    def __init__(self, name):
        self.name = name
    def send(self, out_q):
        while True:
            time.sleep(2);
            packet = packetTam("sender", "receiver", "send packet", time.time())
            print self.name, " sent at time:", time.time()
            out_q.push(packet)
            
    def receive(self, in_q):
        while True:
            time.sleep(3);
            data = in_q.pop()
            print self.name, " recevie packet sent at", data.sendTime," at time:", time.time()
        
class network:
    def schedule(self, in_q, out_q):
        while True:
            time.sleep(4);
            out_q.push(in_q.pop());


hostA = host("Host A")
hostB = host("Host B")
network = network()

in_q = FifoDiskQueue("queuefile")
out_q = FifoDiskQueue("queuefile")
t = Thread(target=hostA.send, args=(in_q))
t.start()
t = Thread(target=hostB.receive, args=(out_q))
t.start()
t = Thread(target=network.schedule, args=(in_q, out_q))
t.start()