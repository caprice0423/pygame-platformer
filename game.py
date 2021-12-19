#!/usr/bin/env python3

import json
from typing import Hashable
import pygame
import sys
from pygame.constants import K_LEFT, K_RIGHT, K_SPACE, K_p
from pygame.mixer import Sound, pre_init, stop

from pygame.mouse import get_pos
from pygame.time import set_timer

pygame.mixer.pre_init()
pygame.init()

# Window settings
TITLE = "Back To The Barnyard"
WIDTH = 960
HEIGHT = 640
FPS = 60
GRID_SIZE = 64

# Options
sound_on = True

# Controls
LEFT = pygame.K_LEFT
LEFT2 = pygame.K_a
RIGHT = pygame.K_RIGHT
RIGHT2 = pygame.K_d
JUMP = pygame.K_UP
JUMP2 = pygame.K_w
SPACE = pygame.K_SPACE
DOWN = pygame.K_DOWN

# Levels
level_Map = ["levels/Level-Map.json"]
levels = ["levels/Level-1.json", "levels/Level-2.json", "levels/Level-3.json"]
intro =  ["levels/Controls.json",
          "levels/Instructions.json"]


# Colors
TRANSPARENT = (0, 0, 0, 0)
DARK_BLUE = (16, 86, 103)
WHITE = (255, 255, 255)

# Fonts
FONT_SM = pygame.font.Font("assets/fonts/minya_nouvelle_bd.ttf", 25)
FONT_MD = pygame.font.Font("assets/fonts/minya_nouvelle_bd.ttf", 64)
FONT_GD = pygame.font.Font("fonts/GOODDC__.TTF", 50)

# Helper functions
def load_image(file_path, width=GRID_SIZE, height=GRID_SIZE):
    img = pygame.image.load(file_path)
    img = pygame.transform.scale(img, (width, height))
    return img

def play_sound(sound, loops=0, maxtime=0, fade_ms=0):
    if sound_on == True:
        sound.play(loops, maxtime, fade_ms)

def play_music():
    pygame.mixer.music.play(-1)
   
   #delete
def stop_music():
    pygame.mixer.music.stop()

# class Images():
hero_duck = load_image("assets/character/Crouch-1.png")
hero_walk1 = load_image("assets/character/Walk-1.png")
hero_walk2 = load_image("assets/character/Walk-2.png")
hero_jump = load_image("assets/character/Jump-1.png")
hero_idle = load_image("assets/character/Idle-1.png")
hero_images = {"run": [hero_walk1, hero_idle, hero_walk2],
               "jump": hero_jump,
               "idle": hero_idle,
               "duck": hero_duck}

block_images = {"fence": pygame.transform.scale(load_image("assets/tiles/skew2.png"), (50,100)),
                "Dirt": pygame.transform.scale(load_image("assets/tiles/Dirt1.png"), (100,200)),
                "barn": pygame.transform.scale(load_image("assets/tiles/testbarn1.png"), (200, 135)),
                "crate": pygame.transform.scale(load_image("assets/tiles/crate.png"), (50, 50)),
                "rock": pygame.transform.scale(load_image("assets/tiles/rock.png"), (80, 50)),
                "Grass": load_image("assets/tiles/grass_r.png"),
                "LV1": load_image("assets/tiles/spot1 (1).png"),
                "LV2": load_image("assets/tiles/spot2.png"),
                "LV3": load_image("assets/tiles/spot3.png"),
                }

intangible_images = {"feathers": pygame.transform.scale(load_image("assets/tiles/feathers1.png"), (50, 20)),
                 "coop": pygame.transform.scale(load_image("assets/tiles/coop1.png"), (200, 150)),
                 "corn field": pygame.transform.scale(load_image("assets/tiles/corn_stock.png"), (50, 150)),
                 "small corn field": pygame.transform.scale(load_image("assets/tiles/corn_stock.png"), (50, 112)),
                 "stables": pygame.transform.scale(load_image("assets/tiles/Stables.png"), (300, 250))
}

#Animal images
pig_img = pygame.transform.scale(load_image("assets/items/piggy.png"), (40,40))
rooster_img = pygame.transform.scale(load_image("assets/items/Rooseter.png"), (50,50))
cow_img = load_image("assets/items/cow.png")

