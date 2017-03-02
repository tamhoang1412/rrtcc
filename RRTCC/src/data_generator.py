import packet as pk


class MultimediaDataGenerator:
    def __init__(self, source_add):
        self.source_add = source_add
    
    
    def gen_RTP_packet(self, dest_add, sq_num, timestamp):
        return pk.RTP(self.source_add, dest_add, sq_num, timestamp)