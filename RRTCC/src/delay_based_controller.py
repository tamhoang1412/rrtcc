import math
'''=========================================================================='''


class DelayBasedController:
    def __init__(self, initial_bandwidth):
        self.del_var_th = [12.5] #ms
        self.overuse_time_th = 10 #ms
        self.K_u = 0.01
        self.K_d = 0.00018
        self.alpha = 0.95
        self.T = 0.5
        self.state = 'I'
        self.last_state = 'I'
        self.last_time_estimate_bandwidth = 0
        self.Ar_arr = [initial_bandwidth]
        self.R_arr = []
        self.R_mean = []
        self.R_deviation = []
        self.state = 'I' # 3 kinds of state, I for increase, D for decrease, N for hold state
        self.HOLD_TIME = 0.01


    def estimate_bandwidth(self, env, rtcp_timestamp, packets_info, m, last_reported_pk, RTCP_limit, RTP_packet_size):
        i = last_reported_pk
        last_m = m[i]
        second_last_m = m[i-1]
        last_arr_time, second_last_arr_time = packets_info[i][2], packets_info[i-1][2]
        self.del_var_th.append(self.new_del_var_th(last_reported_pk, last_m, self.del_var_th[-1], last_arr_time, second_last_arr_time))
        self.last_state = self.state
        last_del_var_th = self.del_var_th[-1]
        self.state = self.update_state(self.state, last_del_var_th, last_m, second_last_m)
        R = self.compute_incoming_bitrate(last_reported_pk, RTCP_limit, packets_info, RTP_packet_size)
        last_Ar = self.Ar_arr[-1]
        Ar = last_Ar
        if (self.state == 'I'):
            Ar = self.estimate_bandwidth_in_increase_state(env, packets_info, last_reported_pk, last_Ar, R)
        elif self.state == 'D':
            print "Ar = 0.85 * R"
            Ar = 0.85 * R
        else:
            print "Ar hold state"
            #Ar = self.estimate_bandwidth_in_increase_state(env, packets_info, last_reported_pk, last_Ar, R)
        self.Ar_arr.append(Ar)
        self.last_time_update_estimated_bandwidth = env.now
        return Ar

    def estimate_bandwidth_in_increase_state(self, env, packets_info, last_reported_pk, last_Ar, R):
        Ar = last_Ar
        increase_state = self.get_increase_state()
        time_since_last_update_ms = (env.now - self.last_time_estimate_bandwidth) * 1000
        if increase_state == "multiplicative":
            eta = 1.08 ** min(time_since_last_update_ms / float(1000), 1.0)
            Ar = eta * last_Ar
            print " Ar = eta * last_Ar"
        else:
            rtt_ms = 2 * (packets_info[last_reported_pk][2] - packets_info[last_reported_pk][1]) * 1000
            bits_per_frame = last_Ar / float(30)
            packets_per_frame = math.ceil(bits_per_frame / float(1200 * 8))
            avg_packet_size_bits = bits_per_frame / float(packets_per_frame)
            expected_packet_size_bits = avg_packet_size_bits
            response_time_ms = 100 + rtt_ms
            beta = 0.5 * min(time_since_last_update_ms / float(response_time_ms), 1.0)
            Ar = last_Ar + max(1000, beta * expected_packet_size_bits)
            print "Ar = last_Ar + max(1000"
        if Ar > 1.5 * R:
            print  " Ar = 1.5 * R"
            Ar = 1.5 * R
        return Ar

    def new_del_var_th(self, last_reported_pk, last_m, last_del_var_th, last_arr_time, second_last_arr_time):
        #last_m = m[last_reported_pk]
        #last_arrival_time - bf_last_arrival_time = self.packets_info[i][2]-self.packets_info[i-1][2]
        if abs(last_m) - last_del_var_th < 15:
            if abs(last_m) > self.del_var_th[-1]:
                return last_del_var_th + (last_arr_time - second_last_arr_time) * self.K_d * (abs(last_m)-last_del_var_th)
            else:
                return last_del_var_th + (last_arr_time - second_last_arr_time) * self.K_u * (abs(last_m)-last_del_var_th)


    def update_state(self, current_state, last_del_var_th, last_m, second_last_m):
        signal = self.get_signal(last_del_var_th, last_m, second_last_m)
        print "state: " + str(self.state) + "signal: " + str(signal)
        '''STATE  H: Hold        I: Increase    D: Decrease'''
        '''SIGNAL O: Overuse     U: Underuse    N: Normal'''
        if current_state == 'H':
            if signal == 'O':
                return 'D'
            elif signal == 'N':
                return 'I'
            else:
                return current_state
        elif current_state == 'I':
            if signal == 'O':
                return 'D'
            elif signal == 'N':
                return current_state
            else:
                return 'H'
        else:
            if signal == 'O':
                return current_state
            else:
                return 'H'


    def get_signal(self, last_del_var_th, last_m, second_last_m):
        #last_m, second_last_m = m[self.last_reported_pk], m[self.last_reported_pk - 1]
        if last_m > last_del_var_th and last_m >= second_last_m:
            signal = 'O'
        elif last_m <  -last_del_var_th:
            signal = 'U'
        else:
            signal = 'N'
        return signal


    def get_increase_state(self):
        if self.last_state == "D":
            R = self.R_arr[-1]
            mean = self.R_mean[-1]
            deviation = self.R_deviation[-1]
            if (abs(mean - R) < 3 * deviation):
                print "additive"
                return "additive"
            else:
                print "multiplicative"
                return "multiplicative"
        print "multiplicative"
        return "multiplicative"


    def compute_incoming_bitrate(self, last_reported_pk, RTCP_limit, packets_info, RTP_packet_size):
        print "last received pk at sender " + str(last_reported_pk)
        N = 0
        begin = last_reported_pk - RTCP_limit
        begin = begin if begin > 0 else 0
        for i in range (begin, last_reported_pk + 1):
            if packets_info[i][2] >= (packets_info[last_reported_pk][2] - self.T):
                N += 1
        if N == 0:
            R = 999999
        else:
            R = (RTP_packet_size * N) / float(self.T)
        self.R_arr.append(R)
        if len(self.R_arr) < 2:
            self.R_deviation.append(0)
            self.R_mean.append(self.R_arr[0])
        else:
            self.R_mean.append((1 - self.alpha) * self.R_mean[-1] + self.alpha * R)
            self.R_deviation.append((1 - self.alpha) * (self.R_mean[-1] + self.alpha * (R - self.R_mean[-2])))
        print "R: " + str(R)
        return R


'''=========================================================================='''