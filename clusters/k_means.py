'''
Clustering method using the distance function defined in
Discovering Important People and objects for Egocentric Video Summarization


by Jaeho Bang
'''

# Import necessary libraries

import os
import cv2
import numpy as np
from copy import deepcopy
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib
from loaders import load
matplotlib.use('Agg')
from matplotlib import pyplot as plt


'''
Distance function between any frame in the video is defined as follows
D(f_m, f_n) = 1 - w^t_{m,n} * exp(-1/rho chi^2(f_m, f_n))
where
w^t_{m,n} = 1/t * max(0, t - |m - n|), 
t is the size of the temporal window surrounding frame f_m
chi^2(f_m, f_n) is the chi square distance between color histograms f_m, f_n
rho denotes the mean of the chi square distance among all the frames

'''

'''
  1st iteration:
We manually define the threshold

  2nd iteration:
How we want to cluster..,
computation time of O(n^2)
we will compute the distance of frames among each other
we will start grouping frames 
until the maximum distance between members of each group is 2x sd of rho

  3rd iteration:
make a network to predict the threshold given all the frames in video

'''

class DistanceCalculator:


  def __init__(self):
    self.frames = []


  def feed_frames(self, frames):
    self.frames = frames
    self._calc()


  def _calc(self):
    """
    Need to calculate...
    t
    rho
    color_histograms of all f_m where m is between 0 and len(frames)
    chi square distances between all f_m,n where m,n is between 0 and len(frames)

    :return:
    """
    t = len(self.frames)
    bucket_x = 8
    bucket_y = 8
    bucket_z = 8
    color_hist = np.ndarry(shape=(len(self.frames),bucket_x, bucket_y, bucket_z))
    for i in xrange(len(self.frames)):
      color_hist[i] = cv2.calcHist([self.frames[i]], [0, 1, 2],
                        None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

    chi = np.ndarray(shape=(len(self.frames, self.frames)))
    w = np.ndarray(shape=(len(self.frames, self.frames)))
    self.dist = np.ndarray(shape=(len(self.frames, self.frames)))
    for i in xrange(len(self.frames)):
      for j in xrange(i, len(self.frames)):

        chi[i][j] = self.chi_squared(color_hist[i], color_hist[j])
        chi[j][i] = self.chi[i][j]
        w[i][j] = 1 * max(0, t - abs(i - j)) / t
        w[j][i] = self.w[i][j]

    rho = np.mean(chi)

    for i in xrange(len(self.frames)):
      for j in xrange(i, len(self.frames)):
        self.dist[i][j] = 1 - w[i][j] * np.exp(-1 / rho * chi[i][j])
        self.dist[j][i] = self.dist[i][j]

    return

  def chi_squared(self, p, q):
    return 0.5 * np.sum((p - q) ** 2 / (p + q + 1e-6))

  def get_dist(self, m, n):
    return self.dist[m][n]


class Kmeans:

  def __init__(self):

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
    
    # Plot the data and the centers generated as random
    fig1 = plt.scatter(data[:,0], data[:,1], s=7)
    plt.savefig('fig1.png')

    fig2 = plt.scatter(centers_new[:,0], centers_new[:,1], marker='*', c='g', s=150)
    plt.savefig('fig2.png')



if __name__ == "__main__":
  load = load.Load()
  eva_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  image_dir = os.path.join(eva_dir, "data", "ua_detrac", "small-data")

  img_table = load._load_images(image_dir)


  """
  1. load the images from data/ua_detrac/small_data
  2. make instances of Kmeans and DistanceCalculator
  3. print out the stats"""
