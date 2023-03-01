import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from scipy.interpolate import InterpolatedUnivariateSpline
from matplotlib.text import Text
import matplotlib.ticker as tck

l = np.array([100, 90, 80, 70, 60, 50][::-1])

f1 = np.array([300, 375, 490, 632, 840, 1190][::-1])

f2 = np.array([840, 1010, 1590, 1570, 1570, 1580][::-1])

ius = InterpolatedUnivariateSpline(l, f2, k = 2)

def func1(x, A, B, x0, C): #simple linear approximation
    return A + B * (x - x0) ** (-C)

p1 = np.array([0, 5.9e+7, -20, 2]) #initial guess

beta_opt1, beta_cov1 = optimize.curve_fit(func1, l, f1, p1, maxfev = 5000)

print(beta_opt1)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

ax1.plot(l, f1, 'o', color = 'blue', label = 'Fundamental')
ax2.plot(l, f1, 'o', color = 'blue', label = 'Fundamental')
#ax1.set_yscale('log')
#ax2.set_yscale('log')
t1 = np.linspace(np.min(l), np.max(l), 1000)
ax1.plot(t1, func1(t1, *beta_opt1), '-', color = 'blue')
ax2.plot(t1, func1(t1, *beta_opt1), '-', color = 'blue')

t2 = np.linspace(np.min(l), np.max(l), 1000)
ax1.plot(l, f2, 'o', color = 'crimson', label = 'Third')
ax2.plot(l, f2, 'o', color = 'crimson', label = 'Third')
ax1.plot(t2, ius(t2), '-', color = 'crimson')
ax2.plot(t2, ius(t2), '-', color = 'crimson')

ax1.legend()
ax1.set_title(r'Frequency over length')
ax1.set_xlabel(r'Length $l$, cm')
ax1.set_ylabel(r'Frequency $f$, Hz')
ax2.set_yticks([329, 392, 440, 523, 587, 659, 783, 880, 987, 1047, 1174, 1318, 1396, 1567])
ax2.set_yticklabels([r'$E_4$', r'$G_4$', r'$A_4$', r'$C_5$', r'$D_5$', r'$E_5$', r'$G_5$', r'$A_5$', r'$B_5$', r'$C_6$', r'$D_6$', r'$E_6$', r'$F_6$', r'$G_6$'])
ax2.grid()
'''
ax1.set_yscale('log')
ax2.set_yscale('log')
'''
plt.savefig('LSQ.png', dpi = 300)