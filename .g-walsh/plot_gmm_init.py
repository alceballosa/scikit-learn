"""
==========================
GMM Initialization Methods
==========================

Examples of the different methods of initialization in Gaussian Mixture Models

See :ref:`gmm` for more information on the estimator.

Here we generate some sample data with 4 relatively easy to identify clusters.
The purpose of this example is to show the 4 different methods for the
initialization parameter `init_param`.

* `kmeans` performs kmeans clustering on the dataset to produce the initial
centers. This will be the most resource intensive initialization but will often
produce intitial means that are very close to the converged gmm model.
* `k-means++` uses the initialization of kmeans clustering (called k-means++) to
use input data points as the initial centers but to pick them such that they are
sufficiently far apart from each other.
* `rand_data` uses randomly selected data points as the initial centers. This is
a fast method but can potentially lead to unstable results if all of the
selected points are close together.
* `random` os the simplest method. It uses centers that are close to the mean of
 the data. This can be the slowest initialization to converge.
"""


# Author Gordon Walsh (github: g-walsh) gordon.p.walsh@gmail.com
# data generation code from https://jakevdp.github.io/

import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.utils.extmath import row_norms
from sklearn.cluster.k_means_ import _k_init


# Generate some data
from sklearn.datasets.samples_generator import make_blobs
X, y_true = make_blobs(n_samples=400, centers=4,
                       cluster_std=0.60, random_state=0)
X = X[:, ::-1]

n_samples = 400
n_components = 4
x_squared_norms = row_norms(X, squared=True)


def genGmm(init_params, seed=None):
    r = np.random.RandomState(seed)
    if init_params == 'kmeans':
        init_means = calculateMeans(kmeansMean(r))
    elif init_params == 'random':
        init_means = calculateMeans(randMean(r))
    elif init_params == 'rand_data':
        init_means = calculateMeans(randPointMean(r))
    elif init_params == 'k-means++':
        init_means = calculateMeans(kmeansPlusPlus(r))
    else:
        raise ValueError("Unimplemented initialisation method '%s'"
                         % init_params)

    gmm = GaussianMixture(n_components=4, means_init=init_means, tol=1e-9,
                          max_iter=2000, random_state=r).fit(X)
    labels = gmm.predict(X)
    # plt.scatter(X[:, 0], X[:, 1], c=labels, s=40, cmap='viridis')
    # plt.scatter(init_means[:, 0], init_means[:, 1], s=100,
    #             marker='x', c='black')
    return labels, init_means, seed, init_params
    # plt.show()


def kmeansMean(r):
    # Calculate the responsibilities by kmeans
    resp_km = np.zeros((n_samples, n_components))
    label = KMeans(n_clusters=n_components,
                   n_init=1, random_state=r).fit(X).labels_
    resp_km[np.arange(n_samples), label] = 1
    return resp_km
    # This will label all data points with one of the components absolutely.


def randPointMean(r):
    # Generate responsibilities to pick random points from the data.
    resp_select_point = np.zeros((n_samples, n_components))
    points = r.choice(range(n_samples), n_components, replace=False)
    for n, i in enumerate(points):
        resp_select_point[i, n] = 1
    return resp_select_point
    # This will label one random data point for each component. All others 0.


def randMean(r):
    # Generate random responsibilities for all points.
    resp_random_orig = r.rand(n_samples, n_components)
    resp_random_orig /= resp_random_orig.sum(axis=1)[:, np.newaxis]
    return resp_random_orig
    # This will label all points with random weighting.
    # Sum of responsibilities across a given point is 1.


def kmeansPlusPlus(r):
    # Generate responsibilities that end up picking points based on k-means++
    resp_kmpp = np.zeros((n_samples,n_components))
    centers, indices = _k_init(X, n_components, x_squared_norms=x_squared_norms,
                      random_state=r)
    for n, i in enumerate(indices.astype(int)):
        resp_kmpp[i, n] = 1
    return resp_kmpp


def calculateMeans(resp):
    # Generate the means of the components. These are the initial parameters.
    nk = resp.sum(axis=0) + 10 * np.finfo(resp.dtype).eps
    means = np.dot(resp.T, X) / nk[:, np.newaxis]
    return means


# Example plot


def testSeed(seed):
    methods = ['random', 'kmeans', 'rand_data', 'k-means++']
    colors = ['navy', 'turquoise', 'cornflowerblue', 'darkorange']

    plt.figure(figsize=(3 * len(methods) // 2, 6))
    plt.subplots_adjust(bottom=.1, top=0.9, hspace=.15, wspace=.05,
                        left=.05, right=.95)

    for n, i in enumerate(methods):
        plt.subplot(2, len(methods) // 2, n+1)
        labels, ini, seed, params = genGmm(i, seed)
        for n, color in enumerate(colors):
            data = X[labels == n]
            plt.scatter(data[:, 0], data[:, 1], color=color, marker='x')

        #plt.scatter(X[:, 0], X[:, 1], c=labels, s=40, cmap='viridis', lw=0.5,
        #            edgecolors='black')
        plt.scatter(ini[:, 0], ini[:, 1], s=150, marker='P', c='orange',
                    lw=1.5, edgecolors='black')
        plt.xticks(())
        plt.yticks(())
        plt.title(i)
    plt.show()

testSeed(1234)