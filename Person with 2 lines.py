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

    def timedOut(self):
        return self.done

    def going_UP(self, line_down, line_up):
        if len(self.tracks) >= 2 and self.done == False:
            if self.state == '0':
                if self.tracks[-1][1] < line_down and self.tracks[-2][1] >= line_down: # Есть пересечение нижней линии снизу-вверх
#                    print("Up state 1")
                    self.state = '1'
                    self.dir = 'up'
                return False
            elif self.state == '1':
                if self.tracks[-1][1] >= line_up and self.tracks[-2][1] < line_up and self.dir == "up": # Если есть пересечение второй линии снизу-вверх
#                    print("Up state 2")
                    self.state = '2'
                    return True
                else:
                    return False
            elif self.state == '2':
#                print("Up All")
                self.done = True
                return False
            else:
                return False
        else:
            return False

    def going_DOWN(self,line_down, line_up):
        if len(self.tracks) >= 2 and self.done == False:
            if self.state == '0':
                if self.tracks[-1][1] < line_up and self.tracks[-2][1] >= line_up: # Есть пересечение верхней линии сверху-вниз
#                    print("Down state 1")
                    self.state = '1'
                    self.dir = 'down'
                return False
            elif self.state == '1':
                if self.tracks[-1][1] >= line_down and self.tracks[-2][1] < line_down and self.dir == "down": # Есть пересечение нижней линии сверху-вниз
#                    print("Down state 2")
                    self.state = '2'
                    return True
                else:
                    return False
            elif self.state == '2':
#                print("Down All")
                self.done = True
                return False
            else:
                return False
        else:
            return False
