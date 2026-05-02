import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 500
TILE = 40

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

P = (108,0,108)
R = (255,0,0)
O = (255,100,100)
G = (0,255,0)
BG = (30,30,30)
W = (255,255,255)

font = pygame.font.SysFont(None, 28)

title_font = font
title_surface = title_font.render("GAMMA's Clone Game", True, P)
title_rect = title_surface.get_rect(topleft=(10, 10))

# player stuff
player_x, player_y = 0, 0
speed = 2

# clone stuff
clone_active = False
clone_x, clone_y = 0, 0

camera_x, camera_y = 0, 0


def generate_map():
    cols, rows = 30, 20

    for _ in range(100):  # try multiple times cuz sometimes it just gives garbage
        grid = [[1 for _ in range(cols)] for _ in range(rows)]

        x, y = 2, 10  # spawn on left side
        path = [(x, y)]
        grid[y][x] = 0

        direction = random.choice([(1,0),(0,1),(0,-1)])

        # making a zigzag path not a  straight line path
        for _ in range(12):
            length = random.randint(4, 7)

            for _ in range(length):
                nx, ny = x + direction[0], y + direction[1]

                if 2 < nx < cols-2 and 2 < ny < rows-2:
                    x, y = nx, ny
                    path.append((x, y))
                    grid[y][x] = 0
                else:
                    break

            if direction in [(1,0),(-1,0)]:
                direction = random.choice([(0,1),(0,-1)])
            else:
                direction = random.choice([(1,0),(-1,0)])

        # if path too small its useless so retry
        if len(path) < 20:
            continue

        path_len = len(path)

        # plate comes front
        plate_index = int(path_len * random.uniform(0.2, 0.3))

        # door comes later so player actually uses the clone
        door_index = int(path_len * random.uniform(0.45, 0.6))

        # just making sure indices dont break stuff
        plate_index = max(2, min(plate_index, path_len - 5))
        door_index = max(plate_index + 5, min(door_index, path_len - 2))

        start_pos = path[0]
        plate_pos = path[plate_index]
        door_pos  = path[door_index]
        goal_pos  = path[-1]  # ALWAYS last point (end of path)

        # extra check: goal should be far from start or its boring af
        dist = abs(goal_pos[0] - start_pos[0]) + abs(goal_pos[1] - start_pos[1])
        if dist < 15:
            continue

        return grid, start_pos, plate_pos, door_pos, goal_pos

    # fallback
    grid = [[1 for _ in range(cols)] for _ in range(rows)]
    path = []

    for i in range(2, 25):
        grid[10][i] = 0
        path.append((i, 10))

    start_pos = path[0]
    plate_pos = path[len(path)//3]
    door_pos  = path[2*len(path)//3]
    goal_pos  = path[-1]

    return grid, start_pos, plate_pos, door_pos, goal_pos


# first map
grid, start_pos, plate_pos, door_pos, goal_pos = generate_map()
player_x, player_y = start_pos[0]*TILE, start_pos[1]*TILE

running = True
dead = False
won = False

death_messages = [
    "you died\n press  R and act like that did not happen",
    "bro really touched the wall \n press R",
    "skill issue detected \n press R to respawn",
    "even the clone gave up \n press R",
    "that was NOT the move \n press R",
    "wall 1 - you 0 \n press R"
]

win_messages = [
    "you won   \n  press R before ego kicks in",
    "W play     \n press R run it back",
    "clone carried btw \n press R",
    "ok that was clean ngl \n press R",
    "main character moment \n press R",
    "you beat it… somehow \n press R"
]

current_message = ""

while running:
    dt = clock.tick(60) / 1000
    screen.fill(BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # restart = new random map
    if keys[pygame.K_r]:
        grid, start_pos, plate_pos, door_pos, goal_pos = generate_map()
        player_x, player_y = start_pos[0]*TILE, start_pos[1]*TILE
        clone_active = False
        dead = False
        won = False
        current_message = ""

    if not dead and not won:

        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= 1#WASD controls just like in physics considering y as vertical and x as horizontal we took dy and dx as motion vectors
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        new_x = player_x + dx * speed
        new_y = player_y + dy * speed

        px = int(new_x // TILE)#positions
        py = int(new_y // TILE)

        # just preventing collision errors
        px = max(0, min(px, len(grid[0]) - 1))
        py = max(0, min(py, len(grid) - 1))

        # plate logic
        plate_active = False
        if (px, py) == plate_pos:
            plate_active = True

        if clone_active:
            cx, cy = int(clone_x // TILE), int(clone_y // TILE)
            if (cx, cy) == plate_pos:
                plate_active = True

        # door logic
        door_closed = not plate_active

        # collision
        if grid[py][px] == 1:
            dead = True
            if current_message == "":
                current_message = random.choice(death_messages)

        elif (px, py) == door_pos and door_closed:
            pass  # blocked but not dead

        else:
            player_x, player_y = new_x, new_y

        # clone placement (just one, overwrites old one if any)
        if keys[pygame.K_c]:
            clone_active = True
            clone_x, clone_y = player_x, player_y

        # win condition
        if (px, py) == goal_pos:
            won = True
            if current_message == "":
                current_message = random.choice(win_messages)

        # camera follows player
        camera_x = player_x - WIDTH // 2
        camera_y = player_y - HEIGHT // 2


    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] == 1:
                pygame.draw.rect(screen, R,
                    (x*TILE - camera_x, y*TILE - camera_y, TILE, TILE))

    # plate
    pygame.draw.rect(screen, O,
        (plate_pos[0]*TILE - camera_x,
         plate_pos[1]*TILE - camera_y,
         TILE, TILE))

    # door
    plate_now = False
    px, py = int(player_x//TILE), int(player_y//TILE)#player position

    if (px, py) == plate_pos:#condition for door to open
        plate_now = True
    if clone_active:
        cx, cy = int(clone_x//TILE), int(clone_y//TILE)#clone position
        if (cx, cy) == plate_pos:#condition for clone to open the door
            plate_now = True

    door_open = plate_now
    color = (0,200,200) if door_open else (0,80,80)

    pygame.draw.rect(screen, color,
        (door_pos[0]*TILE - camera_x,
         door_pos[1]*TILE - camera_y,
         TILE, TILE))

    # to ensure goals always at the  end of  the path
    pygame.draw.rect(screen, (255,255,0),
        (goal_pos[0]*TILE - camera_x,
         goal_pos[1]*TILE - camera_y,
         TILE, TILE))

    # player
    pygame.draw.rect(screen,P,
        (player_x - camera_x, player_y - camera_y, 20, 20))

    # clone
    if clone_active:
        pygame.draw.rect(screen, G,
            (clone_x - camera_x, clone_y - camera_y, 20, 20))

    if dead or won:
        lines = current_message.split("\n")
        for i, line in enumerate(lines):
            text = font.render(line, True, W)
            screen.blit(text, (200, 200 + i*30))

    screen.blit(title_surface, title_rect)

    pygame.display.flip()

    if keys[pygame.K_ESCAPE]:
        running = False

pygame.quit()