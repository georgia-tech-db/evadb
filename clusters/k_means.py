'''
Clustering method using the distance function defined in
Discovering Important People and objects for Egocentric Video Summarization


by Jaeho Bang
'''

# Import necessary libraries

import os
import sys
import cv2
import numpy as np
import random
import time

from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import fclusterdata
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.append("/nethome/jbang36/eva")
from loaders.load import Load

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
    self.frames = None


  def feed_frames(self, frames, is_grayscale):
    self.frames = frames



  def chi_squared(self, p, q):
    return 0.5 * np.sum((p - q) ** 2 / (p + q + 1e-6))


  def get_dist(self, frame1, frame2):
    t = len(self.frames)
    bucket_x = 256

    color_hist1, _ = np.histogram(frame1.ravel(), bucket_x, [0, 255])
    color_hist2, _ = np.histogram(frame2.ravel(), bucket_x, [0, 255])

    color_hist1 = np.array(color_hist1)
    color_hist2 = np.array(color_hist2)

    #print("QWERQWERQWERWER")
    #print(color_hist1)
    #print(color_hist2)

    #print("ASDFASDFASDFASDFSA")
    chi = self.chi_squared(color_hist1, color_hist2)
    w = 1
    rho = np.mean(chi)

    if rho == 0:
      rho = 0.0001

    return 1 - w * np.exp(-1 / rho * chi)


  """  
  def get_dist(self, m, n):
    return self.dist[m][n]
  """

class Kmeans:

  def feed_frames(self, frames, is_grayscale = False):
    #self.frames = frames.astype(np.int8)
    self.frames = frames

    self.frames = self.frames.reshape(n_samples, height*width*channels)

    self.dc.feed_frames(self.frames, is_grayscale)



  def __init__(self):

    self.dc = DistanceCalculator()
    self.frames = None


  def run(self):
    # Set three centers, the model should predict similar results
    if self.frames is None:
      print ("Frames have not been fed ... returning")
      return

    # calculate the number of centers
    n_samples, arr_size = self.frames.shape
    fps = 20
    centers = np.ndarray(shape=(n_samples / fps, arr_size))

    for i in xrange(n_samples / fps):
      centers[i] = np.random.randn(1, arr_size) * random.randint(10, 100)



    # For now, we will use both clustering algorithms to see how effective each one is
    # we will include print statments to see how long it takes
    tic = time.time()
    #Method 1. clustering with custom distance function - we can make this faster but need different hierarchical clustering method
    """
    fclust1 = fclusterdata(self.frames, t=1.0, metric=self.dc.get_dist)
    toc = time.time()
    print("Time elapsed for custom distance function is %d", toc - tic)
    print (fclust1)
    x = np.array([i for i in xrange(len(fclust1))])
    y = np.array([i for i in xrange(len(fclust1))])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    scatter = ax.scatter(x,y, c=fclust1)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.colorbar(scatter)
    plt.savefig('results/custom_clust.png')
    """

    #Method 2. normal clustering
    fclust2 = fclusterdata(self.frames, t=1.0, metric='euclidean')
    """
    Let's try doing some analysis here
    1. How many categories are there?
    2. Are there any grouping that are the continuous?"""
    fclust2_set = set(fclust2)
    print("Number of individual categories is ", len(fclust2_set))
    print("Length of array", len(fclust2))
    fclust2_set_tmp = set()
    for i in xrange(1, len(fclust2)):
      if fclust2[i] not in fclust2_set_tmp:
        fclust2_set_tmp.add(fclust2[i])
      else:
        if fclust2[i-1] != fclust2[i]:
          print("Value ", fclust2[i], " already seen!!!!")

    toc2 = time.time()
    print("Time elasped for euclidean distance is %d", toc2 - tic)
    print (fclust2)
    x = np.array([i for i in xrange(len(fclust2))])
    y = np.array([10 for i in xrange(len(fclust2))])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    scatter = ax.scatter(x, y, c=fclust2)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.colorbar(scatter)
    plt.savefig('results/custom_clust_euc.png')

    # Method 3. K-Means clustering

    # Number of clusters
    kmeans = KMeans(n_clusters=len(self.frames) / 20)
    # Fitting the input data
    kmeans = kmeans.fit(self.frames)
    # Getting the cluster labels
    labels = kmeans.predict(self.frames)
    # Centroid values
    centroids = kmeans.cluster_centers_

    print("----------------------")
    print(labels)
    x = np.array([i for i in xrange(len(fclust2))])
    y = np.array([10 for i in xrange(len(fclust2))])
    fig = plt.figure()
    ax = fig.add_subplot(111)
    scatter = ax.scatter(x, y, c=labels)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.colorbar(scatter)
    plt.savefig('results/kmeans.png')

    #Method 4. DEC Deep Learning Clustering
    


if __name__ == "__main__":
  load = Load()
  eva_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  image_dir = os.path.join(eva_dir, "data", "ua_detrac", "medium-data")

  #TODO: Need to make sure the load comes in grayscale
  img_table = load.load_images_nn(image_dir, downsize_rate = 12, grayscale=True)
  n_samples, height, width, channels = img_table.shape

  kmeans_obj = Kmeans()
  kmeans_obj.feed_frames(img_table, True)
  kmeans_obj.run()



