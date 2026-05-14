# PacManWakawakaDAA

PacManWakawakaDAA is a Pac-Man style game built with Python and Pygame for the Design & Analysis of Algorithms course. The project focuses on applying graph traversal and pathfinding algorithms in a playable maze game.

## Course Information

**Class Code:** EF234405  
**Class:** Design & Analysis of Algorithms (E)  
**Lecturer:** Irfan Subakti

## Team Members

| Name | NRP |
| --- | --- |
| Muhammad Daffa Nurrahman | 5025231208 |
| Muhammad Naufal Dzakwan | 5025231234 |
| Muhammad Rafi Budiman | 5025231297 |

## Features

- Pac-Man style maze gameplay using Pygame.
- Player movement and collision handling.
- Ghost behavior powered by pathfinding algorithms.
- Algorithm comparison report output.
- Metrics collection for algorithm performance.

## Algorithms

This project is used to demonstrate and compare pathfinding algorithms in a maze environment:

- **BFS (Breadth-First Search):** Finds the shortest path in an unweighted graph.
- **DFS (Depth-First Search):** Explores paths deeply before backtracking.
- __A* Search:__ Uses a heuristic to find an efficient shortest path.
- **Dijkstra's Algorithm:** Finds shortest paths based on accumulated cost.

## Project Structure

```text
PacManWakawakaDAA/
|-- algorithm/
|   |-- analysis.py
|   |-- pathfinding.py
|-- character/
|   |-- ghost.py
|   |-- player.py
|-- logic/
|   |-- audio.py
|   |-- game_state.py
|   |-- render.py
|-- sounds/
|-- config.py
|-- main.py
|-- map.py
|-- requirements.txt
|-- algorithm_metrics.csv
|-- algorithm_report.txt
```

## Requirements

- Python 3.10 or newer
- Pygame

Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Run

Run the game from the project root:

```bash
python main.py
```

## Report Files

- `algorithm_metrics.csv`: stores collected algorithm performance metrics.
- `algorithm_report.txt`: contains generated analysis results.

## Gallery
Main Menu <br>
<img width="533" height="653" alt="image" src="https://github.com/user-attachments/assets/1639ced3-74d8-443d-8f9a-94aa4af2477d" />

Maze 1 <br>
<img width="530" height="657" alt="image" src="https://github.com/user-attachments/assets/ebafc811-a0ad-4707-85e8-8c3bbe5ecd15" />

Maze 2 <br>
<img width="531" height="652" alt="image" src="https://github.com/user-attachments/assets/c2c35f98-5b6c-4a2f-93fb-42685d2ced20" />

Maze 3 <br>
<img width="531" height="652" alt="image" src="https://github.com/user-attachments/assets/743d0fae-2a5c-4d03-a4a4-d55508a1d822" />

Maze 4 <br>
<img width="533" height="651" alt="image" src="https://github.com/user-attachments/assets/76decc2c-9646-4dbb-a8fe-3f7574ac469c" />
