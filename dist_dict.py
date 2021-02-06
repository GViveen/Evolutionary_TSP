# -*- coding: utf-8 -*-

from classes import City
import itertools

def build_dist_dict(coordinates):
    cities = {i:City(x, y) for i, (x, y) in enumerate(zip(coordinates[:,0], coordinates[:,1]))}
    dist_dict = {p:cities[p[0]].calc_distance_to(cities[p[1]]) for p in itertools.product(cities, cities)}
    
    return dist_dict