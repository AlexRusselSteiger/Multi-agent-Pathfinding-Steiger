import subprocess
from argparse import ArgumentParser

def load_instance(input_file):
    global MAKESPAN
    global LEN_OF_GRID
    global WIDTH_OF_GRID
    global NR_OF_AGENTS

    grid = []
    agents_starts = []
    agents_targets = []

    with open(input_file, "r") as file:
        MAKESPAN = int(next(file))
        LEN_OF_GRID = int(next(file))
        WIDTH_OF_GRID = int(next(file))
        grid = [next(file).strip() for i in range(LEN_OF_GRID)]
        NR_OF_AGENTS = int(next(file))

        for line in file:
            c = line.split()
            agents_starts.append((int(c[0]), int(c[1])))
            agents_targets.append((int(c[2]), int(c[3])))

    return grid, agents_starts, agents_targets