class RTP:
    def __init__(self, source_add, dest_add, sq_num, timestamp):
        self.source_address = source_add
        self.dest_address = dest_add
        self.sq_num = sq_num
        self.timestamp = timestamp
        
        self.SSRC = ""
        self.payload_type = 'MP3'
        
        
class RTCP:
    def __init__(self, source_add, dest_add, pk_type, timestamp):
        self.source_address = source_add
        self.dest_address = dest_add
        self.type = pk_type
        self.timestamp = timestamp
        
        #for sender report and receiver report
        self.fraction_lost = 0
        self.cumulative_num_pk_lost = 0
        self.sender_pk_count = 0
        self.LSR = 0
        
        #for transport-wide feedback message
        self.fb_sq_num = 0
        self.sq_num_vector = None
        self.base_transport_sq_num = 0
        