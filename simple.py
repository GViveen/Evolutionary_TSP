# -*- coding: utf-8 -*-

import numpy as np
import tsplib95 as tsp
import argparse
import matplotlib.pyplot as plt
from tqdm import tqdm
from dist_dict import build_dist_dict
from classes import Generation

# Parse command line arguments
parser = argparse.ArgumentParser(description="Use a simple genetic algorithm to find a solution to the Traveling Salesman problem.")
parser.add_argument('--file', dest='filename', default='file-tsp.txt', help="Should be either 'file-tsp.txt', 'gr21.tsp', or 'dantzig42.tsp'.")
parser.add_argument('--pop_size', dest='pop_size', default=100, type=int, help="How large the population should be.")
parser.add_argument('--generations', dest='nr_gens', default=10000, type=int, help="How many generations are to be simulated.")
parser.add_argument('--mutation_rate', dest='mutation_rate', default=0.005, type=float, help="Set how often mutations occur between generations.")
parser.add_argument('--cores', dest='cores', default=-1, type=int, help="How many cores is the kernel allowed to use. Default: -1, which indicates that as many cores as possible will be used.")

args = parser.parse_args()

# Load in tsp file and build distance dictionary
if args.filename == 'file-tsp.txt':
    coordinates = np.loadtxt("tsp/"+args.filename)
    city_dists = build_dist_dict(coordinates)
    nr_of_cities = len(coordinates[:,0])
else: 
    problem = tsp.load("tsp/"+args.filename)
    city_dists = {i:problem.get_weight(*i) for i in problem.get_edges()}
    nr_of_cities = len(list(problem.get_nodes()))
    
# Random initialization:

current_gen = Generation(city_dists, nr_of_cities, random=args.pop_size, cores=args.cores)

log_entry = "{}, {}, {}".format(current_gen.get_best()[0], current_gen.get_worst()[0], current_gen.get_average_fitness())
with open("output_log.txt", "w") as output:
    output.write("Best Fitness Score, Worst Fitness Score, Average Fitness")
    output.write("\n"+log_entry)

with tqdm(range(args.nr_gens), desc="Full Evolutionary Run", leave=True) as bar:
    for i in bar:
        new_gen = current_gen.next_gen()
        log_entry = "{}, {}, {}".format(new_gen.get_best()[0], new_gen.get_worst()[0], new_gen.get_average_fitness())
        with open("output_log.txt", "a") as output:
            output.write("\n"+log_entry)
        with open("last_best_backup.txt", "w") as backup:
            backup.write("{}".format(new_gen.get_best()[1].tour))
        current_gen = new_gen
    
results = np.loadtxt("output_log.txt", skiprows=1, delimiter=", ")

best, = plt.plot(results[:, 0], 'c-.', label="Best")
worst, = plt.plot(results[:, 1], 'r-.', label="Worst")
avg, = plt.plot(results[:, 2], 'b-', label="Average")
plt.ylim(bottom=0)
plt.legend(handles=[best, worst, avg])
plt.show()