# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 13:48:00 2016

@author: tamho
"""

import time
from threading import Timer

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
        
def simulate(hostA, hostB, network):
    seconds = 0
    packet = packetTam("sender", "receiver", "send packet", time.time())
    while(seconds < 10):
        Timer(0, hostA.send, ()).start()
        Timer(2, network.receive, [packet]).start()
        Timer(4.1, hostB.receive, [packet]).start()
        seconds = seconds + 2
        time.sleep(2);
        
hostA = host("Host A")
hostB = host("Host B")
network = network()
simulate(hostA, hostB, network)