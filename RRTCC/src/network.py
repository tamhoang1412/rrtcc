import numpy as np
import copy
import json

'''=========================================================================='''

class Network:
    def __init__(self, manager):
        self.manager = manager
        self.NORMAL_LOSS_THRESHOLD = 0.01
        self.NETWORK_NOISE_MEAN = 0.01
        self.NETWORK_NOISE_DEVIATION = 0.001
        self.loss_threshold = self.NORMAL_LOSS_THRESHOLD
        self.RTP_packet_size = 1200 * 30 * 8  # bits

        self.available_bandwidth_coef = [0, 5, 10, 15]
        #self.available_bandwidth_coef = [0, 10, 15, 20]
        #self.available_bandwidth_coef = [0, 15, 20, 25]
        #self.available_bandwidth_coef = [0, 20, 25, 35]

        self.lambda_outs = [self.RTP_packet_size * i for i in self.available_bandwidth_coef]
        self.lambda_outs_indexes = []
        self.lambda_outs_num = len(self.lambda_outs)
        self.lambda_out = self.lambda_outs[-1]
        self.lambda_in = 0
        self.lambda_out_interval = 2
        self.last_time_update_lambda_out = 0
        self.congestion_probability_threshold = 0.05
        self.free_bandwidth_probability_threshold = 0.3


    def get_delay(self):
        delay = np.random.normal(self.NETWORK_NOISE_MEAN, self.NETWORK_NOISE_DEVIATION)
        if delay < 0:
            delay = self.NETWORK_NOISE_MEAN
        return delay


    def fwd(self, env, packet):
        self.update_loss_threshold(copy.deepcopy(env.now))
        loss_probability = np.random.uniform(0.0, 1.0)
        print "loss_threshold: " + str(self.loss_threshold)
        if loss_probability < self.loss_threshold:
            return
        dest = self.manager.get_element_by_address(packet.dest_address)
        yield env.timeout(self.get_delay())
        env.process(dest.receive_process(env, packet))

    def generate_lambda_outs(self):
        for i in range(0, 50):
            index_probability = np.random.uniform(0.0, 1.0)
            if index_probability < self.congestion_probability_threshold:
                index = 0  # congestion
            elif index_probability > self.free_bandwidth_probability_threshold:
                index = self.lambda_outs_num - 1
            else:
                index = np.random.randint(1, self.lambda_outs_num)
            self.lambda_outs_indexes.append(index)

    def load_lambda_outs(self, filename):
        file = open('D:\SimulationResults' + filename, 'r')
        log_string = file.read()
        log = json.loads(log_string)
        file.close()
        for i in range(0, len(log['lambda_outs_index'])):
            index = log['lambda_outs_index'][i]
            self.lambda_outs_indexes.append(index)


    def update_loss_threshold(self, current_time):
        time_index = int(current_time / self.lambda_out_interval)
        self.lambda_out = self.lambda_outs[self.lambda_outs_indexes[time_index]]
        if self.lambda_in > self.lambda_out:
            self.loss_threshold = (self.lambda_in - self.lambda_out) / float(self.lambda_in)
        else:
            self.loss_threshold = self.NORMAL_LOSS_THRESHOLD
        return
