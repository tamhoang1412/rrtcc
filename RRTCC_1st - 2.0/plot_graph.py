import json
import matplotlib
import matplotlib.pyplot as plt

f = open('D:\log200.05.10.txt', 'r')
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

jitter = log['jitter']
lost_ratio = []
lost_ratio_time = []

for i in range(0, len(log['lost_ratio'])):
    lost_ratio.append(log['lost_ratio'][i][0])
    lost_ratio_time.append(log['lost_ratio'][i][1])

for i in range(0, len(log['packets_info'])):
    packets.append(i)
    send_time.append(log['packets_info'][i][1])
    receive_time.append(log['packets_info'][i][2])

for i in range(0, len(log['A_arr'])):
    A_arr.append(log['A_arr'][i][0])
    A_time.append(log['A_arr'][i][1])
    As_arr.append(log['As_arr'][i][0])
    Ar_arr.append(log['Ar_arr'][i][0])

def plot_send_and_receive_time():
    
    plt.plot(packets, send_time, color="red")
    plt.plot(packets, send_time, 'ro', color="red")
    plt.plot(packets, receive_time, color="blue")
    plt.plot(packets, receive_time, 'ro', color="blue")
    plt.show()


def plot_jitter():
    plt.plot(packets, jitter, color="yellow")
    plt.plot(packets, jitter, 'ro', color="yellow")
    plt.show()


def plot_bandwidth():
    fig = plt.figure()
    plt.plot(A_time, As_arr, color="black", linestyle="-", label="As")
    plt.plot(A_time, Ar_arr, color="red", label="Ar")
    plt.plot(A_time, A_arr, 'ro', color="yellow", label="A")
    fig.suptitle("Estimated bandwidth", fontsize=20)
    plt.xlabel("Time(s)")
    plt.ylabel("Value(bit/s)")
    plt.legend()
    plt.show()


def plot_lost_ratio():
    plt.plot(lost_ratio_time, lost_ratio, color="green")
    plt.plot(lost_ratio_time, lost_ratio, 'ro', color="green")
    plt.show()


plot_bandwidth()
#plot_send_and_receive_time()
#plot_lost_ratio()