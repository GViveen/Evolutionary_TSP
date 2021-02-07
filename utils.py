# -*- coding: utf-8 -*-

import itertools

def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def rotate(l, n):
    l = list(l)
    return l[n:] + l[:n]