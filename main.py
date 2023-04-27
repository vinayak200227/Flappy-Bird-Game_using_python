import random  # for generating random numbers
import sys    # sys.exit will used to exit the program
import pygame
from pygame.locals import *

#Global variables
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'

def welcomeScreen():
    # Shows welcome images on screeen 
    playerx = int(SCREENWIDTH / 5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    messagey = int(SCREENWIDTH * 0.13)
    basex = 0
    while True:
        for event in pygame.event.get():
            # if user clicks an cross button, close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # If the user pressess space or up key, start the game
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                # blit images on screen
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
                SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                pygame.display.update() 
                FPSCLOCK.tick(FPS)  # control FPS to 32


def mainGame():
    score = 0
    # position of player
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENWIDTH/2)
    # position of base
    basex = 0

    # Create 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH+200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y': newPipe2[0]['y']},
    ]
    # List of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH+200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y': newPipe2[1]['y']},
    ]

    # velocity
    pipeVelX = -4  # negative because we have to move pipes in backward direction

    playerVelY = -9  # player will fall down by -9 velocity
    playerMaxVelY = 10  # max velocity of player when we press up arrow
    playerMinVelY = -8
    playerAccY = 1  # acceleration

    playerFlapAccv = -8  # velocity while flapping
    playerFlapped = False  # It is true only when the bird is flapping

    while True:
        for event in pygame.event.get():
            # if we quit the game or pressed any button on keyboard and pressed escape then exit the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
             # if we presss any button and (pressed up arrow or space) then
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:  # if player is in screen
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()  # play 'wing' sound

        # This function will return true if the player is crashed
        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest:
            return

        #check for score
        playerMidPos = playerx + GAME_SPRITES['player'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width()/2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                print(f"Your score is {score}")
                GAME_SOUNDS['point'].play()  # play sound

        # if player velocity is less than max velocity and player is not flapping then add acceleration to velocity of player
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY       # ( so that player will start falling down )

        # if player flapped ( by pressing up arrow once ) then set flapping as false
        if playerFlapped:
            playerFlapped = False
        # again if player presses up arrow button playerFlapped will be set to True in while loop
        playerHeight = GAME_SPRITES['player'].get_height()
        # if player touches to ground then (GROUNDY - playery - playerHeight) will be zero , so 0 will be returned by min and there will no further addition in y coordinate of player ( so that player should not go below ground)
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        # move pipes to the left
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # if the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Lets blit our sprites now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))   # blit background image at (0, 0)
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):  
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y'])) # blit upper pipe
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y'])) # blit lower pipe

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()  # will get width required for number image 
        Xoffset = (SCREENWIDTH - width)/2   # for blitting first digit at center

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width() # (for more than 1 digit score)
        pygame.display.update()
        FPSCLOCK.tick(FPS)  # control FPS

def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > GROUNDY -25 or playery < 0: # if player close to ground(colloid down) or player is not in screen(colliod up)
        GAME_SOUNDS['hit'].play()
        return True
    
    # collision with upper pipe
    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if(playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True

    # collision with lower pipe
    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True
       
    return False

 # generate positions of two pipes ( one bottom straight and one top roated) for blitting

def getRandomPipe():
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3      # offset is set so that there should be some gap betwwen two pipes , to pass bird in between them
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))  # y coordinate of lower pipe is from offset to base 
    pipeX = SCREENWIDTH + 10   # x coordinate will be 10 units ahead of screen width later we will move pipes into the screen (left side) 
    y1 = pipeHeight - y2 + offset  # y coordinate of upper pipe
    pipe = [
        {'x' : pipeX, 'y': -y1}, # upper pipe
        {'x' : pipeX, 'y' : y2}  # lower pipe
    ]
    return pipe


if __name__ == "__main__":
    # This will be main function from game will start
    pygame.init() # initialized pygame modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird')
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),
    )

    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (
        pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),  # rotate pipe image by 180 degrees
        pygame.image.load(PIPE).convert_alpha()
    )

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['smooth'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()


    while True:
        welcomeScreen() # shows welcome screen to the user until he presses a button
        mainGame()    # This is main game function
