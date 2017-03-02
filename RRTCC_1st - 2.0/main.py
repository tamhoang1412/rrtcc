import simpy
from manager import manager
import os, json

SIM_TIME = 2000


'''=========================================================================='''    
manager = manager()
sender = manager.nodes['A']
receiver = manager.nodes['B']

env = simpy.Environment()
send_RTP_process = env.process(sender.send_RTP(env, receiver.address))
env.run(SIM_TIME)

'''=========================================================================='''
def log_data():
    os.remove("D:/log.txt")
    fo = open("D:/log.txt", "wb")
    x = {
        'packets_info': sender.packets_info,
        'A_arr': sender.A_arr,
        'Ar_arr': sender.Ar_arr,
        'As_arr': sender.As_arr,
        'lost_ratio': sender.lost_ratio,
        'delay_rate': sender.delay_rate,
        'jitter': sender.d
    }
    fo.write(json.dumps(x))
    fo.close()

