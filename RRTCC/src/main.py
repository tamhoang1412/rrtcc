import simpy
from manager import Manager
from application import RTPAplication
import os, json

SIM_TIME = 2000

env = simpy.Environment()
manager = Manager()

'''Create sender and add it to the manager'''
sender_address = 'A'
sender = RTPAplication(sender_address)
manager.add_node(sender)

'''Create receiver and add it to the manager'''
receiver_address = 'B'
receiver = RTPAplication(receiver_address)
manager.add_node(receiver)

sender.add_dest_address(receiver.address)
sender.connect(manager)
receiver.connect(manager)
#env.process(sender.send_RTP(env, receiver.address, network))
sender.start(env)

env.run(SIM_TIME)

'''=========================================================================='''
def log_data():
    os.remove("D:/log.txt")
    fo = open("D:/log.txt", "wb")
    x = {
        'packets_info': sender.packets_info,
        'A_arr': sender.gcc_controller.A_arr,
        'Ar_arr': sender.gcc_controller.db_controller.Ar_arr,
        'As_arr': sender.gcc_controller.lb_controller.As_arr,
        'lost_ratio': sender.gcc_controller.lb_controller.lost_ratio,
        'jitter': sender.d
    }
    fo.write(json.dumps(x))
    fo.close()

