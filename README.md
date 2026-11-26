# Multi-agent-Pathfinding-Steiger

## Problem description

The Multi-agent Pathfinding task is about finding paths for $k$ agents $A = \lbrace 0, 1, \dots, k-1 \rbrace$ in a 2D grid of size $W \times L$ (width $\times$ length) from their starting positions to their target destinations. Each cell $(x, y)$ in the grid is either open (`.`) or blocked by an obstacle (`X`).

There are several variations of MAPF. The one implemented here has the following rules:
1. **Allowed moves:** At each timestep, an agent can either move orthogonally (up, down, left, right) to an adjacent open cell, or wait on its current cell.
2. **Makespan limit:** There is a time limit $T$ (`MAKESPAN`). Every agent starts at its initial coordinate $start(a)$ at timestep $t = 0$ and must reach its destination $target(a)$ at timestep $t = T$. If the agents cannot reach their targets within $T$ steps, the instance is unsolvable (`UNSAT`).
3. **Forbidden conflicts:**
   - **Obstacle collision:** Agents cannot enter or pass through cells occupied by obstacles (`X`).
   - **Vertex conflict:** Two different agents cannot occupy the same cell $(x, y)$ at the same timestep $t$.
   - **Edge (swapping) conflict:** Two different agents cannot swap positions along the same edge between adjacent cells in a single timestep (i.e., moving from $(x_1, y_1)$ to $(x_2, y_2)$ while another agent moves from $(x_2, y_2)$ to $(x_1, y_1)$ at the same time).

## Encoding

For each cell $(x, y)$, agent $a \in \lbrace 0, \dots, k-1 \rbrace$, and timestep $t \in \lbrace 0, \dots, T \rbrace$, there is a variable $p_{x,y,a,t}$, which means that agent $a$ is at cell $(x, y)$ at time $t$. `position_to_ID(x, y, agent, time)` then gives each variable $p_{x,y,a,t}$ a unique ID:

$$\text{ID}(x, y, a, t) = a + x \cdot k + y \cdot W \cdot k + t \cdot L \cdot W \cdot k + 1$$

The encoder in `encode()` then builds the following CNF clauses:

- **Starting positions:** Each agent $a$ starts at $(x_0, y_0) = start(a)$ at $t = 0$:
  $$p_{x_0, y_0, a, 0}$$

- **Target positions:** Each agent $a$ reaches $(x_T, y_T) = target(a)$ at $t = T$:
  $$p_{x_T, y_T, a, T}$$

- **No vertex conflicts:** For any two different agents $a_1$ and $a_2$, cell $(x, y)$, and timestep $t \in \lbrace 0, \dots, T \rbrace$, both agents cannot be on the same cell:
  $$\neg p_{x,y,a_1,t} \vee \neg p_{x,y,a_2,t}$$

- **Valid transitions (move or wait):** If agent $a$ is at $(x, y)$ at timestep $t < T$, in the next step it must either stay at $(x, y)$ or move to one of its accessible orthogonal neighbors $N(x, y)$:
  $$\neg p_{x,y,a,t} \vee p_{x,y,a,t+1} \vee \bigvee_{(x', y') \in N(x, y)} p_{x',y',a,t+1}$$

  Obstacles do not need extra clauses: an agent starts on an open cell (this is checked when the start positions are encoded) and the transition clauses only allow moves to open cells, so it can never get onto an obstacle.

- **At most one position per agent:** At any timestep $t \in \lbrace 0, \dots, T \rbrace$, agent $a$ cannot occupy two different cells $(x_1, y_1) \neq (x_2, y_2)$ at the same time:
  $$\neg p_{x_1,y_1,a,t} \vee \neg p_{x_2,y_2,a,t}$$

- **No edge (swapping) conflicts:** For any two distinct agents $a_1$ and $a_2$, timestep $t < T$, cell $(x_1, y_1)$, and its accessible neighbor $(x_2, y_2) \in N(x_1, y_1)$, they cannot swap positions along that edge in one step:
  $$\neg p_{x_1,y_1,a_1,t} \vee \neg p_{x_2,y_2,a_1,t+1} \vee \neg p_{x_2,y_2,a_2,t} \vee \neg p_{x_1,y_1,a_2,t+1}$$

## Input

The script reads the instance from a plain-text file (`-i`, default "input.in"). Example:

```
4
3
3
...
X.X
XXX
2
0 0 2 0
2 0 0 0
```

- **Line 1:** MAKESPAN, the time limit $T$.
- **Line 2:** Grid width $W$.
- **Line 3:** Grid length $L$.
- **Next $L$ lines:** The map (`.` = open cell, `X` = obstacle).
- **Next line:** Number of agents $k$.
- **Last $k$ lines:** Start and target of each agent in the form `start_x start_y target_x target_y` (coordinates start from 0).

## Output

The script writes the CNF formula in DIMACS format to "formula.cnf" and prints the raw output of the SAT solver. After that it prints the decoded result:

