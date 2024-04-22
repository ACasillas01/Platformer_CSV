from __future__ import annotations
from abc import ABC
import pygame
from pygame.locals import *
import csv
from enum import Enum

vec = pygame.math.Vector2
ACC = 0.8
FRIC = -0.12
FPS = 60
WIDTH, HEIGHT = 800, 600
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()

class Assets(Enum):
        # name           # value
        #SKY  = './assets/8692941.jpg'
        SKY  = './assets/sky.jpg'
        DIRT = './assets/O8WNFV0.jpg'
        ROCK = './assets/rock.png'

class Block(pygame.sprite.Sprite):
    def __init__(self, sprite: Sprite, x = 0, y = 0):
        super().__init__()
        self.x = x
        self.y = y
        self.sprite = sprite
        self.surf = pygame.image.load(self.sprite.image_path)
        self.surf = pygame.transform.scale(self.surf, (self.sprite.sprite_size, self.sprite.sprite_size))
        self.rect = self.surf.get_rect(center = (self.x, self.y))

    def draw(self, screen):  
        screen.blit(self.surf, self.rect)
    
    def move(self):
        pass


class Sprite():
    def __init__(self, img):
        self.image_path = img
        self.sprite_size = 50

class Player(pygame.sprite.Sprite):
    def __init__(self, sprite: Sprite, x = 0, y = 0) -> None:
        super().__init__()
        self.sprite = sprite
        self.x = x
        self.y = y
        self.acc = 0.5
        self.fric = -0.12
        self.jumping = False

        self.pos = vec((x,y))
        self.vel = vec(0,0)
        self.acc = vec(0,0)

        self.surf = pygame.image.load(self.sprite.image_path)
        self.surf = pygame.transform.scale(self.surf, (self.sprite.sprite_size, self.sprite.sprite_size))
        self.rect = self.surf.get_rect(center = (self.x, self.y))

    def draw(self, screen):  
        screen.blit(self.surf, self.rect)
    
    def jump(self): 
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits and not self.jumping:
            self.jumping = True
            self.vel.y = -12

    def cancel_jump(self):
        if self.jumping:
            if self.vel.y < -2:
                self.vel.y = -2
    
    def move(self):
        self.acc = vec(0,0.5)
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC
        #Acelerate + Braking
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        #Screen Wrapping
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
            
        self.rect.midbottom = self.pos
        
    def update(self):
        hits = pygame.sprite.spritecollide(self , platforms, False)
        if self.vel.y > 0: 
            if hits:    	
                self.vel.y = 0
                if len(hits) > 2:
                    if self.pos.x < hits[2].rect.left : 
                        self.pos.x = hits[2].rect.left - self.sprite.sprite_size/2
                        self.pos.y = hits[2].rect.top + 1
                        self.vel.y = 0
                    if self.pos.x > hits[1].rect.right : 
                        self.pos.x = hits[1].rect.right + self.sprite.sprite_size/2
                        self.pos.y = hits[1].rect.top + 1
                        self.vel.y = 0
                else:
                    if self.pos.x < hits[0].rect.left and self.jumping == True : 
                        self.pos.x = hits[0].rect.left - self.sprite.sprite_size/2
                        self.pos.y = hits[0].rect.top + 1
                        self.vel.y = 0
                    if self.pos.x > hits[0].rect.right and self.jumping == True: 
                        self.pos.x = hits[0].rect.right + self.sprite.sprite_size/2
                        self.pos.y = hits[0].rect.top + 1
                        self.vel.y = 0
                if self.pos.y < hits[0].rect.bottom : 
                    self.pos.y = hits[0].rect.top + 1
                    self.jumping = False
                    self.vel.y = 0

                


class App():
    """A class representing a generic platformer game game. """
    
    def __init__(self, move_speed = 50, sprite_scale = 50/128, sprite_size = 50 ):
        self._move_speed = move_speed
        self.sprite_scale = sprite_scale
        self.sprite_size = sprite_size
        self.x = 0
        self.y = 0
        self._running = True
        self.screen = None
        self.size = self.width, self.height = 800, 600
        
        self.player = Player(Sprite('assets/player.png'), 15, self.height - 100)

        self.FramePerSec = pygame.time.Clock()

        all_sprites.add(self.player)

        self.sky = pygame.image.load(Assets.SKY.value);
        self.sky = pygame.transform.scale(self.sky, (self.width, self.height))


    def on_init(self) -> bool: 
        """Called when the program is started"""
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)
        self._running = True
        self.draw_scenary()

    def choose_block(self, x: int):
        if x==0:
            return Assets.SKY.value
        if x==1:
            return Assets.DIRT.value
    
    def draw_sky(self, screen):
        screen.blit(self.sky, (0, 0))
    
    def draw_block(self, screen):
        x = 25
        y = 25
        for row in self.scene:
            for tile in row:
                if tile == 0:
                    x +=50
                    continue
                if tile == 1:
                    B = Block(Sprite(Assets.DIRT.value), x, y)
                if tile == 2:
                    B = Block(Sprite(Assets.ROCK.value), x, y)
                platforms.add(B)
                all_sprites.add(B)
                B.draw(self.screen)
                x +=50
            x = 25
            y+=50
        return
    
    def draw_scenary(self):

        self.scene = []
        with open("scene.csv", "r") as csvfile:
            reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC) # change contents to floats
            for row in reader: # each row is a list
                self.scene.append(row)
        print(self.scene)
        self.screen.fill((136,244,255))
        self.draw_block(self.screen)
        
    def on_event(self, event) -> None:
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.player.update()
        for entity in all_sprites:
            entity.draw(self.screen)
            entity.move()

    def on_render(self):
        self.player.draw(self.screen)
        #pygame.draw.rect(self.screen,(255,150,140),self.player)

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self) -> None: 
        pygame.display.set_caption("Platformer")
        if self.on_init() == False:
            self._running = False
        
    
        while(self._running):
            for event in pygame.event.get():
                self.on_event(event)
                if event.type == pygame.KEYDOWN:    
                    if event.key == pygame.K_UP:
                        self.player.jump()
                if event.type == pygame.KEYUP:    
                    if event.key == pygame.K_UP:
                        self.player.cancel_jump()  
            
            #self.screen.fill((136,244,255))
            self.draw_sky(self.screen)

            self.on_loop()
            self.on_render()

            pygame.display.update()
            self.FramePerSec.tick(FPS)

        self.on_cleanup() #Pygame.quit



if __name__ == "__main__" :

    theApp = App()
    theApp.on_execute()
        