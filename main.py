import asyncio
import pygame
from math import *
from random import *

pygame.init()
pygame.font.init() # Initialize font system
pygame.display.set_caption("Asteroid Collision")
clock = pygame.time.Clock()

WIDTH = 1500
HEIGHT = 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))

score = 0

# Fonts and Colors
FONT_BIG = pygame.font.SysFont(None, 80)
FONT_SMALL = pygame.font.SysFont(None, 40)
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)

try:
    spaceship = pygame.image.load("spaceship.png").convert_alpha()
except pygame.error:
    spaceship = pygame.Surface((70, 100), pygame.SRCALPHA)
    pygame.draw.polygon(spaceship, (0, 255, 0), [(35, 0), (0, 100), (70, 100)])

spaceship = pygame.transform.scale(spaceship, (70, 100))
spaceship_pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
ship_speed = pygame.math.Vector2(0, 0)
angle = 0
rad = radians(angle + 90)
direction_ship = pygame.math.Vector2(cos(rad), -sin(rad))

THRUST = 0.12
DRAG = 0.993

asteroids = []
missiles = []
enemyMissile = []
respawnTime = 300

class Asteroid:
    def __init__(self):
        self.r = randint(40, 60)
        self.velocity = pygame.math.Vector2(randint(-3, 3), randint(-3, 3))
        if self.velocity.length() == 0:
            self.velocity = pygame.math.Vector2(2, 2)

        while True:
            self.pos = pygame.math.Vector2(randint(0, WIDTH), randint(0, HEIGHT))

            if self.pos.distance_to(spaceship_pos) > self.r + 150:
                break

        self.mass = self.r ** 2
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
        try:
            self.image = pygame.image.load("asteroid.png").convert_alpha()
        except pygame.error:
            self.image = pygame.Surface((self.r * 2, self.r * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (150, 150, 150), (self.r, self.r), self.r)

        self.image = pygame.transform.scale(self.image, (self.r * 2, self.r * 2))
        self.angle = randint(0, 360)
        self.rotated = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.rotated.get_rect(center=self.pos)

    def move(self):
        self.pos += self.velocity
        if self.pos.x >= WIDTH + self.r: self.pos.x = 0 - self.r
        elif self.pos.x <= 0 - self.r: self.pos.x = WIDTH + self.r
        if self.pos.y >= HEIGHT + self.r: self.pos.y = 0 - self.r
        elif self.pos.y < 0 - self.r: self.pos.y = HEIGHT + self.r

        self.rect = self.rotated.get_rect(center=self.pos)

    def draw(self):
        screen.blit(self.rotated, self.rect.topleft)

class Missile:
    def __init__(self, pos, direction):
        self.radius = 7
        self.pos = pygame.math.Vector2(pos.x, pos.y)
        self.direction = direction
        self.velocity = 20

    def move(self):
        self.pos += self.velocity * self.direction

    def draw(self):
        pygame.draw.circle(screen, (255, 0, 100), (int(self.pos.x), int(self.pos.y)), self.radius)

class Enemy:
    def __init__(self, pos):
        try:
            self.image = pygame.image.load("enemy.png").convert_alpha()
        except pygame.error:
            self.image = pygame.Surface((70, 100), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, (255, 0, 0), [(35, 0), (0, 100), (70, 100)])

        self.pos = pos
        self.image = pygame.transform.scale(self.image, (70, 100))
        self.angle = 0
        self.change_angle = choice([-1, 1])
        self.rotation = 3
        self.patrol_distance = 400
        self.shoot_cooldown = 0
        self.rotated = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.rotated.get_rect(center=self.pos)
        self.choice_cooldown = 0
        self.speed = 5

    def act(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.forward = pygame.Vector2(cos(radians(self.angle)), -sin(radians(self.angle)))
        distanceToPlayer = self.pos.distance_to(spaceship_pos)

        if distanceToPlayer > 0:
            toPlayer = (spaceship_pos - self.pos).normalize()
            dot = self.forward.dot(toPlayer)
            self.mode(dot, distanceToPlayer, toPlayer)

    def mode(self, dot, distanceToPlayer, toPlayer):
        if distanceToPlayer <= self.patrol_distance:
            if dot > 0.99:
                self.shoot(enemyMissile)
            else:
                cross = (self.forward[0] * toPlayer[1]) - (self.forward[1] * toPlayer[0])
                if cross > 0:
                    self.angle -= self.rotation
                else:
                    self.angle += self.rotation
        else:
            if self.choice_cooldown <= 0:
                self.action = choice([self.rotate, self.travel])
                self.choice_cooldown = 300

            self.action()

        self.choice_cooldown -= 1
        self.rotated = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.rotated.get_rect(center=self.pos)

    def rotate(self):
        self.angle += self.change_angle * self.rotation

    def travel(self):
        self.pos += self.speed * self.forward

    def shoot(self, target_list):
        if self.shoot_cooldown == 0:
            target_list.append(Missile(self.pos, self.forward))
            self.shoot_cooldown = 30

    def draw(self):
        screen.blit(self.rotated, self.rect.topleft)

async def main():
    global spaceship_pos, ship_speed, angle, rad, direction_ship
    global asteroids, missiles, enemyMissile, enemies, respawnTime, score

    running = True
    gameOver = False

    # Spawn initial entities
    enemies = []
    for x in range(6):
        asteroids.append(Asteroid())

    # Main Game Loop
    while running:
        # Event loop handles both gameplay and restart mechanics smoothly
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not gameOver:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    missiles.append(Missile(spaceship_pos, direction_ship))
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Reset game state
                    asteroids = [Asteroid() for _ in range(6)]
                    missiles.clear()
                    enemyMissile.clear()
                    enemies.clear()
                    spaceship_pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
                    ship_speed = pygame.math.Vector2(0, 0)
                    angle = 0
                    score = 0
                    gameOver = False

        if not gameOver:
            ship_speed *= DRAG
            spaceship_pos += ship_speed

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: angle += 3
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: angle -= 3

            rad = radians(angle + 90)
            direction_ship = pygame.math.Vector2(cos(rad), -sin(rad))

            rotated_ship = pygame.transform.rotate(spaceship, angle)
            ship_rect = rotated_ship.get_rect(center=spaceship_pos)

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                acceleration = direction_ship * THRUST
                ship_speed += acceleration

            # Wrap ship
            if ship_rect.left > WIDTH: spaceship_pos.x = -ship_rect.width / 2
            elif ship_rect.right < 0: spaceship_pos.x = WIDTH + ship_rect.width / 2
            if ship_rect.top > HEIGHT: spaceship_pos.y = -ship_rect.height / 2
            elif ship_rect.bottom < 0: spaceship_pos.y = HEIGHT + ship_rect.height / 2
            ship_rect.center = spaceship_pos

            for asteroid in asteroids:
                asteroid.move()

            for missile in list(missiles):
                missile.move()
                if missile.pos.x < 0 or missile.pos.x > WIDTH or missile.pos.y < 0 or missile.pos.y > HEIGHT:
                    if missile in missiles: missiles.remove(missile)

            for enemy in enemies:
                enemy.act()
                # Wrap enemy
                if enemy.rect.left > WIDTH: enemy.pos.x = -enemy.rect.width / 2
                elif enemy.rect.right < 0: enemy.pos.x = WIDTH + enemy.rect.width / 2
                if enemy.rect.top > HEIGHT: enemy.pos.y = -enemy.rect.height / 2
                elif enemy.rect.bottom < 0: enemy.pos.y = HEIGHT + enemy.rect.height / 2
                enemy.rect.center = enemy.pos

            for missile in list(enemyMissile):
                missile.move()
                if missile.pos.x < 0 or missile.pos.x > WIDTH or missile.pos.y < 0 or missile.pos.y > HEIGHT:
                    if missile in enemyMissile:
                        enemyMissile.remove(missile)

            # Asteroid collisions
            for i in range(len(asteroids)):
                for j in range(i + 1, len(asteroids)):
                    a1 = asteroids[i]
                    a2 = asteroids[j]
                    distance = a1.pos.distance_to(a2.pos)
                    if distance <= a1.r + a2.r:
                        v1x, v1y = a1.velocity.x, a1.velocity.y
                        v2x, v2y = a2.velocity.x, a2.velocity.y
                        a1.velocity = pygame.math.Vector2(
                            ((a1.mass - a2.mass) / (a1.mass + a2.mass) * v1x + (2 * a2.mass) / (a1.mass + a2.mass) * v2x),
                            ((a1.mass - a2.mass) / (a1.mass + a2.mass) * v1y + (2 * a2.mass) / (a1.mass + a2.mass) * v2y)
                        )

                        a2.velocity = pygame.math.Vector2(
                            ((a2.mass - a1.mass) / (a2.mass + a1.mass) * v2x + (2 * a1.mass) / (a2.mass + a1.mass) * v1x),
                            ((a2.mass - a1.mass) / (a2.mass + a1.mass) * v2y + (2 * a1.mass) / (a2.mass + a1.mass) * v1y)
                        )

            for asteroid in asteroids:
                if spaceship_pos.distance_to(asteroid.pos) < asteroid.r * 0.85 + 35:
                    gameOver = True

            # Player missile hits asteroid
            for missile in list(missiles):
                for asteroid in list(asteroids):
                    if missile.pos.distance_to(asteroid.pos) < missile.radius + asteroid.r:
                        if missile in missiles: missiles.remove(missile)
                        if asteroid in asteroids: asteroids.remove(asteroid)
                        asteroids.append(Asteroid())
                        score += 1
                        break

                for enemy in list(enemies):
                    if enemy.rect.collidepoint(missile.pos):
                        if enemy in enemies: enemies.remove(enemy)
                        if missile in missiles: missiles.remove(missile)
                        score += 5
                        break

            # Enemy missile hits player
            for missile in list(enemyMissile):
                if ship_rect.collidepoint(missile.pos):
                    gameOver = True

            # Respawn enemy
            if len(enemies) == 0:
                if respawnTime == 0:
                    enemies.append(Enemy(pygame.math.Vector2(randint(0, WIDTH), randint(0, HEIGHT))))
                    respawnTime = 300
                else:
                    respawnTime -= 1

            # Drawing everything
            screen.fill((20, 24, 40))
            for asteroid in asteroids: asteroid.draw()
            for missile in missiles: missile.draw()
            for missile in enemyMissile: missile.draw()
            for enemy in enemies: enemy.draw()
            screen.blit(rotated_ship, ship_rect.topleft)
            screen.blit(FONT_SMALL.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))

        else:
            # Game Over Screen
            screen.fill((20, 24, 40))
            go_text = FONT_BIG.render("GAME OVER", True, COLOR_RED)
            go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(go_text, go_rect)

            restart_text = FONT_SMALL.render("Press SPACE to Restart", True, COLOR_WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            screen.blit(restart_text, restart_rect)

            score_text = FONT_SMALL.render(f"Your Score: {score}", True, COLOR_WHITE)
            score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 70))
            screen.blit(score_text, score_rect)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # Yields execution to the event loop per frame

    pygame.quit()

asyncio.run(main())