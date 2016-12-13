import simpy, random
import packet as pk

'''=========================================================================='''

def get_network_delay():
    return 0.1
    #return random.expovariate(10)


def network_fwd(env, packet, dest_address):
    dest = manager.get_element_by_address(dest_address)
    yield env.timeout(get_network_delay())
    env.process(dest.recv(env, packet))

'''=========================================================================='''
    
class application:
    def __init__(self, address):
        self.address = address

        self.in_RTP_session = False
        
        self.RTP_sending_rate = 1
        self.RTP_interval = 1
        self.current_bandwidth = 1
        self.estimated_bandwidth = [self.current_bandwidth]
        self.lost_ratio = [0]
        self.delay_rate = [0]
        
        self.RTCP_interval = 5
        
        self.RTP_packets_num = 50
        self.last_sent_RTP = 0
        self.last_received_RTP = 0
        
        self.RTCP_limit = 10
        self.RTCP_process = None
        
        #for RRTCC
        self.packets_info = [[0, 0, 0] for i in range(0, self.RTP_packets_num)]
        '''
        (a, b, c)
        a: status: 1 for arriving on time, 2 for late, 0 for missing
        b: sent time
        c: received time
        '''
        self.received_pk_list = [[0, 0] for i in range(0, self.RTCP_limit * 2)]
        self.d = [0 for i in range(0, self.RTP_packets_num)]
        self.dL = [0 for i in range(0, self.RTP_packets_num)]
        self.C = [0 for i in range(0, self.RTP_packets_num)]
        self.m = [0 for i in range(0, self.RTP_packets_num)]
        self.v = [0 for i in range(0, self.RTP_packets_num)]


    def send_RTP(self, env, dest_address):
        sq_num = 0
        while sq_num < self.RTP_packets_num:
            RTP_packet = pk.RTP('A', 'B', sq_num, env.now)
            env.process(network_fwd(env, RTP_packet, dest_address))
            self.last_sent_RTP = sq_num
            self.packets_info[sq_num][1] = env.now
            yield env.timeout(self.RTP_interval)
            sq_num += 1
        RTCP_packet = pk.RTCP(self.address, dest_address, 'BYE', env.now)
        env.process(network_fwd(env, RTCP_packet, dest_address))


    


    def send_RTCP(self, env, dest_address, report_type):
        fb_sq_num = 0
        while True:
            try:
                yield env.timeout(self.RTCP_interval)
            except simpy.Interrupt:
                print 'stop RTCP process'
                return
            for i in range (0, self.RTCP_limit):
                self.received_pk_list.append((0, 0))
            rtcp_packet = pk.RTCP(self.address, dest_address, report_type, env.now)
            rtcp_packet.fb_sq_num = fb_sq_num
            rtcp_packet.sq_num_vector, rtcp_packet.base_transport_sq_num = self.get_sq_num_vector_and_base_transport_sq_num()
            try:
                env.process(network_fwd(env, rtcp_packet, dest_address))
            except simpy.Interrupt:
                print 'stop RTCP process'
                return

    def get_sq_num_vector_and_base_transport_sq_num(self):
        base_transport_sq_num = 0
        sq_num_vector = []
        for i in range (self.last_received_RTP - self.RTCP_limit, self.last_received_RTP):
            if self.received_pk_list[i][1] >= (env.now - self.RTCP_interval):
                base_transport_sq_num = i
                break
        for i in range (base_transport_sq_num, self.last_received_RTP + 1):
            sq_num_vector.append(self.received_pk_list[i])
        return (sq_num_vector, base_transport_sq_num)
  

    def recv(self, env, packet):
        '''
        if packet is RTP
        '''
        if isinstance(packet, pk.RTP):
            if not self.in_RTP_session:
                self.in_RTP_session = True
                self.RTCP_process = env.process(self.send_RTCP(env, packet.source_address, 'RR'))
                yield env.timeout(0.0001)
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
            x = self.address + " received RTCP type:" + packet.type + " time:" + str(env.now)
            print packet.base_transport_sq_num
            print repr(packet.sq_num_vector)
            print x
            if packet.type == 'SR':
                self.update_packets_info(packet)
                self.adjust_RTP_sending_rate(packet)
                return
            elif packet.type == 'RR':
                self.update_packets_info(packet)
                self.adjust_RTP_sending_rate(packet)
                return
            elif packet.type == 'BYE':
                if self.RTCP_process != None:
                    try:
                        self.RTCP_process.interrupt()
                    except Exception as err:
                        print err
        return


    def adjust_RTP_sending_rate(self, RTCP_packet):
        p = self.compute_lost_ratio()
        d = self.compute_delay_rate()
        
        if p > 0.1:
            self.current_bandwidth = self.current_bandwidth * (1 - 0.5*p)
        elif p >= 0.02:
            '''
            do nothing
            '''
        else:
            self.current_bandwidth = self.current_bandwidth * 1.05
        self.estimated_bandwidth.append(self.current_bandwidth)
        '''
        need to compate with delay based estimated bandwidth
        '''
        self.RTP_sending_rate = self.current_bandwidth
        self.RTP_interval = 1 / self.RTP_sending_rate
        print 'RTP interval:' + str(self.RTP_interval)
        return


    def compute_lost_ratio(self):
        '''
        Need to deploy
        '''
        return 0.01


    def compute_delay_rate(self):
        '''
        Need to deploy
        '''
        return 0.01


    def update_packets_info(self, rtcp_pk):
        i = 0
        for info in rtcp_pk.sq_num_vector:
            self.packets_info[rtcp_pk.base_transport_sq_num + i][0], self.packets_info[rtcp_pk.base_transport_sq_num + i][2] = info
            i += 1
        return


'''=========================================================================='''

class manager:
    def __init__(self):
        self.nodes = {'A': application('A'), 'B': application('B')}


    def get_element_by_address(self, address):
        return self.nodes[str(address)]

'''=========================================================================='''
SIM_TIME = 100
RANDOM_SEED = 40
MAXIMUM_DELAY = 0.5

manager = manager()
sender = manager.nodes['A']
receiver = manager.nodes['B']
random.seed(RANDOM_SEED)
env = simpy.Environment()
send_RTP_process = env.process(sender.send_RTP(env, receiver.address))
env.run(SIM_TIME)