- **SAT (solver exit code 10):** The grid for every timestep from `Timestep 0:` to `Timestep <MAKESPAN>:`, with each agent shown by its index (0, 1, ...) on its current cell.
- **UNSAT:** `No solution for MAKESPAN = <MAKESPAN>`.

The repository contains the SAT solver Glucose Syrup for Linux (`glucose-syrup`, version 4.2.1) and for Windows (`glucose-syrup.exe`).

Usage:

```
python multi_agent_pathfinding.py [-h] [-i INPUT] [-o OUTPUT] [-s SOLVER] [-v {0,1}] [-c]
```

For example, on Linux:

```
python3 multi_agent_pathfinding.py -i instances/small-sat.in
```

on Windows:

```
python multi_agent_pathfinding.py -i instances/small-sat.in -s glucose-syrup.exe
```

- `-h`, `--help`: Show the help message and exit.
- `-i INPUT`, `--input INPUT`: The instance file (default "input.in").
- `-o OUTPUT`, `--output OUTPUT`: Where the DIMACS CNF formula is saved (default "formula.cnf").
- `-s SOLVER`, `--solver SOLVER`: Name of the SAT solver executable in the working directory (default "glucose-syrup", on Windows use "glucose-syrup.exe").
- `-v {0,1}`, `--verb {0,1}`: Verbosity of the SAT solver (0 = minimal output, 1 = solver statistics such as the number of variables and clauses, conflicts and CPU time; default 0).
- `-c`, `--print-cnf`: Also print the CNF formula to standard output before the solver is called.

## Example instances

All instances are in the `instances/` directory. In the previews, `AX` is the start of agent `X`, `TX` is its target, and `AX/TY` is a cell where agent `X` starts and agent `Y` ends. The paths described below are from my runs, the solver may find a different solution. Full outputs of all runs are in [all_runs.md](all_runs.md).

- **`small-unsat.in`** (3 × 1, 2 agents, `MAKESPAN = 2`): Two agents in a corridor want to swap places. There is no place where they could pass each other, so the instance is `UNSAT` for any makespan.

  ```
  A0/T1 .  A1/T0
  ```

- **`small-sat.in`** (3 × 2, 2 agents, `MAKESPAN = 5`): The same swap, but with one open cell below the middle of the corridor. Agent `0` steps down to `(1, 1)` at $t = 2$, agent `1` passes along the top row, and agent `0` then goes back up and reaches `(2, 0)` at $t = 5$. The shortest possible makespan is 4, with `MAKESPAN = 3` the instance is `UNSAT`.

  ```
  A0/T1 .  A1/T0
  X     .  X
  ```

- **`test1-solo.in`** (10 × 10, 1 agent, `MAKESPAN = 18`): One agent goes across an empty grid from `(0, 0)` to `(9, 9)` in 18 steps, which is exactly the Manhattan distance, so 18 is also the shortest possible makespan.

  ```
  A0 .  .  .  .  .  .  .  .  .
  .  .  .  .  .  .  .  .  .  .
  .  .  .  .  .  .  .  .  .  .
  .  .  .  .  .  .  .  .  .  .
  .  .  .  .  .  .  .  .  .  .
  .  .  .  .  .  .  .  .  .  .
  .  .  .  .  .  .  .  .  .  .
  .  .  .  .  .  .  .  .  .  .
  .  .  .  .  .  .  .  .  .  .
  .  .  .  .  .  .  .  .  .  T0
  ```

- **`test2-loop.in`** (5 × 3, 2 agents, `MAKESPAN = 6`): Two agents on opposite sides of a wall (`XXX`) with swapped targets. Agent `0` goes through the lower corridor and agent `1` through the upper one, and both reach their targets at $t = 6$ without waiting. With `MAKESPAN = 5` the instance is `UNSAT`.

  ```
  .     .  .  .  .
  A0/T1 X  X  X  A1/T0
  .     .  .  .  .
  ```

- **`test3-corridor.in`** (7 × 3, 2 agents, `MAKESPAN = 8`): Two agents meet in a corridor one cell wide, with one open cell in the middle. They meet at $t = 3$, agent `0` steps up to `(3, 0)` at $t = 4$, agent `1` passes below it, and both reach their targets at $t = 8$. Going into the open cell and back costs 2 extra steps, so 8 is the shortest possible makespan.

  ```
  X     X  X  .  X  X  X
  A0/T1 .  .  .  .  .  A1/T0
  X     X  X  X  X  X  X
  ```

- **`medium-sat.in`** (10 × 10, 8 agents, `MAKESPAN = 18`): Four pairs of agents go around symmetric obstacle blocks (`XX`) and swap corners by $t = 18$. With `MAKESPAN = 17` the instance is `UNSAT`.

  ```
  A0/T1 .   .   A4/T5 .   .   .   .   .   A2/T3
  .     X   X   .     .   .   .   X   X   .
  .     X   X   .     .   .   .   X   X   .
  A6/T7 .   .   .     .   .   .   .   .   .
  .     .   .   X     X   X   X   .   .   .
  .     .   .   X     X   X   X   .   .   .
  .     .   .   .     .   .   .   .   .   A7/T6
  .     X   X   .     .   .   .   X   X   .
  .     X   X   .     .   .   .   X   X   .
  A3/T2 .   .   .     .   .   T4/A5 .   .   A1/T0
  ```

