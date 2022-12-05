import pygame
import os
pygame.init()

s_widht = 800
s_height = int(s_widht*0.8)
screen = pygame.display.set_mode((s_widht,s_height))

clock = pygame.time.Clock()
fps = 60

# player variable 
move_left = False
move_right = False
shoot = False
grenade = False

# constants 
GRAVITY = 0.8
TILE_SIZE = 40

# loading images 
bullet_image = pygame.image.load("img/icons/bullet.png")
grenade_image = pygame.image.load("img/icons/grenade.png")
health_image = pygame.image.load("img/icons/health_box.png")
ammo_box_image = pygame.image.load("img/icons/ammo_box.png")
grenade_box_image = pygame.image.load("img/icons/grenade_box.png")

item_boxs = {
    'Health':health_image,
    'Ammo':ammo_box_image,
    'Grenade':grenade_box_image
}


def fill():
    screen.fill((0,0,0))


class Soldier(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed,ammo,grenade):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.max_ammo = ammo
        self.grenade = grenade
        self.max_grenade = grenade
        self.health = 100
        self.max_health = self.health
        self.animation_list = []
        self.animation = ['Idle','Run','Jump','Death']
        self.index = 0
        self.action = 0
        self.counter = 0
        self.flip = False
        self.direction = 1
        self.jump = False
        self.in_air = True
        self.vel_y = 0
        self.alive = True

        for i in self.animation:
            temp_list = []
            files = os.listdir(f"img/{self.char_type}/{i}")
            for j in range(len(files)):
                img = pygame.image.load(f"img/{self.char_type}/{i}/{j}.png")
                img = pygame.transform.scale(img, (scale,scale*1.4))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center =(x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        

    def update_animation(self):
        self.counter += 1
        if self.counter > 5:
            self.counter = 0
            self.index += 1
        if self.index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.index = len(self.animation_list[self.action])
            else:
                self.index = 0

        self.image = self.animation_list[self.action][self.index]
    
    def move(self,move_left,move_right):
        dx = 0
        dy = 0
        
        if move_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        
        if move_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        
        # jump of player 
        if self.jump and self.in_air == False:
            self.vel_y = -13
            self.jump = False
            self.in_air = True
        
        # applying gravity 
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10

        # floor 
        if self.rect.bottom >= 550:
            self.rect.bottom = 550
            self.in_air = False

        dy = self.vel_y
    
        self.rect.x += dx
        self.rect.y += dy

    def update_action(self,new_action):
        if self.action!=new_action:
            self.action = new_action
            self.index = 0
        
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.speed = 0
            self.update_action(3)
    
    def shoot(self):
        blt = Bullet(self.rect.centerx+(self.width*0.6*self.direction), self.rect.centery, self.direction)
        bullet_group.add(blt)


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False),self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 20
        self.image = bullet_image 
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
    
    def update(self):
        self.rect.x += self.speed*self.direction

        if self.rect.left >= s_widht or self.rect.right < 0:
            self.kill()

        # collision 
        if pygame.sprite.spritecollide(player, bullet_group, False):
            self.kill()
            player.health -= 10

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                self.kill()
                enemy.health -= 10


class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer =100
        self.speed = 10
        self.vel_y = -13
        self.image = grenade_image 
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
    
    def update(self):
        dx = self.speed*self.direction
        dy = self.vel_y

        self.vel_y+=GRAVITY
        if self.vel_y >10:
            self.vel_y = 10
        
        if self.rect.bottom >= 550:
            self.rect.bottom = 550
            self.speed = 0
        

        self.rect.x += dx
        self.rect.y += dy
    
        self.timer -= 1
        if self.timer <= 0:
            self.timer = 0
            self.kill()
            exp = Explosion(self.rect.x, self.rect.y, 100)
            explosion_group.add(exp)


            # check for damage 
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE*2 and \
                abs(self.rect.centery - player.rect.centery) < TILE_SIZE*2 :
                player.health -= 50
            
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE*2 and \
                abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE*2 :
                    enemy.health -= 50
            

class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for i in range(1,6):
            img = pygame.image.load(f'img/explosion/exp{i}.png')
            img = pygame.transform.scale(img, (scale,scale))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)


    
    def update(self):
        self.counter += 1
        if self.counter > 5:
            self.counter = 0
            self.index +=1 

        if self.index>=len(self.images)-1:
            self.kill()
        self.image = self.images[self.index]
    
class ItemBox(pygame.sprite.Sprite):
    def __init__(self,Item_type,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = Item_type
        self.image = item_boxs[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x+TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))
    
    def update(self):
        # check collision 
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Ammo':
                player.ammo+=5
            if self.item_type == 'Grenade':
                player.grenade+=3
            if self.item_type == 'Health':
                player.health +=25
                if player.health > 100:
                    player.health = player.max_health
            self.kill()
                
        

# creating groups 
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()


ammo = ItemBox('Ammo', 200, 300)
greande = ItemBox('Grenade', 300, 500)
item_box_group.add(ammo,greande)

player = Soldier('player', 200, 550, 100, 10, 30, 10)

enemy = Soldier('enemy', 500, 300, 100, 10, 30, 10)
enemy_group.add(enemy)


run = True
while run:
    fill()
    clock.tick(fps)


    player.update()
    player.move(move_left,move_right)
    player.draw()

    bullet_group.update()
    bullet_group.draw(screen)

    grenade_group.update()
    grenade_group.draw(screen)

    explosion_group.update()
    explosion_group.draw(screen)
    
    item_box_group.update()
    item_box_group.draw(screen)

    for enemy in enemy_group:
        enemy.update()
        enemy.move(False,False)
        enemy.draw()

    if player.alive:
        if move_left or move_right:
            player.update_action(1)
        elif player.in_air :
            player.update_action(2)
        elif shoot :
            player.shoot()
            shoot = False
            
        elif grenade:
            gr = Grenade(player.rect.centerx+(player.width*0.3*player.direction), player.rect.centery-(player.height*0.3), player.direction)
            grenade_group.add(gr)
            grenade = False

        else:
            player.update_action(0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                move_left = True
            if event.key == pygame.K_d:
                move_right = True
            if event.key == pygame.K_w:
                player.jump = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                move_left = False
            if event.key == pygame.K_d:
                move_right = False
            
        
    pygame.display.update()

pygame.quit()