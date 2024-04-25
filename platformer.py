from __future__ import annotations

import csv
import random
import time
from abc import ABC, abstractmethod
from enum import Enum

import pygame
from pygame.locals import *

vec = pygame.math.Vector2
ACC = 0.8
FRIC = -0.12
FPS = 60
WIDTH, HEIGHT = 800, 600
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
coins = pygame.sprite.Group()


class Assets(Enum):
    """Enumeration of asset paths."""

    SKY = "./assets/sky.jpg"
    DIRT = "./assets/O8WNFV0.jpg"
    ROCK = "./assets/rock.png"
    COIN = "./assets/coin.png"


class Block(pygame.sprite.Sprite):
    """Represents a block in the game."""

    def __init__(self, sprite: Sprite, x=0, y=0):
        """
        Initializes the Block instance.

        Args:
            sprite (Sprite): The sprite of the block.
            x (int): X-coordinate of the block.
            y (int): Y-coordinate of the block.
        """
        super().__init__()
        self.x = x
        self.y = y
        self.sprite = sprite
        self.surf = pygame.image.load(self.sprite.image_path)
        self.surf = pygame.transform.scale(
            self.surf, (self.sprite.sprite_size, self.sprite.sprite_size)
        )
        self.rect = self.surf.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        """
        Draw the block on the screen.

        Args:
            screen: The pygame screen.
        """
        screen.blit(self.surf, self.rect)

    def move(self):
        """Placeholder method for moving the block."""
        pass


class Sprite:
    """Represents a game sprite."""

    def __init__(self, img):
        """
        Initializes the Sprite instance.

        Args:
            img (str): Path to the image file.
        """
        self.image_path = img
        self.sprite_size = 50


class Player(pygame.sprite.Sprite):
    """Represents the player in the game."""

    def __init__(self, sprite: Sprite, x=0, y=0) -> None:
        """
        Initializes the Player instance.

        Args:
            sprite (Sprite): The sprite of the player.
            x (int): X-coordinate of the player.
            y (int): Y-coordinate of the player.
        """
        super().__init__()
        self.sprite = sprite
        self.x = x
        self.y = y
        self.acc = 0.5
        self.fric = -0.12
        self.jumping = False
        self.score = 0
        self.pos = vec((x, y))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.surf = pygame.image.load(self.sprite.image_path)
        self.surf = pygame.transform.scale(
            self.surf, (self.sprite.sprite_size, self.sprite.sprite_size)
        )
        self.rect = self.surf.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        """
        Draw the player on the screen.

        Args:
            screen: The pygame screen.
        """
        screen.blit(self.surf, self.rect)

    def jump(self):
        """Make the player jump."""
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -12

    def cancel_jump(self):
        """Cancel the player's jump."""
        if self.jumping:
            if self.vel.y < -2:
                self.vel.y = -2

    def move(self):
        """Move the player."""
        self.acc = vec(0, 0.5)
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC
        # Accelerate + Braking
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        # Screen Wrapping
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos

    def update(self):
        """Update the player's position."""
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if self.vel.y > 0:
            if hits:
                self.vel.y = 0
                if (
                    len(hits) > 2
                ):  # Checking for the players collision with multiple blocks (floor + wall)
                    if self.pos.x < hits[2].rect.left:
                        self.pos.x = (
                            hits[2].rect.left - self.sprite.sprite_size / 2
                        )
                        self.pos.y = hits[2].rect.top + 1
                        self.vel.y = 0
                    if self.pos.x > hits[1].rect.right:
                        self.pos.x = (
                            hits[1].rect.right + self.sprite.sprite_size / 2
                        )
                        self.pos.y = hits[1].rect.top + 1
                        self.vel.y = 0
                else:  # Checking for the players collision with single blocks (floor)
                    if self.pos.x < hits[0].rect.left and self.jumping == True:
                        self.pos.x = (
                            hits[0].rect.left - self.sprite.sprite_size / 2
                        )
                        self.pos.y = hits[0].rect.top + 1
                        self.vel.y = 0
                    if (
                        self.pos.x > hits[0].rect.right
                        and self.jumping == True
                    ):
                        self.pos.x = (
                            hits[0].rect.right + self.sprite.sprite_size / 2
                        )
                        self.pos.y = hits[0].rect.top + 1
                        self.vel.y = 0
                if self.pos.y < hits[0].rect.bottom:
                    self.pos.y = hits[0].rect.top + 1
                    self.jumping = False
                    self.vel.y = 0


