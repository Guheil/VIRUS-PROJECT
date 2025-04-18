# VIRUS-PROJECT

A thrilling top-down shooter game where you battle against waves of enemies and challenging boss fights in a cyberpunk-themed environment.

## Features

- Fast-paced top-down shooter gameplay
- Dynamic enemy spawning system
- Boss battles with unique attack patterns
- Health system and score tracking
- Scrolling starfield background
- Smooth player movement and shooting mechanics

## Controls

- **W** - Move Up
- **S** - Move Down
- **A** - Move Left
- **D** - Move Right

## Installation

1. Clone this repository
2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Dependencies

- Python 3.x
- pygame >= 2.5.2
- python-vlc >= 3.0.20123
- pyinstaller >= 5.13.0

## Running the Game

1. Navigate to the script directory
2. Run the game:
   ```
   python main.py
   ```

## Building Executable

To create a standalone executable:

```
pyinstaller --onefile script/main.py
```

The executable will be created in the `dist` directory.

## Development

The game is built using Python and Pygame, featuring:
- Object-oriented design with sprite-based game objects
- Collision detection system
- Enemy AI with tracking behavior
- Boss battles with multiple attack patterns
- Particle effects and smooth animations

## License

This project is licensed under the MIT License - see the LICENSE file for details.