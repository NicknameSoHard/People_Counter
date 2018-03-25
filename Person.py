from random import randint
import time

class MyPerson:
    tracks = []
    def __init__(self, xi, yi):
        self.x = xi
        self.y = yi
        self.tracks = []
        self.done = False
        self.state = '0' # 0 - если объект не пересек контрольную линию, 1 - если пересек одну линию, 2 - если пересек две линии
        self.dir = None
        self.crossed = 0

    def getTracks(self):
        return self.tracks

    def getState(self):
        return self.state

    def getDir(self):
        return self.dir

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def updateCoords(self, xn, yn):
        self.tracks.append([self.x, self.y])
        self.x = xn
        self.y = yn


    def setDone(self):
        self.done = True

    def timedOut(self):
        return self.done

    def going_UP(self, line_down, line_up):
        if len(self.tracks) >= 3:
            if self.state == '0':
                print("State 0")
                if self.tracks[-1][1] < line_down and self.tracks[-2][1] >= line_down: # Есть пересечение конца снизу-вверх
                    self.state = '1'
                    self.dir = 'up'
                    return False
            elif self.state == '1':
                print("State 1")
                if self.tracks[-2][1] < line_up and self.tracks[-1][1] >= line_up:
                    self.state = '2'
                    return True
            elif self.state == '2':
                print("State 2")
                self.setDone();
                return False
            else:
                return False
        else:
            return False

    def going_DOWN(self,line_down, line_up):
        if len(self.tracks) >= 2:
            if self.state == '0':
                if self.tracks[-1][1] > line_up and self.tracks[-2][1] <= line_up: # Есть пересечение линии
                    state = '1'
                    self.dir = 'down'
                    return True
            else:
                return False
        else:
            return False
