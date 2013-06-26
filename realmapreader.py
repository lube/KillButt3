import pygame, random, sys, time, math, os, copy
from pygame.locals import *

RIGHT, UP, LEFT, DOWN = (1,1), (1,-1), (-1,-1), (-1,1)
NE, SE, NO, SO = (0,-1), (1,0), (-1,0), (0,1)

FACINGS = {RIGHT:0, DOWN:1, NE:6, NO:3 ,UP:4 ,SE:5 ,SO:2 ,LEFT:7, (0,0): 0}
 
Key2Dir   = {275: RIGHT, 273:DOWN, 276:LEFT, 274:UP, K_ESCAPE:QUIT}
NONE = (0,0)
FPS = 45
WINDOWWIDTH, WINDOWHEIGHT = 1000, 700
TILEH, TILEW, GAPSIZE = 32, 64, 1
BOARDWIDTH = 15
HALF = WINDOWWIDTH / 2
HTILEH = 0.5 * TILEH
HTILEW = 0.5 * TILEW


def main():

    global FPSCLOCK, DISPLAYSURF, BASICFONT, aSpriteSheet, unMapa, aCamera, tileList
        
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('mapReader 2.0')
    
    unMapa = readMap('pancamera.txt')
    
    
    
    aSpriteSheet = spritesheet(unMapa.tileset)
    bSpriteSheet = spritesheet('swordwalking.png')
    aChar = character()
    
    for directions in range(8):
        aChar.animations.append(bSpriteSheet.load_strip((0,directions*48,48,48), 8, colorkey=(0, 0, 0)))
        
    tileList = {}
    
    command = (0,0)   
    
    aCamera = Camera('DYNAMIC', aChar)
    
    Collisionables = unMapa.getCollisionables()
    
    while command != QUIT:
        
        aCamera.update(aChar)
        
        unMapa.draw(aCamera, aChar)
        
        if aChar.moving:                
            aChar.draw()
        
        command = getCommand()
        aChar.update(command, Collisionables)
          
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        
def getCommand ():
        event = pygame.event.poll()
        
        if event.type == pygame.KEYUP:
            return Key2Dir[event.key] , KEYUP
        elif event.type == pygame.KEYDOWN:   
            return Key2Dir[event.key] , KEYDOWN
        return NONE, NONE 

class Camera(object):
    x = 0
    y = 0
    xyTile = 0,0
    mode = ''
    xRange = 0
    yRange = 0
    
    def __init__(self, aMode, aChar):
        self.x = 0
        self.y = 0
        self.xyTile = 0,0
        self.mode = aMode
        
        if self.mode == 'DYNAMIC':
            self.xyTile = copy.copy(aChar.pos)
            self.xRange, self.yRange = 10,10
        else:
            self.xRange, self.yRange = 5,5
            self.xyTile = aChar.pos
            
        
    def update(self, aChar):
        if self.mode == 'DYNAMIC':
            if aChar.pos[0] > (self.xyTile[0] + (self.xRange - 2)):
                self.xyTile[0] += 1
            elif aChar.pos[0] < (self.xyTile[0] - (self.xRange - 1)):
                self.xyTile[0] -= 1
            elif aChar.pos[1] > (self.xyTile[1] + (self.yRange - 2)):
                self.xyTile[1] += 1
            elif aChar.pos[1] < (self.xyTile[1] - (self.yRange - 1)):
                self.xyTile[1] -= 1
            else:
                pass
            
        self.x = HALF + (self.xyTile[0]*HTILEW) - (self.xyTile[1]*HTILEW)
        self.y =(self.xyTile[0] + self.xyTile[1]) * HTILEH + 32
        #tuple(map(int,getVertsOfTile(aChar.pos[0], aChar.pos[1])))
        self.x, self.y = (self.x - WINDOWWIDTH/2), (self.y - WINDOWHEIGHT/2)
        
class spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error, message:
            print 'Unable to load spritesheet image:', filename
            raise SystemExit, message
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image, rect
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

