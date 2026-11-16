import subprocess
from argparse import ArgumentParser

def load_instance(input_file):
    # reads the parameters of instance from the file and returns the grid and locations of the agents starts and targets
    global MAKESPAN
    global LEN_OF_GRID      
    global WIDTH_OF_GRID
    global NR_OF_AGENTS
    global NR_SQUARES
    global NR_AT_VAR

    grid = []
    agents_starts = []
    agents_targets = []

    with open(input_file, "r") as file:
        MAKESPAN = int(next(file))
        LEN_OF_GRID = int(next(file))
        WIDTH_OF_GRID = int(next(file))
        grid = [next(file).strip() for i in range(LEN_OF_GRID)]     # reads the map topology line by line and stores into "grid","." for empty, "X" for obstacle
        NR_OF_AGENTS = int(next(file))

        for line in file:
            c = line.split()
            agents_starts.append((int(c[0]), int(c[1])))        # start_X start_Y  
            agents_targets.append((int(c[2]), int(c[3])))       # target_X target_Y 

    return grid, agents_starts, agents_targets  


def position_to_ID(x, y, agent, time):
    return agent + + (x * NR_OF_AGENTS) + (y * WIDTH_OF_GRID * NR_OF_AGENTS) + (time * LEN_OF_GRID * WIDTH_OF_GRID * NR_OF_AGENTS) + 1

def accessible_neighbour_tiles(x, y, grid):
    neighbour_tiles = []
    moves = [(0, 1), (1, 0), (-1, 0), (0, -1)]
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < WIDTH_OF_GRID and 0 <= ny < LEN_OF_GRID:
            if grid[ny][nx] == ".":
                neighbour_tiles.append((nx, ny))

    return neighbour_tiles