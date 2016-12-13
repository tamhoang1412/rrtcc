# -*- coding: utf-8 -*-
from Queue import PriorityQueue
from threading import Thread
import time
import os
import json
import copy as cp

os.remove("D:/logA.txt")
os.remove("D:/logB.txt")
foA = open("D:/logA.txt", "wb")
foB = open("D:/logB.txt", "wb")

blocking = 0
eventQueue = PriorityQueue()
            
'''====================== Header, Packet, Event ============================='''
class Header:
    def __init__(self, source, destination, sqNumber = 0,  AckFlag = 0):
        self.Source = source
        self.Destination = destination
        self.AckFlag = AckFlag
        self.SqNumber = sqNumber

class Packet:
    def __init__(self, header, payload):
        self.Header = header
        self.Payload = payload

    def ToJSON(self):
        x = {
            'Source': self.Header.Source,
            'Destination': self.Header.Destination,
            'AckFlag': self.Header.AckFlag,
            'SqNumber': self.Header.SqNumber,
            'Payload': self.Payload
        }
        return x
        
    def ToString(self):
        
        x = 'Source:' + self.Header.Source
        x += '_Destination:' + self.Header.Destination
        x += '_AckFlag:' + str(self.Header.AckFlag)
        x += '_SqNumber:' + str(self.Header.SqNumber)
        x += '_Payload:' + self.Payload
        '''
        x = {
            'Source': self.Header.Source,
            'Destination': self.Header.Destination,
            'AckFlag': self.Header.AckFlag,
            'SqNumber': self.Header.SqNumber,
            'Payload': self.Payload
        }
        '''
        return x
        
class Event:
    def __init__(self, type, target, data, timestamp):
        self.Type = type
        self.Target = target
        self.Data = data
        self.Timestamp = timestamp


def CreatePacket(source, dest, payload, sqNumber = 0, AckFlag = 0) :
    return Packet(Header(source, dest, sqNumber, AckFlag), payload)

def CreateEvent(type, target, packet, timestamp):
    return Event(type, target, packet, timestamp)

def LogEvent(specifier, event):
    
    x = specifier + '___Timestamp:' + str(event.Timestamp)
    x += '___EventType:' + event.Type
    x += '___Target:' + event.Target.Address
    x += '___Data:'
    if isinstance(event.Data, Packet):
        x += event.Data.ToString()
    else:
        x += str(event.Data)
    return x
    '''
    if isinstance(event.Data, Packet):
        data = event.Data.ToJSON()
    else:
        data = event.Data
    x = {
        'Specifier': specifier,
        'EventType': event.Type,
        'Timestamp': event.Timestamp,
        'Target': event.Target.Address,
        'Data': data
    }
    return json.dumps(x);
    '''

def LogEventJSON(specifier, event):
    if isinstance(event.Data, Packet):
        data = event.Data.ToJSON()
    else:
        data = event.Data
    x = {
        'Specifier': specifier,
        'EventType': event.Type,
        'Timestamp': event.Timestamp,
        'Target': event.Target.Address,
        'Data': data
    }
    return json.dumps(x);

def ScheduleEvent(event):
    eventQueue.put((event.Timestamp, event))

def GetNextEvent():
    return eventQueue.get()[1]


'''====================== Manager & Dispatcher =============================='''

class Manager:
    def __init__(self):
        #BaseElement array
        self.Nodes = {'A': TCPNode('A', foA), 'B': TCPNode('B', foB)}
        self.Networks = [Network0()]
        self.EventTypes = {'SP': 'Send pk', 'RP': 'Receive packet', 'CTO':'Check timeout', 'TO':'Timeout'}

    def GetElementByAddress(self, address):
        return self.Nodes[str(address)]

    def GetNetwork(self, sourceAddress, destinationAddress):
        return self.Networks[0]

class Dispatcher:    
    def mainLoop(self):
        while True:
            event = GetNextEvent()
            print LogEvent(event.Target.Address, event)
            event.Target.HandleEvent(event)
            time.sleep(0.6)

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
        self.check = 0
        '''
        '''
    '''
    def HandleEvent(self, event):
        #print LogEvent(self.Address, event)
        if event.data == None:
            print 'Critical error'
            exit()
        if isinstance(event.Data, Packet):
            if event.Type == 'SP':
                self.Send(event.data, event.Timestamp)
            elif event.Type == 'RP':
                self.Recv(event.data, event.Timestamp)
    '''
    def Send(self, packet, timestamp):
        # gen random delay
        #delay = random.randrange(4, 7, 1)
        delay = 5
        destination = manager.GetElementByAddress(packet.Header.Destination)
        #x = "sch nhan packet " + str(packet.Header.SqNumber) + "tai time " + str(timestamp)
        #print x
        event = CreateEvent('RP', destination, packet, cp.deepcopy(timestamp) + delay)
        ScheduleEvent(event)
        
    def Recv(self, packet, timestamp):
        if (packet.Header.SqNumber == 10) and (self.check == 0):
            self.check == 1
            return
        self.Send(packet, cp.deepcopy(timestamp))


