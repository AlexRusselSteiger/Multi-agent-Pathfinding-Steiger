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

For each cell $(x, y)$, agent $a \in \lbrace 0, \dots, k-1 \rbrace$, and timestep $t \in \lbrace 0, \dots, T \rbrace$, we have a variable $p_{x,y,a,t}$, which means that agent $a$ is at cell $(x, y)$ at time $t$, `position_to_ID(x, y, agent, time)` then gives each variable $p_{x,y,a,t}$ a unique ID:

$$\text{ID}(x, y, a, t) = a + x \cdot k + y \cdot W \cdot k + t \cdot L \cdot W \cdot k + 1$$

The encoder in `encode()` then builds the following CNF clauses:

- **Starting positions:** Each agent $a$ starts at $(x_0, y_0) = start(a)$ at $t = 0$:
  $$p_{x_0, y_0, a, 0}$$

- **Target positions:** Each agent $a$ reaches $(x_T, y_T) = target(a)$ at $t = T$:
  $$p_{x_T, y_T, a, T}$$

- **No vertex conflicts:** For any two different agents $a_1 and a_2$, cell $(x, y)$, and timestep $t \in \lbrace 0, \dots, T \rbrace$, both agents cannot be on the same cell:
  $$\neg p_{x,y,a_1,t} \vee \neg p_{x,y,a_2,t}$$

- **Valid transitions (move or wait):** If agent $a$ is at $(x, y)$ at timestep $t < T$, in the next step it must either stay at $(x, y)$ or move to one of its accessible orthogonal neighbors $N(x, y)$:
  $$\neg p_{x,y,a,t} \vee p_{x,y,a,t+1} \vee \bigvee_{(x', y') \in N(x, y)} p_{x',y',a,t+1}$$

- **At most one position per agent:** At any timestep $t \in \lbrace 0, \dots, T \rbrace$, agent $a$ cannot occupy two different cells $(x_1, y_1) \neq (x_2, y_2)$ at the same time:
  $$\neg p_{x_1,y_1,a,t} \vee \neg p_{x_2,y_2,a,t}$$

- **No edge (swapping) conflicts:** For any two distinct agents $a_1 and a_2$, timestep $t < T$, cell $(x_1, y_1)$, and its accessible neighbor $(x_2, y_2) \in N(x_1, y_1)$, they cannot swap positions along that edge in one step:
  $$\neg p_{x_1,y_1,a_1,t} \vee \neg p_{x_2,y_2,a_1,t+1} \vee \neg p_{x_2,y_2,a_2,t} \vee \neg p_{x_1,y_1,a_2,t+1}$$