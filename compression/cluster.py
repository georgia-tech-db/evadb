import time
from sklearn.cluster import AgglomerativeClustering


"""
Clustering Class with two primary function run and plot
###
run: Fits an Agglomerative Clustering Model and returns the 
cluster labels 

Inputs: latent representation of image, fps default set at 10. 
fps = 10 set as default to be applicable to all videos

Outputs: cluster labels from model. 
###

###
plot distribution: provides a plot of the cluster distribution for analysis

Inputs: Clustered Model file 

Outputs: Matplotlib based graphic
###

"""
class ClusterModule:

    def __init__(self):
        self.ac = None

    def run(self, image_compressed, fps=10):
        n_samples = image_compressed.shape[0]
        self.ac = AgglomerativeClustering(n_clusters=n_samples // fps)
        start_time = time.time()
        self.ac.fit(image_compressed)
        return self.ac.labels_

    def plot_distribution(self):
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
        axs.hist(self.ac.labels_, bins=max(self.ac.labels_) + 1)
        plt.xlabel("Cluster Numbers")
        plt.ylabel("Number of datapoints")

