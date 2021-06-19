import random
import pygame
import math
import perlin

FPS = 60
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 900

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GREY = (128, 128, 128)

PP = -1
ERN = 361

RAY_COLOR = WHITE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ray Sim")
screen.fill(BLACK)
rays = {}
walls = []
walldims = [[random.randrange(0, 900), random.randrange(0, 900), random.randrange(0, 900), random.randrange(0, 900)]
            for _ in range(5)]

walldims.extend([[10, 10, 10, 890], [10, 890, 890, 890], [890, 890, 890, 10], [890, 10, 10, 10]])


def newwalls():
    global  walldims
    walldims.clear()
    walldims = [[random.randrange(0, 900), random.randrange(0, 900), random.randrange(0, 900), random.randrange(0, 900)]
                for _ in range(5)]

    walldims.extend([[10, 10, 10, 890], [10, 890, 890, 890], [890, 890, 890, 10], [890, 10, 10, 10]])

def on_segment(p, q, r):
    if max(p[0], q[0]) >= r[0] >= min(p[0], q[0]) and r[1] <= max(p[1], q[1]) and r[1] >= min(p[1], q[1]):
        return True
    return False


def orientation(p, q, r):
    val = ((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1]))
    if val == 0 : return 0
    return 1 if val > 0 else -1


def intersects(seg1, seg2):
    p1, q1 = seg1
    p2, q2 = seg2

    o1 = orientation(p1, q1, p2)

    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if o1 != o2 and o3 != o4:
        return True

    if o1 == 0 and on_segment(p1, q1, p2) : return True
    if o2 == 0 and on_segment(p1, q1, q2) : return True
    if o3 == 0 and on_segment(p2, q2, p1) : return True
    if o4 == 0 and on_segment(p2, q2, q1) : return True

    return False

def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def intersection(L1, L2):
    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x, y
    else:
        return -1, -1


def getdist(line1, line2):
    return math.dist(line1, line2)


def getnormalscreen():
    screen.fill(BLACK)
    getrandomwalls()


def translate(x, y, angle, distance):
    dY = distance * math.cos(math.radians(angle))
    dX = distance * math.sin(math.radians(angle))
    Xfinal = x + dX
    Yfinal = y + dY
    return Xfinal, Yfinal


def getrandomwalls():
    for x1, y1, x2, y2 in walldims:
        walls.append(pygame.draw.line(screen, WHITE, (x1, y1), (x2, y2)))
    # walls.append(pygame.draw.line(screen, WHITE, (100, 100), (100, 800)))
    # walls.append(pygame.draw.line(screen, WHITE, (100, 800), (800, 800)))
    # walls.append(pygame.draw.line(screen, WHITE, (800, 800), (800, 100)))
    # walls.append(pygame.draw.line(screen, WHITE, (800, 100), (100, 100)))


def dotheyintersect(x1, y1, x2, y2, x3, y3, x4, y4):
    segment_one = ((x1, y1), (x2, y2))
    segment_two = ((x3, y3), (x4, y4))
    if intersects(segment_one, segment_two):
        L1 = line([x1, y1], [x2, y2])
        L2 = line([x3, y3], [x4, y4])

        ptx, pty = intersection(L1, L2)

        if [ptx, pty] != [-1, -1]:
            return [ptx, pty], getdist([ptx, pty], [x3, y3])
    else:
        return [-1, -1], -1


def getnearestpoint(mousex, mousey, dirx, diry):
    maindist = 100000
    mainpt = [100000, 100000]
    wal = []
    for wall in walldims:
        try:
            pt, dist = dotheyintersect(wall[0], wall[1], wall[2], wall[3], mousex, mousey, dirx, diry)
        except:
            print("rando error")
            continue
        if pt != [-1, -1] and dist < maindist and dist != -1:
            maindist = dist
            mainpt = pt
            wal = wall
    return mainpt, wal


def getangle(mousex, mousey, ptx, pty, wallx1, wally1, wallx2, wally2):
    ax = mousex - ptx
    ay = mousey - pty
    bx = wallx1 - ptx
    by = wally1 - pty
    cx = wallx2 - ptx
    cy = wally2 - pty
    a1 = ((ax*bx)+(ay*by)/(math.sqrt(ax*ax + ay*ay) + math.sqrt(bx*bx + by*by)))
    a2 = ((ax * cx) + (ay * cy) / (math.sqrt(ax * ax + ay * ay) + math.sqrt(cx * cx + cy * cy)))
    if a1< a2:
        return a1, wallx1, wally1
    if a2< a1:
        return a2, wallx2, wally2
    else:
        return 0, 0, 0


# def getreflections(ray):
#     ptx, pty = ray[2], ray[3]
#     opx, opy = ray[0], ray[1]
#     a1, ax, ay = getangle(ray[0], ray[1], ray[2], ray[3], ray[4][0], ray[4][1], ray[4][2], ray[4][3])
#     ray_len = ray[5][3]
#     while(ray_len < 1273):
#         if a1 == 0:
#             ray = pygame.draw.line(screen, RAY_COLOR, (ptx, pty), (opx+1273, opy+1273))
#



def getrays(mousex, mousey):
    for i in range(0, 361, 1):
        dirx, diry = translate(mousex, mousey, i, 10000)
        pt, wall = getnearestpoint(mousex, mousey, dirx, diry)
        if pt != [100000, 100000]:
            ray = pygame.draw.line(screen, RAY_COLOR, (mousex, mousey), (pt[0], pt[1]))
            rays[i] = [mousex, mousey, pt[0], pt[1], wall, ray]
            # getreflections(rays[i])



def setup(mousex, mousey):
    getnormalscreen()
    getrays(mousex, mousey)
    pygame.display.update()
    rays.clear()
    walls.clear()


def pnoise():
    p = perlin.Perlin(1234)
    xoff = 23
    yoff = 1000
    for i in range(100):
        print(p.two(xoff, yoff))
        xoff += 0.01
        yoff += 0.01


def main():
    run = True
    clock = pygame.time.Clock()
    mousex, mousey = 0, 0
    global RAY_COLOR, PP
    while run:
        setup(mousex, mousey)
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    print("Enbled perlin noise")
                    pnoise()
                    PP *=-1
                if event.key == pygame.K_r:
                    print("new walls entered")
                    newwalls()
                if event.key == pygame.K_1:
                    RAY_COLOR = WHITE
                    print("new ray color: ", RAY_COLOR)
                if event.key == pygame.K_2:
                    RAY_COLOR = RED
                    print("new ray color: ", RAY_COLOR)
                if event.key == pygame.K_3:
                    RAY_COLOR = GREEN
                    print("new ray color: ", RAY_COLOR)
                if event.key == pygame.K_4:
                    RAY_COLOR = GREY
                    print("new ray color: ", RAY_COLOR)
            if PP == -1:
                if event.type == pygame.MOUSEMOTION:
                    mousex, mousey = pygame.mouse.get_pos()

    pygame.quit()


if __name__ == '__main__':
    main()