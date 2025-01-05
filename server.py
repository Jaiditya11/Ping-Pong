from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import random
import time
from threading import Thread

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")
HEIGHT = 600
BALL_SPEED = 5.0
PADDLE_SPEED = 25
FPS = 60
# Game state
def init_game_state():
    return {
        'ball_position': [400, 300],
        'ball_velocity': [BALL_SPEED, BALL_SPEED],
        'paddle_positions': [[50, 250], [750, 250]],
        'scores': [0, 0],
        'obstacles': [
            # Smaller obstacles: reduced width from 20 to 10, height from 100 to 60
            [random.randint(300, 500), random.randint(100, 500), 10, 60],  # [x, y, width, height]
            [random.randint(300, 500), random.randint(100, 500), 10, 60]
        ]
    }

game_state = init_game_state()


@app.route('/')
def index():
    return render_template('index.html')

def game_loop():
    """Continuous game loop to update and broadcast game state"""
    last_update = time.time()
    while True:
        try:
            current_time = time.time()
            elapsed = current_time - last_update
            
            if elapsed >= 1/FPS:  # Only update if enough time has passed
                update_ball()
                socketio.emit('update_game_state', game_state)
                last_update = current_time
            else:
                time.sleep(0.001)  # Small sleep to prevent CPU overload
                
        except Exception as e:
            print(f"Error in game loop: {e}")
            time.sleep(0.1)

@socketio.on('move_paddle')
def handle_move_paddle(data):
    try:
        player_id = data['player_id']
        direction = data['direction']
        
        # Use PADDLE_SPEED constant for smoother movement
        if direction == 'up':
            game_state['paddle_positions'][player_id][1] = max(
                0, 
                game_state['paddle_positions'][player_id][1] - PADDLE_SPEED
            )
        elif direction == 'down':
            game_state['paddle_positions'][player_id][1] = min(
                HEIGHT - 100, 
                game_state['paddle_positions'][player_id][1] + PADDLE_SPEED
            )
        
        socketio.emit('update_game_state', game_state)
    except Exception as e:
        print(f"Error moving paddle: {e}")

def update_ball():
    global game_state
    try:
        # Update ball position
        game_state['ball_position'][0] += game_state['ball_velocity'][0]
        game_state['ball_position'][1] += game_state['ball_velocity'][1]

        # Ball collision with obstacles
        ball_x = game_state['ball_position'][0]
        ball_y = game_state['ball_position'][1]
        
        for obstacle in game_state['obstacles']:
            if (ball_x + 15 >= obstacle[0] and 
                ball_x - 15 <= obstacle[0] + obstacle[2] and 
                ball_y + 15 >= obstacle[1] and 
                ball_y - 15 <= obstacle[1] + obstacle[3]):
                # Determine which side of the obstacle was hit
                if abs(ball_x - obstacle[0]) <= 15 or abs(ball_x - (obstacle[0] + obstacle[2])) <= 15:
                    game_state['ball_velocity'][0] *= -1
                else:
                    game_state['ball_velocity'][1] *= -1

        # Ball collision with top and bottom walls
        if game_state['ball_position'][1] <= 15 or game_state['ball_position'][1] >= 585:
            game_state['ball_velocity'][1] *= -1

        # Improved paddle collision detection
        left_paddle = game_state['paddle_positions'][0]
        right_paddle = game_state['paddle_positions'][1]
        ball_x = game_state['ball_position'][0]
        ball_y = game_state['ball_position'][1]

        # Left paddle collision
        if (ball_x <= left_paddle[0] + 15 and 
            ball_x >= left_paddle[0] and 
            left_paddle[1] <= ball_y <= left_paddle[1] + 100):
            game_state['ball_velocity'][0] = abs(game_state['ball_velocity'][0])  # Move right
            
        # Right paddle collision
        if (ball_x >= right_paddle[0] - 15 and 
            ball_x <= right_paddle[0] + 10 and 
            right_paddle[1] <= ball_y <= right_paddle[1] + 100):
            game_state['ball_velocity'][0] = -abs(game_state['ball_velocity'][0])  # Move left

        # Score updates - only when ball completely passes the paddle
        if ball_x < 0:  # Ball passed left paddle
            game_state['scores'][1] += 1  # Player 2 scores
            reset_ball()
        elif ball_x > 800:  # Ball passed right paddle
            game_state['scores'][0] += 1  # Player 1 scores
            reset_ball()
            
    except Exception as e:
        print(f"Error updating ball: {e}")

def reset_ball():
    """Reset the ball to the center of the screen with a random direction."""
    game_state['ball_position'] = [400, 300]
    # Ensure consistent ball speed
    direction_x = random.choice([-1, 1])
    direction_y = random.uniform(-0.8, 0.8)  # Add some randomness to vertical direction
    game_state['ball_velocity'] = [
        BALL_SPEED * direction_x,
        BALL_SPEED * direction_y
    ]


@socketio.on('connect')
def handle_connect():
    print("A player has connected.")
    # Reset the game state when a new connection is made
    global game_state
    game_state = init_game_state()
    emit('update_game_state', game_state)

@socketio.on('disconnect')
def handle_disconnect():
    print("A player has disconnected.")

# if __name__ == '__main__':
#     socketio.run(app)
    #     update_ball()
    #     print("Broadcasting game state:", game_state)
    #     socketio.emit('update_game_state', game_state)
    #     time.sleep(1/60)  # 60 FPS

if __name__ == '__main__':
    # Start the game loop in a separate thread
    game_thread = Thread(target=game_loop)
    game_thread.daemon = True
    game_thread.start()
    
    # Add host and port parameters to make the server accessible
    socketio.run(app, host='0.0.0.0', port=5002, debug=False)  # Set debug to False for production