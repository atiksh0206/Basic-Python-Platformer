
import os 
import random
import math
import pygame
from os import listdir 
from os.path import isfile, join #allows us to dynamically load spreadsheets and images
pygame.init() #intitalizes the pygame module

pygame.display.set_caption("Platformer") #sets the caption at the top of the window

Width, Height = 800, 600 #dimensions of playable window
FPS = 60 
Player_Vel = 5 #speed at which character moves

window = pygame.display.set_mode((Width, Height)) #creates the pygame window

def flip(sprites):
    return[pygame.transform.flip(sprite,True,False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction = False):
    path =join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path,f))] #loads every file in the directories 
    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha() #loads the image and converts it into transparent

        sprites =[]
        for i in range(sprite_sheet.get_width()//width):
            surface = pygame.Surface((width,height), pygame.SRCALPHA, 32) #strips each individual frame and doubles it through the code below
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png", "")+ "_right"] = sprites
            all_sprites[image.replace(".png", "")+ "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size), pygame.SRCALPHA,32)
    rect = pygame.Rect(96, 0, size, size) # "96,0" is the start of the coordinate in the terrain png of the grass block, if we want to load a different one we have to experiment
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite): #we use sprite.Sprite for better collisions
    Color = (255,0,0)
    Gravity = 1
    Sprites = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
    Animation_Delay = 3

    def __init__(self,x,y,width,height):
       super().__init__()
       self.rect = pygame.Rect(x,y,width,height) # ".rect" is a tuple that stores 4 individual values and "pygame.rect" lets us use different equations
       self.x_vel = 0 #these velocities is how fast we move the character in each direction
       self.y_vel = 0 #this also helps with gravity
       self.mask = None
       self.direction = "left"
       self.animation_count = 0 #changes the animation frames
       self.fall_count = 0
       self.jump_count = 0
       self.hit = False
       self.hit_count = 0

    def jump(self):
        self.y_vel = -self.Gravity * 7 #multiplying by 8 will make it jump 8x faster than gravity
        self.animation_count = 0
        self.jump_count +=1
        if self.jump_count >= 1:
            self.fall_count = 0 #resets the gravity only if this is the first jump

    
    def move(self,dx,dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self, vel): #pygame formats its windows with (0,0) in the top left corner so if you want to move right you need to add vel and left is -vel
        self.x_vel = -vel
        if self.direction != "left": #dictates the direction the sprite will be looking in (default is left)
            self.direction = "left"
            self.animation_count = 0

    def move_right(self,vel): #opposite of move_left
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps): #gets called once every frame (one iteration of while loop)
        self.y_vel += min(1, (self.fall_count / FPS) * self.Gravity)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count +=1
        if self.hit_count > fps *2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0 #resets the gravity
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.count=0
        self.y_vel *= -1

    
    def update_sprite(self):
        sprite_sheet = "idle" #our default animation of the sprite is in its idle position
        if self.hit:
            sprite_sheet = "hit"
        if self.y_vel <= 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.Gravity*2:
            sprite_sheet = "fall"
        elif self.x_vel != 0: #anytime it is moving, we will use the running animation
            sprite_sheet = "run"
        
        sprite_sheet_name = sprite_sheet + "_" + self.direction #addes the "_left" or "_right" directional tag we added during our spriting
        sprites = self.Sprites[sprite_sheet_name]
        sprite_index = (self.animation_count // self.Animation_Delay) % len(sprites) #every 5 seconds we will show a new sprite and we use the mod to show a specific frame and this code allows it to work universally
        self.sprite = sprites[sprite_index]
        self.animation_count +=1
        self.update()
    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y)) # note: make sure you use topleft all lowercase!!! makes sure the rectangle bounding the character is adjusted based on sprite size
        self.mask = pygame.mask.from_surface(self.sprite) #it tells us where there are actually pixels and it allows us to do pixel perfect collisions 

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x,self.rect.y))


class Object(pygame.sprite.Sprite): #base class which contains all properties of any valid sprite(blocks,traps etc)... allows us to use this for anything 
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width,height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size) #function that gets the image we need
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image) #need for collision between pixels of sprites instead of rects

class Fire(Object):
    Animation_Delay = 3 
    def __init__(self, x, y, width, height ):
        super().__init__( x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"
    def off(self):
        self.animation_name = "off"
    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.Animation_Delay) % len(sprites) #every 5 seconds we will show a new sprite and we use the mod to show a specific frame and this code allows it to work universally
        self.image = sprites[sprite_index]
        self.animation_count +=1
        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y)) # note: make sure you use topleft all lowercase!!! makes sure the rectangle bounding the character is adjusted based on sprite size
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.Animation_Delay > len(sprites):
            self.animation_count = 0
        

def get_background(name): #allows us to change the background and set up a grid based on screen dimensions
    image = pygame.image.load(join("assets", "Background", name)) #this joins the assets path with the background path and the image name (file name which will be loaded)
    _, _, width, height = image.get_rect() #the two underscores refers to "x,y" but since we dont care it doesnt matter. the only thing that matters is the width and height
    tiles =[]
    for i in range(Width// width + 1): #estimates the amount of tiles we need for our window
        for j in range(Height // height + 1):
            #this nested for loop finds the coordinate that each background tile needs to be at and appends it into the list for tiles
            pos = (i*width, j*height)
            tiles.append(pos)
    return tiles,image

def draw(window,background,bg_image,player, objects, offset_x): #this function draws everything for this game
    for tile in background: #loops through every tile we have and it draws the background image at every cooirdinate
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
    
    pygame.display.update() 

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for i in objects:
        if pygame.sprite.collide_mask(player, i):
            if dy > 0:
                player.rect.bottom = i.rect.top
                player.landed()
            elif dy <0:
                player.rect.top = i.rect.bottom
                player.hit_head()

            collided_objects.append(i)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx,0)
    player.update()
    return collided_object

def handle_move(player, objects): #checks what keys are being pressed in the keyboard
    keys = pygame.key.get_pressed()
    player.x_vel = 0 #if we dont reset it to 0, it will keep moving forward, this allows us to only move only when the keys are being held down
    collide_left = collide(player, objects, -Player_Vel*2)
    collide_right = collide(player, objects, Player_Vel*2)
    if keys[pygame.K_LEFT] and not collide_left: #checks for left key being pressed then moves left
        player.move_left(Player_Vel)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(Player_Vel)
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

def main(window): #where our event loop will be (collisons, etc.)
    clock = pygame.time.Clock()
    background, bg_image = get_background("Yellow.png")
    block_size = 96 

    player = Player(100,100,50,50)
    fire = Fire(100, Height- block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i*block_size, Height - block_size, block_size) for i in range(-Width // block_size, (Width*2) // block_size)] #creates blocks on and off the screen (1000 pixels left and 1k right)
    objects = [*floor, Block(0, Height - block_size *2, block_size), Block(block_size*3, Height - block_size *4, block_size), fire]

    offset_x = 0 
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS) #ensures our while loop runs 60 frames a second (might be less if its slower)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count <2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image,player, objects, offset_x)

        if((player.rect.right - offset_x >= Width - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            
            offset_x += player.x_vel

    pygame.quit() #quits out of the game when the red "X" is clicked
    quit()

if __name__ == "__main__": #we only call this function only if we run this file directly, otherwise it wont run
    main(window) 