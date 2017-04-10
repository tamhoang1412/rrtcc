import json
import matplotlib.pyplot as plt

filename = '\log_17.txt'
f = open('D:\SimulationResults' + filename, 'r')
log_string = f.read()
f.close()
log = json.loads(log_string)

packets = []
send_time = []
receive_time = []

A_arr = []
As_arr = []
Ar_arr = []
A_time = []

#jitter = log['jitter']
m = []
del_val_th_index = []
del_val_th = []
lost_ratio = []
lost_ratio_time = []

for i in range(0, len(log['lost_ratio'])):
    lost_ratio.append(log['lost_ratio'][i])
    #lost_ratio_time.append(log['lost_ratio'][i])

'''
for i in range(0, len(log['m'])):
    packets.append(i)
    m.append(log['m'][i])
    #send_time.append(log['packets_info'][i][1])
    #receive_time.append(log['packets_info'][i][2])

for i in range(0, len(log['del_val_th'])):
    del_val_th_index.append(i)
    del_val_th.append(log['del_val_th'][i])
    #send_time.append(log['packets_info'][i][1])
    #receive_time.append(log['packets_info'][i][2])
'''
for i in range(0, len(log['A_arr'])):
    A_arr.append(log['A_arr'][i][0])
    A_time.append(log['A_arr'][i][1])
    As_arr.append(log['As_arr'][i])
    Ar_arr.append(log['Ar_arr'][i])

def plot_send_and_receive_time():
    plt.plot(packets, send_time, color="red")
    plt.plot(packets, send_time, 'ro', color="red")
    plt.plot(packets, receive_time, color="blue")
    plt.plot(packets, receive_time, 'ro', color="blue")
    plt.show()

def plot_m():
    plt.plot(packets, m, color="red")
    plt.plot(packets, m, 'ro', color="red")
    plt.show()

def plot_del_val_th():
    plt.plot(del_val_th_index, del_val_th, color="blue")
    plt.plot(del_val_th_index, del_val_th, 'ro', color="blue")
    plt.show()

'''
def plot_jitter():
    plt.plot(packets, jitter, color="yellow")
    plt.plot(packets, jitter, 'ro', color="yellow")
    plt.show()
'''

def plot_bandwidth():
    fig = plt.figure()
    plt.plot(A_time, As_arr, color="black", linestyle="-", label="As")
    plt.plot(A_time, Ar_arr, color="red", label="Ar")
    plt.plot(A_time, A_arr, 'ro', color="yellow", label="A")
    fig.suptitle("Estimated bandwidth " + filename, fontsize=20)
    plt.xlabel("Time(s)")
    plt.ylabel("Value(bit/s)")
    plt.legend()
    plt.show()


def plot_lost_ratio():
    plt.plot(A_time, lost_ratio, color="green")
    plt.plot(A_time, lost_ratio, 'ro', color="green")
    plt.xlabel("Time(s)")
    plt.ylabel("Loss ratio")
    plt.show()

#plot_bandwidth()
#plot_send_and_receive_time()
plot_lost_ratio()
#plot_jitter()
#plot_del_val_th()