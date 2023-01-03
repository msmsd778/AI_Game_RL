class Node:

    def __init__(self, cords, reward):
        self.type = 'normal'
        self.cords = cords
        self.is_wall = False
        self.is_door = False
        self.door = ''
        self.key = ''
        self.diamond = ''
        self.is_wired = False
        self.v = 0
        self.r = reward
        self.pi = 0
        self.available = True

