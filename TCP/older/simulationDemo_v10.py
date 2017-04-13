# -*- coding: utf-8 -*-
from Queue import PriorityQueue
from threading import Thread

eventQueue = PriorityQueue()
            
'''====================== Header, Packet, Event ============================='''
class Header:
    def __init__(self, source, destination, sqNumber = 0,  ACKFlag = 0):
        self.Source = source
        self.Destination = destination
        self.ACKFlag = ACKFlag
        self.SqNumber = sqNumber

class Packet:
    def __init__(self, header, payload):
        self.Header = header
        self.Payload = payload

    def ToString(self):
        x = 'Source:' + self.Header.Source
        x += '_Destination:' + self.Header.Destination
        x += '_ACKFlag:' + str(self.Header.ACKFlag)
        x += '_SqNumber:' + str(self.Header.SqNumber)
        x += '_Payload:' + self.Payload
        return x
        
class Event:
    def __init__(self, type, target, data, timestamp):
        self.Type = type
        self.Target = target
        self.Data = data
        self.Timestamp = timestamp

def CreatePacket(source, dest, payload, sqNumber = 0, ACKFlag = 0) :
    return Packet(Header(source, dest, sqNumber, ACKFlag), payload)

def CreateEvent(type, target, packet, timestamp):
    return Event(type, target, packet, timestamp)

def LogEvent(specifier, event):
    x = specifier + '___Timestamp:' + str(event.Timestamp)
    x += '___EventType:' + event.Type
    x += '___Target:' + event.Target.Address
    x += '___Data:' + event.Data.ToString()
    return x;

def ScheduleEvent(event):
    eventQueue.put((event.Timestamp, event))

def GetNextEvent():
    return eventQueue.get()[1]


'''====================== Manager & Dispatcher =============================='''

class Manager:
    def __init__(self):
        #BaseElement array
        self.Nodes = {'A': Node('A'), 'B': Node('B')}
        self.Networks = [Network0()]
        self.EventTypes = {'SP': 'Send pk', 'RP': 'Receive packet'}

    def GetElementByAddress(self, address):
        return self.Nodes[str(address)]

    def GetNetwork(self, sourceAddress, destinationAddress):
        return self.Networks[0]

class Dispatcher:    
    def mainLoop(self):
        while True:
            event = GetNextEvent()
            event.Target.HandleEvent(event)
            
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

class Network0(BaseElement):
    def __init__(self):
        '''
        '''

    def HandleEvent(self, event):
        print LogEvent(self.Address, event)
        if event.data == None:
            print 'Critical error'
            exit()
        if type(event.Data) is Packet:
            if event.Type == 'SP':
                self.Send(event.data, event.Timestamp)
            elif event.Type == 'RP':
                self.Recv(event.data, event.Timestamp)

    def Send(self, packet, timestamp):
        # gen random delay, e.g. delay = 10
        delay = 10
        destination = manager.GetElementByAddress(packet.Header.Destination)
        event = CreateEvent('RP', destination, packet, timestamp + delay)
        ScheduleEvent(event)
        print 'Network send'
        
    def Recv(self, packet, timestamp):
        print 'Network recv'
        self.Send(packet, timestamp)


class Node(BaseElement):
    def __init__(self, address) :
        self.Address = address
    
    def HandleEvent(self, event):
        print LogEvent(self.Address, event)
        if event.Data == None:
            print "Critical error"
            exit()
        if isinstance(event.Data, Packet):
            if event.Type == 'SP':
                self.Send(event.Data, event.Timestamp)
            elif event.Type == 'RP':
                self.Recv(event.Data, event.Timestamp)

    def NodeSend(self, payload, destinationAddress, timestamp, sqNumber = 0, ACKFlag = 0):
        newPacket = CreatePacket(self.Address, destinationAddress, payload, sqNumber, ACKFlag)
        newEvent = CreateEvent('SP', self, newPacket, timestamp)
        ScheduleEvent(newEvent)

    def Send(self, packet, timestamp):
        network = manager.GetNetwork(self.Address, packet.Header.Destination);
        network.Recv(packet, timestamp)
    
    def Process(self, packet, timestamp):
        if packet.Header.ACKFlag == 0:
            newPacket = CreatePacket(self.Address, packet.Header.Source, "" , packet.Header.SqNumber , 1)
            newEvent = CreateEvent('SP', self, newPacket, timestamp + 1)
            ScheduleEvent(newEvent)
        else:
            return
        
    def Recv(self, packet, timestamp):
        self.Process(packet, timestamp)


''' ============================== MAIN PROGRAM ============================ '''
manager = Manager()
dispatcher = Dispatcher()
if __name__ == '__main__':
    p = Thread(target=dispatcher.mainLoop)
    p.start()
    
''' Bootstrap event: node1 send nothing to node4
'''
manager.Nodes['A'].NodeSend('nothing', 'B', 0)
