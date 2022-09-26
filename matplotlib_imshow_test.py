import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


x = np.abs(np.arange(-100, 150))**(1/3)
y = np.arange(-230, 100)
data = np.zeros((x.shape[0], y.shape[0]))

for i in range(x.shape[0]):
    for j in range(y.shape[0]):
        data[i, j] = (np.exp(-(x[i]**2 + y[j]**2) / 500))
        
plt.figure()
a = plt.imshow(data, interpolation ='nearest')
plt.colorbar(a)
plt.yticks(np.arange(x.shape[0], step = x.shape[0] // 10), x[::x.shape[0] // 10])
plt.xticks(np.arange(y.shape[0], step = y.shape[0] // 10), y[::y.shape[0] // 10])
           

