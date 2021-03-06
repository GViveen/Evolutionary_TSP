# -*- coding: utf-8 -*-

import itertools
import numpy as np
from numpy.random import default_rng
from utils import pairwise, rotate

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
        self.fitness_score=None
        
    def fitness(self): #Calculate total distance for own tour
        if self.fitness_score is not None:
            return self.fitness_score
        tour_dist = 0
        for pair in pairwise(self.tour):
            if pair in self.dists_table:
                tour_dist += self.dists_table[pair]
            elif pair[::-1] in self.dists_table:
                tour_dist += self.dists_table[pair[::-1]]
            else:
                raise NameError("Invalid city in tour.")
        self.fitness_score = tour_dist
        return self.fitness_score
        
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
    
    def local_search(self):
        # Assume self to be best
        best_score = self.fitness()
        best_ind = self
        
        # Check local neighbours using 2-opt, return best neighbour
        for i in itertools.combinations(range(len(self.tour)), 2):
            candidate_tour = self.tour.copy()
            candidate_tour[i[0]], candidate_tour[i[1]] = candidate_tour[i[1]], candidate_tour[i[0]]
            candidate = Individual(self.dists_table, tour=candidate_tour)
            if candidate.fitness() < best_score:
                best_score = candidate.fitness()
                best_ind = candidate
                
        return best_ind
            
class Generation:
    def __init__(self, dists_table, nr_of_cities, inds=None, random=0, mutation_rate=0.005, local_search=False):
        # When setting random to a value higher than 0, that is how many individuals will be in the generation.
        self.dists_table = dists_table
        self.nr_of_cities = nr_of_cities
        self.mutation_rate = mutation_rate
        self.fitness_list = []
        self.local_search = local_search
        
        if random>0:
            self.inds = [Individual(dists_table, random=self.nr_of_cities) for i in range(random)]
        elif inds is None:
            raise ValueError("argument 'inds' must either be a list or 'random' must be set to a value > 0.")
        else:
            self.inds = inds
            
    def next_gen(self):
        rng = default_rng()
        tournaments = [np.array(self.inds)[rng.choice(len(self.inds), size=4, replace=False)] for i in range(int(len(self.inds)/2))]
        
        # Prepare computation
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
                
            # Apply local search if running memetic
            if self.local_search:
                return offspring[0].local_search(), offspring[1].local_search()
            
            return offspring
        
        # Perform computation
        sibling_list = [reproduce(i) for i in tournaments]
        
        # Flatten list of pairs
        new_generation = [i for sublist in sibling_list for i in sublist]
        
        return Generation(self.dists_table, self.nr_of_cities, inds=new_generation, mutation_rate=self.mutation_rate, local_search=self.local_search)
    
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