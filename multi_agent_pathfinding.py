import subprocess
from argparse import ArgumentParser

def load_instance(input_file):   # reads the parameters of instance from the file and returns the grid and locations of the agents starts and targets
    global MAKESPAN
    global LEN_OF_GRID      
    global WIDTH_OF_GRID
    global NR_OF_AGENTS

    grid = []
    agents_starts = []
    agents_targets = []

    with open(input_file, "r") as file:
        MAKESPAN = int(next(file))
        WIDTH_OF_GRID = int(next(file))
        LEN_OF_GRID = int(next(file))
        grid = [next(file).strip() for i in range(LEN_OF_GRID)]     # reads the map topology line by line and stores into "grid","." for empty, "X" for obstacle
        NR_OF_AGENTS = int(next(file))

        for line in file:
            c = line.split()
            agents_starts.append((int(c[0]), int(c[1])))        # start_X start_Y  
            agents_targets.append((int(c[2]), int(c[3])))       # target_X target_Y 

    return grid, agents_starts, agents_targets  

def position_to_ID(x, y, agent, time):
    return agent + (x * NR_OF_AGENTS) + (y * WIDTH_OF_GRID * NR_OF_AGENTS) + (time * LEN_OF_GRID * WIDTH_OF_GRID * NR_OF_AGENTS) + 1

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

def encode(grid, agents_starts, agents_targets):
    cnf = []

    for agent, (x,y) in enumerate(agents_starts):   # starting agents positions, they have to be open
        if grid[y][x] == "X":
            print(f"Agent {agent} starts on an obstacle ({x}, {y})")
            exit(1)
        cnf.append([position_to_ID(x, y, agent, 0), 0])

    for agent, (x,y) in enumerate(agents_targets):      # target agents positions
        cnf.append([position_to_ID(x, y, agent, MAKESPAN), 0])

    for agent1 in range(NR_OF_AGENTS):      # multiple agents cant be at the same square at the same time
        for agent2 in range(agent1 + 1, NR_OF_AGENTS):
            for t in range(MAKESPAN + 1):
                for x in range(WIDTH_OF_GRID):
                    for y in range(LEN_OF_GRID):
                        cnf.append([-position_to_ID(x, y, agent1, t), -position_to_ID(x, y, agent2, t), 0])

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

    for agent1 in range(NR_OF_AGENTS):  # forbidding head-on collisions/swaps
        for agent2 in range(agent1 + 1, NR_OF_AGENTS):
            for t in range(MAKESPAN):
                for x in range(WIDTH_OF_GRID):
                    for y in range(LEN_OF_GRID):
                        for x2, y2 in accessible_neighbour_tiles(x, y, grid):
                            cnf.append([-position_to_ID(x, y, agent1, t), -position_to_ID(x2, y2, agent1, t + 1), -position_to_ID(x2, y2, agent2, t), -position_to_ID(x, y, agent2, t + 1), 0])

    nr_vars = WIDTH_OF_GRID * LEN_OF_GRID * NR_OF_AGENTS * (MAKESPAN + 1)   
    return (cnf, nr_vars)

def call_solver(cnf, nr_vars, output_name, solver_name, verbosity): # writes CNF into output file in DIMACS format
    with open(output_name, "w") as file:
        file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + "\n")
        for clause in cnf:
            file.write(" ".join(str(lit) for lit in clause) + "\n")

    return subprocess.run(["./" + solver_name, "-model", "-verb=" + str(verbosity), output_name], stdout=subprocess.PIPE)   # calls the SAT solver and returns its output

def print_result(result, grid):
    output = result.stdout.decode("utf-8")
    for line in output.splitlines():
        print(line)

    if result.returncode != 10: # returns if there isnt a solution for given makespan
        print(f"No solution for MAKESPAN = {MAKESPAN}")
        return
    
    model = []  # parses the model from the output of the solver
    for line in result.stdout.decode("utf-8").split("\n"):
        if line.startswith("v"):
            vars = line.split()
            vars.remove("v")
            model.extend(int(v) for v in vars)
    model.remove(0)

    for t in range(MAKESPAN + 1):   # decodes agent positions for each timestep
        print("Timestep " + str(t) + ":")
        display_grid = [list(row) for row in grid]

        for agent in range(NR_OF_AGENTS):
            for y in range(LEN_OF_GRID):
                for x in range(WIDTH_OF_GRID):
                    if model[position_to_ID(x, y, agent, t) - 1] > 0:
                        display_grid[y][x] = str(agent)

        for row in display_grid:
            print(" ".join(row))
        print()

if __name__ == "__main__":
    parser = ArgumentParser()  # parses command line arguments

    parser.add_argument(
        "-i",
        "--input",
        default="input.in",
        type=str,
        help="The instance file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help="Output file for the DIMACS format (i.e. the CNF formula).",
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose-syrup",
        type=str,
        help="The SAT solver to be used.",
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=0,
        type=int,
        choices=range(0, 2),
        help="Verbosity of the SAT solver used.",
    )
    parser.add_argument(
        "-c",
        "--print-cnf",
        action="store_true",
        help="Print the constructed CNF formula in DIMACS format.",
    )
    args = parser.parse_args()

    grid, starts, goals = load_instance(args.input)  # loads the input instance
    cnf, nr_vars = encode(grid, starts, goals)  # encodes the problem into CNF formula

    if args.print_cnf:  # prints the CNF formula to stdout
        print(f"p cnf {nr_vars} {len(cnf)}")
        for clause in cnf:
            print(" ".join(str(lit) for lit in clause))

    result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)  # calls the SAT solver
    print_result(result, grid)  # decodes and prints the result