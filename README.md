# Multi-agent-Pathfinding-Steiger

## Problem description

The Multi-agent Pathfinding task is about finding paths for $k$ agents $A = \{0, 1, \dots, k-1\}$ in a 2D grid of size $W \times L$ (width $\times$ length) from their starting positions to their target destinations. Each cell $(x, y)$ in the grid is either open (`.`) or blocked by an obstacle (`X`).

There are several variations of MAPF. The one implemented here has the following rules:
1. **Allowed moves:** At each timestep, an agent can either move orthogonally (up, down, left, right) to an adjacent open cell, or wait on its current cell.
2. **Makespan limit:** There is a time limit $T$ (`MAKESPAN`). Every agent starts at its initial coordinate $start(a)$ at timestep $t = 0$ and must reach its destination $target(a)$ at timestep $t = T$. If the agents cannot reach their targets within $T$ steps, the instance is unsolvable (`UNSAT`).
3. **Forbidden conflicts:**
   - **Obstacle collision:** Agents cannot enter or pass through cells occupied by obstacles (`X`).
   - **Vertex conflict:** Two different agents cannot occupy the same cell $(x, y)$ at the same timestep $t$.
   - **Edge (swapping) conflict:** Two different agents cannot swap positions along the same edge between adjacent cells in a single timestep (i.e., moving from $(x_1, y_1)$ to $(x_2, y_2)$ while another agent moves from $(x_2, y_2)$ to $(x_1, y_1)$ at the same time).