heart_img = pygame.transform.scale(load_image("assets/items/corn.png"), (40,40))
flag_img = load_image("assets/items/tractor1.png")

tomatoe_img =  pygame.transform.scale(load_image("assets/items/tomatoe.png"),(25,25))

#Enemy images
trap_img = pygame.transform.scale(load_image("assets/enemies/trap.png"), (50, 50))
obstacle_img = [trap_img]
wolf_image =  pygame.transform.flip(load_image("assets/enemies/wolf2_walk1.png"), 1, 0)
wolf_image2 =  pygame.transform.flip(load_image("assets/enemies/wolf2_walk2.png"), 1,0)
wolf_image3 = pygame.transform.flip(load_image("assets/enemies/wolf2_walk3 (1).png"), 1,0)
wolf_images = [wolf_image3, wolf_image, wolf_image2]

# Sounds
JUMP_SOUND = pygame.mixer.Sound("sounds/jump.wav")
COIN_SOUND = pygame.mixer.Sound("sounds/pickup_coin.wav")
POWERUP_SOUND = pygame.mixer.Sound("sounds/powerup.wav")
HURT_SOUND = pygame.mixer.Sound("sounds/hurt.ogg")
DIE_SOUND = pygame.mixer.Sound("sounds/death.wav")
LEVELUP_SOUND = pygame.mixer.Sound("sounds/level_up.wav")
GAMEOVER_SOUND = pygame.mixer.Sound("sounds/game_over.wav")

class Entity(pygame.sprite.Sprite):

#BE CAREFUL WITH NAME BECAUSE OF ENEMIES
    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        # self.name = name
        self.rect = self.image.get_rect()
        
        self.rect.x = x
        self.rect.y = y

        self.vy = 0
        self.vx = 0

    def apply_gravity(self, level):
        self.vy += level.gravity
        self.vy = min(self.vy, level.terminal_velocity)

