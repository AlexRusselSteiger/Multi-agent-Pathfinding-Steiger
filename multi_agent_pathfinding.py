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
        new_x = x + dx
        new_y = y + dy
        if 0 <= new_x < WIDTH_OF_GRID and 0 <= new_y < LEN_OF_GRID:
            if grid[new_y][new_x] == ".":
                neighbour_tiles.append((new_x, new_y))

    return neighbour_tiles

def encode(instance):
    cnf = []
    grid = instance[0]
    agents_starts = instance[1]
    agents_targets = instance[2]

    for agent, (x,y) in range(len(agents_starts)):   # starting agents positions
        cnf.append([position_to_ID(x, y, agent, 0)])

    for agent, (x,y) in range(len(agents_targets)):      # target agents positions
        cnf.append([position_to_ID(x, y, agent, MAKESPAN),0])

    for agent1 in range(NR_OF_AGENTS):      # multiple agents cant be at the same square at the same time
        for agent2 in range(agent1 + 1, NR_OF_AGENTS):
            for t in range(MAKESPAN + 1):
                for x in range(WIDTH_OF_GRID):
                    for y in range(LEN_OF_GRID):
                        cnf.append([-position_to_ID(x, y, agent1, t)], [-position_to_ID(x, y, agent2, t), 0])

    for agent in range(NR_OF_AGENTS):   # clause for allowed agent moves
        for t in range(MAKESPAN):
            for x in range(WIDTH_OF_GRID):
                for y in range(LEN_OF_GRID):
                        clause = [-position_to_ID(x, y, agent, t), position_to_ID(x, y, agent, t+1)]        # forbiding current position, but allowing waiting 
                        for new_x, new_y in accessible_neighbour_tiles(x, y, grid):     # using support function for listing available positions
                            clause.append(position_to_ID(new_x, new_y, agent, t + 1))
                        clause.append(0)
                        cnf.append(clause)

    for agent in range(NR_OF_AGENTS):       # agent cant be at 2 squares at the same time
        for t in range(MAKESPAN + 1):
            for x in range(WIDTH_OF_GRID):
                for y in range(LEN_OF_GRID):
                        for x2 in range(WIDTH_OF_GRID):
                            for y2 in range(LEN_OF_GRID):
                                if (x, y) != (x2, y2):
                                    cnf.append([-position_to_ID(x, y, agent, t), -position_to_ID(x2, y2, agent, t), 0])

    for agent1 in range(NR_OF_AGENTS): # forbiding head on collisions/swaps
       for agent2 in range(agent1 + 1, NR_OF_AGENTS):
            for t in range(MAKESPAN):
                for x in range(WIDTH_OF_GRID):
                    for y in range(LEN_OF_GRID):
                       for x2, y2 in accessible_neighbour_tiles(x, y, grid):
                        cnf.append([-position_to_ID(x, y, agent1, t), -position_to_ID(x2, y2, agent1, t + 1), -position_to_ID(x2, y2, agent2, t), -position_to_ID(x, y, agent2, t + 1), 0])