import json
import numpy as np
import matplotlib.pyplot as plt

filename_gcc = '\log_thesis_10.txt'
filename_udp = '\log_thesis_09.txt'
f1 = open('D:\SimulationResults' + filename_gcc, 'r')
f2 = open('D:\SimulationResults' + filename_udp, 'r')
log_string_gcc = f1.read()
log_string_udp = f2.read()
f1.close()
f2.close()
log_gcc = json.loads(log_string_gcc)
log_udp = json.loads(log_string_udp)
'''
filename_para_gcc = '\log_thesis_07_para.txt'
filename_para_udp = '\log_thesis_08_para.txt'
f3 = open('D:\SimulationResults' + filename_para_gcc, 'r')
f4 = open('D:\SimulationResults' + filename_para_udp, 'r')
log_string_gcc_para = f3.read()
log_string_udp_para = f4.read()
f3.close()
f4.close()
para_gcc = json.loads(log_string_gcc_para)
para_udp = json.loads(log_string_udp_para)
'''

packets = []
send_time = []
receive_time = []

A_arr_gcc = []
As_arr_gcc = []
Ar_arr_gcc = []
A_time_gcc = []

A_arr_udp = []
A_time_udp = []

#jitter = log['jitter']
m = []
del_val_th_index = []
del_val_th = []
lost_ratio_gcc = []
lost_ratio_udp = []
lambda_outs_index_gcc = []
lambda_outs_index_udp = []
lambda_outs_index_gcc_time = []
lambda_outs_index_udp_time = []

for i in range(0, len(log_gcc['lambda_outs_index'])):
    index = log_gcc['lambda_outs_index'][i]
    lambda_outs_index_gcc.append(index[0])
    lambda_outs_index_gcc_time.append(index[1])


for i in range(0, len(log_udp['lambda_outs_index'])):
    index = log_udp['lambda_outs_index'][i]
    lambda_outs_index_udp.append(index[0])
    lambda_outs_index_udp_time.append(index[1])


for i in range(0, len(log_gcc['lost_ratio'])):
    lost_ratio_gcc.append(log_gcc['lost_ratio'][i])

for i in range(0, len(log_udp['lost_ratio'])):
    lost_ratio_udp.append(log_udp['lost_ratio'][i])

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
for i in range(0, len(log_gcc['A_arr'])):
    A_arr_gcc.append(log_gcc['A_arr'][i][0])
    A_time_gcc.append(log_gcc['A_arr'][i][1])
    As_arr_gcc.append(log_gcc['As_arr'][i])
    Ar_arr_gcc.append(log_gcc['Ar_arr'][i])

for i in range(0, len(log_udp['A_arr'])):
    A_arr_udp.append(log_udp['A_arr'][i][0])
    A_time_udp.append(log_udp['A_arr'][i][1])

'''
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

def plot_jitter():
    plt.plot(packets, jitter, color="yellow")
    plt.plot(packets, jitter, 'ro', color="yellow")
    plt.show()
'''

def plot_bandwidth():
    fig = plt.figure()
    #plt.plot(A_time_gcc, As_arr_gcc, 'r--', color="black", label="As")
    #plt.plot(A_time_gcc, Ar_arr_gcc, 'bs', color="black", label="Ar")


    #plt.plot(A_time_gcc, A_arr_gcc, '--', color="black", label="A (RRTCC)")
    #plt.step(lambda_outs_index_gcc_time, lambda_outs_index_gcc, 'g^', color="black", label='Real bandwidth (RRTCC)')

    plt.plot(A_time_udp, A_arr_udp, '-.', color="black", label="A (UDP)")
    plt.step(lambda_outs_index_udp_time, lambda_outs_index_udp, 'bs', color="black", label='Real bandwidth (UDP)')

    fig.suptitle("Estimated bandwidth " + filename_gcc, fontsize=20)
    plt.xlabel("Time(s)")
    plt.ylabel("Value(bit/s)")
    plt.legend()
    plt.show()


def plot_lost_ratio():
    fig = plt.figure()
    plt.plot(A_time_gcc, lost_ratio_gcc, '-', color="black", label="Loss ratio (RRTCC)")
    plt.plot(A_time_udp, lost_ratio_udp, '--', color="black", label="Loss ratio (UDP)" )
    fig.suptitle("Loss ratio " + filename_gcc, fontsize=20)
    plt.xlabel("Time(s)")
    plt.ylabel("Loss ratio")
    plt.legend()
    plt.show()

#plot_lost_ratio()
plot_bandwidth()
#for p in A_arr: print p