#def getVertsOfTile(Cola, Fila):   
#    Y = -32 + (Cola + Fila) * 0.5 * TILEH + 64
#    X = HALF + (Cola*TILEW * 0.5) - (Fila*TILEW* 0.5)
#   return X,Y

def drawtile(tile, Col, Fila):
    Y = (Col + Fila) * HTILEH + 32 - aCamera.y
    X = HALF + (Col*HTILEW) - (Fila*HTILEW) - aCamera.x

    DISPLAYSURF.blit(tile, (X,Y))

def readMap(filename):
    assert os.path.exists(filename), 'No se puede encontrar el archivo' 
    mapFile = open(filename, 'r')
    # Cada nivel finaliza con una nueva linea
    lineas = mapFile.readlines() + ['\r\n']
    mapFile.close() # Cerramos el Archivo

    mapObj = mapObject() # Objeto mapa
    
    readingLayer, readingData = False, False
    nLayers = -1
    nRows = -1
    csv = []
    
    for nLinea in lineas:
        # Process each line that was in the level file.
        line = nLinea.rstrip('\r\n')
        
        if ';' in line:
            # Ignore the ; lines, they're comments in the level file.
            line = line[:line.find(';')]
        if line.startswith('width='):
            mapObj.width = int(line[line.find('width='):].lstrip('width='))
        if line.startswith('height='):
            mapObj.height = int(line[line.find('height='):].lstrip('height='))
        if line.startswith('tilewidth='):
            mapObj.tilew = int(line[line.find('tilewidth='):].lstrip('tilewidth='))
        if line.startswith('tileheight='):
            mapObj.tileh = int(line[line.find('tileheight='):].lstrip('tileheight='))
        if 'tileset=' in line:
            tilesetdata = line[line.find('tileset='):].lstrip('tileset=').split(',')
            mapObj.tileset = tilesetdata[0]
            mapObj.tilesetXOffset = int(tilesetdata[3])
            mapObj.tilesetYOffset = int(tilesetdata[4])
            mapObj.tilesetWidth = int(tilesetdata[5])
            mapObj.tilesetHeight = int(tilesetdata[6])
            
        if '[layer]' in line:
            nLayers = nLayers + 1
            readingLayer = True
            
        if readingLayer and line == '':
            readingLayer = False
            readingData = False

        if 'type=' in line and readingLayer:
            mapObj.layers.append((line[line.find('type='):].lstrip('type='),[]))
            nRows = 0
            #mapObj.layers[nLayers][0] = line[line.find('type='):].lstrip('type=')
        
        if 'data=' in line:
            readingData = True
        
        if readingLayer and readingData and 'data=' not in line:
            mapObj.layers[nLayers][1].append([])
            csv = line.rstrip(',').split(',')
            for id in csv:
                trueId = int(id)  
                x = ((trueId-1) % (mapObj.tilesetWidth / mapObj.tilew)) * mapObj.tilew
                y = int((trueId-1) / (mapObj.tilesetWidth / mapObj.tilew)) * mapObj.tileh
                mapObj.layers[nLayers][1][nRows].append((x,y))
            nRows += 1
                
    return mapObj

class mapObject:
    width = 0
    height = 0
    tilew = 0
    tileh = 0
    tileset = ''
    tilesetXOffset = 0
    tilesetYOffset = 0
    tilesetWidth = 0
    tilesetHeight = 0
    layers = []
    
    def getCollisionables(self):
        Collisionables = []
        for y, row in enumerate(self.layers[2][1]):
            for x, tile in enumerate(row):
                    if tile != (960, -32):
                        Collisionables.append((x, y))
        return Collisionables

    def draw(self, aCamera, aChar):
        if aChar.moving:
            DISPLAYSURF.fill((0,0,0))
            for layer, rows in self.layers:
                for Fila, row in filter(lambda (x,y): x < aCamera.xyTile[1] + aCamera.yRange and x > aCamera.xyTile[1] - aCamera.yRange, enumerate(rows)):
                    for Col, tile in filter(lambda (x,y): x < aCamera.xyTile[0] + aCamera.xRange and x > aCamera.xyTile[0] - aCamera.xRange, enumerate(row)):
                        if tile in tileList:
                            drawtile(tileList[tile][0], Col, Fila)
                        else:
                            tileList[tile] =  aSpriteSheet.image_at((tile[0],tile[1],64,32), colorkey=(0, 0, 0))
                            drawtile(tileList[tile][0], Col, Fila)

