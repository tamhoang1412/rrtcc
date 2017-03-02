import numpy as np

'''=========================================================================='''
LOSS_THRESHOLD = 0.001
NETWORK_NOISE_MEAN = 0.01
NETWORK_NOISE_DEVIATION = 0.001

class network:
    
    def get_delay():
        #gen random delay for network link
        delay = np.random.normal(NETWORK_NOISE_MEAN, NETWORK_NOISE_DEVIATION)
        if delay < 0:
            delay = NETWORK_NOISE_MEAN
        return delay


    def fwd(self, env, packet, manager):
        loss_probability = np.random.uniform(0.0, 1.0)
        if loss_probability < LOSS_THRESHOLD:
            return
        dest = manager.get_element_by_address(packet.dest_add)
        yield env.timeout(self.get_delay())
        env.process(dest.recv(env, packet))

'''=========================================================================='''