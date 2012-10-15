from math import *
import random
import operator

import os, pygame
from pygame.locals import *


## newer versions use NumPy, instead of this homebrewn vector stuff

def sadd (x, y):
    return map (operator.add, x, y)
def smul (s, x):
    def m (i):
        return s*i
    return map (m, x)

def rotate (angle, (x, y)):
    return (x * cos (angle) + y * sin (angle),
           -x * sin (angle) + y * cos (angle))

#Window size:
maxx, maxy = (1200, 900)
origin = (maxx/2, maxy/2)

start_at_mouse = True

#Do you want to see how it works?
drawRects = True


#(inner workings, too) How many balls in a rectangle until it gets split up:
maxBalls = 50

#How many balls per frame:
step = 10

# size of balls (in abstract units):
radius = 4
# and how many abstracts units per pixel:
gear = 0.25

def randcol (bright_from = 0.0, bright_to = 1.0):
    return [random.randrange(256*bright_from, 256*bright_to) for _ in 3*[None]]

def drawCirc (surf, p):
    color = randcol (0.5, 1)
    np = sadd (smul (gear, p), origin)
    if (gear * radius > 1):
        pygame.draw.circle (surf, color, np, gear * radius)
    else:
        surf.set_at (np, color)
def orts_richt ((angle, offset)):
    return ((sin (angle) * offset, cos (angle) * offset),
           (sin (angle - pi/2), cos (angle - pi/2)))
    
def drawLine (surf, (angle, offset)):
    color = randcol()
    p, r = orts_richt ((angle, offset))
    p1 = sadd (smul (-1000, r), p)
    p2 = sadd (smul ( 1000, r), p)
    pygame.draw.line (surf, color, sadd (smul (gear, p1), origin),
                      sadd (smul (gear, p2), origin))


class mRect:
    def __init__ (self, rect):
        self.rect = rect
        self.balls = []
        self.nballs = len (self.balls)
        self.rects = []
        nrect = Rect (self.rect.left*gear, self.rect.top*gear, self.rect.width*gear, self.rect.height*gear)
        if drawRects:
            pygame.draw.rect (screen, randcol(0, 0.5), nrect.move(maxx/2, maxy/2), 1)
    def meet (self, line):
        p, r = orts_richt (line)
        (px, py), (rx, ry) = p, r
        rect = self.rect
        ms = []
        try:
            y = rect.top
            x = rx * (y - py) / ry + px
            if (rect.left <= x < rect.right):
                ms.append ((x, y))
        except ZeroDivisionError:
            pass
        try:
            y = rect.bottom
            x = rx * (y - py) / ry + px
            if (rect.left <= x < rect.right):
                ms.append ((x, y))
        except ZeroDivisionError:
            pass
        try:
            x = rect.left
            y = ry * (x - px) / rx + py
            if (rect.top <= y < rect.bottom):
                ms.append ((x,y))
        except ZeroDivisionError:
            pass
        try:
            x = rect.right
            y = ry * (x - px) / rx + py
            if (rect.top <= y < rect.bottom):
                ms.append ((x,y))
        except ZeroDivisionError:
            pass
        return ms
    def meet1 (self, line):
        try:
            angle, offset = line
            return min ([rotate (-angle, m) for m in self.meet (line)])
        except ValueError:
            return None
    def hit (self, line):
        #debug:
        try:
            self.meet1 (line)
        except ValueError:
            raise NameError
        if self.nballs == 0:
            return None
        elif self.rects:
            rs_sorted = sorted ([(r.meet1 (line), r) for r in self.rects])
            rs = [r for (_, r) in rs_sorted if _ != None]
            for subrect in rs:
                pos = subrect.hit (line)
                if pos != None:
                    self.nballs += 1
                    return pos
            return None
        else:
            return self.hitballs (line)
    def hitballs (self, (angle, offset)):
        kd = [rotate (-angle, k) for k in self.balls]
        try:
            (b1, boffset) = min ([(b1, boffset) for (b1, boffset) in kd if abs (boffset - offset) <= 2*radius])
            k_ = rotate (angle, (b1 - sqrt (4*radius**2-(boffset-offset)**2), offset))
            return k_
        except ValueError:
            pass
    def splitting (self):
        left, width = self.rect.left, self.rect.width
        top, height = self.rect.top, self.rect.height
        self.rects = [mRect(Rect (left + i * width/2,
                                  top  + j * height/2,
                                  width/2,
                                  height/2))
                      for i in range(2) for j in range(2)]
    def addball (self, pos):
        global flag, n
        if not self.rect.collidepoint (pos):
            return False
        else:
            self.nballs += 1
            if len(self.balls) <= maxBalls and self.rects == []:
                self.balls.append (pos)
                return True
            elif self.rects == []:
                self.splitting ()
                balls = self.balls
                self.balls = []
                for r in self.rects:
                    for b in balls:
                        r.addball (b)
                for r in self.rects:
                    r.addball (pos) 
                return True
            else:
                return any ([r.addball (pos) for r in self.rects])
    def count (self):
        if self.rects == []:
            return len(self.balls)
        else:
            return sum([r.count() for r in self.rects])
def p (u, v):
    return sum (map (operator.mul, u, v))

def randLine ():
    angle = random.random() * 2 * pi
    offset = rotate (-angle, sadd ((-maxx/2, -maxy/2), pygame.mouse.get_pos ()))[1] /gear
    return (angle, offset)


pygame.init()
screen = pygame.display.set_mode((maxx, maxy))

def main():

    screen.get_rect ()
    mrect = mRect (Rect(-maxx/2/gear, -maxy/2/gear, maxx/gear, maxy/gear))
    if start_at_mouse:
        first_ball = smul(1/gear,  sadd ((-maxx/2, -maxy/2), pygame.mouse.get_pos ()))
    else:
        first_ball = (0,0)
    mrect . addball (first_ball)
    drawCirc (screen, first_ball)

    nballs = 1
    while True:
        for c in range(step):
            line = randLine()
            pos = mrect.hit (line)
            if pos and mrect.addball (pos):
                nballs += 1
                drawCirc (screen, pos)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
        pygame.display.flip()
    
main ()
