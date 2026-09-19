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


class Asteroid:
    def __init__(self):
        self.r = randint(10, 70)
        self.velocity = pygame.math.Vector2(randint(-10, 10), randint(-10, 10))
        self.pos = pygame.math.Vector2(randint(0, WIDTH), randint(0, HEIGHT))

        # Move Offscreen
        if self.pos[0] == 0:
            self.pos[0] -= self.r
        if self.pos[0] == WIDTH:
            self.pos[0] += self.r
           
        if self.pos[1] == 0:
            self.pos[1] -= self.r
        if self.pos[1] == HEIGHT:
            self.pos[1] += self.r

        self.mass = self.r**2
        self.color = (
            randint(0, 255),
            randint(0, 255),
            randint(0, 255)
        )

    def move(self):
        self.pos += self.velocity

        if self.pos[0] >=  WIDTH + self.r:
            self.pos[0] = 0-self.r
        elif self.pos[0] <= 0-self.r:
            self.pos[0] = WIDTH + self.r

        if self.pos[1] >=  HEIGHT + self.r:
            self.pos[1] = 0-self.r
        elif self.pos[1] < 0-self.r:
            self.pos[1] = HEIGHT + self.r

    def draw(self):
        pygame.draw.circle(
            screen,
            self.color,
            (self.pos[0], self.pos[1]),
            self.r
        )


asteroids = []
for x in range(6):
    asteroids.append(Asteroid())

while running:
    for event in pygame.event.get():
        if event == pygame.QUIT:
            running = False

    for asteroid in asteroids:
        asteroid.move()

    for i in range(len(asteroids)):
        for j in range(i + 1, len(asteroids)):

            a1 = asteroids[i]
            a2 = asteroids[j]

            distance = sqrt(
                (a1.pos[0] - a2.pos[0])**2 +
                (a1.pos[1] - a2.pos[1])**2
            )

            # Detect collision
            if distance <= a1.r + a2.r:
                # Apply change in velocity for both 
                v1x = a1.velocity[0]
                v1y = a1.velocity[1]
                v2x = a2.velocity[0]
                v2y = a2.velocity[1]

                a1.velocity[0] = (
                    (a1.mass-a2.mass)/(a1.mass+a2.mass)*v1x +
                    (2*a2.mass)/(a1.mass+a2.mass)*v2x
                )
                a1.velocity[1] = (
                    (a1.mass-a2.mass)/(a1.mass+a2.mass)*v1y +
                    (2*a2.mass)/(a1.mass+a2.mass)*v2y
                )

                a2.velocity[0] = (
                    (a2.mass-a1.mass)/(a2.mass+a1.mass)*v2x +
                    (2*a1.mass)/(a2.mass+a1.mass)*v1x
                )
                a2.velocity[1] = (
                    (a2.mass-a1.mass)/(a2.mass+a1.mass)*v2y +
                    (2*a1.mass)/(a2.mass+a1.mass)*v1y
                )

    # Render
    screen.fill((20, 24, 40))                
    for asteroid in asteroids:
        asteroid.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

                

       




