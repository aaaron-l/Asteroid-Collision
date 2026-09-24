import pygame
from math import *
from random import *

pygame.init()
pygame.display.set_caption("Asteroid Collision")
clock = pygame.time.Clock()

WIDTH = 1500
HEIGHT = 1000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
running = True

try:
    spaceship = pygame.image.load("spaceship.png").convert_alpha()
except pygame.error:
    spaceship = pygame.Surface((70, 100), pygame.SRCALPHA)
    pygame.draw.polygon(spaceship, (0, 255, 0), [(35, 0), (0, 100), (70, 100)])

spaceship = pygame.transform.scale(spaceship, (70, 100))
spaceship_pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
ship_speed = 5
angle = 0


class Asteroid:
    def __init__(self):
        self.r = randint(10, 70)
        self.velocity = pygame.math.Vector2(randint(-5, 5), randint(-5, 5))

        if self.velocity.length() == 0:
            self.velocity = pygame.math.Vector2(2, 2)

        self.pos = pygame.math.Vector2(randint(0, WIDTH), randint(0, HEIGHT))
        self.mass = self.r ** 2
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))

    def move(self):
        self.pos += self.velocity

        if self.pos.x >= WIDTH + self.r:
            self.pos.x = 0 - self.r
        elif self.pos.x <= 0 - self.r:
            self.pos.x = WIDTH + self.r

        if self.pos.y >= HEIGHT + self.r:
            self.pos.y = 0 - self.r
        elif self.pos.y < 0 - self.r:
            self.pos.y = HEIGHT + self.r

    def draw(self):
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.pos.x), int(self.pos.y)),
            self.r
        )


class Missile:
    def __init__(self, target_pos):
        self.radius = 7
        self.pos = pygame.math.Vector2(spaceship_pos.x, spaceship_pos.y)

        direction_vector = target_pos - self.pos

        if direction_vector.length() == 0:
            self.direction = pygame.math.Vector2(1, 0)
        else:
            self.direction = direction_vector.normalize()

        self.velocity = 20

    def move(self):
        self.pos += self.velocity * self.direction

    def draw(self):
        pygame.draw.circle(
            screen,
            (255, 0, 100),
            (int(self.pos.x), int(self.pos.y)),
            self.radius
        )


asteroids = []
missiles = []

for x in range(6):
    asteroids.append(Asteroid())


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            missiles.append(Missile(pygame.math.Vector2(event.pos)))

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        angle += 3

    if keys[pygame.K_RIGHT]:
        angle -= 3

    rad = radians(angle + 90)
    direction_ship = pygame.math.Vector2(cos(rad), -sin(rad))

    # Create the rotated image and its Rect
    rotated_ship = pygame.transform.rotate(spaceship, angle)
    ship_rect = rotated_ship.get_rect(center=spaceship_pos)

    if keys[pygame.K_UP]:
        spaceship_pos += direction_ship * ship_speed

    # Wrap ship
    if ship_rect.left > WIDTH:
        spaceship_pos.x = -ship_rect.width / 2

    elif ship_rect.right < 0:
        spaceship_pos.x = WIDTH + ship_rect.width / 2

    if ship_rect.top > HEIGHT:
        spaceship_pos.y = -ship_rect.height / 2

    elif ship_rect.bottom < 0:
        spaceship_pos.y = HEIGHT + ship_rect.height / 2

    ship_rect.center = spaceship_pos

    for asteroid in asteroids:
        asteroid.move()

    for missile in list(missiles):
        missile.move()

        if (
            missile.pos.x < 0
            or missile.pos.x > WIDTH
            or missile.pos.y < 0
            or missile.pos.y > HEIGHT
        ):
            if missile in missiles:
                missiles.remove(missile)

    for i in range(len(asteroids)):
        for j in range(i + 1, len(asteroids)):
            a1 = asteroids[i]
            a2 = asteroids[j]

            distance = sqrt(
                (a1.pos.x - a2.pos.x) ** 2
                + (a1.pos.y - a2.pos.y) ** 2
            )

            if distance <= a1.r + a2.r:
                v1x = a1.velocity.x
                v1y = a1.velocity.y
                v2x = a2.velocity.x
                v2y = a2.velocity.y

                a1.velocity = pygame.math.Vector2(
                    ((a1.mass - a2.mass) / (a1.mass + a2.mass) * v1x
                     + (2 * a2.mass) / (a1.mass + a2.mass) * v2x),

                    ((a1.mass - a2.mass) / (a1.mass + a2.mass) * v1y
                     + (2 * a2.mass) / (a1.mass + a2.mass) * v2y)
                )

                a2.velocity = pygame.math.Vector2(
                    ((a2.mass - a1.mass) / (a2.mass + a1.mass) * v2x
                     + (2 * a1.mass) / (a2.mass + a1.mass) * v1x),

                    ((a2.mass - a1.mass) / (a2.mass + a1.mass) * v2y
                     + (2 * a1.mass) / (a2.mass + a1.mass) * v1y)
                )

    for missile in list(missiles):
        for asteroid in list(asteroids):
            distance = sqrt(
                (missile.pos.x - asteroid.pos.x) ** 2
                + (missile.pos.y - asteroid.pos.y) ** 2
            )

            if distance < missile.radius + asteroid.r:
                if missile in missiles:
                    missiles.remove(missile)

                if asteroid in asteroids:
                    asteroids.remove(asteroid)

                asteroids.append(Asteroid())
                break

    screen.fill((20, 24, 40))

    for asteroid in asteroids:
        asteroid.draw()

    for missile in missiles:
        missile.draw()

    screen.blit(rotated_ship, ship_rect.topleft)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()