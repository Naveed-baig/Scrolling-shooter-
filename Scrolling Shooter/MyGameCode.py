import pygame
from pygame import mixer
import os
import random
import csv
import button
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60


GRAVITY = 0.98
SCROLL_THRESH = 200
width = 800
height = int(width*0.8)
ROWS = 16
COLS = 150
TILE_SIZE = height // ROWS
TILE_TYPES = 21
screen_scroll =0
bg_scroll = 0
level = 1
MAX_LEVELS = 3
start_game = False
start_intro = False



screen = pygame.display.set_mode((width,height))
pygame.display.set_caption("Scrolling Shooter")
bullet_image = pygame.image.load('img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
heal_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("img/icons/grenade_box.png").convert_alpha()
item_boxes = {
    'Health':heal_box_img,
    'Ammol':ammo_box_img,
    'grenade':grenade_box_img  
}
# game variables 
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# load music and sounds 
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1,0.0,5000)

jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.5)


# button images 
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()




# loading background images 
pine1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()


bg = (10 ,100 ,100)
RED = (255 ,0 , 0) 
WHITE = (255,255,255)
GREEN = (0,255,0)
BLACK = (0,0,0)
PINK = (124,45,23)

img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f"img/tile/{x}.png")
    img = pygame.transform.scale(img,(TILE_SIZE,TILE_SIZE))
    img_list.append(img)

#define font 
font = pygame.font.SysFont('Futura',30)

def draw_text(text,font,text_col,x,y):
    img = font.render(text,True,text_col)
    screen.blit(img,(x,y))

def reset_level():
    enemy_Group.empty()
    bullet_Group.empty()
    grenade_Group.empty()
    item_box_Group.empty()
    explosion_Group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #create empty tile list 
    data= []
    for row in range(ROWS):
        r = [-1]*COLS
        data.append(r)
    
    return data 
def fillbg():      

    wid = sky_img.get_width()         
    for x in range(5):
        screen.blit(sky_img,((x*wid)-bg_scroll*0.5,0))
        screen.blit(mountain_img,((x*wid)-bg_scroll*0.6,height-mountain_img.get_height()-300))
        screen.blit(pine1_img,((x*wid)-bg_scroll*0.7,height-pine1_img.get_height()-150))
        screen.blit(pine2_img,((x*wid)-bg_scroll*0.8,height-pine1_img.get_height()))


    

