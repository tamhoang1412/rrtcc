class Packet(object):
    def __init__(self, source_add, dest_add, timestamp):
        self.source_address = source_add
        self.dest_address = dest_add
        self.timestamp = timestamp


class RTP(Packet):
    def __init__(self, source_add, dest_add, sq_num, timestamp):
        super(RTP, self).__init__(source_add, dest_add, timestamp)
        self.sq_num = sq_num


class RTCP(Packet):
    def __init__(self, source_add, dest_add, pk_type, timestamp):
        super(RTCP, self).__init__(source_add, dest_add, timestamp)
        self.type = pk_type
        #for sender report and receiver report
        self.fraction_lost = 0
        #for transport-wide feedback message
        self.fb_sq_num = 0
        self.sq_num_vector = None
        self.base_transport_sq_num = 0