- **`big-sat.in`** (12 × 12, 16 agents, `MAKESPAN = 24`): 16 agents along all four borders of an empty grid go through the middle to the opposite borders by $t = 24$. The makespan is not tight, the instance is solvable already with `MAKESPAN = 20`, which is the Manhattan distance of the agents on the top and bottom border.

  ```
  .     A0/T5 .     A1/T6 .     A2/T7 .     A3/T8 .     A4/T9 .     .
  .     .     .     .     .     .     .     .     .     .     .     .
  A10   .     .     .     .     .     .     .     .     .     .     A13
  T15   .     .     .     .     .     .     .     .     .     .     T12
  .     .     .     .     .     .     .     .     .     .     .     .
  A11   .     .     .     .     .     .     .     .     .     .     A14
  T14   .     .     .     .     .     .     .     .     .     .     T11
  .     .     .     .     .     .     .     .     .     .     .     .
  A12   .     .     .     .     .     .     .     .     .     .     A15
  T13   .     .     .     .     .     .     .     .     .     .     T10
  .     .     .     .     .     .     .     .     .     .     .     .
  .     A5/T0 .     A6/T1 .     A7/T2 .     A8/T3 .     A9/T4 .     .
  ```

- **`CRAZY-sat.in`** (15 × 14, 22 agents, `MAKESPAN = 29`): The largest instance. 22 agents on an irregular map with many narrow passages. This is the instance where the solver alone runs for more than 10 s.

  ```
  .     T7    X     .     .     .     A10   X     .     X     .     A17   T11   .     .
  T4    T0    .     .     .     .     .     .     .     X     .     T15   .     T21   .
  X     X     A13   A3    X     .     .     .     .     .     .     X     T20   .     .
  .     .     .     .     .     X     .     .     .     X     .     .     .     A5    .
  .     X     .     .     X     .     .     .     .     .     .     A12   T8    .     .
  T6    .     X     .     .     .     .     X     .     X     .     .     A9    .     .
  .     T9    .     X     .     .     .     .     .     .     X     .     X     .     .
  A11   .     .     X     A16   .     .     .     .     X     .     .     .     X     .
  .     X     .     A1    .     .     .     X     .     X     X     .     .     .     A19
  .     X     .     .     .     A14   X     X     X     X     A0    .     A6    A7    .
  .     .     A15   A20   .     .     .     .     .     .     A4    X     X     .     .
  T5    .     .     X     .     .     .     .     .     .     X     X     .     .     .
  .     T12   .     .     .     X     .     T17   .     X     .     T16   T3    T13   .
  A2    A21   .     A18   .     A8    .     .     .     X     .     T1    T10   .     .
  ```

## Experiments

Experiments were run on Windows 11 with an AMD Ryzen 9 8945H (4.00 GHz) CPU and 16 GB RAM.

Total time was measured in PowerShell with `System.Diagnostics.Stopwatch` for the whole run (loading the instance, generating the CNF and writing it to a file, running `glucose-syrup.exe`, and decoding the result). Solver time is the time reported by `glucose-syrup` (for `small-unsat.in` it reports no time, the formula is UNSAT right away).

| Instance | Grid ($W \times L$) | Agents ($k$) | Makespan ($T$) | Variables | Clauses | Result | Solver Time (s) | Total Time (s) |
|:---------|:-------------------:|-------------:|---------------:|----------:|--------:|:------:|----------------:|---------------:|
| `small-unsat.in` | 3 × 1 | 2 | 2 | 18 | 69 | UNSAT | - | 0.08 |
| `small-sat.in` | 3 × 2 | 2 | 5 | 72 | 510 | SAT | < 0.01 | 0.08 |
| `test2-loop.in` | 5 × 3 | 2 | 6 | 210 | 3,421 | SAT | 0.01 | 0.09 |
| `test3-corridor.in` | 7 × 3 | 2 | 8 | 378 | 8,321 | SAT | 0.01 | 0.09 |
| `test1-solo.in` | 10 × 10 | 1 | 18 | 1,900 | 189,902 | SAT | 0.07 | 0.41 |
| `medium-sat.in` | 10 × 10 | 8 | 18 | 15,200 | 1,705,472 | SAT | 0.85 | 3.85 |
| `big-sat.in` | 12 × 12 | 16 | 24 | 57,600 | 10,244,768 | SAT | 1.80 | 19.94 |
| `CRAZY-sat.in` | 15 × 14 | 22 | 29 | 138,600 | 34,810,589 | SAT | 11.15 | 79.38 |

The solver itself is fast even on the largest instances, but most of the total time is spent generating the CNF and writing it to the file.