import numpy as np
import matplotlib.pyplot as plt

from pykalman import KalmanFilter
plt.rcParams['figure.figsize'] = (10, 8)

# intial parameters
n_iter = 50
x = 0 # truth value (typo in example at top of p. 13 calls this z)
kf = KalmanFilter(transition_matrices = [1], observation_matrices = [1])
measurements = np.asarray([1, -1, 1, -2, 5])  # 3 observations
kf = kf.em(measurements, n_iter=100)
(filtered_state_means, filtered_state_covariances) = kf.filter(measurements)


plt.figure()
plt.plot(measurements,'k+',label='noisy measurements')
plt.plot(filtered_state_means,'b-',label='a posteri estimate')
plt.axhline(x,color='g',label='truth value')
plt.legend()
plt.title('Estimate vs. iteration step', fontweight='bold')
plt.xlabel('Iteration')
plt.ylabel('Voltage')
plt.show()