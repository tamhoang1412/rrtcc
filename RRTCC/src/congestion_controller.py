from loss_based_controller import LossBasedController
from delay_based_controller import DelayBasedController
'''=========================================================================='''

class GccController:
    def __init__(self, current_bandwidth):
        '''Constant'''
        self.del_var_th = [12.5] #ms
        self.overuse_time_th = 10 #ms
        self.K_u = 0.01
        self.K_d = 0.00018
        self.alpha = 0.85
        self.T = 0.5
        self.rate_bandwidth_relation = 0.5
        
        self.A_arr = [(current_bandwidth, 0)]
        self.lb_controller = LossBasedController(current_bandwidth)
        self.db_controller = DelayBasedController(current_bandwidth)


    def adjust_RTP_sending_rate(self, env, RTCP_packet, packets_info, m, last_received_RTP, RTCP_limit, RTP_packet_size, RTP_interval, last_sent_RTP):
        As = self.lb_controller.estimate_bandwidth(env, packets_info, RTP_interval, last_sent_RTP, RTCP_limit, RTCP_packet.timestamp)
        Ar = self.db_controller.estimate_bandwidth(env, RTCP_packet.timestamp, packets_info, m, self.del_var_th, last_received_RTP, RTCP_limit, RTP_packet_size)
        print 'As:' + str(As) + ' Ar:' + str(Ar)
        current_bandwidth = As if As < Ar else Ar
        self.A_arr.append((current_bandwidth, env.now))
        RTP_sending_rate = current_bandwidth * self.rate_bandwidth_relation
        print 'current bandwidth:' + str(current_bandwidth)
        print 'RTP interval:' + str(RTP_interval)
        return (RTP_sending_rate, current_bandwidth)

'''=========================================================================='''