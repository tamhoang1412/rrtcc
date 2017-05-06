import simpy
from manager import Manager
from application import RTPAplication
from congestion_controller import GccController, NonsenseCongestionController
import os, json


def log_data():
    print ("log data.")
    filename = "D:/SimulationResults/log_thesis_udp_" + version +".txt"
    fo = open(filename, "wb")
    x = {
        'A_arr': sender.congestion_controller.A_arr,
        'Ar_arr': sender.congestion_controller.db_controller.Ar_arr,
        'As_arr': sender.congestion_controller.lb_controller.As_arr,
        'lost_ratio': sender.congestion_controller.lb_controller.lost_ratio,
        'R': sender.congestion_controller.db_controller.R_arr,
        'm': sender.congestion_controller.m,
        'del_val_th': sender.congestion_controller.db_controller.del_var_th,
        'lambda_outs_index': sender.network.lambda_outs_indexes,
        'lambda_outs': sender.network.lambda_outs,
        'lambda_out_interval': sender.network.lambda_out_interval,
        'packets_info': sender.congestion_controller.packets_info,
        'received_pk_list': receiver.received_pk_list
    }
    fo.write(json.dumps(x))
    fo.close()
    filename = "D:/SimulationResults/log_thesis_udp_" + version + "_para.txt"
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
        'lambda_outs': sender.network.lambda_outs,
        'lambda_out_interval': sender.network.lambda_out_interval,
        'coef': sender.network.available_bandwidth_coef,
        'maximum_sending_rate': sender.congestion_controller.maximum_sending_rate,
        'minimum_sending_rate': sender.congestion_controller.minimum_sending_rate
    }
    fo.write(json.dumps(x))
    fo.close()

network_coef = [
    [0, 5, 10, 15],
    [0, 10, 15, 20],
    [0, 15, 20, 25],
    [0, 20, 25, 35]
]
for i in range(10, 14):
    version = str(i)
    SIM_TIME = 1000
    env = simpy.Environment()
    manager = Manager(network_coef[i-10])
    '''Create sender and add it to the manager'''
    sender_address = 'A'
    sender = RTPAplication(sender_address)
    Gcc_controller = GccController(sender.current_bandwidth, sender.RTP_packets_num)
    UDP_controller = NonsenseCongestionController(sender.current_bandwidth, sender.RTP_packets_num)
    sender.congestion_controller = UDP_controller
    manager.add_node(sender)

    '''Create receiver and add it to the manager'''
    receiver_address = 'B'
    receiver = RTPAplication(receiver_address)
    manager.add_node(receiver)

    sender.add_dest_address(receiver.address)
    sender.connect(manager)
    receiver.connect(manager)
    sender.network.generate_lambda_outs()
    sender.start(env)

    env.run(SIM_TIME)
    log_data()