class Bloque(ABC):
    """Abstract class representing a block."""

    @abstractmethod
    def draw(self) -> Sprite:
        """Draw a new block on the screen."""
        pass


class DirtBlock(Bloque):
    """Concrete class representing a dirt block."""

    def draw(self) -> Sprite:
        """Draw a new dirt block on the screen."""
        dirt = Sprite(Assets.DIRT.value)
        return dirt


class RockBlock(Bloque):
    """Concrete class representing a rock block."""

    def draw(self) -> Sprite:
        """Draw a new rock block on the screen."""
        rock = Sprite(Assets.ROCK.value)
        return rock


class SkyBlock(Bloque):
    """Concrete class representing a sky block."""

    def draw(self) -> Sprite:
        """Draw a new sky block on the screen."""
        sky = Sprite(Assets.SKY.value)
        return sky


class Coin(pygame.sprite.Sprite):
    """Represents a coin in the game."""

    def __init__(self, sprite: Sprite, x=0, y=0):
        """
        Initializes the Coin instance.

        Args:
            sprite (Sprite): The sprite of the coin.
            x (int): X-coordinate of the coin.
            y (int): Y-coordinate of the coin.
        """
        super().__init__()
        self.x = x
        self.y = y
        self.sprite = sprite
        self.surf = pygame.image.load(self.sprite.image_path)
        self.surf = pygame.transform.scale(
            self.surf, (self.sprite.sprite_size, self.sprite.sprite_size)
        )
        self.rect = self.surf.get_rect(center=(self.x, self.y))

    def update(self, player: Player):
        """
        Update on the coin's existance and check for collisions with the player.

        Args:
            player (Player): The player object.
        """
        if self.rect.colliderect(player.rect):
            player.score += 5
            self.kill()


