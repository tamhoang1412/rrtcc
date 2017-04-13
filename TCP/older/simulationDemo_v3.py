# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 13:48:00 2016

@author: tamho
"""

import time
from threading import Timer
from threading import Thread

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
    def send(self):
        #scheduler.put(time.time() + 2, packetTam("sender", "receiver", "send packet", time.time()))
        print self.name, " sent at time:", time.time()
    def receive(self, packet):
        print self.name, " received at time: ", time.time()

class network:
    def send(self, packet):
        #scheduler.put(time.time() + 2, packet)
        print "Network sent at time:", time.time()
    def receive(self, packet):
        print "Network received at time: ", time.time()
        self.send(packet)
 

def simulateSending(host, packet):
    n = 1
    while(n < 15):
        Timer(2, host.send, ()).start()
        n=2
        
def simulateForwarding(network, packet):
    n = 3
    while(n < 15):
        Timer(3, network.receive, [packet]).start()
        n+=3
    
def simulateReceiving(host, packet):
    n = 4
    while(n < 15):
        Timer(4, hostB.receive, [packet]).start()
        n+=4

hostA = host("Host A")
hostB = host("Host B")
network = network()
packet = packetTam("sender", "receiver", "send packet", time.time())

t = Thread(target=simulateSending, args=(hostA, packet))
t.start()
t = Thread(target=simulateForwarding, args=(network, packet))
t.start()
t = Thread(target=simulateReceiving, args=(hostB, packet))
t.start()