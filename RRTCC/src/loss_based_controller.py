class LossBasedController:
    def __init__(self, current_bandwidth):
        self.As_arr = [current_bandwidth]
        self.lost_ratio = [0]


    def compute_lost_ratio(self, env, packets_info, RTP_interval, last_sent_RTP, RTCP_limit, rtcp_timestamp):
        n_lost_pks = 0
        n_unchecked_pks = int((env.now - rtcp_timestamp) / float(RTP_interval))
        begin = last_sent_RTP - RTCP_limit - n_unchecked_pks
        begin = begin if begin > 0 else 0
        end = last_sent_RTP - n_unchecked_pks
        for i in range(begin, end):
            if packets_info[i][0] == 0:
                n_lost_pks += 1
        p = n_lost_pks / float(end - begin + 1)
        print "loss begin: " + str(begin) + " end: " + str(end) + " rate: " + str(p)
        self.lost_ratio.append(p)
        return p

    def estimate_bandwidth(self, env, packets_info, RTP_interval, last_sent_RTP, RTCP_limit, rtcp_timestamp):
        p = self.compute_lost_ratio(env, packets_info, RTP_interval, last_sent_RTP, RTCP_limit, rtcp_timestamp)
        last_As = self.As_arr[-1]
        As = last_As
        if p > 0.1:
            As = last_As * (1 - 0.5*p)
        elif p >= 0.02:
            '''Do nothing'''
        else:
            As = last_As * 1.05 + 1000
        self.As_arr.append(As)
        return As