#Standard tiles 
class Block(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

#Main class for the Character
class Character(Entity):

    def __init__(self, images):
        super().__init__(0, 0, images['idle'])

        self.image_idle_right = images['idle']
        self.image_idle_left = pygame.transform.flip(self.image_idle_right, 1, 0)
        self.images_run_right = images['run']
        self.images_run_left = [pygame.transform.flip(img, 1, 0) for img in self.images_run_right]
        self.image_jump_right = images['jump']
        self.image_jump_left = pygame.transform.flip(self.image_jump_right, 1, 0)
        self.image_duck_right = images['duck']
        self.image_duck_left = pygame.transform.flip(self.image_duck_right, 1, 0)

        self.running_images = self.images_run_right
        self.image_index = 0
        self.steps = 0

        self.ducking = False

        self.speed = 6
        self.jump_power = 17

        self.vx = 0
        self.vy = 0
        self.facing_right = True
        self.on_ground = True

        self.score = 0

        self.hearts = 3
        self.max_hearts = 3
        self.invincibility = 0

        self._layer = 1

    def move_left(self):
        self.vx = -self.speed
        self.facing_right = False
        self.movingleft = True
        self.ducking = False

    def move_right(self):
        self.vx = self.speed
        self.facing_right = True
        self.ducking = False
       

    def stop(self):
        self.vx = 0

    def jump(self, blocks):
        self.ducking = False
        self.rect.y += 1

        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        if len(hit_list) > 0:
            self.vy = -1 * self.jump_power
            play_sound(JUMP_SOUND)

        self.rect.y -= 1

    #Make it smoother?
    def duck(self):
       self.ducking = True
       

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > level.width:
            self.rect.right = level.width

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx

        hit_list = pygame.sprite.spritecollide(self, blocks, False)
        
        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = 0
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = 0

        self.on_ground = False
        self.rect.y += self.vy + 1 # the +1 is hacky. not sure why it helps.
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def inventory(self, animals):
        hit_list = pygame.sprite.spritecollide(self, animals, True)
    
        for animals in hit_list:
            self.score += animals.value
           
    def getval(self):
        return self.score

    def process_enemies(self, enemies):
        hit_list = pygame.sprite.spritecollide(self, enemies, False)

        if len(hit_list) > 0 and self.invincibility == 0:
            play_sound(HURT_SOUND)
            self.hearts -= 1
            self.invincibility = int(0.75 * FPS)


    def process_powerups(self, powerups):
        hit_list = pygame.sprite.spritecollide(self, powerups, True)

        for p in hit_list:
            play_sound(POWERUP_SOUND)
            p.apply(self)

    def check_flag(self, level):
        hit_list = pygame.sprite.spritecollide(self, level.flag, False)

        if len(hit_list) > 0:
            level.completed = True
            play_sound(LEVELUP_SOUND)

    def set_image(self):
        if self.on_ground:
            if self.vx != 0:
                if self.facing_right:
                    self.running_images = self.images_run_right
                else:
                    self.running_images = self.images_run_left

                self.steps = (self.steps + 1) % self.speed # Works well with 2 images, try lower number if more frames are in animation

                if self.steps == 0:
                    self.image_index = (self.image_index + 1) % len(self.running_images)
                    self.image = self.running_images[self.image_index]

            elif self.ducking == True:
                if self.facing_right:
                    self.image = self.image_duck_right
                else:
                    self.image = self.image_duck_left
            else:
                if self.facing_right:
                    self.image = self.image_idle_right
                   
                else:
                    self.image = self.image_idle_left
                   
        else:
            if self.facing_right:
                self.image = self.image_jump_right
            else:
                self.image = self.image_jump_left

    def die(self):
        
        if self.hearts > 0:
            play_sound(DIE_SOUND)
        else:
            play_sound(GAMEOVER_SOUND)

    def respawn(self, level):
        self.rect.x = level.start_x
        self.rect.y = level.start_y
        self.hearts = self.max_hearts
        self.invincibility = 0
        self.facing_right = True

    def update(self, level):
        self.process_enemies(level.enemies)
        self.apply_gravity(level)
        self.move_and_process_blocks(level.blocks)
        self.check_world_boundaries(level)
        self.set_image()

        if self.hearts > 0:
            self.inventory(level.animals)
            self.process_powerups(level.powerups)
            self.check_flag(level)

            if self.invincibility > 0:
                self.invincibility -= 1

        else:
            self.die()

#Animals the farmer finds
class Animals(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.value = 1

#Main class for all the enemy capabilities and constraints        
class Enemy(Entity):
    def __init__(self, x, y, images):
        super().__init__(x, y, images[0])
        self.images_left = images
        self.images_right = [pygame.transform.flip(img, 1, 0) for img in images]
        self.current_images = self.images_left
        self.image_index = 0
        self.steps = 0

    def reverse(self):
        self.vx *= -1

        if self.vx < 0:
            self.current_images = self.images_left
        else:
            self.current_images = self.images_right

        self.image = self.current_images[self.image_index]

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.reverse()
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.reverse()

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()
               

        self.rect.y += self.vy # the +1 is hacky. not sure why it helps.
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def set_images(self):
        if self.steps == 0:
            self.image = self.current_images[self.image_index]
            self.image_index = (self.image_index + 1) % len(self.current_images)

        self.steps = (self.steps + 1) % 20 # Nothing significant about 20. It just seems to work okay.

    def is_near(self, hero):
        return abs(self.rect.x - hero.rect.x) < 2 * WIDTH

    def update(self, level, hero):
        if self.is_near(hero):
            self.apply_gravity(level)
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.set_images()
       

    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.vx = self.start_vx
        self.vy = self.start_vy
        self.current_images = self.images_left
        self.image = self.current_images[0]
        self.steps = 0

#Attack Method
class Throw(Entity):
    def __init__(self, x, y, images):#, movement_speed, existing_time):
        super().__init__(x, y, images)#, movement_speed, existing_time)

#Wolf Enemy
class Wolf(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.start_x = x
        self.start_y = y
        self.start_vx = 5
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy 




#stagnant objects that decrease players health
class Obstacles(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.start_x = x
        self.start_y = y
        self.start_vx = 0
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

    def move_and_process_blocks(self, blocks):
        reverse = False

        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy + 1 # the +1 is hacky. not sure why it helps.
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        reverse = True

        for block in hit_list:
            if self.vy >= 0:
                self.rect.bottom = block.rect.top
                self.vy = 0

                if self.vx > 0 and self.rect.right <= block.rect.right:
                    reverse = False

                elif self.vx < 0 and self.rect.left >= block.rect.left:
                    reverse = False

            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

        if reverse:
            self.reverse()

#Objects that once touched, increase health
class Heart(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.hearts += 1
        character.hearts = max(character.hearts, character.max_hearts)

#End of game checkpoint
class Flag(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

# The class that sets up the levels
class Level():

    def __init__(self, file_path):
        #List of images
        self.starting_blocks = []
        self.starting_intangible = []
        self.starting_enemies = []
        self.starting_animals = []
        self.starting_powerups = []
        self.starting_flag = []
        self.starting_basic = []
        self.starting_spritez = []
        self.tomatoes = []

        #sprite groups
        self.blocks = pygame.sprite.Group()
        self.intangible = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.animals = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.flag = pygame.sprite.Group()
        self.active_sprites = pygame.sprite.Group()
        self.inactive_sprites = pygame.sprite.Group()
        self.spritez = pygame.sprite.Group()

      #reads the JSON file
        with open(file_path, 'r') as f:
            data = f.read()

        self.map_data = json.loads(data)

        self.width = self.map_data['width'] * GRID_SIZE
        self.height = self.map_data['height'] * GRID_SIZE
       
        self.start_x =  self.map_data['start'][0] * GRID_SIZE
        self.start_y =  self.map_data['start'][1] * GRID_SIZE
            

        for item in self.map_data['intangible_blocks']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            img = intangible_images[item[2]]
            self.starting_intangible.append(Block(x, y, img))

        for item in self.map_data['blocks']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            img = block_images[item[2]]
            self.starting_blocks.append(Block(x, y, img))


        for item in self.map_data['wolf']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(Wolf(x, y, wolf_images))
   

        for item in self.map_data['obstacles']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(Obstacles(x, y, obstacle_img))


#Checks the json file and adds elements to map
        for item in self.map_data['pig']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_animals.append(Animals(x, y, pig_img))

        for item in self.map_data['rooster']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_animals.append(Animals(x, y, rooster_img))

        for item in self.map_data['cow']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_animals.append(Animals(x, y, cow_img)) 

        for item in self.map_data['hearts']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(Heart(x, y, heart_img))

        for i, item in enumerate(self.map_data['flag']):
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE

            if i == 0:
                img = flag_img
            # else:
            #     img = flagpole_img
                self.starting_flag.append(Flag(x, y, img))

        self.background_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.scenery_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.inactive_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.active_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)

        #Setting display
        if self.map_data['background-color'] != "":
            self.background_layer.fill(self.map_data['background-color'])

        if self.map_data['background-img'] != "":
            background_img = pygame.image.load(self.map_data['background-img']).convert_alpha()

            if self.map_data['background-fill-y']:
                 h = background_img.get_height()
                 w = int(background_img.get_width() * HEIGHT / h)
                 background_img = pygame.transform.scale(background_img, (w, HEIGHT))

            if "top" in self.map_data['background-position']:
                start_y = 0
            elif "bottom" in self.map_data['background-position']:
                start_y = self.height - background_img.get_height()

            if self.map_data['background-repeat-x']:
                for x in range(0, self.width, background_img.get_width()):
                    self.background_layer.blit(background_img, [x, start_y])
            else:
                self.background_layer.blit(background_img, [0, start_y])

        if self.map_data['scenery-img'] != "":
            scenery_img = pygame.image.load(self.map_data['scenery-img']).convert_alpha()

            if self.map_data['scenery-fill-y']:
                h = scenery_img.get_height()
                w = int(scenery_img.get_width() * HEIGHT / h)
                scenery_img = pygame.transform.scale(scenery_img, (w, HEIGHT))

            if "top" in self.map_data['scenery-position']:
                start_y = 0
            elif "bottom" in self.map_data['scenery-position']:
                start_y = self.height - scenery_img.get_height()

            if self.map_data['scenery-repeat-x']:
                for x in range(0, self.width, scenery_img.get_width()):
                    self.scenery_layer.blit(scenery_img, [x, start_y])
            else:
                self.scenery_layer.blit(scenery_img, [0, start_y])

        pygame.mixer.music.load(self.map_data['music'])

        self.gravity = self.map_data['gravity']
        self.terminal_velocity = self.map_data['terminal-velocity']

        self.completed = False

        #adding images to respective sprite groups
        self.blocks.add(self.starting_blocks)
        self.intangible.add(self.starting_intangible)
        self.enemies.add(self.starting_enemies)
        self.animals.add(self.starting_animals)
        self.spritez.add(self.starting_spritez)
        self.powerups.add(self.starting_powerups)
        self.flag.add(self.starting_flag)

        self.active_sprites.add(self.animals, self.enemies, self.powerups, self.spritez)
        self.inactive_sprites.add(self.intangible, self.flag, self.blocks)

        # with this speed up blitting on slower computers?
        for s in self.active_sprites:
            s.image.convert()

        for s in self.inactive_sprites:
            s.image.convert()

        self.inactive_sprites.draw(self.inactive_layer)


        # is converting layers helpful at all?
        self.background_layer.convert()
        self.scenery_layer.convert()
        self.inactive_layer.convert()
        self.active_layer.convert()


    def reset(self):
        self.enemies.add(self.starting_enemies)
        self.animals.add(self.starting_animals)
        self.powerups.add(self.starting_powerups)
        self.active_sprites.add(self.animals, self.enemies, self.powerups)

        for e in self.enemies:
            e.reset()

        

class Game():

    SPLASH = 0
    START = 1
    PLAYING = 2
    PAUSED = 3
    LEVEL_COMPLETED = 4
    GAME_OVER = 5
    VICTORY = 6
    CONTROLS = 7
    INSTRUCTIONS = 8
    LEVELMAP = 9

    elapsed_time = 0
    lock = False

    

    def __init__(self):
        self.window = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        self.done = False 
        
        self.reset()

    def start(self):
        self.level = Level(levels[self.current_level])
        self.level.reset()
        self.hero.respawn(self.level)
        

    def advance(self):
        self.current_level += 1
        self.start()
        self.stage = Game.PLAYING
       
    def reset(self):
        self.hero = Character(hero_images)
        self.current_level = 0
        self.start()
        self.stage = Game.SPLASH

    def display_splash(self, surface):
        self.color = WHITE
        line1 = FONT_GD.render(TITLE, 1,  WHITE)
        line2 = FONT_SM.render("Press any key to start.", 1,  self.color) #remove
        line3 = FONT_SM.render("Play Game", 1,  self.color)
        line4 = FONT_SM.render("Controls", 1,  self.color)
        line5 = FONT_SM.render("Instructions", 1,  self.color)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;

        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;

        self.titled = surface.blit(line1, ((x1 ), y1 - 125))
        self.pg = surface.blit(line3, (x2 + 70, y2 - 50)) #ORIENTATION
        self.instruct = surface.blit(line4, (x2 + 70, y2 - 0))
        self.cred = surface.blit(line5, (x2 + 70, y2 + 50))
        
        self.pos = pygame.mouse.get_pos()
        
        
    def display_controls(self, surface):

         line = FONT_SM.render("Controls", 1, WHITE)      
         line2 = FONT_SM.render("back", 1, WHITE)
         line4 = FONT_SM.render("Character Move Left: Left arrow Key or Key “A”", 1, WHITE)
         line5 = FONT_SM.render("Character Jump: Up arrow Key or Key “W”", 1, WHITE)
         line6 = FONT_SM.render("Character Duck: Down arrow Key or Key “S”", 1, WHITE)
         line7 = FONT_SM.render("Throw Tomatoes:  Space Bar", 1, WHITE)
         line8 = FONT_SM.render("Pause the Game: Key “P”", 1, WHITE)
         line9 = FONT_SM.render("Mute the Game: Key “M”, Unmute with “U”", 1, WHITE)
         line10 = FONT_SM.render("Character Move Right: Right arrow Key or Key “D”", 1, WHITE)
      
         y1 = HEIGHT / 3 - line.get_height() / 2;

         x2 = WIDTH / 2 - line.get_width() / 2;
         y2 = y1 + line.get_height() + 16;

         self.instruct = surface.blit(line, (x2 , y2 -200)) #change name
         self.returning = surface.blit(line2, (x2 - 395, y2 +350))

         self.text2 = surface.blit(line5, (x2 - 300, y2 - 150))
         self.text3 = surface.blit(line4, (x2 - 300, y2 - 100))
         self.text4 = surface.blit(line6, (x2 - 300, y2 - 50))
         self.text5 = surface.blit(line10, (x2 - 300, y2 + 0))
         self.text6 = surface.blit(line8, (x2 - 300, y2 + 50))
         self.text7 = surface.blit(line9, (x2 - 300, y2 + 100))
         self.text1 = surface.blit(line7, (x2 - 300, y2 + 150))

         pos = pygame.mouse.get_pos()
         for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and self.stage == Game.CONTROLS:
                 if self.returning.collidepoint(pos):
                    self.stage = Game.SPLASH
                    self.level = Level(levels[self.current_level]) 
                  
                    
    def display_instructions(self, surface):

         line = FONT_SM.render("Instructions", 1, WHITE)
         line2 = FONT_SM.render("back", 1, WHITE)
         line3 = FONT_SM.render("You’re a farmer and your animals have gone missing!", 1, WHITE)
         line4 = FONT_SM.render("It’s your job to find them all and bring them back home.", 1, WHITE)
         line5 = FONT_SM.render("Beware of animal traps, ditches, and lurking wild animals!", 1, WHITE)
         line7 = FONT_SM.render("But dont worry, you aren't completely defenseless, you're armed with tomatoes!", 1, WHITE)
         line6 = FONT_SM.render("Good Luck Farmer!!", 1, WHITE)

         y1 = HEIGHT / 3 - line.get_height() / 2;

         x2 = WIDTH / 2 - line.get_width() / 2;
         y2 = y1 + line.get_height() + 16;

         self.cred = surface.blit(line, (x2 , y2 -200)) #change name
         self.returning = surface.blit(line2, (x2 - 395, y2 +350))
         self.ins1 = surface.blit(line3, (x2 - 200, y2 - 50))
         self.ins2 = surface.blit(line4, (x2 - 215, y2 - 0))
         self.ins3 = surface.blit(line5, (x2 - 220, y2 + 50))
         self.ins5 = surface.blit(line7, (x2 - 325, y2 + 100))
         self.ins4 = surface.blit(line6, (x2 - 45, y2 + 150))

         pos = pygame.mouse.get_pos()
         for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and self.stage == Game.INSTRUCTIONS:
                 if self.returning.collidepoint(pos):
                    self.stage = Game.SPLASH
                    self.level = Level(levels[self.current_level]) 
            

#primary_text --> possible clean up
    def display_message(self, surface, primary_text, secondary_text):

        line1 = FONT_MD.render(primary_text, 1, WHITE)
        line2 = FONT_SM.render(secondary_text, 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2; 
        y1 = HEIGHT / 3 - line1.get_height() / 2; 

        x2 = WIDTH / 2 - line2.get_width() / 2; 
        y2 = y1 + line1.get_height() + 16; 

        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))

    def display_stats(self, surface):
        hearts_text = FONT_SM.render("Hearts: " + str(self.hero.hearts), 1, WHITE)
        inventory_text = FONT_SM.render("Animals: " + str(self.hero.score), 1, WHITE)

        surface.blit(inventory_text, (WIDTH - inventory_text.get_width() - 32, 32))
        surface.blit(hearts_text, (32, 32))

        cool = self.clock.tick()
        self.elapsed_time += cool
 

    def process_events(self):

        Level_Select = {"Level1": "[320, 448]", "Level2": "[640, 448]", "Level3": "[960, 448]"}
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

            # allows mouse usage in the splash menu
            elif event.type == pygame.MOUSEBUTTONDOWN and self.stage == Game.SPLASH:

                if self.pg.collidepoint(self.pos) and self.stage == Game.SPLASH:
                    #change color
                    self.stage = Game.LEVELMAP
                    self.level = Level(level_Map[0])

                    
                elif self.instruct.collidepoint(self.pos):
                    self.stage = Game.CONTROLS
                    self.level = Level(intro[0])

                    #WORK ON INSTRUCTIONS SCREEN
                elif self.cred.collidepoint(self.pos):
                    self.stage = Game.INSTRUCTIONS
                    self.level = Level(intro[1])

            elif event.type == pygame.KEYDOWN:
                #"or self.stage == Game.START" unecessary code? 
                if self.stage == Game.SPLASH and event.key == pygame.K_y:  #change key
                    self.stage = Game.PLAYING
                    play_music()
                   
                elif self.stage == Game.PLAYING:
                     if event.key == JUMP or event.key == JUMP2:
                         self.hero.jump(self.level.blocks)
                     
                #pause constraint
                if self.stage == Game.PLAYING and event.key == pygame.K_p:
                    self.stage = Game.PAUSED
                elif self.stage == Game.PAUSED and event.key == pygame.K_p:    
                    self.stage = Game.PLAYING

                #muted constraint
                if self.stage == Game.PLAYING and event.key == pygame.K_m:
                    stop_music()
                elif self.stage == Game.PLAYING and event.key == pygame.K_u:    
                    play_music()

                elif self.stage == Game.LEVEL_COMPLETED:
                    self.advance()
                    self.hero.score = 0

                elif self.stage == Game.VICTORY or self.stage == Game.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset()

                elif self.stage == Game.LEVELMAP:
                    
                    currentpos = [self.level.start_x, self.level.start_y]

                    if str(currentpos) == Level_Select["Level1"]:
                        if event.key == K_RIGHT:   
                                self.level.start_x = 10 * GRID_SIZE
                                self.level.start_y = 7 * GRID_SIZE

                        
                        elif event.key == K_SPACE:
                            self.level = Level(levels[0])
                            self.level.start_x = 4 * GRID_SIZE
                            self.level.start_y = 8 * GRID_SIZE
                            self.stage = Game.PLAYING
                            play_music()
                            self.level.reset()
                            self.hero.respawn(self.level)

                    elif str(currentpos) == Level_Select["Level2"]:
                            if event.key == K_RIGHT:
                                self.level.start_x = 15 * GRID_SIZE
                                self.level.start_y = 7 * GRID_SIZE

                            elif event.key == K_LEFT:
                                self.level.start_x = 5 * GRID_SIZE
                                self.level.start_y = 7 * GRID_SIZE


                            elif event.key == K_SPACE:
                                self.level = Level(levels[1])
                                self.level.start_x = 1 * GRID_SIZE
                                self.level.start_y = 8 * GRID_SIZE
                                self.stage = Game.PLAYING
                                play_music()
                                self.level.reset()
                                self.hero.respawn(self.level)

                    elif str(currentpos) == Level_Select["Level3"]:
                        if event.key == K_LEFT:
                                self.level.start_x = 10 * GRID_SIZE
                                self.level.start_y = 7 * GRID_SIZE
                        
                        elif event.key == K_SPACE:
                                self.level = Level(levels[2])
                                self.level.start_x = 3 * GRID_SIZE
                                self.level.start_y = 8 * GRID_SIZE
                                self.stage = Game.PLAYING
                                self.level.reset()
                                self.hero.respawn(self.level)


#player keys

        pressed = pygame.key.get_pressed()
        
        
        if self.stage == Game.PLAYING:
        
            if (self.hero.rect.y > 600):
                 self.hero.respawn(self.level)
                 self.hero.hearts -= 1
                
            
            if pressed[LEFT] or pressed[LEFT2]:
                self.hero.move_left()
                if pressed[K_SPACE]:
                    if self.elapsed_time > 200 and len(self.level.tomatoes) <= 1:
                        self.level.tomatoes.append(Throw(self.hero.rect.x + 10, self.hero.rect.y, tomatoe_img))
                        self.elapsed_time = 0

            elif pressed[RIGHT] or pressed[RIGHT2]:
                self.hero.move_right()
                if pressed[K_SPACE]:
                    if self.elapsed_time > 200 and len(self.level.tomatoes) <= 1:
                        self.lock = True
                        self.level.tomatoes.append(Throw(self.hero.rect.x + 10, self.hero.rect.y, tomatoe_img))
                        self.elapsed_time = 0
 
            elif pressed[DOWN]: 
                self.hero.duck()
                if pressed[K_SPACE]:
                    if self.elapsed_time > 200 and len(self.level.tomatoes) <= 1:
                        self.level.tomatoes.append(Throw(self.hero.rect.x + 10, self.hero.rect.y +20, tomatoe_img))
                        self.elapsed_time = 0
            
            elif pressed[K_SPACE]:
                    if self.elapsed_time > 200 and len(self.level.tomatoes) <= 1:
                        self.level.tomatoes.append(Throw(self.hero.rect.x + 10, self.hero.rect.y, tomatoe_img))
                        self.elapsed_time = 0

            else:
                self.hero.stop()

    def update(self):
        
        for item in self.level.tomatoes:

            if pygame.sprite.spritecollide(item, self.level.enemies, True):
                self.level.tomatoes.remove(item)
                self.level.active_sprites.remove(item)

            if pygame.sprite.spritecollide(item, self.level.blocks, False):
                self.level.tomatoes.remove(item)
                self.level.active_sprites.remove(item)
                
            
            if self.hero.facing_right == True :
                item.rect.x += 10
                item.rect.y -= 1
                if self.elapsed_time > 50:
                    item.rect.x += 5
                    item.rect.y += 3

            elif self.hero.facing_right == False:
                item.rect.x -= 10 
                item.rect.y -= 1
                if self.elapsed_time > 50:
                    item.rect.x -= 5
                    item.rect.y += 3

            if self.elapsed_time > 500:
                self.level.tomatoes.remove(item)
                self.level.active_sprites.remove(item)
                self.elapsed_time = 0

        if self.stage == Game.PLAYING:
            self.hero.update(self.level)
            self.level.enemies.update(self.level, self.hero)
       

        elif self.stage == Game.LEVELMAP or self.stage == Game.CONTROLS or self.stage == Game.INSTRUCTIONS:
            self.level.reset()
            self.hero.respawn(self.level)

        if self.level.completed:
            if self.current_level < len(levels) - 1:
                self.stage = Game.LEVEL_COMPLETED                
                
            else: 
             self.stage = Game.VICTORY
            pygame.mixer.music.stop()

        elif self.hero.hearts == 0:
            self.level.reset()
            self.hero.respawn(self.level)
            self.stage = Game.GAME_OVER
            pygame.mixer.music.stop()

    def calculate_offset(self):
        x = -1 * self.hero.rect.centerx + WIDTH / 2

        if self.hero.rect.centerx < WIDTH / 2:
            x = 0
        elif self.hero.rect.centerx > self.level.width - WIDTH / 2:
            x = -1 * self.level.width + WIDTH

        return x, 0
    
    def draw(self):

        offset_x, offset_y = self.calculate_offset()
        
        for item in self.level.tomatoes:
            self.level.active_sprites.add(item)

        self.level.active_layer.fill(TRANSPARENT)
        self.level.active_sprites.draw(self.level.active_layer)

        if self.hero.invincibility % 3 < 2:
            self.level.active_layer.blit(self.hero.image, [self.hero.rect.x, self.hero.rect.y])

        self.window.blit(self.level.background_layer, [offset_x / 3, offset_y])
        self.window.blit(self.level.scenery_layer, [offset_x / 2, offset_y])
        self.window.blit(self.level.inactive_layer, [offset_x, offset_y])
        self.window.blit(self.level.active_layer, [offset_x, offset_y])

        if self.stage == Game.SPLASH:
            self.display_splash(self.window)
        elif self.stage == Game.PLAYING:
            self.display_stats(self.window)
        elif self.stage == Game.CONTROLS:
            self.display_controls(self.window)
        elif self.stage == Game.INSTRUCTIONS:
            self.display_instructions(self.window)
        elif self.stage == Game.START:
           pass #self.display_message(self.window, "Ready?!!!", "Press any key to start.")
        elif self.stage == Game.PAUSED:
            self.display_message(self.window, "PAUSED", "Press 'P' to Unpause.")
        elif self.stage == Game.LEVEL_COMPLETED:
            self.display_message(self.window, "Level Complete", "Press any key to continue.")
        elif self.stage == Game.VICTORY:
            self.display_message(self.window, "You Win!", "Press 'R' to restart.")
        elif self.stage == Game.GAME_OVER:
            self.display_message(self.window, "Game Over", "Press 'R' to restart.")

        pygame.display.flip()


    def loop(self):
        while not self.done:
            self.process_events()
            self.update()
            self.draw()
           
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.start()
    game.loop()
    
    pygame.quit()
    sys.exit()