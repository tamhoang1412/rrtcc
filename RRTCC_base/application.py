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
        self.RTCP_interval = 5
        
        self.last_sent_RTP = 0
        self.last_received_RTP = 0
        
        self.RTCP_limit = 10
        self.received_pk_list = {i: 0 for i in range(0, self.RTCP_limit * 2)}
        
        self.RTCP_process = None


    def send_RTP(self, env, dest_address):
        sq_number = 0
        while sq_number < 10:
            RTP_packet = pk.RTP('A', 'B', sq_number, env.timeout)
            env.process(network_fwd(env, RTP_packet, dest_address))
            self.last_sent_RTP = sq_number
            yield env.timeout(self.RTP_interval)
            sq_number += 1
        RTCP_packet = pk.RTCP(self.address, dest_address, 'BYE', env.now)
        env.process(network_fwd(env, RTCP_packet, dest_address))


    def send_RTCP(self, env, dest_address, report_type):
        while True:
            try:
                yield env.timeout(self.RTCP_interval)
            except simpy.Interrupt:
                print 'stop RTCP process'
                return
                
            RTCP_packet = pk.RTCP(self.address, dest_address, report_type, env.now)
            
            try:
                env.process(network_fwd(env, RTCP_packet, dest_address))
            except simpy.Interrupt:
                print 'stop RTCP process'
                return
            

    def adjust_RTP_sending_rate(self, RTCP_packet):
        self.RTP_sending_rate = 2
        self.RTP_interval = 0.5
        '''
        RRTCC or any congestion control algorithm works here
        '''
        return

    def recv(self, env, packet):
        '''
        if packet is RTP
        '''
        if isinstance(packet, pk.RTP):
            if not self.in_RTP_session:
                self.in_RTP_session = True
                self.RTCP_process = env.process(self.send_RTCP(env, packet.source_address, 'RR'))
                yield env.timeout(0.0001)
            x = self.address + " received " + str(packet.sq_number) + " time:" + str(env.now)
            print x
            self.last_received_RTP = packet.sq_number
            if packet.timestamp < (env.now - MAXIMUM_DELAY):
                self.received_pk_list[packet.sq_number] = 2
                return
            self.received_pk_list[packet.sq_number] =  1
            return
        '''
        if packet is RTCP
        '''
        if isinstance(packet, pk.RTCP):
            x = self.address + " received RTCP type:" + packet.type + " time:" + str(env.now)
            print x
            if packet.type == 'SR':
                self.adjust_RTP_sending_rate(packet)
                return
            elif packet.type == 'RR':
                self.adjust_RTP_sending_rate(packet)
                return
            elif packet.type == 'BYE':
                if self.RTCP_process != None:
                    try:
                        self.RTCP_process.interrupt()
                    except Exception as err:
                        print err
        return

'''=========================================================================='''

class manager:
    def __init__(self):
        self.nodes = {'A': application('A'), 'B': application('B')}


    def get_element_by_address(self, address):
        return self.nodes[str(address)]

'''=========================================================================='''
SIM_TIME = 20
RANDOM_SEED = 40
MAXIMUM_DELAY = 0.5

manager = manager()
sender = manager.nodes['A']
receiver = manager.nodes['B']
random.seed(RANDOM_SEED)
env = simpy.Environment()
send_RTP_process = env.process(sender.send_RTP(env, receiver.address))
env.run(SIM_TIME)