class Soldier(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed,ammo,grenade):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.grenades = grenade
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = False
        self.flip = False
        self.animation_list = []
        self.action = 0
        self.index = 0
        self.new_time = pygame.time.get_ticks()
        self.timeAnimation = 0

        # create AI specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        # load all images for the player 
        animation_type = ['Idle','Run','Jump','Death']
        for animation in animation_type:
            # reset temporary list of images 
            temp_list =[]
            # counting amount of files in the folder 
            Num = len(os.listdir(f"img/{self.char_type}/{animation}/"))
            for i in range(Num):
                img = pygame.image.load(f"img/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width()*scale),int(img.get_height()*scale)))
                temp_list.append(img) 
            self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def update(self):
        self.update_Animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown-=1
        
        
    
    def move(self,move_left,move_right):
        screen_scroll =0 
        dx = 0
        dy = 0

    # assign movement variables 
        if move_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
            
        if move_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        
        # jump 
        if self.jump == True and self.in_air==False:
            self.vel_y = -13
            self.jump = False
            self.in_air = True

        # applying gravity 
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y
    
        # check collision 
        for tile in world.obstacle_list:
            # check collision in the x direction 
            if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                dx = 0
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0 
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                # check if below the ground ie jumping 
                if self.vel_y < 0:
                    self.vel_y = 0 
                    dy = tile[1].bottom - self.rect.top
                
                # check if above the ground 
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air= False
                    dy = tile[1].top - self.rect.bottom
                
        # check collision with water 
        if pygame.sprite.spritecollide(self,water_group,False):
            self.health = 0
        
        # check collision with exit 
        level_complete = False
        if pygame.sprite.spritecollide(self,exit_group,False):
            level_complete = True
        
        if self.rect.bottom > height:
            self.health = 0

        # check if player is going off the screen 
        if self.char_type == 'player':
            if self.rect.left+dx <  0 or self.rect.right+dx > width :
                dx = 0
        
        # update rectangular position 
        self.rect.x += dx
        self.rect.y += dy


        # update scroll based on player position 
        if self.char_type == 'player':
            if (self.rect.right > width-SCROLL_THRESH and bg_scroll < (world.level_length*TILE_SIZE)-width)\
                  or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        
        return screen_scroll,level_complete
    
    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullets(self.rect.centerx+(0.8*self.direction*self.rect.size[0]), self.rect.centery, self.direction)
            bullet_Group.add(bullet)
            # reduce the ammo
            self.ammo -=1
            shot_fx.play()
        
    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1,200) == 1:
                self.update_action(0)#0 Idle
                self.idling = True
                self.idling_counter = 50
            
            # check if ai is near the player 
            if self.vision.colliderect(player.rect):
                # stop running and face the player
                self.update_action(0)#0 Idle 
                self.update_Animation()
                # shoot the player 
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left,ai_moving_right)
                    self.update_action(1)#1 Run
                    self.move_counter+=1

                    # update ai vision as the enemy moves 
                    self.vision.center = (self.rect.centerx+75*self.direction,self.rect.centery)  

                    if self.move_counter > TILE_SIZE:
                        self.direction*=-1
                        self.move_counter*=-1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False
        # screen scroll 
        self.rect.x += screen_scroll


    def update_Animation(self):
        self.timeAnimation+=1
        cooldown = 7
        
        self.image = self.animation_list[self.action][self.index]

        # if pygame.time.get_ticks()-self.new_time > cooldown:
        #     new_time = pygame.time.get_ticks()
        #     self.index += 1
        
        if self.timeAnimation>=cooldown:
            self.timeAnimation = 0
            self.index += 1
        
        if self.index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.index = len(self.animation_list[self.action])-1
            else:
                self.index = 0 
    
    def update_action(self,new_action):
        if new_action != self.action:
            self.action = new_action
            self.index = 0
            self.new_time = pygame.time.get_ticks()
        
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False    
            self.update_action(3)
    
    def draw(self):
        # drawing the soldier on the screen 
        screen.blit(pygame.transform.flip(self.image,self.flip,False),self.rect)

class World():
    def __init__(self):
        self.obstacle_list = []
    
    def process_data(self,data):
        self.level_length = len(data[0])
        # iterate through each value in level data file 
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x*TILE_SIZE
                    img_rect.y = y*TILE_SIZE 
                    tile_data = (img,img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img,x*TILE_SIZE,y*TILE_SIZE)
                        water_group.add(water) 
                    elif tile >= 11 and tile <= 14:
                        decorate = Decoration(img,x*TILE_SIZE,y*TILE_SIZE)
                        decoration_group.add(decorate)
                    elif tile == 15:# Create a player
                        player = Soldier('player',x*TILE_SIZE,y*TILE_SIZE,1.65,5,20,5 )
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16: # Create Enemies
                        Enemy = Soldier('enemy',x*TILE_SIZE,y*TILE_SIZE,1.65,2,20,0)
                        enemy_Group.add(Enemy)
                    elif tile == 17: # Create Ammo Box
                        item_box = ItemBox('Ammol',x*TILE_SIZE,y*TILE_SIZE)
                        item_box_Group.add(item_box)
                    elif tile == 18: # Create Grenade Box
                        item_box = ItemBox('grenade',x*TILE_SIZE,y*TILE_SIZE)
                        item_box_Group.add(item_box)
                    elif tile == 19: # Create Health Box
                        item_box = ItemBox('Health',x*TILE_SIZE,y*TILE_SIZE)
                        item_box_Group.add(item_box)
                    elif tile == 20: # Create Exit Box
                        exit = Exit(img,x*TILE_SIZE,y*TILE_SIZE)
                        exit_group.add(exit)
        return player , health_bar
    
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0],tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2 , y + TILE_SIZE -self.image.get_height())
    
    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2 , y + TILE_SIZE -self.image.get_height())
    
    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2 , y + TILE_SIZE -self.image.get_height())
    
    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self,item_type,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x+TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))

    def update(self):
        # checking if the player has picked the particular box
        if pygame.sprite.collide_rect(self, player):
            # check what kind of it is 
            if self.item_type == "Health":
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == "Ammol":
                player.ammo += 15
            elif self.item_type == "Grenade":
                player.grenades +=3
            
            # delete the item box 
            self.kill()
        
        self.rect.x += screen_scroll