class App:
    """Represents the main application."""

    def __init__(self, move_speed=50, sprite_scale=50 / 128, sprite_size=50):
        """
        Initializes the App instance.

        Args:
            move_speed (int): The movement speed of the game.
            sprite_scale (float): The scale of the game sprites.
            sprite_size (int): The size of the game sprites.
        """
        self._move_speed = move_speed
        self.sprite_scale = sprite_scale
        self.sprite_size = sprite_size
        self.x = 0
        self.y = 0
        self._running = True
        self.screen = None
        self.size = self.width, self.height = 800, 600
        self.chanceOfCoin = 0.01
        self.player = Player(
            Sprite("assets/player.png"), 15, self.height - 100
        )

        self.FramePerSec = pygame.time.Clock()

        all_sprites.add(self.player)

        self.sky = pygame.image.load(Assets.SKY.value)
        self.sky = pygame.transform.scale(self.sky, (self.width, self.height))

    def generateCoin(self, x, y):
        """
        Generate a coin at the specified position.

        Args:
            x (int): X-coordinate of the coin.
            y (int): Y-coordinate of the coin.
        """
        coins.add(Coin(Sprite("./assets/coin.png"), x, y))

    def on_init(self) -> bool:
        """Called when the program is started."""
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        self._running = True
        self.draw_scenary()

    @abstractmethod
    def create_block(self, tipo) -> Bloque:
        """Factory method to create a block."""
        return tipo.value

    def choose_block(self, tipo) -> int:
        """Choose the block to draw."""
        return self.create_block(tipo).draw()

    def draw_sky(self, screen):
        """
        Draw the sky background.

        Args:
            screen: The pygame screen.
        """
        screen.blit(self.sky, (0, 0))

    @abstractmethod
    def create_block(self, x: int, y: int):
        # Flyweight variables
        # dirtSprite = Sprite(Assets.DIRT.value)
        # rockSprite = Sprite(Assets.ROCK.value)
        dirtSprite = DirtBlock().draw()
        rockSprite = RockBlock().draw()
        for row in self.scene:
            for tile in row:
                if tile == 0:
                    if random.random() < self.chanceOfCoin and y >= 50:
                        self.generateCoin(x, y)
                        print("Coin Added!")
                    x += 50
                    continue
                if tile == 1:
                    # B = Block(Sprite(Assets.DIRT.value), x, y) = No Flyweight
                    B = Block(dirtSprite, x, y)
                if tile == 2:
                    # B = Block(Sprite(Assets.ROCK.value), x, y) = No Flyweight
                    B = Block(rockSprite, x, y)
                platforms.add(B)
                all_sprites.add(B)
                B.draw(self.screen)
                x += 50
            x = 25
            y += 50

    def draw_block(self, screen):  # FLYWEIGHT - PATRON ESTRUCTURAL
        """
        Draw blocks on the screen.

        Args:
            screen: The pygame screen.
        """
        self.create_block(25, 25)
        return

    @abstractmethod
    def create_scene(self) -> str:
        """Create the game scene."""
        scene = random.choice(
            [
                "scene.csv",
                "scenario_1.csv",
                "scenario_2.csv",
                "scenario_3.csv",
                "scenario_4.csv",
                "scenario_5.csv",
            ]
        )
        return scene

    def draw_scenary(self):
        """Draw the game scenery."""
        self.scene = []
        with open(self.create_scene(), "r") as csvfile:
            reader = csv.reader(
                csvfile, quoting=csv.QUOTE_NONNUMERIC
            )  # change contents to floats
            for row in reader:  # each row is a list
                self.scene.append(row)
        print(self.scene)
        self.screen.fill((136, 244, 255))
        self.draw_block(self.screen)

    def on_event(self, event) -> None:
        """Handle game events."""
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        """Update the game state."""
        self.player.update()
        for entity in all_sprites:
            entity.draw(self.screen)
            entity.move()

    def on_render(self):
        """Render game objects."""
        self.player.draw(self.screen)
        f = pygame.font.SysFont("Verdana", 20)
        g = f.render(str(self.player.score), True, (123, 255, 0))
        self.screen.blit(g, (WIDTH / 2, 10))
        if coins:
            for coin in coins:
                self.screen.blit(coin.surf, coin.rect)
                coin.update(self.player)
        else:
            self._running = False

    def end_screen(self):
        """Show end screen"""
        time.sleep(1)
        self.screen.fill((255, 0, 0))
        f = pygame.font.SysFont("Verdana", 20)
        g = f.render(str("Game ended!"), True, (0, 0, 0))
        self.screen.blit(g, (WIDTH / 2 - 80, HEIGHT / 2))
        g = f.render(
            str(f"Score: {self.player.score} points!"), True, (0, 0, 0)
        )
        self.screen.blit(g, (WIDTH / 2 - 80, HEIGHT / 2 + 50))
        pygame.display.update()
        time.sleep(3)

    def on_cleanup(self):
        """Clean up resources, show end screen and exit the game."""
        self.end_screen()
        pygame.quit()

    def on_execute(self) -> None:
        """Start the game."""
        pygame.display.set_caption("Platformer")
        if self.on_init() == False:
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.player.jump()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.player.cancel_jump()

            self.draw_sky(self.screen)

            self.on_loop()
            self.on_render()

            pygame.display.update()
            self.FramePerSec.tick(FPS)

        self.on_cleanup()


if __name__ == "__main__":

    theApp = App()
    theApp.on_execute()
