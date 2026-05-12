# Refactored Pac-Man Structure Guide

## File Organization

Your game is now split into logical, maintainable modules:

### **config.py** - Configuration & Constants
- All game settings (tile size, screen dimensions, FPS)
- Color palette
- Fonts
- Direction vectors
- Ghost configuration
- Player settings

**Use this to:** Adjust game difficulty, change colors, modify speeds, add new ghosts

---

### **map.py** - Map Logic & Tile Utilities
- Game map data
- Map parsing (`parse_game_map`)
- Tile helper functions
  - `tile_center()` - Get pixel center of a tile
  - `is_walkable()` - Check if player can walk there
  - `is_ghost_walkable()` - Check if ghost can walk there
  - `wrap_tile()` - Handle map wrapping
  - `ghost_neighbors()` - Get valid adjacent tiles

**Use this to:** Modify the game map, change walkability rules, adjust wrapping behavior

---

### **pathfinding.py** - AI Algorithms
- A* pathfinding algorithm
- Breadth-First Search (BFS)
- Dijkstra's algorithm
- Helper functions for pathfinding

**Use this to:** Modify ghost AI behavior, add new pathfinding algorithms, adjust chase patterns

---

### **player.py** - Player Logic
- `PlayerState` class - Encapsulates all player data
  - Position, movement, score, lives
  - Methods: `update()`, `eat_pellets()`, `reset_position()`, `start_step()`

**Use this to:** Change player movement speed, modify collision detection, adjust scoring

---

### **ghost.py** - Ghost Logic
- Ghost creation and initialization
- Ghost position reset
- Ghost behavior functions
- `update_ghost()` - Main ghost update logic

**Use this to:** Modify ghost behavior, change ghost AI, adjust ghost speeds

---

### **game_state.py** - Game State Management
- `GameState` class - Central state manager
  - Manages walls, pellets, player, ghosts
  - Game state transitions (countdown → playing → dying → game_over)
  - Methods: `restart_game()`, `reset_round()`, `handle_death()`, `activate_power_mode()`

**Use this to:** Add new game states, modify game logic flow, add features

---

### **render.py** - Drawing & Graphics
- All drawing functions:
  - `draw_background()`, `draw_walls()`, `draw_pellets()`
  - `draw_player()`, `draw_ghosts()`
  - `draw_hud()`, `draw_win_message()`, `draw_game_over_message()`
  - Animation functions

**Use this to:** Modify visuals, change colors, add new graphics, adjust animations

---

### **main.py** - Game Loop & Entry Point
- Main game loop
- Event handling (keyboard input)
- Game logic orchestration
- Collision detection
- Run this file to start the game: `python main.py`

**Use this to:** Adjust game loop timing, add new game mechanics, modify inputs

---

## How to Extend

### Add a New Ghost Algorithm
1. Add the algorithm to `pathfinding.py`
2. Update `find_path()` to route to it
3. Add ghost config to `GHOSTS_CONFIG` in `config.py`

### Change Game Difficulty
1. Modify speeds in `config.py` (PLAYER_SPEED, ghost "speed" values)
2. Adjust release timings in `GHOSTS_CONFIG`
3. Modify `FRIGHTENED_DURATION` for power-up timing

### Modify the Map
1. Edit `GAME_MAP` in `map.py`
2. Symbols:
   - `#` = Wall
   - `.` = Pellet
   - `o` = Power Pellet
   - `P` = Player spawn
   - ` ` = Empty path

### Add Visual Features
1. Create drawing functions in `render.py`
2. Call them from `main.py` in the render section

---

## Dependencies
- pygame (for graphics and input)
- heapq (for A* and Dijkstra)
- collections.deque (for BFS)

All modules are self-contained and interact through clean interfaces!
