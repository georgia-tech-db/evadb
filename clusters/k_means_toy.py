'''
Toy clustering algorithm from webpage:
https://www.kaggle.com/andyxie/k-means-clustering-implementation-in-python

by Jaeho Bang
'''



# Import necessary libraries
from copy import deepcopy
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

# Set three centers, the model should predict similar results
center_1 = np.array([1,1])
center_2 = np.array([5,5])
center_3 = np.array([8,1])

# Generate random data and center it to the three centers
data_1 = np.random.randn(200, 2) + center_1
data_2 = np.random.randn(200,2) + center_2
data_3 = np.random.randn(200,2) + center_3

data = np.concatenate((data_1, data_2, data_3), axis = 0)

plt.scatter(data[:,0], data[:,1], s=7)

# Number of clusters
k = 3
# Number of training data
n = data.shape[0]
# Number of features in the data
c = data.shape[1]

# Generate random centers, here we use sigma and mean to ensure it represent the whole data
mean = np.mean(data, axis = 0)
std = np.std(data, axis = 0)
centers = np.random.randn(k,c)*std + mean

# Plot the data and the centers generated as random
plt.scatter(data[:,0], data[:,1], s=7)
plt.savefig('fig3.png')

plt.scatter(centers[:,0], centers[:,1], marker='*', c='g', s=150)
plt.savefig('fig4.png')


centers_old = np.zeros(centers.shape)  # to store old centers
centers_new = deepcopy(centers)  # Store new centers

data.shape
clusters = np.zeros(n)
distances = np.zeros((n, k))

error = np.linalg.norm(centers_new - centers_old)

# When, after an update, the estimate of that center stays the same, exit loop
while error != 0:
  # Measure the distance to every center
  for i in range(k):
    distances[:, i] = np.linalg.norm(data - centers[i], axis=1)
  # Assign all training data to closest center
  clusters = np.argmin(distances, axis=1)

  centers_old = deepcopy(centers_new)
  # Calculate mean for every cluster and update the center
  for i in range(k):
    centers_new[i] = np.mean(data[clusters == i], axis=0)
  error = np.linalg.norm(centers_new - centers_old)
centers_new

# Plot the data and the centers generated as random
fig1 = plt.scatter(data[:,0], data[:,1], s=7)
plt.savefig('fig1.png')

fig2 = plt.scatter(centers_new[:,0], centers_new[:,1], marker='*', c='g', s=150)
plt.savefig('fig2.png')
