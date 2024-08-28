"""
This script generates smoothed plots of call distributions across different hours of the day for various tenant sizes.
It uses data representing the volume of calls made each hour and creates visual representations to analyze call patterns for different scenarios.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.interpolate import make_interp_spline


hour_of_day = np.arange(start=7, stop=19)

patterns = [
    # [np.array([0, 7, 48, 66, 80, 72, 56, 17, 85, 66, 50, 10]), 'Real', 'Call distribution: Real client', 'real'],
    # # [np.array([1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1]), '< 10,000', 'Call distribution: < 10,000', 'small'],
    # [np.array([1, 3, 7, 9, 9, 8, 4, 6, 6, 5, 3, 2]), '10,000 to 100,000', 'Call distribution: 10,000 to 100,000', 'medium'],
    # [np.array([9, 51, 159, 193, 191, 175, 91, 128, 127, 109, 75, 36]), '100,000 to 1,000,000', 'Call distribution: 100,000 to 1,000,000', 'large'],
    [np.array([144, 984, 3069, 4187, 4196, 3901, 2468, 3058, 3025, 2901, 1803, 726]), '> 1,000,000', 'Call distribution: > 1,000,000', 'call_center']
]

for i, pattern in enumerate(patterns):
    plt.figure(figsize=(8, 6))
    plt.rcParams.update({'font.size': 14})
    
    x = np.array(hour_of_day)
    y = np.array(pattern[0])

    coefficients = np.polyfit(x, y, 10)
    polynomial = np.poly1d(coefficients)
    
    # Adjust 300 for smoother or less smooth curve
    x_smooth = np.linspace(x.min(), x.max(), 300)
    spl = make_interp_spline(x, y, k=2)
    spl = make_interp_spline(x, y, k=1)
    y_smooth = spl(x_smooth)
    
    plt.plot(x_smooth, y_smooth, label=pattern[1], linewidth=5.0)
    
    plt.xlim(min(hour_of_day), max(hour_of_day))
    plt.xticks(hour_of_day)
    plt.gca().yaxis.set_major_locator(mticker.MultipleLocator(1))
    
    plt.title(pattern[2])
    plt.xlabel("Hour of Day")
    plt.ylabel("Call volume")
    plt.grid(True)
    plt.savefig(f'call_distribution_{pattern[3]}.png', dpi=400)
