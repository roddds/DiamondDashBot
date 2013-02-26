'''
Diamond Dash bot

'''

import time
import autopy
import ImageGrab
from random import randint
from collections import Counter
import os
import WConio

class Board:
    def __init__(self):
        self.corners = self.autodetect()
        self.diamond = autopy.bitmap.Bitmap.open('diamond.png')

        game_size = (760, 500)
        self.board_offsets = (79, 93, 281, 47)

        self.boardcoord = (self.corners[0]+self.board_offsets[0],
                           self.corners[1]+self.board_offsets[1],
                           self.corners[2]-self.board_offsets[2],
                           self.corners[3]-self.board_offsets[3])

        self.board = ImageGrab.grab(self.boardcoord)


        self.colors =  {(0, 119, 255):  'b', (0, 122, 254):   'b', (0, 125, 254):   'b',
 (0, 129, 253):   'b', (0, 132, 253):   'b', (0, 135, 252):   'b', (0, 136, 252):   'b',
 (0, 139, 252):   'b', (0, 142, 252):   'b', (0, 146, 251):   'b', (0, 149, 251):   'b',
 (0, 152, 250):   'b', (8, 141, 4):     'g', (9, 137, 5):     'g', (18, 143, 11):   'g',
 (63, 223, 36):   'g', (70, 224, 40):   'g', (78, 225, 45):   'g', (86, 227, 49):   'g',
 (88, 196, 82):   'g', (95, 229, 76):   'g', (127, 197, 113): 'g', (158, 238, 104): 'g',
 (160, 29, 237):  'p', (163, 35, 240):  'p', (180, 82, 246):  'p', (183, 60, 254):  'p',
 (185, 65, 255):  'p', (185, 68, 255):  'p', (185, 72, 255):  'p', (185, 76, 255):  'p',
 (185, 80, 255):  'p', (185, 85, 255):  'p', (185, 90, 255):  'p', (190, 113, 251): 'p',
 (196, 131, 255): 'p', (200, 246, 194): 'g', (233, 246, 229): 'g', (255, 92, 107):  'r',
 (255, 94, 109):  'r', (255, 96, 111):  'r', (255, 98, 113):  'r', (255, 100, 115): 'r',
 (255, 101, 117): 'r', (255, 102, 118): 'r', (255, 103, 119): 'r', (255, 104, 120): 'r',
 (255, 105, 121): 'r', (255, 107, 123): 'r', (255, 108, 125): 'r', (255, 110, 126): 'r',
 (255, 225, 0):   'y', (255, 226, 0):   'y', (255, 228, 0):   'y', (255, 228, 4):   'y',
 (255, 229, 0):   'y', (255, 230, 0):   'y', (255, 231, 0):   'y'}

        self.buffer = []

    def autodetect(self):
        corner = autopy.bitmap.Bitmap.open('corner.png')
        uprc = autopy.bitmap.capture_screen().find_bitmap(corner)
        if not uprc:
            raise ValueError("Game area not visible")

        uprc = uprc[0]-1, uprc[1]-1
        lolc = uprc[0]+760, uprc[1]+500
        return uprc+lolc
    
    def get_sq(self, x,y):
        assert x<=9
        assert y<=8
        return self.board.crop((40*x, 40*y, (40*x)+40, (40*y)+40))

    def get_colortuple(self, x,y):
        return self.get_sq(x,y).crop((20,20,21,21)).getcolors()[0][1]

    def update(self):
        self.board = ImageGrab.grab(self.boardcoord)

    def save(self, x, y):
        self.get_sq(x,y).save('%d.%d.png' % (x,y))

    def color(self, x,y):
        return self.colors.get(self.get_sq(x,y).crop((20,20,21,21)).getcolors()[0][1], ' ')

    def get_matrix(self):
        self.update()
        return [[self.color(x,y) for x in range(10)] for y in range(9)]
        

    def find(self, direction='h'):
        if direction == 'h':
            matrix = zip(range(9), self.get_matrix())
        elif direction == 'v':
            matrix = zip(range(9), list(zip(*self.get_matrix())))

        results = []
        for pair in matrix:
            x = pair[0]
            for color in 'ygbrp':
                line = ''.join(pair[1])
                search = line.find(color*3)
                if search != -1:
                    results.append([search, x])

        if direction == 'h':
            #print 'Search returned %d 3-parts horizontal pieces' % len(results)
            return results
        elif direction == 'v':
            #print 'Search returned %d 3-parts vertical pieces' % len(results)
            return [x[::-1] for x in results]


    def find_diamond(self):
        d = autopy.bitmap.capture_screen().find_bitmap(self.diamond)
        if d:
            x, y = d
            x += 15
            y += 5
            autopy.mouse.move(x, y)
            autopy.mouse.click()
            time.sleep(1.2)


    def click(self, cords):
        x, y = cords
        autopy.mouse.move(self.boardcoord[0]+(x*40)+20,
                          self.boardcoord[1]+(y*40)+20)
        autopy.mouse.click()

    def move(self, *cords):
        x, y = cords
        autopy.mouse.move(self.boardcoord[0]+(x*40)+20,
                          self.boardcoord[1]+(y*40)+20)

    def randomclick(self):
        self.click((randint(0,9), randint(0,8)))

    def get_squares(self):
        matrix = self.get_matrix()

        square = [[[x,y],
                  [matrix[y][x],
                   matrix[y+1][x],
                   matrix[y][x+1],
                   matrix[y+1][x+1]]] for x in range(9) for y in range(8)]

        points = []
        for item in square:
            coords, colors = item
            c = Counter(colors)
            if 3 in c.itervalues():
                letter = c.most_common()[0][0]
                if letter != ' ':
                    offset = colors.index(letter)
                    x, y = coords
                    points.append([x, y+offset])

        #print 'Search returned %d 3-parts clusters' % len(points)
        return points

    def find_all(self):
        return self.get_squares()+self.find('h')+self.find('v')

    def find_one(self):
        one = self.get_squares()
        if one:
            if len(one) >1:
                self.buffer = one[1:] + self.buffer
            return one[0]

        two = self.find('h')
        if two:
            if len(two)>1:
                self.buffer = two[1:] + self.buffer
            return two[0]

        three = self.find('v')
        if three:
            if len(three)>1:
                self.buffer = three[1:] + self.buffer
            return three[0]


    def play(self):
        repeats = 0
        lastclick = None

        while True:
            #self.find_diamond()
            items = self.find_one()
            if items:
                self.click(items)
                #print "clicked", items
                if items == lastclick:
                    repeats += 1
                else:
                    lastclick = items
                #time.sleep(0.1)
            #os.system('cls')
            WConio.clrscr()
            print '\n'.join([' '.join(x) for x in self.get_matrix()])
            # else:
            #     #time.sleep(0.5)
            #     self.click(self.buffer[0])
            #     print "Clicked from buffer", self.buffer[0]
            #     self.buffer.remove(self.buffer[0])
            #     time.sleep(0.1)
            #     #print "Waiting..."
            #     # fails += 1

            if repeats >= 5:
                return "Finished!"


if __name__ == '__main__':
    try:
        Board().play()
    except ValueError:
        print 'Game area not visible.'