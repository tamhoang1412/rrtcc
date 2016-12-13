from Queue import Queue
from threading import Thread
from dijkstras import Dijkstra, shortestPath

eventQueue = Queue()

class Header:
    def __init__(self, source, destination):
        self.Source = source
        self.Destination = destination

class Packet:
    def __init__(self, header, payload):
        self.Header = header
        self.Payload = payload

class Data:
    def __init__(self, packet):
        self.Packet = packet

class Event:
    def __init__(self, type, source, destination, data, timestamp):
        self.Type = type
        self.Source = source
        self.Destination = destination
        self.Data = data
        self.Timestamp = timestamp

class Event1:
    def __init__(self, type, target, data, timestamp):
        self.Type = type
        self.Target = target
        self.Data = data
        self.Timestamp = timestamp

def WriteLog(specifier, event):
        x = specifier + ' Timestamp:' + str(event.Timestamp)
        x += ' event_type: ' + event.Type
        x += ' nextElement: ' + event.Target
        x += ' Data: ' + event.Data.Packet.Payload
        print x;
        return

def WriteLog1(specifier, packet):
        x = specifier + ' Timestamp:' + str(event.Timestamp)
        x += ' event_type: ' + event.Type
        x += ' nextElement: ' + event.Target
        x += ' Data: ' + event.Data.Packet.Payload
        print x;
        return


def createPacket(source, dest, payload) :
    return Packet(Header(source, dest), payload)

def createEvent(type, target, packet, timestamp):
    return Event1(type, target, Data(packet), timestamp)    
    
    
def scheduleEvent(event):
    eventQueue.put(event)

class BaseElement:
    def __init__(self):
        return
    def send(data):
        '''check if data.Packet != NULL
        '''

    def recv(data):
        '''do receive
        '''

class Node:
    def __init__(self, ip) :
        self.Address = IP
        
    def nodeSend(self, payload, dest):
        WriteLog1(...)
        packet = createPacket(self.Address, dest, payload)
        self.send(packet)
        
        #event = createEvent('RP', nextNode, packet, -1)
        #scheduleEvent(event)
        
    def send(self, packet):
        nextNode = Manager.getNextNode(self)
        nextNode.recv(packet)
        
    def process(payload):
        return
        
    def recv(self, packet):
        #check if packet.Header.Destination == self.Address
        payload = packet.Payload
        #process Payload
        process(payload)

class Network:
    def send(self, packet):
        # gen random delay, e.g. delay = 10
        delay = 10
        nextNode = manager.getNextNode(self)
        event = createEvent('RP', nextNode, packet, now() + delay)
        scheduleEvent(event)
        
    def process(self, payload):
        # generate random delay 
        self.send()
        
    def recv(self, packet):
        #check if packet.Header.Destination == self.Address
        payload = packet.Payload
        #process Payload
        self.process(payload)


class Manager:
    def __init__(self):
        self.CurrentTS = 0
        self.Elements = {'0': '192.168.1.1', '1': '203.90.21.14', '2': '124.126.123.123', '3': '8.8.8.8', '4': '1.1.1.1'}
        a = self.Elements
        self.Network = {a['0']:{a['1']:4, a['2']:5},
                        a['1']:{a['0']:4, a['2']:2, a['3']:3},
                        a['2']:{a['0']:5, a['1']:2},
                        a['3']:{a['1']:3, a['4']: 4},
                        a['4']:{a['3']:4}}
        self.EventTypes = {'SP': 'Send pk', 'RP': 'Receive packet'}
        
    def getNextNode(self, refNode):
        return None
    def now(self):
        return ++self.CurrentTS;

class Dispatcher:
    def WriteLog(self, event):
        x = '* Timestamp: ' + str(event.Timestamp)
        x += '   Event Type: ' + event.Type
        x += '\nSource: ' + event.Source
        x += '   Destination: ' + event.Destination
        x += '\nData: ' + event.Data.Packet.Payload
        print x;
        return
    
    def HandleEvent(self):
        while True:
            event = eventQueue.get()
            self.WriteLog(event)
            if event.Type == 'SP':
                newEvent = Event('RP', event.Source, event.Destination, event.Data, event.Timestamp + 2)
                eventQueue.put(newEvent)
            elif event.Type == 'RP':
                if event.Destination != event.Data.Packet.Header.Destination:
                    nextPath = shortestPath(manager.Network, event.Destination, event.Data.Packet.Header.Destination)
                    newEvent = Event('SP', event.Destination, nextPath[1], event.Data, event.Timestamp + 1)
                    eventQueue.put(newEvent)


class Dispatcher1:
        if event.data == None:
            print "Critical error"
            sys.exit(0)
            
        if event.data is a packet:
            if event.Type == 'SP':
                event.Target.send(event.data)
            else if event.Type == 'RP':
                event.Target.recv(event.data)
    
    def mainLoop(self):
        while True:
            event = eventQueue.get()
            event.Target.handle(event.data)

''' ============================= MAIN PROGRAM ===================== '''
manager = Manager()
dispatcher = Dispatcher1()
if __name__ == '__main__':
    p = Thread(target=dispatcher.mainLoop)
    p.start()
    
''' Bootstrap event: node1 send nothing to node4
'''
manager.Elements['1'].nodeSend('nothing', manager.Elements['4'])

