from pykalman import KalmanFilter
import numpy as np
from loss_based_controller import LossBasedController
from delay_based_controller import DelayBasedController
from abc import abstractmethod


class CongestionController(object):
    def __init__(self, initial_bandwidth, max_num_packets):
        self.initial_bandwidth = initial_bandwidth
        self.max_num_packets = max_num_packets
        self.rate_bandwidth_relation = 1
        self.packets_info = [[0, 0, 0] for i in range(0, max_num_packets)]
        ''' (a, b, c)
                   a: status: 1 for arriving on time, 2 for late, 0 for missing
                   b: sent time
                   c: received time '''
        self.A_arr = [(initial_bandwidth, 0)]
        self.lb_controller = LossBasedController(initial_bandwidth)
        self.db_controller = DelayBasedController(initial_bandwidth)
        self.d = [0 for i in range(0, max_num_packets)]
        self.m = [0 for i in range(0, max_num_packets)]


    @abstractmethod
    def update_packets_info(self, rtcp_pk):
        '''

        :param rtcp_pk:
        :return:
        '''


    @abstractmethod
    def adjust_RTP_sending_rate(self, env, RTCP_packet, RTCP_limit, RTP_packet_size, RTP_interval, last_sent_RTP):
        '''
        :param env:
        :param RTCP_packet:
        :param RTCP_limit:
        :param RTP_packet_size:
        :param RTP_interval:
        :param last_sent_RTP:
        :return:
        '''


class GccController(CongestionController):
    def __init__(self, initial_bandwidth, max_num_packets):
        super(GccController, self).__init__(initial_bandwidth, max_num_packets)
        '''Constant'''
        self.overuse_time_th = 10 #ms
        self.K_u = 0.01
        self.K_d = 0.00018
        self.alpha = 0.85
        self.T = 0.5
        self.last_reported_pk = 0


    def update_packets_info(self, rtcp_pk):
        i = 0
        base_sq = rtcp_pk.base_transport_sq_num
        index = base_sq
        for info in rtcp_pk.sq_num_vector:
            index = base_sq + i
            if info[1] != 0:
                self.packets_info[index][0], self.packets_info[index][2] = info
            else:
                self.packets_info[index][0] = info[0]
            i += 1
            if index > 0:
                if (self.packets_info[index][2] == 0) or (self.packets_info[index-1][2] == 0):
                    self.d[index] = self.d[index - 1]
                else:
                    self.d[index] = (self.packets_info[index][2]-self.packets_info[index-1][2]) - (self.packets_info[index][1]-self.packets_info[index-1][1])
            self.last_received_RTP = index
            if index > 0:
                kf = KalmanFilter(transition_matrices = [1], observation_matrices = [1])
                measurements = np.asarray([self.d[j] for j in range (0, self.last_received_RTP + 1)])
                kf = kf.em(measurements, n_iter=20)
                (filtered_state_means, filtered_state_covariances) = kf.filter(measurements)
                self.m[index] = np.array(filtered_state_means[index])[0]
        self.last_reported_pk = index
        return

    def adjust_RTP_sending_rate(self, env, RTCP_packet, RTCP_limit, RTP_packet_size, RTP_interval, last_sent_RTP):
        As = self.lb_controller.estimate_bandwidth(env, self.packets_info, RTP_interval, last_sent_RTP, RTCP_limit, RTCP_packet.timestamp)
        Ar = self.db_controller.estimate_bandwidth(env, RTCP_packet.timestamp, self.packets_info, self.m, self.last_reported_pk, RTCP_limit, RTP_packet_size)
        print 'As:' + str(As) + ' Ar:' + str(Ar)
        current_bandwidth = As if As < Ar else Ar
        current_bandwidth = 3000000 if current_bandwidth < 3000000 else current_bandwidth
        current_bandwidth = 10000000 if current_bandwidth > 10000000 else current_bandwidth
        self.A_arr.append((current_bandwidth, env.now))
        self.lb_controller.As_arr[-1] = current_bandwidth #bounded As
        RTP_sending_rate = current_bandwidth * self.rate_bandwidth_relation
        return (RTP_sending_rate, current_bandwidth)


class NonsenseCongestionController(CongestionController):
    def __init__(self, initial_bandwidth, max_num_packets):
        super(NonsenseCongestionController, self).__init__(initial_bandwidth, max_num_packets)

    def update_packets_info(self, rtcp_pk):
        i = 0
        base_sq = rtcp_pk.base_transport_sq_num
        index = base_sq
        for info in rtcp_pk.sq_num_vector:
            index = base_sq + i
            if info[1] != 0:
                self.packets_info[index][0], self.packets_info[index][2] = info
            else:
                self.packets_info[index][0] = info[0]
            i += 1
        self.last_reported_pk = index
        return


    def adjust_RTP_sending_rate(self, env = None, RTCP_packet = None, RTCP_limit = 0, RTP_packet_size = 0, RTP_interval = 0, last_sent_RTP = 0):
        self.lb_controller.compute_lost_ratio(env, self.packets_info, RTP_interval, last_sent_RTP, RTCP_limit, RTCP_packet.timestamp)
        self.A_arr.append((self.initial_bandwidth, env.now))
        self.lb_controller.As_arr.append(0)
        self.db_controller.Ar_arr.append(0)
        RTP_sending_rate = self.initial_bandwidth * self.rate_bandwidth_relation
        return (RTP_sending_rate, self.initial_bandwidth)
