# -*- coding: utf-8 -*-
from Queue import PriorityQueue
from threading import Thread
from dijkstras import Dijkstra, shortestPath

eventQueue = PriorityQueue()

'''====================== Manager & Dispatcher =============================='''

class Manager:
    def __init__(self):
        #BaseElement array
        self.Elements = {'0': Node('192.168.1.1', 'A'), '1': Network('B'), '2': Node('124.126.123.123', 'C')}
        a = self.Elements
        
        #Cần định nghĩa cái này này
        self.Network = {a['0']:{a['2']:a['1']},
                        a['2']:{a['0']:a['1']}}
                        
            
        self.EventTypes = {'SP': 'Send pk', 'RP': 'Receive packet'}

    def getNextElement(self, sourceIPAddress, destIPAddess):
        return None

    def getEndPoints(self, network):
        return

class Dispatcher:    
    def mainLoop(self):
        while True:
            event = eventQueue.get()[1]
            event.Target.handle(event)
            
'''====================== Header, Packet, Event ============================='''
class Header:
    def __init__(self, source, destination):
        self.Source = source
        self.Destination = destination

class Packet:
    def __init__(self, header, payload):
        self.Header = header
        self.Payload = payload
        
class Event:
    def __init__(self, type, target, data, timestamp):
        self.Type = type
        self.Target = target
        self.Data = data
        self.Timestamp = timestamp

def CreatePacket(source, network, dest, payload) :
    return Packet({'L3Header': Header(source, dest), 'L2Header': Header(source, network)}, payload)

def CreateEvent(type, target, packet, timestamp):
    return Event(type, target, packet, timestamp)    

def LogEvent(specifier, event):
        x = specifier + ' Timestamp:' + str(event.Timestamp)
        x += ' EventType:' + event.Type
        x += ' NextElement:' + event.Target
        x += ' Data:' + event.Data.Packet.Payload
        return x;

def ScheduleEvent(event):
    eventQueue.put(event.Timestamp, event)

'''============================== Elements =================================='''

class BaseElement:
    def __init__(self):
        return
        
    def Send(data, timestamp):
        '''check if data.Packet != NULL
        '''

    def Recv(data, timestamp):
        '''do receive
        '''

    def HandleEvent(self, event):
        ''' Handle event
        '''

class Node(BaseElement):
    def __init__(self, IPAddress, MACAddress) :
        self.IPAddress = IPAddress
        self.MACAddress = MACAddress
    
    def HandleEvent(self, event):
        print LogEvent(event)
        if event.data == None:
            print "Critical error"
            exit()
        if event.Data.Header['L2Header'].Destination == self.MACAddress:
            if type(event.data) is Packet:
                if event.Type == 'SP':
                    self.Send(event.data, event.Timestamp)
                elif event.Type == 'RP':
                    self.Recv(event.data, event.Timestamp)
        else:
            print('wrong target')
    
    def NodeSend(self, payload, destination, timestamp):
        newPacket = CreatePacket({'L3Header': Header(self.IPAddress, destination),
                                'L2Header': Header(self.MACAddress, self.MACAddress)}, payload)
        newEvent = CreateEvent('SP', destination, newPacket, timestamp)
        ScheduleEvent(newEvent)
    
    def Send(self, packet, timestamp):
        nextNetwork = manager.getNextElement(self.IPAddress, packet.Header['L3Header'].Destination)
        packet.Header['L2Header'] = Header(self.MACAddress, nextNetwork)
        nextNetwork.recv(packet, timestamp)
        
    def Process(payload, timestamp):
        return
        
    def Recv(self, packet, timestamp):
        if packet.Header['L3Header'].Destination == self.IPAddress:
            x = 'Receive pk successfully! '
            x += 'Source:' + packet.Header['L2Header'].Source
            x += 'Destination:' + packet.Header['L2Header'].Destination
            x += 'Payload:' + packet.Payload
            print x
        else:
            self.Send(packet, timestamp)

class Network(BaseElement):
    def __init__(self, MACAddress):
        self.MACAddress = MACAddress

    def HandleEvent(self, event):
        print LogEvent(event)
        if event.data == None:
            print 'Critical error'
            exit()
        if type(event.data) is Packet:
            if event.Type == 'SP':
                self.Send(event.data, event.Timestamp)
            elif event.Type == 'RP':
                self.Recv(event.data, event.Timestamp)

    def Send(self, packet, timestamp):
        # gen random delay, e.g. delay = 10
        delay = 10
        endPoints = manager.getEndPoints(self.MACAddress)
        #fat = True
        #fitness = ("skinny", "fat")[fat]
        nextNode = endPoints[endPoints[1] == packet.Header['L2Header'].Source]
        packet.Header['L2Header'] = Header(self.MACAddress, nextNode.MACAddress)
        event = CreateEvent('RP', nextNode, packet, timestamp + delay)
        ScheduleEvent(event)
        
    def Process(self, payload):
        # generate random delay 
        self.send()
        
    def Recv(self, packet, timestamp):
        self.send(packet, timestamp)


''' ============================= MAIN PROGRAM ===================== '''
manager = Manager()
dispatcher = Dispatcher()
if __name__ == '__main__':
    p = Thread(target=dispatcher.mainLoop)
    p.start()
    
''' Bootstrap event: node1 send nothing to node4
'''
manager.Elements['1'].NodeSend('nothing', manager.Elements['4'], 0)
