# Monte Carlo Tree Search (MCTS)

Monte Carlo Tree Search (MCTS) is a heuristic search algorithm used for decision-making in games and planning problems. It combines the precision of tree search with the efficiency of random sampling to find good moves without exhaustively evaluating every possibility.

## Core Idea

Instead of analyzing every possible future state (which is computationally infeasible in complex games), MCTS runs many random simulations ("playouts") to estimate which moves are most promising, then focuses exploration on those.

## The Four Phases

Each iteration of MCTS repeats four steps:

1. **Selection** — Starting from the root (current state), traverse the tree by picking children according to a selection policy until you reach a node that hasn't been fully expanded. The most common policy is **UCB1** (Upper Confidence Bound), which balances exploitation (visiting known good nodes) with exploration (trying less-visited ones).
2. **Expansion** — Add one or more child nodes to the tree representing new, unexplored states.
3. **Simulation (Rollout)** — From the new node, play out the game randomly (or with a heuristic) until a terminal state is reached (win/loss/draw).
4. **Backpropagation** — Propagate the result back up the tree, updating each ancestor node's visit count and win statistics.

After many iterations, the move with the highest visit count (or win rate) from the root is chosen.

## Why It Works

- **No need for a hand-crafted evaluation function** — the random rollouts provide a statistical estimate of value.
- **Asymmetric tree growth** — it naturally focuses computation on promising branches.
- **Anytime algorithm** — you can stop it at any point and get the best answer found so far.

## Famous Applications

- **Go** — AlphaGo (DeepMind) used MCTS combined with neural networks to defeat world champions, a landmark AI achievement.
- **Chess & Shogi** — AlphaZero extended this approach across multiple games.
- **Video games** — Used in real-time strategy and puzzle games.
- **General planning** — Robotics, scheduling, and combinatorial optimization.

## Key Tradeoff

MCTS trades exactness for scalability. It won't always find the optimal move, but it finds very good moves efficiently in state spaces too large for exhaustive search — like Go, which has more possible positions than atoms in the observable universe.
