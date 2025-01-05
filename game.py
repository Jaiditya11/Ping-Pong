import pygame
import socketio
import random
import asyncio
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 15
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60
PADDLE_MOVE_DELAY = 1/30  # Limit paddle movement updates

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping Pong Game")

# Initialize Socket.IO client
# sio = socketio.Client()
# sio.connect('http://localhost:5002')
sio = socketio.Client()
try:
    sio.connect('http://localhost:5002')
except Exception as e:
    print(f"Failed to connect to server: {e}")
    pygame.quit()
    exit(1)

# Game state variables
ball_position = [400, 300]
ball_velocity = [5, 5]
paddle_positions = [[50, 250], [750, 250]]
scores = [0, 0]

class GameState:
    def __init__(self):
        self.last_paddle_update = 0
        self.last_state = None

game_state = GameState()

def draw():
    # Clear screen with black background
    screen.fill(BLACK)  
    
    # Draw obstacles
    if game_state.last_state and 'obstacles' in game_state.last_state:
        for obstacle in game_state.last_state['obstacles']:
            pygame.draw.rect(screen, WHITE, (obstacle[0], obstacle[1], obstacle[2], obstacle[3]))
    
    # Draw ball (white circle)
    pygame.draw.circle(screen, WHITE, [int(ball_position[0]), int(ball_position[1])], BALL_RADIUS)
    
    # Draw paddles (white rectangles)
    pygame.draw.rect(screen, WHITE, (paddle_positions[0][0], paddle_positions[0][1], PADDLE_WIDTH, PADDLE_HEIGHT))  # Left paddle
    pygame.draw.rect(screen, WHITE, (paddle_positions[1][0], paddle_positions[1][1], PADDLE_WIDTH, PADDLE_HEIGHT))  # Right paddle
    
    # Draw scores
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"{scores[0]} - {scores[1]}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
    
    # Make sure we're actually updating the display
    pygame.display.flip()

@sio.on('update_game_state')
def update_game_state(state):
    global ball_position, paddle_positions, scores
    # Only update if the state has changed
    if state != game_state.last_state:
        ball_position = state['ball_position']
        paddle_positions = state['paddle_positions']
        scores = state['scores']
        game_state.last_state = state

async def main():
    clock = pygame.time.Clock()
    
    running = True
    while running:
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sio.disconnect()
                pygame.quit()
                return
        
        # Handle paddle movement with rate limiting
        if current_time - game_state.last_paddle_update >= PADDLE_MOVE_DELAY:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                sio.emit('move_paddle', {'player_id': 0, 'direction': 'up'})
            if keys[pygame.K_s]:
                sio.emit('move_paddle', {'player_id': 0, 'direction': 'down'})
            if keys[pygame.K_UP]:
                sio.emit('move_paddle', {'player_id': 1, 'direction': 'up'})
            if keys[pygame.K_DOWN]:
                sio.emit('move_paddle', {'player_id': 1, 'direction': 'down'})
            game_state.last_paddle_update = current_time

        draw()
        clock.tick(FPS)  # Maintain consistent frame rate
        await asyncio.sleep(0)

if __name__ == "__main__":
   asyncio.run(main())
