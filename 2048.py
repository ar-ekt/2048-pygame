#--------------------Modules----------------
from os.path import basename
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.locals import *
import sys
from random import choice
from time import sleep
from copy import deepcopy

#--------------------Initial-screen---------------
screenWidth = 700
screenHeight = 730
pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("2048")
pygame.mouse.set_visible(0)

Font = pygame.font.SysFont("", 45)
numberFont = pygame.font.SysFont("", 55)

#-----------------------Colors--------------------
black = (0,0,0)
white = (255,255,255)
purple = (170,0,120)
pink = (255,0,150)
light_blue = (0,70,250)
blue = (0,0,160)
light_azure = (0,240,240)
azure = (0,140,140)
azure_green = (0,220,60)
light_green = (45,250,0)
green = (0,120,0)
yellow = (240,230,0)
mustard = (190,170,0)
orange = (255,80,0)
red = (245,0,0)

colors = [light_blue, red, yellow, green, pink, blue, orange, azure_green, light_azure, mustard, purple, light_green, azure]

def changeBest(best):
    pathOfScript = basename(__file__)
    
    #---------------Read-current-script---------------
    f = open(pathOfScript)
    lines = f.readlines()
    f.close()
    
    #---------------Change-value-of-best--------------
    for index in range(len(lines)):
        if lines[index] == "#best-place\n":
            lines[index+1] = "best = %d\n" % best
            
    #---------------Write-edited-script---------------
    f = open(pathOfScript, "w")
    f.write("".join(lines))
    f.close()

def updateScreen(board, score, best):
    global screen, screenWidth, screenHeight
    global colors, black, white
    global Font, numberFont
    
    #--------------------Background-------------------
    pygame.draw.rect(screen, black, (0, 0, screenWidth, screenHeight))
    
    #--------------------Bordes-----------------------
    coorOfBorders = [(20,50,660,3), (20,50,3,660) ,(20,707,660,3), (677,50,3,660)]
    for border in coorOfBorders:
        pygame.draw.rect(screen, white, border)
    
    #---------------Score-&-BestScore-----------------
    label = Font.render("Score: %d" % score, 1, white)
    screen.blit(label, (20, 10))
    
    bestShow = max(best, score)
    label = Font.render("Best: %d" % bestShow, 1, white)
    lenOfDigs = {"0":17, "1":12, "2":18, "3":18, "4":19, "5":18, "6":18, "7": 19, "8": 18, "9":18}
    lenOfBest = sum([lenOfDigs[digit] for digit in str(bestShow)])
    widthOfBest = screenWidth - lenOfBest - 110
    screen.blit(label, (widthOfBest, 10))
    
    #--------------------tiles---------------------
    heightOftile = widthOftile = 156
    for row in range(4):
        for column in range(4):
            tile = board[row][column]
            if tile != 0: # not empty
                colorOftile = colors[tile-1]
                
                #--------------Display-frame-of-tile--------------
                coorOftile = (29+(widthOftile+6)*column, 59+(heightOftile+6)*row, widthOftile, heightOftile)
                pygame.draw.rect(screen, colorOftile, coorOftile)
                
                #--------------Display-value-of-tile--------------
                label = numberFont.render("%4d" % 2**tile, 1, white)
                screen.blit(label, (65+(widthOftile+6)*column, 118+(heightOftile+6)*row))
    
    pygame.display.flip()

def gameOverMsg():
    global screen, red, Font
    
    label = Font.render("Game Over", 1, red)
    screen.blit(label, (260, 10))
    pygame.display.flip()
    
    sleep(2)

def gameOver(board):
    for row in range(4):
        for column in range(4):
            tile = board[row][column]
            neighbours = [board[row+j][column+i] for j,i in ((0,1), (1,0)) if 0 <= row+j <= 3 and 0 <= column+i <= 3]
            if tile == 0 or tile in neighbours:
                return 0
    return 1

def shift(board, plus, rowRange, columnRange):
    for row in rowRange:
        for column in columnRange:
            tile = board[row][column]
            old_row = row
            old_column = column
            new_row = row + plus[0]
            new_column = column + plus[1]
            while 0 <= new_row <= 3 and 0 <= new_column <= 3 and tile != 0 and board[new_row][new_column] == 0:
                board[new_row][new_column] = tile
                board[old_row][old_column] = 0
                old_row = new_row
                old_column = new_column
                new_row = new_row + plus[0]
                new_column = new_column + plus[1]
            
def merge(board, plus, rowRange, columnRange):
    newScore = 0
    for row in rowRange:
        for column in columnRange:
            tile = board[row][column]
            new_row = row + plus[0]
            new_column = column + plus[1]
            if 0 <= new_row <= 3 and 0 <= new_column <= 3 and tile != 0 and tile == board[new_row][new_column]:
                board[row][column] = 0
                board[new_row][new_column] = tile + 1
                newScore += 2 ** board[new_row][new_column]
    return newScore

def changeBoard(board, score, motion):
    plus = {"up": (-1,0), "down": (1,0), "right": (0,1), "left": (0,-1)}[motion]
    rowRange = range(4)[::-1] if motion == "down" else range(4)
    columnRange = range(4)[::-1] if motion == "right" else range(4)
    
    shift(board, plus, rowRange, columnRange)
    score += merge(board, plus, rowRange, columnRange)
    shift(board, plus, rowRange, columnRange)
    
    return score

def rand(start, end, step=1):
    return choice(range(start, end+1, step))

def game(best):
    score = 0
    board = [[0]*4 for _ in range(4)]
    board[rand(0,3)][rand(0,3)] = 1
    board[rand(0,3)][rand(0,3)] = rand(1,2)
    
    #--------------previous-board-&-score-------------
    temp = {"board": deepcopy(board), "score": score}
    temp_temp = {"board": deepcopy(board), "score": score}
    
    arrowKeys = {pygame.K_UP: "up", pygame.K_DOWN: "down", pygame.K_RIGHT: "right", pygame.K_LEFT: "left"}
    z_flag = True
    
    while True:
        #--------------------Update-screen----------------
        updateScreen(board, score, best)
        
        #----------------------Game-over------------------
        if gameOver(board):
            gameOverMsg()
            return max(best, score)
        
        #------------------------Moves--------------------
        for event in pygame.event.get():
            #------------------Quit-button--------------------
            if event.type == pygame.QUIT:
                return max(best, score)
            
            elif event.type == pygame.KEYDOWN:
                #------------------Escape-key---------------------
                if event.key == pygame.K_ESCAPE:
                    return max(best, score)
                
                #------------------Arrow-keys---------------------
                elif event.key in arrowKeys:
                    temp_temp["board"] = deepcopy(board)
                    temp_temp["score"] = score
                    score = changeBoard(board, score, arrowKeys[event.key])
                                        
                    if board == temp_temp["board"]: # Invalid move
                        continue
                    
                    temp = deepcopy(temp_temp)
                    
                    emptytiles = [(j,i) for j in range(4) for i in range(4) if board[j][i] == 0]
                    if emptytiles:
                        tileAdd = choice(emptytiles)
                        board[tileAdd[0]][tileAdd[1]] = rand(1,2)
                    z_flag = False
                
                #------------------Ctrl-+-z-----------------------
                elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL and not z_flag:
                    board = deepcopy(temp["board"])
                    score = temp["score"]
                    z_flag = True

#best-place
best = 8200

new_best = game(best)
if new_best > best:
    changeBest(new_best)

pygame.quit()
sys.exit(0)
