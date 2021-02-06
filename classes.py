# -*- coding: utf-8 -*-

import numpy as np
from numpy.random import default_rng
from tqdm import tqdm
from joblib import Parallel, delayed
from utils import pairwise, rotate, tqdm_joblib

class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def calc_distance_to(self, city):
        return np.sqrt(np.square(self.x-city.x)+np.square(self.y-city.y))

class Individual:
    def __init__(self, dists_table, tour=None, random=0):
        self.dists_table = dists_table
        if random>0:
            rng = default_rng()
            self.tour = rng.permutation(random)
        elif tour is None:
            raise ValueError("argument 'tour' must either be a list or 'random' must be set to a value > 0.")
        else:
            self.tour = tour
        
    def fitness(self): #Calculate total distance for own tour
        tour_dist = 0
        for pair in pairwise(self.tour):
            if pair in self.dists_table:
                tour_dist += self.dists_table[pair]
            elif pair[::-1] in self.dists_table:
                tour_dist += self.dists_table[pair[::-1]]
            else:
                raise NameError("Invalid city in tour.")
        return tour_dist
        
    def mutate(self):
        mutated_tour = self.tour.copy()
        rng = default_rng()
        swap_indices = rng.choice(len(mutated_tour), size=2, replace=False)
        mutated_tour[swap_indices[0]], mutated_tour[swap_indices[1]] = mutated_tour[swap_indices[1]], mutated_tour[swap_indices[0]] #Swap two elements
        self.tour=mutated_tour
    
    def crossover(self, mate):
        rng = default_rng()
        tour_len = len(self.tour)
        
        # Make random cutting points
        left_cut = rng.integers(low=0, high=tour_len, size=1)[0] #First include
        right_cut = rng.integers(low=left_cut, high=tour_len, size=1)[0] #Last include
        
        # Define carryover
        carryover_self = [i for i in self.tour[left_cut:right_cut+1]]
        carryover_mate = [i for i in mate.tour[left_cut:right_cut+1]]
        
        # Rotate tours for easy iteration
        rotated_mate = rotate(mate.tour, right_cut+1)
        rotated_self = rotate(self.tour, right_cut+1)
        
        # Define new tours
        new_tour_1 = rotate(carryover_self+[i for i in rotated_mate if not(i in carryover_self)], -left_cut)
        new_tour_2 = rotate(carryover_mate+[i for i in rotated_self if not(i in carryover_mate)], -left_cut)
        
        # Create new objects and return
        offspring_1 = Individual(self.dists_table, tour = new_tour_1)
        offspring_2 = Individual(self.dists_table, tour = new_tour_2)
        return offspring_1, offspring_2
            
class Generation:
    def __init__(self, dists_table, nr_of_cities, inds=None, random=0, mutation_rate=0.005, cores=-1):
        # When setting random to a value higher than 0, that is how many individuals will be in the generation.
        self.dists_table = dists_table
        self.nr_of_cities = nr_of_cities
        self.mutation_rate = mutation_rate
        self.fitness_list = []
        self.cores = cores
        
        if random>0:
            self.inds = [Individual(dists_table, random=self.nr_of_cities) for i in range(random)]
        elif inds is None:
            raise ValueError("argument 'inds' must either be a list or 'random' must be set to a value > 0.")
        else:
            self.inds = inds
            
    def next_gen(self):
        rng = default_rng()
        tournaments = [np.array(self.inds)[rng.choice(len(self.inds), size=4, replace=False)] for i in range(int(len(self.inds)/2))]
        
        # Prepare parallel computation
        def reproduce(tourney):
            # Find best in first binary tourney
            if tourney[0].fitness() < tourney[1].fitness():
                candidate_1 = tourney[0]
            else:
                candidate_1 = tourney[1]
            # Find best in second binary tourney
            if tourney[2].fitness() < tourney[3].fitness():
                candidate_2 = tourney[2]
            else:
                candidate_2 = tourney[3]
                
            offspring = candidate_1.crossover(candidate_2)
            # Check for mutation in children
            rng = default_rng()
            mutate_1 = rng.random()
            mutate_2 = rng.random()
            if mutate_1 < self.mutation_rate:
                offspring[0].mutate()
            if mutate_2 < self.mutation_rate:
                offspring[1].mutate()
            
            return offspring
        
        # Perform parallel computation
        with tqdm_joblib(tqdm(desc="reproduction cycle", total=int(len(self.inds)/2), leave=False)) as progress_bar:
            sibling_list = Parallel(n_jobs=self.cores)(delayed(reproduce)(i) for i in tournaments)
        
        # Flatten list of pairs
        new_generation = [i for sublist in sibling_list for i in sublist]
        
        return Generation(self.dists_table, self.nr_of_cities, inds=new_generation, mutation_rate=self.mutation_rate, cores=self.cores)
    
    def get_best(self):
        if not self.fitness_list:
            self.fitness_list = [ind.fitness() for ind in self.inds]
        return np.min(self.fitness_list), self.inds[np.argmin(self.fitness_list)]
    
    def get_worst(self):
        if not self.fitness_list:
            self.fitness_list = [ind.fitness() for ind in self.inds]
        return np.max(self.fitness_list), self.inds[np.argmax(self.fitness_list)]
    
    def get_average_fitness(self):
        if not self.fitness_list:
            self.fitness_list = [ind.fitness() for ind in self.inds]
        return np.mean(self.fitness_list)