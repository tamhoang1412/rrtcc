import json
import matplotlib.pyplot as plt

f = open('D:\log1000.txt', 'r')
logRaw = f.read()
f.close()

logJsonArr = logRaw.split('|')[:-1]
logDictArr = []

for log in logJsonArr:
    logDictArr.append(json.loads(log))

SPArr = []
SPTimeArr = []

RPArr = []
RPTimeArr = []

CTOArr = []
CTOTimeArr = []

CwndArr = []
CwndTimeArr = []

LastSentArr = []
LastSentTimeArr = []

LastAckedArr = []
LastAckedTimeArr = []

ThresholdArr = []
ThresholdTimeArr = []

for log in logDictArr:
    #print log['Timestamp']
    if log['EventType'] == 'SP':
        '''
        '''
        SPArr.append(log['Data']['SqNumber'])
        SPTimeArr.append(log['Timestamp'])
    elif log['EventType'] == 'RP':
        '''
        '''
        RPArr.append(log['Data']['SqNumber'])
        RPTimeArr.append(log['Timestamp'])
    elif log['EventType'] == 'CTO':
        '''
        '''
        CTOArr.append(log['Data'])
        CTOTimeArr.append(log['Timestamp'])
        
    elif log['EventType'] == 'LI':
        '''
        '''
        #print log['Timestamp']
        #print log['Cwnd']
        
        CwndArr.append(log['Cwnd'])
        CwndTimeArr.append(log['Timestamp'])
        
        LastSentArr.append(log['LastSqNumSent'])
        LastSentTimeArr.append(log['Timestamp'])
        
        LastAckedArr.append(log['LastSqNumAcked'])
        LastAckedTimeArr.append(log['Timestamp'])
        
        ThresholdArr.append(log['Threshold'])
        ThresholdTimeArr.append(log['Timestamp'])
        #print log['Threshold']       

'''
plt.plot(SPTimeArr, SPArr, color="red")
plt.plot(SPTimeArr, SPArr, 'ro', color="red")

plt.plot(RPTimeArr, RPArr, color="blue")
plt.plot(RPTimeArr, RPArr, 'ro', color="blue")

plt.plot(CTOTimeArr, CTOArr, color="green")
plt.plot(CTOTimeArr, CTOArr, 'ro', color="green")

plt.plot(ThresholdTimeArr, ThresholdArr, color='pink')
plt.plot(ThresholdTimeArr, ThresholdArr, 'ro', color='pink')

plt.plot(CwndTimeArr, CwndArr, color='orange')
plt.plot(CwndTimeArr, CwndArr, 'ro', color='orange')

plt.plot(LastSentTimeArr, LastSentArr, color="brown")
plt.plot(LastSentTimeArr, LastSentArr, 'ro', color="brown")

plt.plot(LastAckedTimeArr, LastAckedArr, color="violet")
plt.plot(LastAckedTimeArr, LastAckedArr, 'ro', color="violet")

'''
plt.plot(SPTimeArr, SPArr, color="red")
plt.plot(SPTimeArr, SPArr, 'ro', color="red") 
plt.plot(CwndTimeArr, CwndArr, color='orange')
plt.plot(CwndTimeArr, CwndArr, 'ro', color='orange')

#plt.axis([0, 1900, 0, 510])
plt.show()