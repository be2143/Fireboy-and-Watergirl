import time

add_library('minim')
player = Minim(this)
path = os.getcwd()

RESOLUTION_W = 1245
RESOLUTION_H = 900
GROUND = 60
WATERGIRL_SCORE = 0
FIREBOY_SCORE = 0
START = True

class Creature:
    def __init__(self, x, y, r, g, img, img_w, img_h, num_slices):
        self.x = x
        self.y = y
        self.r = r
        self.g = g
        self.vx = 0
        self.vy = 0
        self.img = loadImage(path + "/images/" + img)
        self.img_w = img_w
        self.img_h = img_h
        self.num_slices = num_slices
        self.slice = 0
        self.dir = RIGHT
        self.on_block = False
        self.jump_sound = player.loadFile(path + "/sounds/jump.mp3")
                
    def gravity(self):
        collision = False
        on_platform = False
        
        # check if there's a platform under, if there's a platform stand on it
        for platform in game.platforms_list[::-1]:
            if self.y + self.r <= platform.y and self.x + self.r//2 >= platform.x and self.x - self.r//2 <= platform.x + platform.w:
                self.g = platform.y 
                on_platform = True
                break
            
        # check if there's a platform on top, if there's a platform creature cannot jump over it            
        for platform in game.platforms_list[::-1]:    
            if self.y + self.r >= platform.y+60+self.r and self.y + self.vy + self.r < platform.y+60+self.r and self.x + self.r//2 >= platform.x and self.x - self.r//2 <= platform.x + platform.w:
                self.vy = -self.vy
                # self.g = platform.y
                collision = True
                break
            
        # check if there's a block under, if so stand on it
        self.on_block = False
        for block in game.block_list:
            if self.y <= block.y and self.x + self.r//2 >= block.x and self.x - self.r//2 <= block.x + block.w and self.g == block.g:
                self.g = block.y + 10
                self.on_block = True
                break
        
        # if not standing on anything, then fall down towards the ground
        if not on_platform and not self.on_block:
            self.g = game.g
        
        # can jump only when it is standing on something
        if self.y + self.r >= self.g:
            self.vy = 0
        else:
            self.vy += 0.4
            if self.y + self.r + self.vy > self.g:
                self.vy = self.g - (self.y + self.r)
        
    def update(self):
        self.gravity()
        
        # make the creatures move left and right, giving velocity (vx)
        if self.key_handler[RIGHT] == True:
            self.vx = 7
            self.dir = RIGHT
        elif self.key_handler[LEFT] == True:
            self.vx = -7
            self.dir = LEFT
        else:
            self.vx = 0 
        
        # make the creatures jump, giving velocity (vy)
        if self.key_handler[UP] == True and self.y + self.r == self.g:
            self.vy = -10.5
            self.jump_sound.rewind()
            self.jump_sound.play()
        
        # creature's sprite would loop through when creature's moving, if not moving won't loop through
        if frameCount % 5 == 0 and self.vy == 0 and self.vx != 0:
            self.slice = (self.slice + 1) % self.num_slices
        elif self.vx == 0:
            self.slice = 0

        # can push the block when collided by its left or right side
        for block in game.block_list:
            if (self.x + self.r -12  >= block.x and self.x - self.r+12 <= block.x + block.w) and \
                (self.y + self.r-12 >= block.y and self.y - self.r+12 <= block.y + block.h):

                # if the creature is moving right and the block is to the left of the creature
                if self.vx > 0 and block.x <= self.x+self.r-12 and block.x >= self.x-self.r-12 and block.y < self.y + self.r -12:
                    self.x = block.x - self.r + 12
                    block.vx = self.vx
                    block.x += self.vx
                    block.pushed = False
                    break
                
                # if the creature is moving left and the block is to the right of the creature
                elif self.vx < 0 and block.x + block.w <= self.x+self.r +12  and block.x + block.w >= self.x - self.r+12  and block.y < self.y + self.r+12:
                    self.x = block.x + block.w +self.r -12
                    block.vx = self.vx
                    block.x += self.vx
                    block.pushed = False
                    break
        
        #finally creatures can move on the canvas with the velocity of vy and vx
        self.x += self.vx
        self.y += self.vy
        
    def display(self):
        self.update()
        
        # Keep the creatures within the game frame
        if self.x < self.img_w//2:
            self.x = self.img_w//2
        if self.x > game.w - self.img_w//2:
            self.x = game.w - self.img_w//2
            
        # Should collide with the square
        if self.x > game.square1.x -30 and game.square1.y < self.y < game.square1.y+ game.square1.h:
            self.x = game.square1.x -30
        
        # creature's sprite loop through when creature's moving only left and right
        if self.dir == RIGHT:
            image(self.img, self.x - self.img_w//2, self.y - self.img_h//2, self.img_w, self.img_h, self.slice * self.img_w, 0, (self.slice + 1) * self.img_w, self.img_h)
        elif self.dir == LEFT:
            image(self.img, self.x - self.img_w//2, self.y - self.img_h//2, self.img_w, self.img_h, (self.slice + 1) * self.img_w, 0, self.slice * self.img_w, self.img_h)

class Fireboy(Creature):
    def __init__(self, x, y, r, g):
        Creature.__init__(self, x, y, r, g, "fireboy.png", 842//8, 85, 8)
        self.key_handler = {RIGHT:False, LEFT:False, UP:False}
        self.diamond_sound = player.loadFile(path + "/sounds/Diamond.mp3")
    # check if there's is a diamond, if so remove the diamonds 
    def check(self):
        for diamonds in game.red_diamond:
            if diamonds.x <= self.x <= diamonds.x + diamonds.w//2 and self.y < diamonds.y + diamonds.h < self.g and self.vy ==0:
                self.diamond_sound.rewind()
                self.diamond_sound.play()
                global FIREBOY_SCORE 
                FIREBOY_SCORE += 1
                game.red_diamond.remove(diamonds)
                    
class Watergirl(Creature):
    def __init__(self, x, y, r, g):
        Creature.__init__(self, x, y, r, g, "watergirl.png", 879//8, 78, 8)
        self.key_handler = {RIGHT:False, LEFT:False, UP:False}
        self.diamond_sound = player.loadFile(path + "/sounds/Diamond.mp3")
     # check if there's is a diamond, if so remove the diamonds
    def check(self):
        for diamonds in game.blue_diamond:
            if diamonds.x <= self.x <= diamonds.x + diamonds.w//2 and self.y < diamonds.y + diamonds.h < self.g and self.vy ==0:
                self.diamond_sound.rewind()
                self.diamond_sound.play()
                global WATERGIRL_SCORE 
                WATERGIRL_SCORE += 1
                game.blue_diamond.remove(diamonds)
            
class Block:
    def __init__(self, x, y, w, h,img, g):
        self.x = x
        self.y= y 
        self.w = w
        self.h = h
        self.g = g
        self.img = loadImage(path + "/images/" + img)
        self.vx = 0
        self.vy = 0
        self.pushed = False
        
    # give gravity to the block, so that it would stay on the platforms and can fall down when pushed by the creature
    def gravity(self):
        on_platform = False
        for platform in game.platforms_list[::-1]:
            if self.y + self.h <= platform.y and self.x + self.w >= platform.x and self.x <= platform.x + platform.w:
                self.g = platform.y 
                on_platform = True
                break
        
        if not on_platform:
            self.g = game.g

        if self.y + self.h >= self.g:
            self.vy = 0
        else:
            self.vy += 0.4
            if self.y + self.h + self.vy > self.g:
                self.vy = self.g - (self.y + self.h)
        self.y += self.vy
        self.x += self.vx
    
    # Block should move when pushed by the creature
    def update(self): 
        self.gravity()
        if self.pushed:
            self.vx += game.fireboy.vx
            self.x += self.vx 
        else:
            self.vx = 0 
            
    def display(self):
        self.update()
        if game.w - 30< self.x + self.w:
            self.x = game.w - self.w -30
        # should be displayed wihtin the game frame    
        if self.x < 30:
            self.x = 30
        image(self.img, self.x, self.y, self.w,self.h)
        
class Platforms: 
    def __init__(self,x,y,w,h,img):
        self.x = x
        self.y= y 
        self.w = w
        self.h = h
        self.img = self.img = loadImage(path + "/images/" + img)
    def display(self):
        image(self.img, self.x, self.y, self.w, self.h)
        
class Square(Platforms):
    def __init__(self,x,y,w,h,img):
        Platforms.__init__(self,x,y,w,h,img)
        
class Doors:
    def __init__(self, x, y, r, img, img_w, img_h, num_slices):
        self.x = x
        self.y = y
        self.r = r
        self.img = loadImage(path + "/images/" + img)
        self.img_w = img_w
        self.img_h = img_h
        self.num_slices = num_slices
        self.slice = 0
        self.door_open = False

    def display(self):
        image(self.img, self.x - self.img_w//2, self.y - self.img_h//2, self.img_w, self.img_h, self.slice * self.img_w, 0, (self.slice + 1) * self.img_w, self.img_h)
    
class WatergirlDoor(Doors):
    def __init__(self, x, y, r):
        Doors.__init__(self, x, y, r, "watergirl_door.png", 1319//7, 119, 7)
        
    def open_door(self):
        # open the door when watergirl comes in front of the watergirl door
        if self.x < game.watergirl.x + game.watergirl.r < self.x+1319//7 - 100 and self.y < game.watergirl.y + game.watergirl.r < self.y+119:
            self.slice = (self.slice + 1)
            if self.slice >= self.num_slices:
                self.slice = self.num_slices-1 # once the door is open, keep it open
                self.door_open = True
        else:
            self.slice = 0
            
class FireboyDoor(Doors):
    def __init__(self, x, y, r):
        Doors.__init__(self, x, y, r, "fireboy_door.png", 1319//7, 121, 7)
    def open_door(self):
        if self.x < game.fireboy.x + game.fireboy.r < self.x+1319//7 - 100 and self.y < game.fireboy.y + game.fireboy.r < self.y+121:
            self.slice = (self.slice + 1)
            if self.slice >= self.num_slices:
                self.slice = self.num_slices-1
                self.door_open = True    
        else:
            self.slice = 0
            
class Obstacle:
    def __init__(self, x, y, img, img_w, img_h, num_slices):
        self.x = x
        self.y = y
        self.img = loadImage(path + "/images/" + img)
        self.img_w = img_w
        self.img_h = img_h
        self.num_slices = num_slices
        self.slice = 0
        
    # give flows to the obstacles
    def flow(self):
        if frameCount % 5 == 0:
            self.slice = (self.slice + 1) % self.num_slices
            
    def display(self):
        self.flow()
        image(self.img, self.x - self.img_w//2, self.y - self.img_h//2, self.img_w, self.img_h, self.slice * self.img_w, 0, (self.slice + 1) * self.img_w, self.img_h)
        
class Water(Obstacle):
    def __init__(self, x, y):
        Obstacle.__init__(self, x, y, "water.png", 447//5, 30, 5)
    
    # if fireboy collides with the water, he would exrtinguish
    def collide(self):
        if self.x < game.fireboy.x+game.fireboy.r < self.x + 600//4 - game.fireboy.r and game.fireboy.g == RESOLUTION_H-30 and game.fireboy.vy == 0:
            game.in_water = True
        else:
            game.in_water = False
        
    def display(self):
        self.flow()
        self.collide()
        image(self.img, self.x - self.img_w//2, self.y - self.img_h//2, self.img_w, self.img_h, self.slice * self.img_w, 0, (self.slice + 1) * self.img_w, self.img_h)

class Lava(Obstacle):
    def __init__(self, x, y):
        Obstacle.__init__(self, x, y, "lava.png", 476//5, 30, 5)
        
    # if watergirl collides with the water, she would evaporate
    def collide(self):
        if self.x < game.watergirl.x+game.watergirl.r < self.x + 600//4 - game.watergirl.r and game.watergirl.g == RESOLUTION_H-30 and game.watergirl.vy == 0:
            game.in_lava = True
        else:
            game.in_lava = False
            
    def display(self):
        self.flow()
        self.collide()
        image(self.img, self.x - self.img_w//2, self.y - self.img_h//2, self.img_w, self.img_h, self.slice * self.img_w, 0, (self.slice + 1) * self.img_w, self.img_h)
    
class Acid(Obstacle):
    def __init__(self, x, y):
        Obstacle.__init__(self, x, y, "acid.png", 453//5, 30, 5)
        
     # if fireboy or watergirl collides with acit, they would extinguish or evaporate
    def collide(self):
        if self.x < game.watergirl.x+game.watergirl.r < self.x + 600//4 - game.watergirl.r -25 and game.watergirl.g == 660 and game.watergirl.vy == 0:
            game.in_acid_watergirl = True
        else:
            game.in_acid_watergirl = False
            
        if self.x < game.fireboy.x+game.fireboy.r < self.x + 600//4 - game.fireboy.r -25 and game.fireboy.g == 660 and game.fireboy.vy == 0:
            game.in_acid_fireboy = True
        else:
            game.in_acid_fireboy = False
            
    def display(self):
        self.flow()
        self.collide()
        image(self.img, self.x - self.img_w//2, self.y - self.img_h//2, self.img_w, self.img_h, self.slice * self.img_w, 0, (self.slice + 1) * self.img_w, self.img_h)
        
class Smoke:
    
    def __init__(self, x, y, img, img_w, img_h, num_slices):
        self.x = x
        self.y = y
        self.img = loadImage(path + "/images/" + img)
        self.img_w = img_w
        self.img_h = img_h
        self.num_slices = num_slices
        self.slice = 0
        self.death = player.loadFile(path + "/sounds/Death.mp3")
        self.over_sound = player.loadFile(path +"/sounds/lose.mp3")
        
    # if one of the character collides withe obstacle, then display smoke    
    def display(self):
        if frameCount % 5 == 0:
            self.slice = (self.slice + 1)
            if self.slice == self.num_slices-1:
                self.slice = self.num_slices-1
                self.death.rewind()
                self.death.play()
                game.over = True # and finish the game
        image(self.img, self.x - self.img_w//2, self.y - self.img_h//2, self.img_w, self.img_h, self.slice * self.img_w, 0, (self.slice + 1) * self.img_w, self.img_h)
                    
class Diamond:
    def __init__(self, x, y, w, h, img):
        self.x = x
        self.y = y
        self.w = w 
        self.h = h
        self.img = loadImage(path + "/images/" + img)
    
    def display(self):
        image(self.img, self.x, self.y, self.w, self.h)    
    
class Board:
    def __init__(self, x, y, w, h, img):
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.img = loadImage(path + "/images/" + img)
        
    def display(self):
        image(self.img, self.x, self.y, self.w, self.h)
        
class Game:
    def __init__(self):
        
        self.w = RESOLUTION_W
        self.h = RESOLUTION_H
        self.g = GROUND
        self.background = loadImage(path + "/images/background.png") # load the background image
        self.bg_sound = player.loadFile(path +"/sounds/background.mp3") # load the background music
        
        self.fireboy = Fireboy(100, self.h - 85//2 - 30, 85//2, self.g)
        self.watergirl = Watergirl(100, 5*(self.h - 60)//6 +30 - 78//2, 78//2, self.g)
        
        self.over = False
        self.level = False
        self.in_water = False
        self.in_lava = False
        self.in_acid_watergirl = False
        self.in_acid_fireboy = False
        
        self.platforms_list = [Platforms(0, self.h - 30, self.w, 30, "platform10.png"), # bottom frame
                               Platforms(0, 5*(self.h - 60)//6 +30, 3*(self.w - 60)//8, 30, "platform01.png"), # platform01
                               Platforms(self.w - 30 - (self.w-60)//8, 5*(self.h - 60)//6+30, (self.w - 60)//8, 30, "platform02.png"), # platform02 (square1)
                               Platforms(30, 2*(self.h - 60)//3+30, 3*(self.w - 60)//8, 30, "platform03.png"), # platform03
                               Platforms((self.w - 60)//2, 3*(self.h - 60)//4 +30, 1*(self.w - 60)//4 + 75, 30, "platform04.png"), # platform04
                               Platforms(30, (self.h - 60)//2 +30, (self.w - 60)//4 +90, 30, "platform05.png"), # platform05
                               Platforms(3*(self.w - 60)//8 +60, (self.h - 60)//2 +30, 5*(self.w - 60)//8 + 60, 30, "platform06.png"), # platform06
                               Platforms(3*(self.w - 60)//4, (self.h - 60)//3 +30, (self.w - 60)//4+90, 30, "platform07.png"), # platform07
                               Platforms(30, (self.h - 60)//4 +30, 3*(self.w - 60)//8, 30, "platform08.png"),# platform08
                               Platforms(0, 0, self.w, 30, "platform11.png"), # top frame
                               Platforms(0, 0, 30, self.h, "platform12.png"), # left frame
                               Platforms(self.w -30, 0, 30, self.h, "platform13.png"), # right frame
                               ]
        
        self.square1 = Square(self.w - 30 - (self.w-60)//8, 5*(self.h - 60)//6+30, (self.w - 60)//8, (self.w - 60)//8, "sq.png")
        self.block_list = [Block(3*(self.w - 60)//4 +100, (self.h - 60)//3 +30 -100, 100, 100, "block.png", 310)]
        self.watergirl_door = WatergirlDoor((self.h - 60)//6 +30, (self.h - 60)//4 -28, 119//2)
        self.fireboy_door = FireboyDoor((self.h - 60)//6 +30 + 121, (self.h - 60)//4 -28, 121//2)
        
        self.water = Water(7*(self.h - 60)//10, self.h-20)
        self.lava = Lava(15*(self.h - 60)//16, self.h-20)
        self.acid = Acid(11*(self.w - 60)//16, 3*(self.h - 60)//4 +40)
        
        self.smoke_water = Smoke(7*(self.h - 60)//10, self.h-60, "end.png", 565//6, 86, 6)
        self.smoke_lava = Smoke(15*(self.h - 60)//16, self.h-60, "end.png", 565//6, 86, 6)
        self.smoke_acid = Smoke(11*(self.w - 60)//16, 3*(self.h - 60)//4, "end.png", 565//6, 86, 6)
        
        self.blue_diamond = [Diamond(100, (self.h - 60)//2 - 30, 36, 30, "blue_diamond.png"), #platform05
                             Diamond(7*(self.h - 60)//10 - 20, self.h-20 -70, 36, 30, "blue_diamond.png"), #on water
                             Diamond(13*(self.w - 60)//16 -30, (self.h - 60)//2 +30 -60, 36, 30, "blue_diamond.png") #platform06
                             ] 
        
        self.red_diamond = [Diamond(100, 2*(self.h - 60)//3 - 30, 36, 30, "red_diamond.png"), #platform03
                            Diamond(15*(self.h - 60)//16 -20, self.h-60 -30, 36, 30, "red_diamond.png"), #on lava
                            Diamond(15*(self.w - 60)//16 -30, (self.h - 60)//2 +30 -60, 36, 30, "red_diamond.png")] #platform06
        
        self.game_over = Board(0, 0, self.w, self.h, "game_over.png")           
        self.level_completed = Board(0, 0, self.w, self.h, "level_completed.png")
        self.start = Board(0, 0, self.w, self.h, "start.png")

        self.retry = Board((self.w-60)//4 - 396//4, 3*(self.h-60)//4, 396, 76, "retry.png")
        self.exit_button = Board(3*(self.w-60)//4 - 272//2, 3*(self.h-60)//4, 272, 80, "exit.png")
        
        self.restart = Board((self.w/2 - 258/2), 0, 258, 100, "restart.png")

    def display(self):
            
        image(self.background, 0, 0, self.w, self.h) # display the background image
    
        self.fireboy_door.open_door()  # display the doors
        self.fireboy_door.display()
        
        self.watergirl_door.open_door()  # open the doors, if crearutus reach them
        self.watergirl_door.display()
        
        # display the platforms to stand on, and game frames
        self.square1.display()
        for platforms in self.platforms_list:
            platforms.display()
            
        # display the obstacles
        self.water.display()
        self.lava.display()
        self.acid.display()
        
        # display diamonds
        for diamonds in self.blue_diamond:
            diamonds.display()
        for diamonds in self.red_diamond:
            diamonds.display()
        
        # display the block
        for blocks in self.block_list:
            blocks.display()
        
        # display the "restart" the game button
        if self.over == False and self.level == False:
            self.restart.display()
        
        # check the water obstacle
        if self.in_water != True and self.in_acid_fireboy != True:
            self.fireboy.check()
            self.fireboy.display()
        if self.in_water == True:
            self.smoke_water.display() 
        
        # check the lava obstacle
        if self.in_lava != True and self.in_acid_watergirl != True:
            self.watergirl.check()
            self.watergirl.display()
        if self.in_lava == True:
            self.smoke_lava.display()
        
        # check the acid obstacle
        if self.in_acid_fireboy or self.in_acid_watergirl:
            self.smoke_acid.display()
        
        # if both doors are open, level is completed
        if self.watergirl_door.door_open == True and self.fireboy_door.door_open == True:
            self.level = True
            
        # if level is completed (win), display the level completed board
        if self.level== True:
            time.sleep(0.5)
            self.level_completed.display()
            self.retry.display() # can retry the game
            self.exit_button.display() # or exit the game
        
        # if game is over (defeat), display the game over board
        if self.over == True:
            time.sleep(0.5)
            self.game_over.display()
            self.retry.display()
            self.exit_button.display()
        
        if START == True:
            self.bg_sound.play()
            self.start.display()

                
            
def setup():
    size(RESOLUTION_W, RESOLUTION_H)
    background(255,255,255)
    
def draw():
    background(255,255,255)
    game.display()
    
    if game.over == True or game.level == True:
        # display the score
        fill(0)
        textSize(70)
        text(str(FIREBOY_SCORE), RESOLUTION_W//2 + 60, RESOLUTION_H//2 - 35)
        text(str(WATERGIRL_SCORE), RESOLUTION_W//2 + 60, RESOLUTION_H//2 + 78)
    
def keyPressed():
    if keyCode == RIGHT:
        game.fireboy.key_handler[RIGHT] = True
    elif keyCode == LEFT:    
        game.fireboy.key_handler[LEFT] = True
    elif keyCode == UP:    
        game.fireboy.key_handler[UP] = True
        
    if key == 'd' or key == 'D':
        game.watergirl.key_handler[RIGHT] = True
    if key == 'a' or key == 'A':
        game.watergirl.key_handler[LEFT] = True
    if key == 'w' or key == 'W':
        game.watergirl.key_handler[UP] = True
    
def keyReleased():
    if keyCode == RIGHT:
        game.fireboy.key_handler[RIGHT] = False
    elif keyCode == LEFT:    
        game.fireboy.key_handler[LEFT] = False 
    elif keyCode == UP:    
        game.fireboy.key_handler[UP] = False  
        
    if key == 'd' or key == 'D':
        game.watergirl.key_handler[RIGHT] = False
    if key == 'a' or key == 'A':
        game.watergirl.key_handler[LEFT] = False
    if key == 'w' or key == 'W':
        game.watergirl.key_handler[UP] = False
        
def mouseClicked():
    global game, WATERGIRL_SCORE, FIREBOY_SCORE, START
    
    # initialize the game and starts the game for the first time
    if START == True:
        START = False
        WATERGIRL_SCORE = 0
        FIREBOY_SCORE = 0
        game = Game()
        loop()
    
    # can restart the game while playing
    if game.over == False and game.level == False:
        if (RESOLUTION_W/2 - 258/2) < mouseX < (RESOLUTION_W/2 + 258/2) and  0 < mouseY < 100:
            game = Game()
    
    if game.over == True or game.level == True:

        # if mouse clicked on RETRY, restarts the game
        if (RESOLUTION_W - 60)//4 - 396//4 < mouseX < (RESOLUTION_W - 60)//4 - 396//4 + 396 and  3*(RESOLUTION_H-60)//4 < mouseY < 3*(RESOLUTION_H-60)//4 + 76:
            game.over = False
            game.level = False
            WATERGIRL_SCORE = 0
            FIREBOY_SCORE = 0
            game = Game()
            loop()
    
        # if mouse clicked on EXIT, exits the game
        if 3*(RESOLUTION_W-60)//4 - 272//2 < mouseX < 3*(RESOLUTION_W-60)//4 - 272//2 + 272 and  3*(RESOLUTION_H-60)//4 < mouseY < 3*(RESOLUTION_H-60)//4 + 80:
            exit()
    
game = Game()
