'''=========================================================================='''

class RTP:
    def __init__(self, source_add, dest_add, sq_num, timestamp):
        self.source_address = source_add
        self.dest_address = dest_add
        self.sq_num = sq_num
        self.timestamp = timestamp

'''=========================================================================='''
        
class RTCP:
    def __init__(self, source_add, dest_add, pk_type, timestamp):
        self.source_address = source_add
        self.dest_address = dest_add
        self.type = pk_type
        self.timestamp = timestamp
        
        #for sender report and receiver report
        self.fraction_lost = 0
    
        #for transport-wide feedback message
        self.fb_sq_num = 0
        self.sq_num_vector = None
        self.base_transport_sq_num = 0

'''=========================================================================='''

