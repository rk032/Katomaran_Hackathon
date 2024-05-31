import pygame
import random
import sys
from queue import PriorityQueue
import time
import tkinter as tk
from tkinter import messagebox

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 10, 10
CELL_SIZE = WIDTH // COLS
FPS = 5  # Lower FPS to slow down the animation

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Initialize Pygame
def initialize_pygame():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Robot Navigation")
    return screen

# Load and scale the robot image
def load_robot_image():
    robot_img = pygame.image.load("robot.jpg")
    robot_img = pygame.transform.scale(robot_img, (CELL_SIZE, CELL_SIZE))
    return robot_img

# Load and scale the grass image
def load_grass_image():
    grass_img = pygame.image.load("grass.jpg")
    grass_img = pygame.transform.scale(grass_img, (CELL_SIZE, CELL_SIZE))
    return grass_img

# A* Algorithm functions
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(came_from, current):
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    total_path.reverse()
    return total_path

def a_star_search(start, end, grid):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    open_set_hash = {start}

    while not open_set.empty():
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            return reconstruct_path(came_from, current)

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLS and grid[neighbor[0]][neighbor[1]] != "grass":
                temp_g_score = g_score[current] + 1

                if neighbor not in g_score or temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + heuristic(neighbor, end)
                    if neighbor not in open_set_hash:
                        count += 1
                        open_set.put((f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)
    return []

# Draw grid
def draw_grid(screen, grid, grass_img):
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] == "grass":
                screen.blit(grass_img, (col * CELL_SIZE, row * CELL_SIZE))
            else:
                pygame.draw.rect(screen, grid[row][col], (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

def validate_path(path, grid):
    for row, col in path:
        if not (0 <= row < ROWS and 0 <= col < COLS) or grid[row][col] == "grass":
            return False
    return True

# Main function
def main(start, end):
    global grid
    screen = initialize_pygame()
    robot_img = load_robot_image()
    grass_img = load_grass_image()

    # Reset grid for new inputs
    grid = [[WHITE for _ in range(COLS)] for _ in range(ROWS)]

    # Generate obstacles
    obstacles = 0
    while obstacles < 30:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)
        if (y, x) != start and (y, x) != end and grid[y][x] != "grass":
            grid[y][x] = "grass"
            obstacles += 1

    grid[start[0]][start[1]] = GREEN  # Start point
    grid[end[0]][end[1]] = RED  # End point
    path = a_star_search(start, end, grid)
    if not path or not validate_path(path, grid):
        print("No valid path found! Please enter another set of start and end points.")
        return
    print("The path: ",path)
    clock = pygame.time.Clock()
    running = True

    current_step = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

        screen.fill(WHITE)
        draw_grid(screen, grid, grass_img)

        # Draw the path step by step
        if current_step < len(path):
            row, col = path[current_step]
            if (row, col) not in [start, end]:
                grid[row][col] = BLUE
            screen.blit(robot_img, (col * CELL_SIZE, row * CELL_SIZE))
            current_step += 1

        pygame.display.flip()
        clock.tick(FPS)
        time.sleep(0.5)  # Adding a delay to further slow down the robot's movement

def get_input():
    def on_submit():
        try:
            start_x = int(start_x_entry.get())
            start_y = int(start_y_entry.get())
            end_x = int(end_x_entry.get())
            end_y = int(end_y_entry.get())

            if not (0 <= start_x < ROWS and 0 <= start_y < COLS and 0 <= end_x < ROWS and 0 <= end_y < COLS):
                raise ValueError

            root.destroy()
            main((start_x, start_y), (end_x, end_y))
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid coordinates within the range (0-9).")

    root = tk.Tk()
    root.title("Input Start and End Points")
    root.geometry("400x300")

    # Centering frame
    frame = tk.Frame(root)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    tk.Label(frame, text="Start X:").grid(row=0, column=0, pady=10)
    start_x_entry = tk.Entry(frame, width=10)
    start_x_entry.grid(row=0, column=1, pady=10)

    tk.Label(frame, text="Start Y:").grid(row=1, column=0, pady=10)
    start_y_entry = tk.Entry(frame, width=10)
    start_y_entry.grid(row=1, column=1, pady=10)

    tk.Label(frame, text="End X:").grid(row=2, column=0, pady=10)
    end_x_entry = tk.Entry(frame, width=10)
    end_x_entry.grid(row=2, column=1, pady=10)

    tk.Label(frame, text="End Y:").grid(row=3, column=0, pady=10)
    end_y_entry = tk.Entry(frame, width=10)
    end_y_entry.grid(row=3, column=1, pady=10)

    submit_button = tk.Button(frame, text="Submit", command=on_submit)
    submit_button.grid(row=4, columnspan=2, pady=20)

    root.mainloop()

if __name__ == "__main__":
    get_input()
