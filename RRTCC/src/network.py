import numpy as np

'''=========================================================================='''
LOSS_THRESHOLD = 0.001
NETWORK_NOISE_MEAN = 0.01
NETWORK_NOISE_DEVIATION = 0.001

class Network:
    def __init__(self, manager):
        self.manager = manager

    def get_delay(self):
        #gen random delay for network link
        delay = np.random.normal(NETWORK_NOISE_MEAN, NETWORK_NOISE_DEVIATION)
        if delay < 0:
            delay = NETWORK_NOISE_MEAN
        return delay


    def fwd(self, env, packet):
        loss_probability = np.random.uniform(0.0, 1.0)
        if loss_probability < LOSS_THRESHOLD:
            return
        dest = self.manager.get_element_by_address(packet.dest_address)
        yield env.timeout(self.get_delay())
        env.process(dest.recv(env, packet))

'''=========================================================================='''