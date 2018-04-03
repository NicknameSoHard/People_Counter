from random import randint
import time

class MyPerson:
    tracks = []
    def __init__(self, xi, yi):
        self.x = xi
        self.y = yi
        self.tracks = []
        self.done = False
        self.state = '0' # 0 - если объект не пересек контрольную линию, 1 - если пересек
        self.dir = None

    def getTracks(self):
        return self.tracks

    def getDir(self):
        return self.dir

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def updateCoords(self, xn, yn):
        self.age = 0
        self.tracks.append([self.x,self.y])
        self.x = xn
        self.y = yn

    def timedOut(self):
        return self.done

    def going_UP(self,mid_start,mid_end):
        if len(self.tracks) >= 2:
            if self.state == '0':
                if self.tracks[-1][1] < mid_end and self.tracks[-2][1] >= mid_end: # Есть пересечение первичной линии конца
                    self.state = '1'
                    self.dir = 'up'
                    return True
            else:
                return False
        else:
            return False

    def going_DOWN(self,mid_start,mid_end):
        if len(self.tracks) >= 2:
            if self.state == '0':
                if self.tracks[-1][1] > mid_start and self.tracks[-2][1] <= mid_start: # Есть пересечение первичной линии начала
                    self.state = '1'
                    self.dir = 'down'
                    return True
            else:
                return False
        else:
            return False
