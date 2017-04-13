import simpy

import packet as pk
from congestion_controller import GccController
from data_generator import MultimediaDataGenerator

class RTPAplication:
    def __init__(self, address):
        self.MAXIMUM_DELAY = 0.011
        self.TIME_TO_START_RTCP_PROCESS = 0.0001

        self.address = address
        self.dest_address = None

        self.in_RTP_session = False
        self.RTP_packets_num = 500
        self.last_sent_RTP = 0
        self.last_received_RTP = 0
        self.RTP_packet_size = 1200 * 30 * 8 # bits ~ 3600 bytes
        self.initial_RTP_interval = 0.1
        self.RTP_interval = self.initial_RTP_interval # 1 packet per RTP_interval
        self.RTP_sending_rate = self.RTP_packet_size  / self.RTP_interval # bit/s
        self.current_bandwidth = self.RTP_packet_size / self.RTP_interval # bit/s (initial estimated bandwidth)S
        self.last_RTCP_sent_time = 0
        self.last_pk_reported = 0
        self.RTCP_interval = 3
        self.RTCP_limit = 50
        self.RTCP_process = None

        self.received_pk_list = [(0, 0) for i in range(0, self.RTCP_limit * 2)]
        self.congestion_controller = GccController(self.current_bandwidth, self.RTP_packets_num)
        self.data_generator = MultimediaDataGenerator(self.address)

        '''Exceptions'''
        self.manager = None
        self.network = None
        self.env = None

    '''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''

    def add_dest_address(self, dest_add):
        self.dest_address = dest_add


    def connect(self, manager):
        self.manager = manager
        self.network = manager.network
        self.network.lambda_in = self.RTP_sending_rate

    def start(self, env):
        self.env = env
        env.process(self.send_process())
        return


    def send_process(self):
        self.in_RTP_session = True
        sq_num = 0
        while sq_num < self.RTP_packets_num:
            '''Get an RTP packet from a data generator'''
            RTP_packet = self.data_generator.gen_RTP_packet(self.dest_address, sq_num, self.env.now)
            '''Update state variables of RTP engine'''
            self.last_sent_RTP = sq_num
            self.congestion_controller.packets_info[sq_num][1] = self.env.now
            '''Send this RTP packet to network'''
            self.do_send_packet(RTP_packet)
            '''Wait timeout until send the next one'''
            yield self.env.timeout(self.RTP_interval)
            sq_num += 1
        yield self.env.timeout(3)
        self.send_finish_signal()
        self.in_RTP_session = False

    def send_finish_signal(self):
        RTCP_packet = pk.RTCP(self.address, self.dest_address, 'BYE', self.env.now)
        self.do_send_packet(RTCP_packet)

    def do_send_packet(self, packet):
        self.env.process(self.network.fwd(self.env, packet))

    '''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''

    def RTCP_report_process(self, dest_address, report_type):
        fb_sq_num = 0
        while True:
            try:
                yield self.env.timeout(self.RTCP_interval)
            except simpy.Interrupt:
                print 'Stop RTCP process'
                return
            for i in range (0, self.RTCP_limit):
                self.received_pk_list.append((0, 0))
            rtcp_packet = pk.RTCP(self.address, dest_address, report_type, self.env.now)
            rtcp_packet.fb_sq_num = fb_sq_num
            rtcp_packet.sq_num_vector, rtcp_packet.base_transport_sq_num = self.get_sq_num_vector_and_base_transport_sq_num()
            try:
                self.do_send_packet(rtcp_packet)
            except simpy.Interrupt:
                print 'Stop RTCP process'
                return


    def get_sq_num_vector_and_base_transport_sq_num(self):
        base_transport_sq_num = self.last_pk_reported + 1
        sq_num_vector = []
        '''
        for i in range (self.last_pk_reported + 1, self.last_received_RTP):
            if self.received_pk_list[i][1] >= (self.last_RTCP_sent_time):
                base_transport_sq_num = i
                break
            base_transport_sq_num += 1
        '''
        for i in range (base_transport_sq_num, self.last_received_RTP + 1):
            sq_num_vector.append(self.received_pk_list[i])
        self.last_pk_reported = self.last_received_RTP
        self.last_RTCP_sent_time = self.env.now
        return (sq_num_vector, base_transport_sq_num)

    '''++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'''

    def receive_process(self, env, packet):
        self.env = env
        '''if packet is RTP'''
        if isinstance(packet, pk.RTP):
            if not self.in_RTP_session:
                self.in_RTP_session = True
                self.RTCP_process = env.process(self.RTCP_report_process(packet.source_address, 'RR'))
                yield env.timeout(self.TIME_TO_START_RTCP_PROCESS)
            x = self.address + " received " + str(packet.sq_num) + " time:" + str(env.now)
            print x
            self.last_received_RTP = packet.sq_num
            if packet.timestamp < (env.now - self.MAXIMUM_DELAY):
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
                if self.in_RTP_session:
                    self.congestion_controller.update_packets_info(packet)
                    self.RTP_sending_rate, self.current_bandwidth = self.congestion_controller.adjust_RTP_sending_rate(env, packet, self.RTCP_limit, self.RTP_packet_size, self.RTP_interval, self.last_sent_RTP)
                    print ("RTP sending rate " + str(self.RTP_sending_rate))
                    self.RTP_interval = 1 / (self.RTP_sending_rate / self.RTP_packet_size)
                    self.network.lambda_in = self.RTP_sending_rate
                    return
                else:
                    self.send_finish_signal()
            elif packet.type == 'RR':
                if self.in_RTP_session:
                    self.congestion_controller.update_packets_info(packet)
                    self.RTP_sending_rate, self.current_bandwidth = self.congestion_controller.adjust_RTP_sending_rate(env, packet, self.RTCP_limit, self.RTP_packet_size, self.RTP_interval, self.last_sent_RTP)
                    print ("RTP sending rate " + str(self.RTP_sending_rate))
                    self.RTP_interval = 1 / (self.RTP_sending_rate / self.RTP_packet_size)
                    self.network.lambda_in = self.RTP_sending_rate
                    return
                else:
                    self.send_finish_signal()
            elif packet.type == 'BYE':
                if self.RTCP_process != None:
                    try:
                        self.RTCP_process.interrupt()
                    except Exception as err:
                        print err
            self.network.lambda_in = self.RTP_sending_rate
        return



'''=========================================================================='''

