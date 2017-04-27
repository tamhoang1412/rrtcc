import simpy
from manager import Manager
from application import RTPAplication
from congestion_controller import GccController, NonsenseCongestionController
import os, json


'''=========================================================================='''
def log_data():
    print ("log data.")
    version = "11"
    filename = "D:/SimulationResults/log_thesis_" + version +".txt"
    fo = open(filename, "wb")
    x = {
        'A_arr': sender.congestion_controller.A_arr,
        'Ar_arr': sender.congestion_controller.db_controller.Ar_arr,
        'As_arr': sender.congestion_controller.lb_controller.As_arr,
        'lost_ratio': sender.congestion_controller.lb_controller.lost_ratio,
        'R': sender.congestion_controller.db_controller.R_arr,
        'm': sender.congestion_controller.m,
        'del_val_th': sender.congestion_controller.db_controller.del_var_th,
        'lambda_outs_index': sender.network.lambda_outs_indexes
    }
    fo.write(json.dumps(x))
    fo.close()
    filename = "D:/SimulationResults/log_thesis_" + version + "_para.txt"
    fo = open(filename, "wb")
    x = {
        'RTP_packets_num': sender.RTP_packets_num,
        'Initial_RTP_interval': sender.initial_RTP_interval,
        'T': sender.congestion_controller.db_controller.T,
        'RTCP_interval': sender.RTCP_interval,
        'RTCP_limit': sender.RTCP_limit,
        'LOSS_THRESHOLD': manager.network.NORMAL_LOSS_THRESHOLD,
        'DELAY_MEAN': manager.network.NETWORK_NOISE_MEAN,
        'DELAY_VARIANCE': manager.network.NETWORK_NOISE_DEVIATION,
        'HOLD_TIME': sender.congestion_controller.db_controller.HOLD_TIME,
        'Rate_bandwidth_relation': sender.congestion_controller.rate_bandwidth_relation,
        'alpha': sender.congestion_controller.db_controller.alpha,
        'lambda_out_interval': sender.network.lambda_out_interval,
        'lambda_outs': sender.network.lambda_outs

    }
    fo.write(json.dumps(x))
    fo.close()

'''=========================================================================='''

SIM_TIME = 1500

env = simpy.Environment()
manager = Manager()

'''Create sender and add it to the manager'''
sender_address = 'A'
sender = RTPAplication(sender_address)
Gcc_controller = GccController(sender.current_bandwidth, sender.RTP_packets_num)
UDP_controller = NonsenseCongestionController(sender.current_bandwidth, sender.RTP_packets_num)
#sender.congestion_controller = UDP_controller
sender.congestion_controller = Gcc_controller
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
log_data()
