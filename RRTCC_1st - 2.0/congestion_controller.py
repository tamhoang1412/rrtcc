import loss_based_controller
import delay_based_controller
'''=========================================================================='''

class GCC_controller:
    def __init__(self):
        '''Constant'''
        self.gamma_1 = [12.5] #ms
        self.gamma_2 = 10 #ms
        self.K_u = 0.01
        self.K_d = 0.00018
        self.alpha = 0.85
        self.T = 0.5
        
        self.A_arr = [(self.current_bandwidth, 0)]
        self.lb_controller = loss_based_controller()
        self.dl_controller = delay_based_controller()

    def adjust_RTP_sending_rate(self, env, RTCP_packet):
        As = self.loss_based_controller.estimate_bandwidth(env, rtcp_timestamp, packets_info, m, gamma_1, last_received_RTP, RTCP_limit, RTP_packet_size)
        Ar = self.delay_based_controller.estimate_bandwidth(env, packets_info, RTP_interval, last_sent_RTP, RTCP_limit, rtcp_timestamp)
        print 'As:' + str(As) + ' Ar:' + str(Ar)
        self.current_bandwidth = As if As < Ar else Ar
        self.A_arr.append((self.current_bandwidth, env.now))
        self.RTP_sending_rate = self.current_bandwidth * self.rate_bandwidth_relation
        self.RTP_interval = 1 / (self.RTP_sending_rate / self.RTP_packet_size)
        print 'current bandwidth:' + str(self.current_bandwidth)
        print 'RTP interval:' + str(self.RTP_interval)
        self.last_time_update_estimated_bandwidth = env.now
        return

'''=========================================================================='''