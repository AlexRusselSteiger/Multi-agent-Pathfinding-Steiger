import subprocess
from argparse import ArgumentParser

def load_instance(input_file):
    global LEN_OF_GRID
    global WIDTH_OF_GRID
    global NR_OF_AGENTS
    global MAKESPAN

    grid = []
    agents_starts = []
    agents_targets = []

    with open(input_file, "r") as file: 
        LEN_OF_GRID = int(next(file))
        WIDTH_OF_GRID = int(next(file))
        grid 
        NR_OF_AGENTS = int(next(file))