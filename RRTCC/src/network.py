import numpy as np

'''=========================================================================='''

class Network:
    def __init__(self, manager):
        self.manager = manager
        self.LOSS_THRESHOLD = 0.015
        self.NETWORK_NOISE_MEAN = 0.01
        self.NETWORK_NOISE_DEVIATION = 0.001

    def get_delay(self):
        #gen random delay for network link
        delay = np.random.normal(self.NETWORK_NOISE_MEAN, self.NETWORK_NOISE_DEVIATION)
        if delay < 0:
            delay = self.NETWORK_NOISE_MEAN
        return delay


    def fwd(self, env, packet):
        loss_probability = np.random.uniform(0.0, 1.0)
        if loss_probability < self.LOSS_THRESHOLD:
            return
        dest = self.manager.get_element_by_address(packet.dest_address)
        yield env.timeout(self.get_delay())
        env.process(dest.receive_process(env, packet))

'''=========================================================================='''