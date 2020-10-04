# importing speech recognition package from google api
import os
from datetime import datetime
from tkinter import *
from tkinter.constants import *
from random import *
import speech_recognition as sr
from gtts import gTTS
import playsound
import time

from itertools import cycle
import random
import sys

import pygame
from pygame.locals import *


def Flappy_Bird():
    FPS = 30
    SCREENWIDTH = 288
    SCREENHEIGHT = 512
    PIPEGAPSIZE = 100  # gap between upper and lower part of pipe
    BASEY = SCREENHEIGHT * 0.79
    # image, sound and hitmask  dicts
    IMAGES, SOUNDS, HITMASKS = {}, {}, {}

    # list of all possible players (tuple of 3 positions of flap)
    PLAYERS_LIST = (
        # red bird
        (
            'assets/sprites/redbird-upflap.png',
            'assets/sprites/redbird-midflap.png',
            'assets/sprites/redbird-downflap.png',
        ),
        # blue bird
        (
            'assets/sprites/bluebird-upflap.png',
            'assets/sprites/bluebird-midflap.png',
            'assets/sprites/bluebird-downflap.png',
        ),
        # yellow bird
        (
            'assets/sprites/yellowbird-upflap.png',
            'assets/sprites/yellowbird-midflap.png',
            'assets/sprites/yellowbird-downflap.png',
        ),
    )

    # list of backgrounds
    BACKGROUNDS_LIST = (
        'assets/sprites/background-day.png',
        'assets/sprites/background-night.png',
    )

    # list of pipes
    PIPES_LIST = (
        'assets/sprites/pipe-green.png',
        'assets/sprites/pipe-red.png',
    )

    try:
        xrange
    except NameError:
        xrange = range

    def main():
        global SCREEN, FPSCLOCK
        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        pygame.display.set_caption('Flappy Bird')

        # numbers sprites for score display
        IMAGES['numbers'] = (
            pygame.image.load('assets/sprites/0.png').convert_alpha(),
            pygame.image.load('assets/sprites/1.png').convert_alpha(),
            pygame.image.load('assets/sprites/2.png').convert_alpha(),
            pygame.image.load('assets/sprites/3.png').convert_alpha(),
            pygame.image.load('assets/sprites/4.png').convert_alpha(),
            pygame.image.load('assets/sprites/5.png').convert_alpha(),
            pygame.image.load('assets/sprites/6.png').convert_alpha(),
            pygame.image.load('assets/sprites/7.png').convert_alpha(),
            pygame.image.load('assets/sprites/8.png').convert_alpha(),
            pygame.image.load('assets/sprites/9.png').convert_alpha()
        )

        # game over sprite
        IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
        # message sprite for welcome screen
        IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
        # base (ground) sprite
        IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

        # sounds
        if 'win' in sys.platform:
            soundExt = '.wav'
        else:
            soundExt = '.ogg'

        SOUNDS['die'] = pygame.mixer.Sound('assets/audio/die' + soundExt)
        SOUNDS['hit'] = pygame.mixer.Sound('assets/audio/hit' + soundExt)
        SOUNDS['point'] = pygame.mixer.Sound('assets/audio/point' + soundExt)
        SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
        SOUNDS['wing'] = pygame.mixer.Sound('assets/audio/wing' + soundExt)

        while True:
            # select random background sprites
            randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
            IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

            # select random player sprites
            randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
            IMAGES['player'] = (
                pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
                pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
                pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
            )

            # select random pipe sprites
            pipeindex = random.randint(0, len(PIPES_LIST) - 1)
            IMAGES['pipe'] = (
                pygame.transform.flip(
                    pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), False, True),
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
            )

            # hismask for pipes
            HITMASKS['pipe'] = (
                getHitmask(IMAGES['pipe'][0]),
                getHitmask(IMAGES['pipe'][1]),
            )

            # hitmask for player
            HITMASKS['player'] = (
                getHitmask(IMAGES['player'][0]),
                getHitmask(IMAGES['player'][1]),
                getHitmask(IMAGES['player'][2]),
            )

            movementInfo = showWelcomeAnimation()
            crashInfo = mainGame(movementInfo)
            showGameOverScreen(crashInfo)

    def showWelcomeAnimation():
        """Shows welcome screen animation of flappy bird"""
        # index of player to blit on screen
        playerIndex = 0
        playerIndexGen = cycle([0, 1, 2, 1])
        # iterator used to change playerIndex after every 5th iteration
        loopIter = 0

        playerx = int(SCREENWIDTH * 0.2)
        playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

        messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
        messagey = int(SCREENHEIGHT * 0.12)

        basex = 0
        # amount by which base can maximum shift to left
        baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

        # player shm for up-down motion on welcome screen
        playerShmVals = {'val': 0, 'dir': 1}

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()

                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    # make first flap sound and return values for mainGame
                    SOUNDS['wing'].play()
                    return {
                        'playery': playery + playerShmVals['val'],
                        'basex': basex,
                        'playerIndexGen': playerIndexGen,
                    }

            # adjust playery, playerIndex, basex
            if (loopIter + 1) % 5 == 0:
                playerIndex = next(playerIndexGen)
            loopIter = (loopIter + 1) % 30
            basex = -((-basex + 4) % baseShift)
            playerShm(playerShmVals)

            # draw sprites
            SCREEN.blit(IMAGES['background'], (0, 0))
            SCREEN.blit(IMAGES['player'][playerIndex],
                        (playerx, playery + playerShmVals['val']))
            SCREEN.blit(IMAGES['message'], (messagex, messagey))
            SCREEN.blit(IMAGES['base'], (basex, BASEY))

            pygame.display.update()
            FPSCLOCK.tick(FPS)

    def mainGame(movementInfo):
        score = playerIndex = loopIter = 0
        playerIndexGen = movementInfo['playerIndexGen']
        playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

        basex = movementInfo['basex']
        baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

        # get 2 new pipes to add to upperPipes lowerPipes list
        newPipe1 = getRandomPipe()
        newPipe2 = getRandomPipe()

        # list of upper pipes
        upperPipes = [
            {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
            {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
        ]

        # list of lowerpipe
        lowerPipes = [
            {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
            {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
        ]

        pipeVelX = -4

        # player velocity, max velocity, downward accleration, accleration on flap
        playerVelY = -9  # player's velocity along Y, default same as playerFlapped
        playerMaxVelY = 10  # max vel along Y, max descend speed
        playerMinVelY = -8  # min vel along Y, max ascend speed
        playerAccY = 1  # players downward accleration
        playerRot = 45  # player's rotation
        playerVelRot = 3  # angular speed
        playerRotThr = 20  # rotation threshold
        playerFlapAcc = -9  # players speed on flapping
        playerFlapped = False  # True when player flaps

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()

                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if playery > -2 * IMAGES['player'][0].get_height():
                        playerVelY = playerFlapAcc
                        playerFlapped = True
                        SOUNDS['wing'].play()

            # check for crash here
            crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                                   upperPipes, lowerPipes)
            if crashTest[0]:
                return {
                    'y': playery,
                    'groundCrash': crashTest[1],
                    'basex': basex,
                    'upperPipes': upperPipes,
                    'lowerPipes': lowerPipes,
                    'score': score,
                    'playerVelY': playerVelY,
                    'playerRot': playerRot
                }

            # check for score
            playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
            for pipe in upperPipes:
                pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
                if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                    score += 1
                    SOUNDS['point'].play()

            # playerIndex basex change
            if (loopIter + 1) % 3 == 0:
                playerIndex = next(playerIndexGen)
            loopIter = (loopIter + 1) % 30
            basex = -((-basex + 100) % baseShift)

            # rotate the player
            if playerRot > -90:
                playerRot -= playerVelRot

            # player's movement
            if playerVelY < playerMaxVelY and not playerFlapped:
                playerVelY += playerAccY
            if playerFlapped:
                playerFlapped = False

                # more rotation to cover the threshold (calculated in visible rotation)
                playerRot = 45

            playerHeight = IMAGES['player'][playerIndex].get_height()
            playery += min(playerVelY, BASEY - playery - playerHeight)

            # move pipes to left
            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                uPipe['x'] += pipeVelX
                lPipe['x'] += pipeVelX

            # add new pipe when first pipe is about to touch left of screen
            if len(upperPipes) > 0 and 0 < upperPipes[0]['x'] < 5:
                newPipe = getRandomPipe()
                upperPipes.append(newPipe[0])
                lowerPipes.append(newPipe[1])

            # remove first pipe if its out of the screen
            if len(upperPipes) > 0 and upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
                upperPipes.pop(0)
                lowerPipes.pop(0)

            # draw sprites
            SCREEN.blit(IMAGES['background'], (0, 0))

            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
                SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

            SCREEN.blit(IMAGES['base'], (basex, BASEY))
            # print score so player overlaps the score
            showScore(score)

            # Player rotation has a threshold
            visibleRot = playerRotThr
            if playerRot <= playerRotThr:
                visibleRot = playerRot

            playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
            SCREEN.blit(playerSurface, (playerx, playery))

            pygame.display.update()
            FPSCLOCK.tick(FPS)

    def showGameOverScreen(crashInfo):
        """crashes the player down ans shows gameover image"""
        score = crashInfo['score']
        playerx = SCREENWIDTH * 0.2
        playery = crashInfo['y']
        playerHeight = IMAGES['player'][0].get_height()
        playerVelY = crashInfo['playerVelY']
        playerAccY = 2
        playerRot = crashInfo['playerRot']
        playerVelRot = 7

        basex = crashInfo['basex']

        upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

        # play hit and die sounds
        SOUNDS['hit'].play()
        if not crashInfo['groundCrash']:
            SOUNDS['die'].play()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()

                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if playery + playerHeight >= BASEY - 1:
                        return

            # player y shift
            if playery + playerHeight < BASEY - 1:
                playery += min(playerVelY, BASEY - playery - playerHeight)

            # player velocity change
            if playerVelY < 15:
                playerVelY += playerAccY

            # rotate only when it's a pipe crash
            if not crashInfo['groundCrash']:
                if playerRot > -90:
                    playerRot -= playerVelRot

            # draw sprites
            SCREEN.blit(IMAGES['background'], (0, 0))

            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
                SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

            SCREEN.blit(IMAGES['base'], (basex, BASEY))
            showScore(score)

            playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
            SCREEN.blit(playerSurface, (playerx, playery))
            SCREEN.blit(IMAGES['gameover'], (50, 180))

            FPSCLOCK.tick(FPS)
            pygame.display.update()

    def playerShm(playerShm):
        """oscillates the value of playerShm['val'] between 8 and -8"""
        if abs(playerShm['val']) == 8:
            playerShm['dir'] *= -1

        if playerShm['dir'] == 1:
            playerShm['val'] += 1
        else:
            playerShm['val'] -= 1

    def getRandomPipe():
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
        gapY += int(BASEY * 0.2)
        pipeHeight = IMAGES['pipe'][0].get_height()
        pipeX = SCREENWIDTH + 10

        return [
            {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
            {'x': pipeX, 'y': gapY + PIPEGAPSIZE},  # lower pipe
        ]

    def showScore(score):
        """displays score in center of screen"""
        scoreDigits = [int(x) for x in list(str(score))]
        totalWidth = 0  # total width of all numbers to be printed

        for digit in scoreDigits:
            totalWidth += IMAGES['numbers'][digit].get_width()

        Xoffset = (SCREENWIDTH - totalWidth) / 2

        for digit in scoreDigits:
            SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
            Xoffset += IMAGES['numbers'][digit].get_width()

    def checkCrash(player, upperPipes, lowerPipes):
        """returns True if player collders with base or pipes."""
        pi = player['index']
        player['w'] = IMAGES['player'][0].get_width()
        player['h'] = IMAGES['player'][0].get_height()

        # if player crashes into ground
        if player['y'] + player['h'] >= BASEY - 1:
            return [True, True]
        else:

            playerRect = pygame.Rect(player['x'], player['y'],
                                     player['w'], player['h'])
            pipeW = IMAGES['pipe'][0].get_width()
            pipeH = IMAGES['pipe'][0].get_height()

            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                # upper and lower pipe rects
                uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
                lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

                # player and upper/lower pipe hitmasks
                pHitMask = HITMASKS['player'][pi]
                uHitmask = HITMASKS['pipe'][0]
                lHitmask = HITMASKS['pipe'][1]

                # if bird collided with upipe or lpipe
                uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
                lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

                if uCollide or lCollide:
                    return [True, False]

        return [False, False]

    def pixelCollision(rect1, rect2, hitmask1, hitmask2):
        """Checks if two objects collide and not just their rects"""
        rect = rect1.clip(rect2)

        if rect.width == 0 or rect.height == 0:
            return False

        x1, y1 = rect.x - rect1.x, rect.y - rect1.y
        x2, y2 = rect.x - rect2.x, rect.y - rect2.y

        for x in xrange(rect.width):
            for y in xrange(rect.height):
                if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                    return True
        return False

    def getHitmask(image):
        """returns a hitmask using an image's alpha."""
        mask = []
        for x in xrange(image.get_width()):
            mask.append([])
            for y in xrange(image.get_height()):
                mask[x].append(bool(image.get_at((x, y))[3]))
        return mask

    if __name__ == '__main__':
        main()


greet = ["hello", "hi", "hey", "heyo"]
out = ""
global e
dob = dom = bot = mar = "0"
command = ""
wish = ""
name = ""
f = 0
# Chooses what to wish
rt = int(datetime.now().time().hour)
wish_set = {"Morning": (0, 12), "Afternoon": (12, 17), "Evening": (17, 24)}
for i in wish_set:
    if wish_set[i][0] <= rt < wish_set[i][1]:
        wish = i


def log():
    global out
    a = open("log.log", 'r')
    out = a.readlines()
    print(out)
    output()


def output():
    global out
    out_window = Tk()

    def outexit():
        print(0)
        time.sleep(10)
        print(1)
        out_window.destroy()

    frame = Frame(out_window, relief=RIDGE, borderwidth=2)
    frame.pack(fill=BOTH, expand=1)
    if type(out) is list:
        print(1)
        for i in range(len(out)):
            if i % 2 == 0:
                label = Label(frame, text=out[i])
                label.grid(row=i, column=1, sticky=W, pady=2)
            else:
                label = Label(frame, text=out[i])
                label.grid(row=i, column=2, sticky=W, pady=2)
    else:
        label = Label(frame, text=out)
        label.pack(fill=X, expand=1)
        outexit
    sp = gTTS(text=out)
    print(out)
    sp.save("sp.mp3")
    playsound.playsound("sp.mp3", True)
    os.remove("sp.mp3")


def input_voice():
    global command
    rObject = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak...")
        # recording the audio using speech recognition
        audio = rObject.listen(source, phrase_time_limit=5)
    print("Stop.")
    command = rObject.recognize_google(audio, language='en-US')
    print(command)
    command_process()


if not os.path.exists("user.user"):
    print()
    tk = Tk()
    frame = Frame(tk, relief=RIDGE, borderwidth=10)
    frame.pack(fill=BOTH, expand=1)


    def dat():
        print(data)
        global name, dob, mar, bot
        name = data[2].get()
        print(name)
        dob = data[4].get()
        bot = data[6].get()
        a = open("user.user", "w")
        a.write("Name = " + name + "\n")
        a.write("dob = " + dob + "\n")
        a.write("bot = " + bot + "\n")
        a.write("0")
        a.close()
        print(dob)
        tk.destroy()


    data = (Label(frame, text="Good " + wish + ",Please enter required data"), Label(frame, text="Enter your name"),
            Entry(frame), Label(frame, text="Enter your date of birth in YYYY-MM-DD format"), Entry(frame),
            Label(frame, text="Enter name by which you would like to call me"), Entry(frame),
            Label(frame, text="Rest data may be entered afterwards"), Button(frame, text="Submit", command=dat))
    for i in data:
        i.pack()
    tk.mainloop()
    f = 1
else:
    f = 1


def command_process():
    global us
    global greet
    global command
    global Bot_Name
    love = int(us[-1])
    global out
    print()
    r = randint(0, 3)
    if command in greet:
        out = greet[r]
    elif command == "bye" or command == "exit":
        out = "bye bye"
    elif command == "log":
        log()
    else:
        words = command.split(' ')

        for i in range(len(words) - 1):
            print(len(words))
            print(i)

            if "i" in words and "love" in words and "you" in words:
                a = open("user.user", "w")

                if love < 2:
                    out = "I love you too, but as a friend"

                elif love < 5:
                    out = "I love you too brother, and will always love you."

                if "as" in words and "lover" in words:
                    out = "Sorry i am a software, and you are a human, we can't match up, next time don't say this to me or else i will suicide"
                    if love > 2:
                        out = "Goodbye foreve, I am comitting suicide"
                love = love + 1
                print(love)
                for i in range(len(us) - 1):
                    print(us[i])
                    a.write(us[i])
                a.write(str(love))
                break

            if "how" in words and "are" in words and "you" in words:
                out = "I am fine, thanks for asking, hope same for you"
                print()
                break

            if "what" in words and "is" in words and "your" in words and "name" in words:
                out = "My name is " + Bot_Name
                break

            if "play" in words:
                Flappy_Bird()
                out = "Welcome to Flappy Bird Game"
    # permanent for result
    a = open("log.log", "a")
    a.write(command + "\n")
    a.write(out + "\n")
    a.close()
    output()


def abc():
    global out
    global Bot_Name
    global us
    user = open("user.user", "r")
    us = user.readlines()
    global name
    data = us[0].split(" ")
    print(data)
    name = data[2]
    q = us[2].split(" ")
    Bot_Name = q[2]
    q = us[1].split(" ")
    Dob = str(q[2][5:])
    tk = Tk()
    frame = Frame(tk, relief=RIDGE, borderwidth=4)
    frame.pack(fill=BOTH, expand=1)
    label = Label(frame, text="Hello " + name + ", Good " + wish)
    label.pack(fill=X, expand=1)
    button1 = Button(frame, text="Voice", command=input_voice)
    button1.pack(side=TOP)
    e = Entry(frame)
    e.pack()
    e.focus_set()

    def call_command():
        global command
        command = e.get()
        if command == "exit" or command == "bye":
            tk.destroy()
        command_process()

    button3 = Button(frame, text="Ok", command=call_command)
    button3.pack()
    logbutton = Button(frame, text="Log", command=log)
    logbutton.pack()
    button2 = Button(frame, text="EXIT", command=tk.destroy)
    button2.pack(side=BOTTOM)
    d = datetime.today().strftime('%Y-%m-%d')
    d = str(d)[5:]
    sp = gTTS(text="Hello " + name + ", Good " + wish)
    sp.save("we.mp3")
    playsound.playsound("we.mp3", True)
    os.remove("we.mp3")
    if Dob == d:
        print(14)
        out = "Happy Birthday "+name
        output()
    tk.mainloop()


if f == 1:
    abc()
