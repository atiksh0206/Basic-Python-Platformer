#at 27:43 in video

import os 
import random
import math
import pygame
from os import listdir 
from os.path import isfile, join #allows us to dynamically load spreadsheets and images
pygame.init() #intitalizes the pygame module

pygame.display.set_caption("Platformer") #sets the caption at the top of the window

Width, Height = 1000, 800 #dimensions of playable window
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




class Player(pygame.sprite.Sprite): #we use sprite.Sprite for better collisions
    Color = (255,0,0)
    Gravity = 1
    Sprites = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)

    def __init__(self,x,y,width,height):
       self.rect = pygame.Rect(x,y,width,height) # ".rect" is a tuple that stores 4 individual values and "pygame.rect" lets us use different equations
       self.x_vel = 0 #these velocities is how fast we move the character in each direction
       self.y_vel = 0 #this also helps with gravity
       self.mask = None
       self.direction = "left"
       self.animation_count = 0 #changes the animation frames
       self.fall_count = 0
    
    def move(self,dx,dy):
        self.rect.x += dx
        self.rect.y += dy

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
        #self.y_vel += min(1, (self.fall_count / FPS) * self.Gravity)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
    def draw(self, win):
        self.sprite = self.Sprites["idle_" + self.direction][0]
        win.blit(self.sprite, (self.rect.x,self.rect.y))





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

def draw(window,background,bg_image,player): #this function draws everything for this game
    for tile in background: #loops through every tile we have and it draws the background image at every cooirdinate
        window.blit(bg_image, tile)
    player.draw(window)
    pygame.display.update() 

def handle_move(player): #checks what keys are being pressed in the keyboard
    keys = pygame.key.get_pressed()
    player.x_vel = 0 #if we dont reset it to 0, it will keep moving forward, this allows us to only move only when the keys are being held down
    if keys[pygame.K_LEFT]: #checks for left key being pressed then moves left
        player.move_left(Player_Vel)
    if keys[pygame.K_RIGHT]:
        player.move_right(Player_Vel)

def main(window): #where our event loop will be (collisons, etc.)
    clock = pygame.time.Clock()
    background, bg_image = get_background("Yellow.png")

    player = Player(100,100,50,50)
    run = True
    while run:
        clock.tick(FPS) #ensures our while loop runs 60 frames a second (might be less if its slower)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        player.loop(FPS)
        handle_move(player)
        draw(window, background, bg_image,player)

    pygame.quit() #quits out of the game when the red "X" is clicked
    quit()

if __name__ == "__main__": #we only call this function only if we run this file directly, otherwise it wont run
    main(window) 