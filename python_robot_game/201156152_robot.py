#!/usr/bin/python

from curses import initscr, curs_set, newwin, endwin, KEY_RIGHT, KEY_LEFT, KEY_DOWN, KEY_UP, start_color, use_default_colors, init_pair, COLOR_BLUE, color_pair, COLOR_GREEN, COLOR_RED
from random import randrange, shuffle, randint
from os import system

class GameOver(Exception):
    pass

class Robot:
    def __init__(self, x=1, y=1, xlimit=37, ylimit=18):
        self.x = x
        self.y = y
        self.xlimit = xlimit
        self.ylimit = ylimit
    def move(self,x,y):
        self.x = self.x + x
        if(self.x <= 0 or self.x >= self.xlimit):
            raise GameOver
        self.y = self.y + y
        if(self.y <= 0 or self.y >= self.ylimit):
            raise GameOver
    def checkCollision(self, coordinates):
        if self.x <= coordinates[0]\
            and self.x + 4 >= coordinates[0]\
            and self.y <= coordinates[1]\
            and self.y + 3 >= coordinates[1]:
            return True
        return False
    def draw(self, window):
        init_pair(1,COLOR_BLUE,-1)
        window.addstr(self.y    , self.x + 2,   '#', color_pair(1))
        window.addstr(self.y + 1, self.x    , "[@ @]", color_pair(1))
        window.addstr(self.y + 2, self.x + 2,   '_', color_pair(1))
        window.addstr(self.y + 3, self.x + 1,  "J L" , color_pair(1))

class Board:
    def __init__(self, width=42, height=22, x=0, y=0):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        initscr()
        start_color()
        use_default_colors()
        self.window = newwin(height, width, y, x)
        self.window.keypad(1)
        self.window.box()
        curs_set(0)
    def draw(self):
        self.window.refresh()
    def clear(self):
        for i in xrange(self.height - 2):
            self.window.addstr( i + 1, 1, " " * (self.width - 2))

class Bomb:
    def __init__(self, win, x, y):
        self.window = win
        self.x = x
        self.y = y
    def draw(self):
        init_pair(2, COLOR_RED, -1)
        self.window.addstr(self.y, self.x, 'B', color_pair(2))

class DefuseCode:
    def __init__(self, win, x, y):
        self.window = win
        self.x = x
        self.y = y
    def draw(self):
        init_pair(3, COLOR_GREEN, -1)
        self.window.addstr(self.y, self.x, 'D', color_pair(3))

class DefuseCount:
    def __init__(self, value=0, incr=4):
        self.value = value
        self.currValue = value
        self.incrValue = incr
    def __sub__(self, val):
        self.value = self.value - val
        assert self.value >= 0
        return self
    def reset(self):
        self.currValue = self.currValue + self.incrValue
        self.value = self.currValue
    def draw(self, window):
        window.addstr(0, 20, " Defuse Codes: " + str(self.value) + " ")

class Score:
    def __init__(self):
        self.value = 0
    def __add__(self, val):
        self.value = self.value + val
        return self
    def draw(self, window):
        window.addstr(0, 2, " Score: " + str(self.value) + " ")

class Game:
    def __init__(self, width=42, height=22):
        self.width = width
        self.height = height
    def loop(self):
        self.board = Board(self.width, self.height)
        self.window = self.board.window
        self.score = Score()
        self.defuse = DefuseCount()
        self.pressedKey = 0
        self.robot = Robot(1, 1, self.width-5, self.height-4)
        self.initLevel()
        while self.update():
            pass
    def initLevel(self):
        self.robot.x = 1
        self.robot.y = 1
        self.pressedKey = 0
        self.defuse.reset()
        self.defuseCoords = []
        coords = []
        for i in range(self.defuse.value):
            xcoord = randint(1, self.width - 2)
            ycoord = randint(1, self.height - 2)
            while self.robot.checkCollision((xcoord, ycoord))\
                or (xcoord, ycoord) in coords:
                xcoord = randint(1, self.width - 2)
                ycoord = randint(1, self.height - 2)
            self.defuseCoords.append(DefuseCode(self.window, xcoord, ycoord))
            coords.append((xcoord, ycoord))
        while self.robot.checkCollision((xcoord, ycoord))\
            or (xcoord, ycoord) in coords:
            xcoord = randint(1, self.width - 2)
            ycoord = randint(1, self.height - 2)
        self.bomb = Bomb(self.window, xcoord, ycoord)
    def update(self):
        try:
            self.window.timeout(100)
            pressedKey = self.window.getch()
            if pressedKey != -1:
                self.pressedKey = pressedKey
            if self.pressedKey == 27:
                endwin()
                system("reset")
                print "Your Score:",self.score.value
                return False
            elif self.pressedKey == KEY_LEFT:
                self.robot.move(-1, 0)
            elif self.pressedKey == KEY_RIGHT:
                self.robot.move(1, 0)
            elif self.pressedKey == KEY_UP:
                self.robot.move(0, -1)
            elif self.pressedKey == KEY_DOWN:
                self.robot.move(0, 1)
           
            # Check if it has collided with defuse codes
            indicesToDelete = []
            for i in range(len(self.defuseCoords)):
                x = self.defuseCoords[i].x
                y = self.defuseCoords[i].y
                if self.robot.checkCollision((x,y)):
                    indicesToDelete.append(i)
                    self.defuse = self.defuse - 1
                    self.score = self.score + 10

            for i in range(len(indicesToDelete)):
                del self.defuseCoords[indicesToDelete[i]-i]

            bx = self.bomb.x
            by = self.bomb.y

            if self.robot.checkCollision((bx, by)):
                if self.defuse.value == 0:
                    self.initLevel()
                else:
                    raise GameOver
            
            self.board.clear()
            self.bomb.draw()
            for defuseCoord in self.defuseCoords:
                defuseCoord.draw()
            self.robot.draw(self.window)
            self.score.draw(self.window)
            self.defuse.draw(self.window)
            self.board.draw()
            return True
        except GameOver:
            endwin()
            system("reset")
            print "Game Over!!"
            print "Your Score:",self.score.value
            return False

win=Game()
win.loop()
