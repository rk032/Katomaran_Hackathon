import pygame
import random
import sys
from queue import PriorityQueue
import time
import tkinter as tk
from tkinter import messagebox

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 40, 40
CELL_SIZE = WIDTH // COLS
FPS = 5  # Lower FPS to slow down the animation

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)  # Yellow color for obstacles

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
            if 0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLS and grid[neighbor[0]][neighbor[1]] != YELLOW:
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
            if grid[row][col] == WHITE:
                screen.blit(grass_img, (col * CELL_SIZE, row * CELL_SIZE))
            elif grid[row][col] == YELLOW:
                pygame.draw.rect(screen, YELLOW, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            else:
                pygame.draw.rect(screen, grid[row][col], (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

def validate_path(path, grid):
    for row, col in path:
        if not (0 <= row < ROWS and 0 <= col < COLS) or grid[row][col] == YELLOW:
            return False
    return True

def point_in_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    y_=[]
    x_=[]
    for i in range(n):
        y_.append(polygon[i][1])
        x_.append(polygon[i][0])
    if (x >=min(x_)) and (x<=max(x_)) and (y>=min(y_)) and (y<=max(y_)):
        return True
    return False
def find_valid_start(pillar_vertices):
    while True:
        position = [random.randint(0, ROWS - 1), random.randint(0, COLS - 1)]
        if not point_in_polygon(position, pillar_vertices):
            return position

def calculate_center(vertices):
    min_x = min(vertices, key=lambda v: v[0])[0]
    max_x = max(vertices, key=lambda v: v[0])[0]
    min_y = min(vertices, key=lambda v: v[1])[1]
    max_y = max(vertices, key=lambda v: v[1])[1]
    center_x = (min_x + max_x) // 2
    center_y = (min_y + max_y) // 2
    return (center_x, center_y)

# Main function
def main(vertices):
    global grid
    screen = initialize_pygame()
    robot_img = load_robot_image()
    grass_img = load_grass_image()

    # Reset grid for new inputs
    grid = [[WHITE for _ in range(COLS)] for _ in range(ROWS)]

    for i in vertices:
        grid[i[0]][i[1]] = YELLOW

    start = find_valid_start(vertices)
    end = calculate_center(vertices)
    path = a_star_search(tuple(start), tuple(end), grid)
    if not path or not validate_path(path, grid):
        print("No valid path found! Please enter another set of start and end points.")
        return

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
    vertices = []

    def on_submit():
        try:
            for i in range(4):
                x = int(entries[i * 2].get())
                y = int(entries[i * 2 + 1].get())
                if 0 <= x < ROWS and 0 <= y < COLS:
                    vertices.append((x, y))
                else:
                    raise ValueError("Coordinates out of grid bounds")
            root.destroy()
        except ValueError as e:
            messagebox.showerror("Invalid input", f"Invalid input: {e}. Please try again.")

    root = tk.Tk()
    root.title("Enter Vertices")

    entries = []
    for i in range(4):
        tk.Label(root, text=f"Enter vertex {i+1} (x y):").grid(row=i, column=0)
        entry_x = tk.Entry(root)
        entry_y = tk.Entry(root)
        entry_x.grid(row=i, column=1)
        entry_y.grid(row=i, column=2)
        entries.append(entry_x)
        entries.append(entry_y)

    submit_button = tk.Button(root, text="Submit", command=on_submit)
    submit_button.grid(row=4, columnspan=3)

    root.mainloop()
    main(vertices)

if __name__ == "__main__":
    get_input()
