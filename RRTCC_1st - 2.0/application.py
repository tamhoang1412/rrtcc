import simpy, random
import numpy as np
from pykalman import KalmanFilter
import matplotlib.pyplot as plt
import math
import os, json

import packet as pk

'''=========================================================================='''

def get_network_delay():
    mean = 0.01
    sigma = 0.001
    #gen random delay for network link
    delay = np.random.normal(mean, sigma)
    if delay < 0:
        delay = mean
    return delay


def network_fwd(env, packet, dest_address):
    loss_probability = np.random.uniform(0.0, 1.0)
    if loss_probability < LOSS_THRESHOLD:
        return
    dest = manager.get_element_by_address(dest_address)
    yield env.timeout(get_network_delay())
    env.process(dest.recv(env, packet))

    '''=========================================================================='''
    
class application:
    def __init__(self, address):
        self.address = address
        
        self.in_RTP_session = False
        #for RRTCC
        self.state = 'I' # 3 kinds of state, I for increase, D for decrease, N for hold state
        self.RTP_packets_num = 500
        self.last_sent_RTP = 0
        self.last_received_RTP = 0
        self.RTP_packet_size = 1200 * 30 * 8 # bits
        self.RTP_interval = 0.5 # 1 packet per RTP_interval
        self.RTP_sending_rate = self.RTP_packet_size  / self.RTP_interval # bit/s
        
        self.current_bandwidth = self.RTP_packet_size / self.RTP_interval # bit/s (initial estimated bandwidth)
        self.rate_bandwidth_relation = 0.5
        self.A_arr = [(self.current_bandwidth, 0)]
        self.Ar_arr = [(self.current_bandwidth, 0)]
        self.As_arr = [(self.current_bandwidth, 0)]
        self.R_arr = []
        self.R_mean = []
        self.R_deviation = []
        
        self.lost_ratio = [(0, 0)]
        self.delay_rate = [(0, 0)]
        self.last_RTCP_sent_time = 0
        self.last_pk_reported = 0
        self.RTCP_interval = 5
        self.RTCP_limit = 30
        self.RTCP_process = None
        self.last_time_update_estimated_bandwidth = 0
        self.packets_info = [[0, 0, 0] for i in range(0, self.RTP_packets_num)]
        '''
        (a, b, c)
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
        
        '''Constant'''
        self.gamma_1 = [12.5] #ms
        self.gamma_2 = 10 #ms
        self.K_u = 0.01
        self.K_d = 0.00018
        self.alpha = 0.85
        self.T = 0.5

    '''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''

    def send_RTP(self, env, dest_address):
        sq_num = 0
        while sq_num < self.RTP_packets_num:
            RTP_packet = pk.RTP('A', 'B', sq_num, env.now)
            env.process(network_fwd(env, RTP_packet, dest_address))
            self.last_sent_RTP = sq_num
            self.packets_info[sq_num][1] = env.now
            yield env.timeout(self.RTP_interval)
            sq_num += 1
        yield env.timeout(3)
        RTCP_packet = pk.RTCP(self.address, dest_address, 'BYE', env.now)
        env.process(network_fwd(env, RTCP_packet, dest_address))    


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
                env.process(network_fwd(env, rtcp_packet, dest_address))
            except simpy.Interrupt:
                print 'Stop RTCP process'
                return


    def get_sq_num_vector_and_base_transport_sq_num(self):
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
        '''
        if packet is RTP
        '''
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
        '''
        if packet is RTCP
        '''
        if isinstance(packet, pk.RTCP):
            x = self.address + " received RTCP type:" + packet.type + " time:" + str(env.now) + ' timestamp:' + str(packet.timestamp)
            print x
            print packet.base_transport_sq_num
            print repr(packet.sq_num_vector)
            if packet.type == 'SR':
                self.update_packets_info(packet)
                self.adjust_RTP_sending_rate(env, packet)
                return
            elif packet.type == 'RR':
                self.update_packets_info(packet)
                self.adjust_RTP_sending_rate(env, packet)
                return
            elif packet.type == 'BYE':
                if self.RTCP_process != None:
                    try:
                        self.RTCP_process.interrupt()
                    except Exception as err:
                        print err
        return


    def adjust_RTP_sending_rate(self, env, RTCP_packet):        
        As = self.lossbased_control_estimated_bandwidth(env, RTCP_packet.timestamp)
        Ar = self.delaybased_control_estimated_bandwidth(env, RTCP_packet.timestamp)
        print 'As:' + str(As) + ' Ar:' + str(Ar)
        self.current_bandwidth = As if As < Ar else Ar
        self.As_arr.append((self.current_bandwidth, env.now))
        self.A_arr.append((self.current_bandwidth, env.now))
        self.RTP_sending_rate = self.current_bandwidth * self.rate_bandwidth_relation
        self.RTP_interval = 1 / (self.RTP_sending_rate/self.RTP_packet_size)
        print 'current bandwidth:' + str(self.current_bandwidth)
        print 'RTP interval:' + str(self.RTP_interval)
        self.last_time_update_estimated_bandwidth = env.now
        return


    def lossbased_control_estimated_bandwidth(self, env, rtcp_timestamp):
        n_lost_pks = 0
        n_unchecked_pks = int((env.now - rtcp_timestamp)/float(self.RTP_interval))
        begin = self.last_sent_RTP - self.RTCP_limit - n_unchecked_pks
        begin = begin if begin > 0 else 0
        for i in range (begin, self.last_sent_RTP - n_unchecked_pks):
            if self.packets_info[i][0] == 0: 
                n_lost_pks += 1
        p = n_lost_pks / float(self.RTCP_limit)
        self.lost_ratio.append((p, env.now))
        last_As = self.As_arr[-1][0]
        As = last_As
        if p > 0.1:
            As = last_As * (1 - 0.5*p)
        elif p >= 0.02:
            '''Do nothing'''
        else:
            As = last_As * 1.05 + 1000
        return As


    def delaybased_control_estimated_bandwidth(self, env, rtcp_timestamp):
        self.update_gamma_1()
        self.update_state()
        R = self.compute_incoming_bitrate()
        print 'R: ' + str(R) 
        self.R_arr.append(R)
        last_Ar = self.Ar_arr[-1][0]
        Ar = last_Ar
        if self.state == 'I':
            increase_state = self.get_increase_state()
            time_since_last_update_ms = (env.now - self.last_time_update_estimated_bandwidth)*1000
            if increase_state == "multiplicative":
                eta = 1.08**min(time_since_last_update_ms / 1000, 1.0)
                Ar = eta * last_Ar
            else:
                rtt_ms = 2 * (self.packets_info[self.last_received_RTP][2] - self.packets_info[self.last_received_RTP][1])*1000
                bits_per_frame = last_Ar / 30                
                packets_per_frame = math.ceil(bits_per_frame / (1200 * 8))
                avg_packet_size_bits = bits_per_frame / packets_per_frame
                expected_packet_size_bits = avg_packet_size_bits
                response_time_ms = 100 + rtt_ms
                beta = 0.5 * min(time_since_last_update_ms / response_time_ms, 1.0)
                Ar = last_Ar + max(1000, beta * expected_packet_size_bits)
            if Ar > 1.5 * R:
                Ar = 1.5 * R
        elif self.state == 'D':
            Ar = 0.85 * R
        else:
            '''
            Hold state, do nothing
            '''
        self.Ar_arr.append((Ar, env.now))
        return Ar


    def update_gamma_1(self):
        i = self.last_received_RTP
        if abs(self.m[i]) - self.gamma_1[-1] < 15:
            if abs(self.m[i]) > self.gamma_1[-1]:
                self.gamma_1.append(self.gamma_1[-1] + (self.packets_info[i][2]-self.packets_info[i-1][2]) * self.K_d * (abs(self.m[i])-self.gamma_1[-1]))
            else:
                self.gamma_1.append(self.gamma_1[-1] + (self.packets_info[i][2]-self.packets_info[i-1][2]) * self.K_u * (abs(self.m[i])-self.gamma_1[-1]))
        return
    

    def update_state(self):
        signal = self.get_signal()
        print "state: " + str(self.state) + "signal: " + str(signal)
        '''STATE  H: Hold        I: Increase    D: Decrease'''
        '''SIGNAL O: Overuse     U: Underuse    N: Normal'''
        if self.state == 'H':
            if signal == 'O':
                self.state = 'D'
            elif signal == 'N':
                self.state == 'I'
            else:
                return
        elif self.state == 'I':
            if signal == 'O':
                self.state = 'D'
            elif signal == 'N':
                return
            else:
                self.state == 'H'
        else:
            if signal == 'O':
                return
            elif signal == 'N':
                self.state = 'H'
            else:
                self.state = 'H'
        return


    def get_signal(self):
        i = self.last_received_RTP
        if self.m[i] < self.m[i-1]:
            signal = 'U'
        elif self.m[i] > self.gamma_1[-1] or self.m[i] > self.gamma_2:
            signal = 'O'
        else:
            signal = 'N'
        return signal


    def get_increase_state(self):
        alpha = 0.95
        R = self.R_arr[-1]
        if len(self.R_arr) == 1:
            self.R_deviation.append(0)
            self.R_mean.append(self.R_arr[0])
        else:
            self.R_mean.append((1-alpha)*self.R_mean[-1] + alpha*R)
            self.R_deviation.append((1-alpha)*(self.R_mean[-1] + alpha*(R - self.R_mean[-2])))
        mean = self.R_mean[-1]
        devitation = self.R_deviation[-1]
        if (abs(mean - R) < 3*devitation):
            print "additive"
            return "additive"
        print "multiplicative"
        return "multiplicative"


    def compute_incoming_bitrate(self):
        N = 0
        begin = self.last_received_RTP - self.RTCP_limit
        begin = begin if begin > 0 else 0
        for i in range (begin, self.last_received_RTP + 1):
            if self.packets_info[i][2] >= (self.packets_info[self.last_received_RTP][2] - self.T):
                N += 1
        if N == 0:
            R = 999999
        else:
            R = (self.RTP_packet_size * N) / float(self.T)
        return R


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

class manager:
    def __init__(self):
        self.nodes = {'A': application('A'), 'B': application('B')}


    def get_element_by_address(self, address):
        return self.nodes[str(address)]

'''=========================================================================='''

manager = manager()
sender = manager.nodes['A']
receiver = manager.nodes['B']

'''=========================================================================='''

SIM_TIME = 2000
RANDOM_SEED = 40
MAXIMUM_DELAY = 0.011
LOSS_THRESHOLD = 0.001
TIME_TO_START_RTCP_PROCESS = 0.0001

random.seed(RANDOM_SEED)

'''=========================================================================='''    
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