class character:
    animations = []
    facing = RIGHT
    pos = [5,5]
    state = 0
    moving = False
    
    def draw(self):
        drawtile(self.animations[FACINGS[self.facing]][self.state][0], self.pos[0], self.pos[1])
        
    def update(self, command, collisionables):
        if not self.moving and command[0] in [UP, DOWN, LEFT, RIGHT] and command[1] == KEYDOWN:
            #self.state = (self.state + 1) % len(self.animations[self.state])
            #self.pos[0] += command[0][0] * 0.1
            #self.pos[1] += command[0][1] * 0.1 
            self.facing = command[0]
            self.moving = True
            
        elif self.moving and command[0] in [UP, DOWN, LEFT, RIGHT] and command[1] == KEYDOWN:
            if (command[0][0] + self.facing[0] + command[0][1] + self.facing[1]) != 0 and self.facing[1]+self.facing[0] != 1:
                #self.state = (self.state + 1) % len(self.animations[self.state])

                if (command[0][0] + self.facing[0]) > 1:
                    xVec = 1
                elif (command[0][0] + self.facing[0]) < -1:
                    xVec = -1
                else:
                    xVec = command[0][0] + self.facing[0]
                                
                if (command[0][1] + self.facing[1]) > 1:
                    yVec = 1
                elif (command[0][1] + self.facing[1]) < -1:
                    yVec = -1
                else:
                    yVec = command[0][1] + self.facing[1]
                
                #self.pos[0] += xVec * 0.1
                #self.pos[1] += yVec * 0.1
                self.facing = (xVec, yVec)
                
            else: pass
                #self.state = (self.state + 1) % len(self.animations[self.state])
                #self.pos[0] += self.facing[0] * 0.1
                #self.pos[1] += self.facing[1] * 0.1 

        elif self.moving and command[0] in [UP, DOWN, LEFT, RIGHT] and command[1] == KEYUP and self.facing not in [UP, DOWN, LEFT, RIGHT]:
            if abs(self.facing[0] + self.facing[1]) == 1:
                if self.facing[0] == 1:
                    xVec = 2
                    yVec = self.facing[1]
                elif self.facing[1] == 1:
                    yVec = 2
                    xVec = self.facing[0]

                if self.facing[0] == -1:
                    xVec = -2
                    yVec = self.facing[1]
                elif self.facing[1] == -1:
                    yVec = -2
                    xVec = self.facing[0]
            else:
                xVec = self.facing[0]
                yVec = self.facing[1]
            
            if (abs(xVec - command[0][0]) < 3) and (abs(yVec - command[0][1]) < 3):
                self.facing = xVec - command[0][0], yVec - command[0][1]
            #self.pos[0] += self.facing[0] * 0.1
            #self.pos[1] += self.facing[1] * 0.1
            

        elif self.moving and command[0] in [UP, DOWN, LEFT, RIGHT] and command[1] == KEYUP and self.facing in [UP, DOWN, LEFT, RIGHT]:
            if command[0] == self.facing:
                self.moving = False
                
            
        else:
            pass
            
        if self.moving and not self.willCollision(collisionables):
            self.pos[0] += self.facing[0] * 0.1
            self.pos[1] -= self.facing[1] * 0.1

            self.state = (self.state + 1) % len(self.animations[FACINGS[self.facing]])
        
    def willCollision (self, collisionables):
        print ((self.pos[0] + (self.facing[0] * 0.1)),(self.pos[1] - (self.facing[1] * 0.1)))
        if (int(self.pos[0] + (self.facing[0] * 0.1))+1,int(self.pos[1] - (self.facing[1] * 0.1))+1) in collisionables:
            return True
        return False
            
if __name__ == '__main__':
    main()