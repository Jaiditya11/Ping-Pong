# Ping-Pong
A real-time multiplayer Pong game implementation using Python, Flask, Socket.IO, and Pygame. The game features the classic Pong gameplay with additional obstacles for increased challenge.
## Features

- Real-time multiplayer gameplay
- Classic Pong mechanics
- Random obstacles for added difficulty
- Score tracking
- Support for both web browser and Python client

## Prerequisites

- Python 3.7+
- Pygame
- Flask
- Flask-SocketIO
- Python-SocketIO

## Installation

1. Clone the repository
2.  Install the required dependencies:
   ```bash
pip install pygame flask flask-socketio python-socketio
```
## Running the Game

1. Start the server:
   ```bash
   python server.py
   ```
2. Run Pygame:
   ```bash
   python game.py
   ```
2. To play, you have two options:

### Web Browser
- Open `http://localhost:5002` in your web browser
- Multiple players can join from different browsers

## Controls

- **Player 1:**
  - W: Move paddle up
  - S: Move paddle down

- **Player 2:**
  - ↑ (Up Arrow): Move paddle up
  - ↓ (Down Arrow): Move paddle down

## Game Rules

- Each player controls a paddle on their side of the screen
- The ball bounces off paddles and walls
- Random obstacles appear in the middle of the field
- Score points when the ball passes your opponent's paddle
- The ball resets to the center after each point
- Ball direction is randomized after each reset

## Technical Details

- Server runs on Flask with Socket.IO for real-time communication
- Supports both web and Python clients simultaneously
- Game state updates at 60 FPS
- Implements collision detection for paddles, walls, and obstacles
- Uses threading for game loop management