class HealthBar():
    def __init__(self,x,y,health,max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health
    
    def draw(self,health):
        #update with new health
        self.health = health
        # calculate health ratio 
        ratio = self.health /self.max_health
        pygame.draw.rect(screen,BLACK,(self.x-2,self.y-2,154,24))
        pygame.draw.rect(screen, RED, (self.x,self.y,150,20))
        pygame.draw.rect(screen, GREEN, (self.x,self.y,150*ratio,20))


class Bullets(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.center= (x,y)
        self.direction = direction
    
    def update(self):
        # move bullet 
        self.rect.x += (self.direction*self.speed)

        #delete bullets that are gone from the screen
        if self.rect.right < 0 or self.rect.left > width:
            self.kill()
        
        # check for the level  
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        
        if pygame.sprite.spritecollide(player, bullet_Group, False):
            if player.alive:
                player.health-=5
                self.kill()
        for enemy in enemy_Group:
            if pygame.sprite.spritecollide(enemy, bullet_Group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()
    
class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center= (x,y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    
    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # check for collision with level 
        for tile in world.obstacle_list:
            # check collision with walls 
            if tile[1].colliderect(self.rect.x + dx , self.rect.y, self.width , self.height):
                self.direction*=-1
                dx = self.direction*self.speed
            
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                self.speed = 0
                # check if below the ground  
                if self.vel_y < 0:
                    self.vel_y = 0 
                    dy = tile[1].bottom - self.rect.top
                
                # check if above the ground 
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air= False
                    dy = tile[1].top - self.rect.bottom


        # upgrating grenade position 
        self.rect.x += dx
        self.rect.y += dy

        # countdown timer 
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x,self.rect.y,0.6)
            explosion_Group.add(explosion)
            # do damage to anyone that is near to grenade 
            if abs(self.rect.centerx-player.rect.centerx) < TILE_SIZE*2\
                and abs(self.rect.centery - player.rect.centery)<TILE_SIZE*2:
                player.health -= 50

            for Enemy in enemy_Group:
                if abs(self.rect.centerx-Enemy.rect.centerx) < TILE_SIZE\
                and abs(self.rect.centery - Enemy.rect.centery)<TILE_SIZE:
                    Enemy.health -= 50
                

class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f'img/explosion/exp{num}.png')
            img = pygame.transform.scale(img,(int(img.get_width()*scale),int(img.get_height()*scale)))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center= (x,y)
        self.counter = 0
    
    def update(self):
        explosion_speed = 4
        # update explosion animation 
        self.counter +=1
        if self.counter >= explosion_speed:
            self.counter = 0
            self.index +=1 
            if self.index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.index]

class screen_fed():
    def __init__(self,direction,color,speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter+=self.speed
        if self.direction == 1:
            pygame.draw.rect(screen,self.color,(0-self.fade_counter,0,width//2,height))
            pygame.draw.rect(screen,self.color,(width//2+self.fade_counter,0,width//2,height))

            pygame.draw.rect(screen,self.color,(0,0-self.fade_counter,width,height//2))
            pygame.draw.rect(screen,self.color,(0,height//2+self.fade_counter,width,height//2))
        if self.direction == 2:
            pygame.draw.rect(screen,self.color,(0,0,width,0+self.fade_counter))
        if self.fade_counter > width:
            fade_complete = True
        
        return fade_complete
    
# create screen fades 
intro_fade = screen_fed(1,BLACK,4)
death_fade = screen_fed(2,PINK,4)

# create button 
start_button = button.Button(width//2-130, height//2-150, start_img, 1)
exit_button = button.Button(width//2-110, height//2+50, exit_img, 1)
restart_button = button.Button(width//2-100, height//2-50, restart_img, 2)



# Creating Enemy Group 
enemy_Group = pygame.sprite.Group()
# Creating Bullets Group
bullet_Group = pygame.sprite.Group()
# Creating grenade Group 
grenade_Group = pygame.sprite.Group()
# Creating Explosion Group 
explosion_Group = pygame.sprite.Group()
# Creatin ItemBox Group
item_box_Group = pygame.sprite.Group()
# Creating Water group 
water_group = pygame.sprite.Group()
# Creating decoration group 
decoration_group = pygame.sprite.Group()
# Creating Exit group 
exit_group = pygame.sprite.Group()






# create empty tile list 
world_data = []
for row in range(ROWS):
    r = [-1]*COLS
    world_data.append(r)
# load in level data and create world 
with open(f'level{level}_data.csv',newline='') as csvfile:
    reader = csv.reader(csvfile,delimiter=',')
    for x, row in enumerate(reader):
        for y,tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)

run = True
while run:
    clock.tick(fps)

    if start_game == False:
        # draw  menu 
        screen.fill((70,70,70))
        if start_button.draw(screen):
            start_game = True
            start_intro= True
        if exit_button.draw(screen):
            run = False
    else:

        # draw world map 
        fillbg()
        world.draw()
        # show player health 
        health_bar.draw(player.health)
        # show ammo 
        draw_text(f'AMMO:',font,WHITE,10,35)
        for x in range(player.ammo):
            screen.blit(bullet_image,(90+(x*10),40))
        # show grenade 
        draw_text(f'GRENADES:',font,WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img,(135+(x*15),60))
        # show
        player.update()
        player.draw()
        
        for Enemy in enemy_Group:
            Enemy.ai()
            Enemy.update()
            Enemy.draw()
            Enemy.move(False,False)

        # update and draw Groups for bullets 
        bullet_Group.update()
        bullet_Group.draw(screen)

        # update and draw Group for grenade 
        grenade_Group.update()
        grenade_Group.draw(screen)

        # update and draw Group for explosion 
        explosion_Group.update()
        explosion_Group.draw(screen)

        # update and draw Group for item box 
        item_box_Group.update()
        item_box_Group.draw(screen)

        # update and draw group for decoration 
        decoration_group.update()
        decoration_group.draw(screen)

        # update and draw group for water 
        water_group.update()
        water_group.draw(screen)

        # update and draw group for exit 
        exit_group.update()
        exit_group.draw(screen) 
    
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # update player actions
        if player.alive: 
            if shoot:
                player.shoot()
            elif grenade and grenade_thrown==False and player.grenades >0:
                grenade = Grenade(player.rect.centerx+(0.6*player.direction*player.rect.size[0]),player.rect.top,player.direction)
                grenade_Group.add(grenade)
                grenade_thrown = True
                player.grenades-=1
            if player.in_air:
                player.update_action(2) #Jump
            elif moving_left or moving_right:
                player.update_action(1) # Run
            else:
                player.update_action(0)# Idle
            screen_scroll,level_complete = player.move(moving_left,moving_right)
            bg_scroll -= screen_scroll

            # check if player has completed the level 
            if level_complete:
                start_intro = True
                level+=1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f'level{level}_data.csv',newline='') as csvfile:
                        reader = csv.reader(csvfile,delimiter=',')
                        for x, row in enumerate(reader):
                            for y,tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)
                
        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    # load in level data and create world 
                    with open(f'level{level}_data.csv',newline='') as csvfile:
                        reader = csv.reader(csvfile,delimiter=',')
                        for x, row in enumerate(reader):
                            for y,tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)
                
        
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_ESCAPE:
                run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False
    pygame.display.update()
pygame.quit()