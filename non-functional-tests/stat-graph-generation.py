#!/usr/bin/python3

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

results = pd.read_csv('integrity_2019-07-16_00-20-47_21_iteraciones.csv')
results.head()
results['Max memory (mb)'] = results['Max memory (kb)'] / 1024
results = results.drop('Max memory (kb)', axis=1)

results['VNFs']=[ i for j in range(24) for i in range(1,101)]
results_part1 = results[900:1300]
results_part1.plot(kind='scatter',x='VNFs', y='Max memory (mb)', color='red')
plt.show()