class TCPNode(BaseElement):
    def __init__(self, address, logFile) :
        self.Address = address
        self.LogFile = logFile
        self.Buffer = []
        self.nPackets = 0
        
        self.LastSqNumSent = 0
        self.LastSqNumAcked = -1
        self.Cwnd = 1
        self.Threshold = 64
        self.Timeout = 10
        self.nDuplicatedAck = 0
        
        self.LastSqNumReceived = 0
        self.CongestionStt = 0
        self.CongestionSttDict = {'Slow start': 0, 'Congestion avoidance':1, 'Fast recovery':2}
        
        self.Delay = 0.5

    def HandleEvent(self, event):
        
        self.LogFile.write(LogEventJSON(self.Address, event))
        self.LogFile.write('|')
        
        if event.Data == None:
            print "Critical error"
            exit()
        if isinstance(event.Data, Packet):
            if event.Type == 'SP':
                self.Send(event.Data, cp.deepcopy(event.Timestamp))
            elif event.Type == 'RP':
                self.Recv(event.Data, cp.deepcopy(event.Timestamp))
            elif event.Type == 'CTO':
                self.CheckTimeout(event.Data, cp.deepcopy(event.Timestamp))

    def NodeSend(self, payload, destinationAddress, timestamp, AckFlag = 0):
        self.nPackets = 20
        for x in range(0, self.nPackets):
            self.Buffer.append(CreatePacket(self.Address, destinationAddress, payload, x, AckFlag))
        newEvent = CreateEvent('SP', self, self.Buffer[0], cp.deepcopy(timestamp))
        ScheduleEvent(newEvent)
        self.LastSqNumSent = 0

    def Send(self, packet, timestamp):
        network = manager.GetNetwork(self.Address, packet.Header.Destination)
        network.Recv(packet, cp.deepcopy(timestamp))
        if packet.Header.AckFlag == 0:
            newEvent = CreateEvent('CTO', self, self.LastSqNumAcked, cp.deepcopy(timestamp) + self.Timeout)
            ScheduleEvent(newEvent)
    
    def Process(self, packet, timestamp):
        if packet.Header.AckFlag == 0:
            '''If host receive normal data (not ack)'''
            if packet.Header.SqNumber == self.LastSqNumReceived + 1:
                self.LastSqNumReceived += 1
            newPacket = CreatePacket(self.Address, packet.Header.Source, "" , self.LastSqNumReceived , 1)
            newEvent = CreateEvent('SP', self, newPacket, cp.deepcopy(timestamp) + 0.1)
            ScheduleEvent(newEvent)
        else:
            if self.CongestionStt == self.CongestionSttDict['Slow start']:
                self.SSHandle(packet, cp.deepcopy(timestamp))
            elif self.CongestionStt == self.CongestionSttDict['Congestion avoidance']:
                self.CAHandle(packet, cp.deepcopy(timestamp))
            elif self.CongestionStt == self.CongestionSttDict['Fast recovery']:
                self.FRHandle(packet, cp.deepcopy(timestamp))
            x = self.Address + '___Timestamp:' + str(timestamp)
            x += '___LastSqNumSent:' + str(self.LastSqNumSent) + '___Cwnd:' + str(self.Cwnd)
            x += '___LastSqNumAcked:' + str(self.LastSqNumAcked) + '___nDuplicatedAck:'
            x += str(self.nDuplicatedAck) + '___Threshold:' + str(self.Threshold)
            x += '___Delay:' + str(self.Delay)
            y = {
                'Specifier': self.Address,
                'EventType': 'LI',
                'Timestamp': timestamp,
                'LastSqNumSent': self.LastSqNumSent,
                'Cwnd': self.Cwnd,
                'LastSqNumAcked': self.LastSqNumAcked,
                'nDuplicatedAck': self.nDuplicatedAck,
                'Threshold': self.Threshold
            }
            print x
            self.LogFile.write(json.dumps(y))
            self.LogFile.write('|')
            timestamp += self.Delay
            #self.Delay += 0.5
            if self.LastSqNumAcked == self.nPackets - 1:
                print "Done"
            else:
                n = self.Cwnd - (self.LastSqNumSent - self.LastSqNumAcked)
                if self.LastSqNumSent + 1 + n <= self.nPackets:
                    for sqNumber in range (self.LastSqNumSent + 1, self.LastSqNumSent + 1 + n):
                        timestamp += 0.1
                        newEvent = CreateEvent('SP', self, self.Buffer[sqNumber], cp.deepcopy(timestamp))
                        ScheduleEvent(newEvent)
                    self.LastSqNumSent = self.LastSqNumSent + n
                else:
                    for sqNumber in range (self.LastSqNumSent + 1, self.nPackets):
                        newEvent = CreateEvent('SP', self, self.Buffer[sqNumber], cp.deepcopy(timestamp))
                        timestamp += 0.1
                        ScheduleEvent(newEvent)
                        self.LastSqNumSent = self.nPackets - 1
        
    def Recv(self, packet, timestamp):
        self.Process(packet, timestamp)

    def CheckTimeout(self, prevLastSqNumAcked, timestamp):
        '''
        '''
        if self.LastSqNumAcked == prevLastSqNumAcked:
            newEvent = CreateEvent('TO', self, self.LastSqNumAcked, timestamp)
            print 'time out'
            LogEvent(self.Address, newEvent)
            self.Threshold = self.Cwnd / 2
            self.Cwnd = 1
            self.DuplicatedAck = 0
            self.LastSqNumSent = self.LastSqNumAcked
            
            

    def CheckCongestion(self):
        ''' Check if cwnd >= Threshold
        '''
        if self.Cwnd >= self.Threshold:
            self.CongestionStt = self.CongestionSttDict['Congestion avoidance']

    def SSHandle(self, packet, timestamp):
        ''' Handle ACK packet if sender is in slow start state
        '''
        #print 'SS'
        if self.LastSqNumAcked < packet.Header.SqNumber:
            self.nDuplicatedAck = 0
            self.LastSqNumAcked = packet.Header.SqNumber
            self.Cwnd += 1
            self.CheckCongestion()
        else:
            self.nDuplicatedAck += 1
            if self.nDuplicatedAck == 3:
                self.Threshold = int(self.Cwnd/2)
                self.Cwnd = self.Threshold + 3
                self.CongestionStt = self.CongestionSttDict['Fast recovery']
                #print 'SS -> FR'
                self.nDuplicatedAck = 0
                self.LastSqNumSent = self.LastSqNumAcked
        

    def CAHandle(self, packet, timestamp):
        ''' Handle ACK packet if sender is in congestion avoidance state
        '''
        #print 'CA'
        if self.LastSqNumAcked < packet.Header.SqNumber:
            self.nDuplicatedAck = 0
            self.LastSqNumAcked = packet.Header.SqNumber
            self.Cwnd += 1/self.Cwnd
        else:
            self.nDuplicatedAck += 1
            if self.nDuplicatedAck == 3:
                self.Threshold = int(self.Cwnd/2)
                self.Cwnd = self.Threshold + 3
                self.CongestionStt = self.CongestionSttDict['Fast recovery']
                #print 'CA -> FR'
                self.nDuplicatedAck = 0
                self.LastSqNumSent = self.LastSqNumAcked

    def FRHandle(self, packet, timestamp):
        ''' Handle ACK packet if sender is in congestion fast recovery state'
        '''
        #print 'FR'
        if self.LastSqNumAcked < packet.Header.SqNumber:
            self.nDuplicatedAck = 0
            self.LastSqNumAcked = packet.Header.SqNumber
            self.Threshold = int(self.Cwnd/2)
            self.Cwnd = 1
            self.CongestionStt = self.CongestionSttDict['Congestion avoidance']
            #print 'FR -> CA'
        else:
            self.Cwnd = self.Cwnd + 1
            self.LastSqNumSent = self.LastSqNumAcked
            self.nDuplicatedAck += 1

''' ============================== MAIN PROGRAM ============================ '''
manager = Manager()
dispatcher = Dispatcher()
if __name__ == '__main__':
    p = Thread(target=dispatcher.mainLoop)
    p.start()
    
''' Bootstrap event: node1 send nothing to node4
'''
manager.Nodes['A'].NodeSend('Something', 'B', 0)
