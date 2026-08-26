# GALAGA FINAL (FINAL POLISH BUILD - MINI BOSS + EASIER BOSSES)
# Python 3.13.7 + pygame

import pygame, random, math, sys, os
pygame.init()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HIGH_SCORE_FILE = os.path.join(BASE_DIR, "highscore.txt")
WIDTH, HEIGHT = 900, 700
FPS = 60

WHITE=(255,255,255); RED=(255,80,80); GREEN=(80,255,80)
YELLOW=(255,255,80); CYAN=(80,255,255); PURPLE=(180,80,255)
ORANGE=(255,140,0); BLUE=(80,160,255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaga Ultimate FINAL MAX")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 22)

difficulty="NORMAL"

settings={
    "EASY":{"enemy_speed":3,"boss_hp":10,"fire_rate":0.5},
    "NORMAL":{"enemy_speed":5,"boss_hp":16,"fire_rate":1},
    "HARD":{"enemy_speed":8,"boss_hp":30,"fire_rate":1.4},
    "INSANE":{"enemy_speed":12,"boss_hp":80,"fire_rate":2.2}
}

# -------- HIGH SCORE --------
if not os.path.exists(HIGH_SCORE_FILE):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write("0")

def load_high():
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_high(score):
    try:
        if score > load_high():
            with open(HIGH_SCORE_FILE, "w") as f:
                f.write(str(score))
    except:
        pass

# -------- STARFIELD --------
stars=[[random.randint(0,WIDTH),random.randint(0,HEIGHT),random.randint(1,3)] for _ in range(150)]

def draw_stars():
    for s in stars:
        s[1]+=s[2]
        if s[1]>HEIGHT:
            s[0]=random.randint(0,WIDTH); s[1]=0
        pygame.draw.circle(screen,(200,200,255),(s[0],s[1]),s[2])

# -------- PARTICLES --------
particles=[]
def spawn_explosion(x,y,n=25):
    for _ in range(n):
        a=random.uniform(0,math.pi*2)
        sp=random.uniform(1.5,4)
        particles.append([x,y,math.cos(a)*sp,math.sin(a)*sp,random.randint(15,25)])

def update_particles():
    for p in particles:
        p[0]+=p[2]; p[1]+=p[3]; p[4]-=1
    particles[:] = [p for p in particles if p[4]>0]

def draw_particles():
    for p in particles:
        pygame.draw.circle(screen,(255,150,0),(int(p[0]),int(p[1])),max(1,p[4]//12))

# -------- UI --------
def tutorial():
    while True:
        clock.tick(FPS)
        screen.fill((0,0,0))
        draw_stars()

        lines=[
            "TUTORIAL",
            "Move: LEFT / RIGHT",
            "Shoot: SPACE",
            "K = skip wave",
            "Wave 4 = Challenge",
            "SPACE to start"
        ]
        for i,l in enumerate(lines):
            screen.blit(font.render(l,True,WHITE),(260,200+i*35))

        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE:
                return

def title():
    global difficulty
    while True:
        clock.tick(FPS)
        screen.fill((0,0,0))
        draw_stars()

        screen.blit(font.render("GALAGA FINAL MAX",True,WHITE),(300,250))
        screen.blit(font.render("1 EASY 2 NORMAL 3 HARD 4 ???",True,WHITE),(230,300))
        screen.blit(font.render(f"Current: {difficulty}",True,WHITE),(320,340))
        screen.blit(font.render("SPACE to Start",True,WHITE),(300,380))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_1: difficulty="EASY"
                if e.key==pygame.K_2: difficulty="NORMAL"
                if e.key==pygame.K_3: difficulty="HARD"
                if e.key==pygame.K_4: difficulty="INSANE"
                if e.key==pygame.K_SPACE: return

# -------- PLAYER --------
class Player:
    def __init__(self):
        self.x=WIDTH//2; self.y=HEIGHT-60
        self.speed=6
        self.bullets=[]
        self.cooldown=0
        self.lives=3
        self.score=0
        self.invincible=0
        self.dead=False
        self.respawn_timer=0
        self.radius=12
        self.death_timer=0

    def move(self,keys):
        if self.dead: return
        if keys[pygame.K_LEFT]: self.x-=self.speed
        if keys[pygame.K_RIGHT]: self.x+=self.speed

    def shoot(self):
        if self.cooldown==0 and not self.dead:
            self.bullets.append([self.x,self.y])
            self.cooldown=8

    def die(self):
        self.dead=True
        self.respawn_timer=90
        self.death_timer=60
        spawn_explosion(self.x,self.y,60)

    def update(self):
        if self.dead:
            self.respawn_timer-=1
            self.death_timer-=1
            if self.respawn_timer<=0:
                if self.lives<=0: return "GAME_OVER"
                self.dead=False
                self.invincible=120
                self.x=WIDTH//2
            return

        if self.cooldown>0: self.cooldown-=1
        if self.invincible>0: self.invincible-=1

        for b in self.bullets:
            b[1]-=10
        self.bullets=[b for b in self.bullets if b[1]>0]

    def draw(self):
        if self.dead:
            if self.death_timer>0:
                r=(60-self.death_timer)*2
                pygame.draw.circle(screen,(255,80,0),(self.x,self.y),r,2)
            return

        if self.invincible>0 and self.invincible%6<3: return

        pygame.draw.circle(screen,(0,180,255),(self.x,self.y+10),20,2)
        pygame.draw.polygon(screen,CYAN,[(self.x,self.y),(self.x-14,self.y+24),(self.x+14,self.y+24)])
        pygame.draw.circle(screen,BLUE,(self.x,self.y+10),5)
        pygame.draw.circle(screen,ORANGE,(self.x,self.y+28),4)

        for b in self.bullets:
            pygame.draw.rect(screen,YELLOW,(b[0]-2,b[1],4,12))

# -------- ENEMY --------
class Enemy:
    def __init__(self,x,y,wave,boss=False,mini=False):
        self.x=x; self.y=-100
        self.ty=y
        self.wave=wave
        self.boss=boss
        self.mini=mini

        base_hp = settings[difficulty]["boss_hp"]

        # ✅ Easier but still scaling
        if mini:
            self.max_hp = base_hp//2 + wave*2
        elif boss:
            self.max_hp = int(base_hp*0.75 + wave*3)  # balanced
        else:
            self.max_hp = 1+wave//3

        self.hp=self.max_hp
        self.radius=34 if boss else (24 if mini else 14)

        self.bullets=[]
        self.t=0
        self.dead_anim=0
        self.diving=False
        self.scored=False
        self.hit_flash=0

    def start_dive(self,player):
        self.diving=True
        dx=player.x-self.x; dy=player.y-self.y
        d=math.hypot(dx,dy)+0.001
        speed=settings[difficulty]["enemy_speed"]+2
        self.dvx=dx/d*speed
        self.dvy=dy/d*speed

    def update(self,player):
        if self.dead_anim>0:
            self.dead_anim-=1
            return

        self.t+=1

        if self.hit_flash>0:
            self.hit_flash-=1

        # side movement
        self.x += math.sin(self.t*0.05)*2

        # random dive
        if not self.diving and random.random()<0.002:
            self.start_dive(player)

        if self.diving:
            self.x+=self.dvx
            self.y+=self.dvy
            if self.y>HEIGHT:
                self.diving=False
                self.y=-100
        else:
            if self.y<self.ty:
                self.y+=2

        # -------- MINI BOSS --------
        if self.mini:
            if self.t % 50 == 0:
                for i in range(6):  # slightly easier (was 8)
                    a=i*(math.pi*2/6)
                    self.bullets.append([self.x,self.y,math.cos(a)*3,math.sin(a)*3])

            if self.t % 75 == 0:
                dx=player.x-self.x; dy=player.y-self.y
                d=math.hypot(dx,dy)+0.001
                self.bullets.append([self.x,self.y,dx/d*4,dy/d*4])

        # -------- BOSS --------
        if self.boss:
            phase = 1
            if self.hp < self.max_hp * 0.65:
                phase = 2
            if self.hp < self.max_hp * 0.35:
                phase = 3
            if difficulty == "INSANE" and self.hp < self.max_hp * 0.15:
                phase = 4

            speed_mult = 1.0
            if difficulty == "INSANE":
                speed_mult = 1.1

            # Phase 1
            if phase == 1:
                if self.t % 60 == 0:
                    for i in range(8):
                        a = i*(math.pi*2/8)
                        self.bullets.append([self.x,self.y,
                            math.cos(a)*3*speed_mult,
                            math.sin(a)*3*speed_mult])

            # Phase 2
            elif phase == 2:
                if self.t % 20 == 0:
                    angle = self.t*0.1
                    for i in range(2):
                        a = angle+i*math.pi
                        self.bullets.append([self.x,self.y,
                            math.cos(a)*4*speed_mult,
                            math.sin(a)*4*speed_mult])

            # Phase 3
            elif phase == 3:
                if self.t % 45 == 0:
                    for i in range(10):
                        a = i*(math.pi*2/10)
                        self.bullets.append([self.x,self.y,
                            math.cos(a)*4.2*speed_mult,
                            math.sin(a)*4.2*speed_mult])

                    dx = player.x-self.x
                    dy = player.y-self.y
                    d = math.hypot(dx,dy)+0.001
                    self.bullets.append([self.x,self.y,
                        dx/d*5*speed_mult,
                        dy/d*5*speed_mult])

            # 🔥 PHASE 4 (FINAL FORM)
            elif phase == 4:
                # spiral attack
                if self.t % 6 == 0:
                    angle = self.t * 0.25
                    for i in range(3):
                        a = angle + i*(math.pi*2/3)
                        self.bullets.append([self.x,self.y,
                            math.cos(a)*5.5,
                            math.sin(a)*5.5])

                # fast aimed shots
                if self.t % 20 == 0:
                    dx = player.x - self.x
                    dy = player.y - self.y
                    d = math.hypot(dx,dy)+0.001
                    self.bullets.append([self.x,self.y,
                        dx/d*6.5,
                        dy/d*6.5])

            speed_mult = 1.0
            if difficulty == "INSANE":
                speed_mult = 1.1  # toned down

            # Phase 1: slower ring
            if phase==1 and self.t % 60 == 0:
                for i in range(8):  # fewer bullets
                    a=i*(math.pi*2/8)
                    self.bullets.append([self.x,self.y,
                        math.cos(a)*3*speed_mult,
                        math.sin(a)*3*speed_mult])

            # Phase 2: slower cross
            elif phase==2 and self.t % 20 == 0:
                angle=self.t*0.1
                for i in range(2):
                    a=angle+i*math.pi
                    self.bullets.append([self.x,self.y,
                        math.cos(a)*4*speed_mult,
                        math.sin(a)*4*speed_mult])

            # Phase 3: controlled burst
            elif phase==3 and self.t % 45 == 0:
                for i in range(10):
                    a=i*(math.pi*2/10)
                    self.bullets.append([self.x,self.y,
                        math.cos(a)*4.2*speed_mult,
                        math.sin(a)*4.2*speed_mult])

                dx=player.x-self.x; dy=player.y-self.y
                d=math.hypot(dx,dy)+0.001
                self.bullets.append([self.x,self.y,
                    dx/d*5*speed_mult,
                    dy/d*5*speed_mult])

        # move bullets
        for b in self.bullets:
            b[0]+=b[2]
            b[1]+=b[3]

    def draw(self):
        if self.dead_anim>0:
            spawn_explosion(self.x,self.y,10)
            return

        shake = random.randint(-2,2) if self.hit_flash>0 else 0

        # -------- MINI BOSS LOOK --------
        if self.mini:
            pulse = int(math.sin(self.t*0.2)*3)

            pygame.draw.circle(screen,(60,30,0),(int(self.x),int(self.y)),self.radius+6+pulse)
            pygame.draw.circle(screen,(255,140,0),(int(self.x),int(self.y)),self.radius)
            pygame.draw.circle(screen,YELLOW,(int(self.x),int(self.y)),6)

            bar_w=80
            ratio=self.hp/self.max_hp
            pygame.draw.rect(screen,RED,(self.x-bar_w//2,self.y-40,bar_w,6))
            pygame.draw.rect(screen,GREEN,(self.x-bar_w//2,self.y-40,bar_w*ratio,6))

        # -------- BOSS LOOK --------
        elif self.boss:

            # 🔥 FINAL FORM VISUAL (INSANE ONLY)
            if difficulty == "INSANE" and self.hp < self.max_hp * 0.15:
                pulse = int(math.sin(self.t*0.3)*8)

                # outer glow (red)
                pygame.draw.circle(screen,(255,0,0),(int(self.x),int(self.y)),self.radius+14+pulse)

                # middle ring (yellow)
                pygame.draw.circle(screen,(255,255,0),(int(self.x),int(self.y)),self.radius+4)

                # inner body (purple)
                pygame.draw.circle(screen,(255,0,255),(int(self.x),int(self.y)),self.radius-10)

                # flashing core
                if self.t % 6 < 3:
                    pygame.draw.circle(screen,WHITE,(int(self.x),int(self.y)),6)

                # BIGGER HP BAR (feels like final form)
                bar_w=140
                ratio=self.hp/self.max_hp
                pygame.draw.rect(screen,RED,(self.x-bar_w//2,self.y-65,bar_w,10))
                pygame.draw.rect(screen,GREEN,(self.x-bar_w//2,self.y-65,bar_w*ratio,10))

            else:
                # NORMAL BOSS LOOK (your original)
                pulse = int(math.sin(self.t*0.15)*5)

                pygame.draw.circle(screen,(25,0,70),(int(self.x),int(self.y)),self.radius+10+pulse)
                pygame.draw.circle(screen,PURPLE,(int(self.x)+shake,int(self.y)),self.radius)
                pygame.draw.circle(screen,BLUE,(int(self.x),int(self.y)),self.radius-10)
                pygame.draw.circle(screen,RED,(int(self.x),int(self.y)),6)

                bar_w=120
                ratio=self.hp/self.max_hp
                pygame.draw.rect(screen,RED,(self.x-bar_w//2,self.y-55,bar_w,8))
                pygame.draw.rect(screen,GREEN,(self.x-bar_w//2,self.y-55,bar_w*ratio,8))
        # -------- NORMAL --------
        else:
            pygame.draw.polygon(screen,(120,0,0),
                [(self.x,self.y),(self.x-16,self.y+20),(self.x+16,self.y+20)])

        for b in self.bullets:
            pygame.draw.circle(screen,GREEN,(int(b[0]),int(b[1])),3)
# -------- WAVES --------
def create_wave(w):
    if w%4==0:
        return [Enemy(WIDTH//2,120,w,mini=True)]
    if w%5==0:
        return [Enemy(WIDTH//2,120,w,boss=True)]
    return [Enemy(120+c*80,80+r*50,w) for r in range(5) for c in range(8)]

# -------- MAIN --------
def main():
    while True:
        player=Player()
        wave=1

        title()
        tutorial()

        enemies=create_wave(wave)

        running=True
        while running:
            clock.tick(FPS)
            screen.fill((0,0,0))
            draw_stars()

            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    save_high(player.score)
                    pygame.quit(); sys.exit()
                if e.type==pygame.KEYDOWN:
                    if e.key==pygame.K_SPACE: player.shoot()
                    if e.key==pygame.K_k:
                        wave+=1
                        enemies=create_wave(wave)

            keys=pygame.key.get_pressed()
            player.move(keys)

            result=player.update()
            if result=="GAME_OVER":
                save_high(player.score)
                running=False
                continue

            for en in enemies:
                en.update(player)

            for b in player.bullets:
                for en in enemies:
                    if math.hypot(b[0]-en.x,b[1]-en.y)<en.radius:
                        en.hp-=1
                        en.hit_flash=5
                        if en.hp<=0 and not en.scored:
                            en.dead_anim=20
                            player.score+=100
                            en.scored=True
                        break

            for en in enemies:
                if math.hypot(player.x-en.x,player.y-en.y) < (player.radius + en.radius):
                    if player.invincible==0 and not player.dead:
                        player.lives-=1
                        player.die()

                for b in en.bullets:
                    if math.hypot(player.x-b[0],player.y-b[1])<player.radius:
                        if player.invincible==0 and not player.dead:
                            player.lives-=1
                            player.die()

            enemies=[e for e in enemies if not (e.hp<=0 and e.dead_anim==0)]

            if not enemies:
                wave+=1
                enemies=create_wave(wave)

            player.draw()
            for en in enemies: en.draw()

            update_particles()
            draw_particles()

            screen.blit(font.render(f"Score: {player.score}",True,WHITE),(10,10))
            screen.blit(font.render(f"Lives: {player.lives}",True,WHITE),(10,60))
            screen.blit(font.render(f"Wave: {wave}",True,WHITE),(10,90))
            screen.blit(font.render(f"High Score: {load_high()}",True,WHITE),(10,35))
            pygame.display.flip()

main()                                                                                                                                                                       