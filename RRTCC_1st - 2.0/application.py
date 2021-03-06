import simpy, random
from pykalman import KalmanFilter
import numpy as np

import packet as pk
from congestion_controller import gcc_controller
from data_generator import multimedia_data_generator
from network import network
    
RANDOM_SEED = 40
MAXIMUM_DELAY = 0.011
TIME_TO_START_RTCP_PROCESS = 0.0001
random.seed(RANDOM_SEED)

class application:
    def __init__(self, address):
        self.address = address
        self.in_RTP_session = False
        self.RTP_packets_num = 500
        self.last_sent_RTP = 0
        self.last_received_RTP = 0
        self.RTP_packet_size = 1200 * 30 * 8 # bits
        self.RTP_interval = 0.5 # 1 packet per RTP_interval
        self.RTP_sending_rate = self.RTP_packet_size  / self.RTP_interval # bit/s
        self.current_bandwidth = self.RTP_packet_size / self.RTP_interval # bit/s (initial estimated bandwidth)
        self.rate_bandwidth_relation = 0.5
        
        self.last_RTCP_sent_time = 0
        self.last_pk_reported = 0
        self.RTCP_interval = 5
        self.RTCP_limit = 30
        self.RTCP_process = None
        self.last_time_update_estimated_bandwidth = 0
        self.packets_info = [[0, 0, 0] for i in range(0, self.RTP_packets_num)]
        ''' (a, b, c)
            a: status: 1 for arriving on time, 2 for late, 0 for missing
            b: sent time
            c: received time
        '''
        self.received_pk_list = [(0, 0) for i in range(0, self.RTCP_limit * 2)]
        self.d = [0 for i in range(0, self.RTP_packets_num)]
        #self.dL = [0 for i in range(0, self.RTP_packets_num)]
        #self.C = [0 for i in range(0, self.RTP_packets_num)]
        self.m = [0 for i in range(0, self.RTP_packets_num)]
        #self.v = [0 for i in range(0, self.RTP_packets_num)]
        
        self.gcc_controller = gcc_controller()
        self.data_generator = multimedia_data_generator(self.address)

    '''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''

    def send_RTP(self, env, dest_add, network):
        sq_num = 0
        while sq_num < self.RTP_packets_num:
            RTP_packet = self.data_generator.gen_RTP_packet(sq_num, dest_add, env.now)
            env.process(network.fwd(env, RTP_packet))
            self.last_sent_RTP = sq_num
            self.packets_info[sq_num][1] = env.now
            yield env.timeout(self.RTP_interval)
            sq_num += 1
        yield env.timeout(3)
        RTCP_packet = pk.RTCP(self.address, dest_add, 'BYE', env.now)
        env.process(network.fwd(env, RTCP_packet))

    '''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''


    def send_RTCP(self, env, dest_address, report_type):
        fb_sq_num = 0
        while True:
            try:
                yield env.timeout(self.RTCP_interval)
            except simpy.Interrupt:
                print 'Stop RTCP process'
                return
            for i in range (0, self.RTCP_limit):
                self.received_pk_list.append((0, 0))
            rtcp_packet = pk.RTCP(self.address, dest_address, report_type, env.now)
            rtcp_packet.fb_sq_num = fb_sq_num
            rtcp_packet.sq_num_vector, rtcp_packet.base_transport_sq_num = self.get_sq_num_vector_and_base_transport_sq_num()
            try:
                env.process(network.fwd(env, rtcp_packet))
            except simpy.Interrupt:
                print 'Stop RTCP process'
                return


    def get_sq_num_vector_and_base_transport_sq_num(self, env):
        base_transport_sq_num = self.last_pk_reported + 1
        sq_num_vector = []
        for i in range (self.last_pk_reported + 1, self.last_received_RTP):
            if self.received_pk_list[i][1] >= (self.last_RTCP_sent_time):
                base_transport_sq_num = i
                break
            base_transport_sq_num += 1
        for i in range (base_transport_sq_num, self.last_received_RTP + 1):
            sq_num_vector.append(self.received_pk_list[i])
        self.last_pk_reported = self.last_received_RTP
        self.last_RTCP_sent_time = env.now
        return (sq_num_vector, base_transport_sq_num)

    '''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''


    def recv(self, env, packet):
        '''if packet is RTP'''
        if isinstance(packet, pk.RTP):
            if not self.in_RTP_session:
                self.in_RTP_session = True
                self.RTCP_process = env.process(self.send_RTCP(env, packet.source_address, 'RR'))
                yield env.timeout(TIME_TO_START_RTCP_PROCESS)
            x = self.address + " received " + str(packet.sq_num) + " time:" + str(env.now)
            print x
            self.last_received_RTP = packet.sq_num
            if packet.timestamp < (env.now - MAXIMUM_DELAY):
                self.received_pk_list[packet.sq_num] = (2, env.now)
                return
            self.received_pk_list[packet.sq_num] =  (1, env.now)
            return
        '''if packet is RTCP'''
        if isinstance(packet, pk.RTCP):
            x = self.address + " received RTCP type:" + packet.type + " time:" + str(env.now) + ' timestamp:' + str(packet.timestamp)
            print x
            print packet.base_transport_sq_num
            print repr(packet.sq_num_vector)
            if packet.type == 'SR':
                self.update_packets_info(packet)
                self.RTP_sending_rate = self.gcc_controller.adjust_RTP_sending_rate(env, packet)
                return
            elif packet.type == 'RR':
                self.update_packets_info(packet)
                self.RTP_sending_rate = self.gcc_controller.adjust_RTP_sending_rate(env, packet)
                return
            elif packet.type == 'BYE':
                if self.RTCP_process != None:
                    try:
                        self.RTCP_process.interrupt()
                    except Exception as err:
                        print err
        return

    def update_packets_info(self, rtcp_pk):
        i = 0
        base_sq = rtcp_pk.base_transport_sq_num
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
        return
'''=========================================================================='''

