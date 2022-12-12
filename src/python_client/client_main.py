import random
from base import BaseAgent, Action
from MainClass import Node



class Agent(BaseAgent):

    states = []
    diamonds = []
    keys = []
    collected_keys = []
    run = False
    target = None

    def __init__(self):
        super().__init__()

        self.states = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]

        for row in range(self.grid_height):
            for col in range(self.grid_width):
                self.states[row][col] = Node((row, col), 0)


    def do_turn(self) -> Action:

        agent = self.get_agent()
        self.update_grid()
        if agent.cords in self.keys:
            self.collected_keys.append(agent)

        if self.is_End(agent, self.target):
            self.run = False
            # return Action.NOOP

        if not self.run:

            if len(self.diamonds) == 0:
                return Action.NOOP

            self.target = self.get_target()
            self.get_reward(self.target)
            print('target = ' , self.target.cords)
            self.valueIteration(self.target, 1, 1e-10)
            self.run = True
            for i in range(self.grid_height):
                print()
                for j in range(self.grid_width):
                    # print(self.states[i][j].cords, '         ' ,self.states[i][j].v, '         ' ,self.states[i][j].r, '    ', self.states[i][j].pi)
                    print(f'{self.states[i][j].v : .2f}', end=' ')
            print('-----------------------------------------------------------')  
        return agent.pi


    def get_agent(self):
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                if 'A' in self.grid[i][j]:
                    return self.states[i][j]
    


    def get_target(self):
        # print(len(self.diamonds))
        return self.diamonds.pop(0)

    def update_grid(self):
        for i in range(self.grid_height):
            for j in range(self.grid_width):

                if 'W' in self.grid[i][j]:
                    self.states[i][j].is_wall = True
                elif '*' in self.grid[i][j]:
                    self.states[i][j].is_wired = True
                    self.states[i][j].type = 'barbed'  
                elif 'T' in self.grid[i][j]:
                    self.states[i][j].type = 'teleport'
                
                # get doors
                elif 'G' in self.grid[i][j] and 'G' not in self.collected_keys:
                    self.states[i][j].door = 'G'
                    self.states[i][j].is_door = True
                elif 'R' in self.grid[i][j] and 'R' not in self.collected_keys:
                    self.states[i][j].door = 'R'
                    self.states[i][j].is_door = True
                elif 'Y' in self.grid[i][j] and 'Y' not in self.collected_keys:
                    self.states[i][j].door = 'Y'
                    self.states[i][j].is_door = True
                
                # get keys
                elif 'g' in self.grid[i][j] and (i,j) not in self.keys:
                    self.states[i][j].key = 'g'
                    self.states[i][j].type = 'slider'
                    self.keys.append((i,j))
                elif 'r' in self.grid[i][j] and (i,j) not in self.keys:
                    self.states[i][j].key = 'r'
                    self.states[i][j].type = 'slider'
                    self.keys.append((i,j))
                elif 'y' in self.grid[i][j] and (i,j) not in self.keys:
                    self.keys.append((i,j))
                    self.states[i][j].key = 'y'
                    self.states[i][j].type = 'slider'

                # get diamonds
                elif '1' in self.grid[i][j] and self.states[i][j] not in self.diamonds:
                    self.states[i][j].type = 'slider'
                    self.states[i][j].diamond = '1'
                    self.diamonds.append(self.states[i][j])
                elif '2' in self.grid[i][j] and self.states[i][j] not in self.diamonds:
                    self.states[i][j].type = 'slider'
                    self.states[i][j].diamond = '2'
                    self.diamonds.append(self.states[i][j])
                elif '3' in self.grid[i][j] and self.states[i][j] not in self.diamonds:
                    self.states[i][j].type = 'slider'
                    self.states[i][j].diamond = '3'
                    self.diamonds.append(self.states[i][j])
                elif '4' in self.grid[i][j] and self.states[i][j] not in self.diamonds:
                    self.states[i][j].type = 'slider'
                    self.states[i][j].diamond = '4'
                    self.diamonds.append(self.states[i][j])


    def get_reward(self, goal):
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                D = 1
                D2 = 2
                dx = abs(self.states[row][col].cords[0] - goal.cords[0])
                dy = abs(self.states[row][col].cords[1] - goal.cords[1])
                self.states[row][col].r =  (-1) * (D * (dx + dy) + (D2 - 2 * D) * min(dx, dy))

                if self.states[row][col].is_wired:
                    self.states[row][col].r = self.states[row][col].r - 50

                elif self.states[row][col].is_door:
                    has_key = False
                    for k in self.collected_keys:
                        if k.key.upper() == self.states[row][col].door:
                            has_key = True
                    if not has_key:
                        self.states[row][col].r = self.states[row][col].r - 100
        
                # elif self.states[row][col].is_wall:
                    # self.states[row][col].r = self.states[row][col].r - 100

                # elif self.states[row][col].key:
                #     self.states[row][col].r = self.states[row][col].r + ((1 - self.states[row][col].r) - 0.5) 

                # elif self.states[row][col].diamond == '1':
                #     self.states[row][col].r = self.states[row][col].r + 2

        goal.r = 1

    
    def succProbReward(self, state, action):

        '''TODO: fix the teleport thing with probability that next state happens'''
        
        result = []
        for a in self.get_actions(state):
        
            # if action == Action.UP:
            if a == Action.UP:

                # result.append((self.states[state.cords[0]-1][state.cords[1]], self.probabilities[state.type][action.name][a.name], state.r))
                result.append((self.states[state.cords[0]-1][state.cords[1]], self.probabilities[state.type][action.name][a.name], self.states[state.cords[0]-1][state.cords[1]].r))
                

                
                    # result.append((self.states[state.cords[0]-1][state.cords[1]], self.probabilities[state.type]['UP']['UP'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1]+1], self.probabilities[state.type]['UP']['UP_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1] -1], self.probabilities[state.type]['UP']['UP_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]], self.probabilities[state.type]['UP']['DOWN'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]+1], self.probabilities[state.type]['UP']['DOWN_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]-1], self.probabilities[state.type]['UP']['DOWN_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]+1], self.probabilities[state.type]['UP']['RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]-1], self.probabilities[state.type]['UP']['LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]], self.probabilities[state.type]['UP']['NOOP'], state.r))
                

            if action == Action.DOWN:

                    result.append((self.states[state.cords[0]+1][state.cords[1]], self.probabilities[state.type][action.name][a.name], self.states[state.cords[0]+1][state.cords[1]].r))


                    # result.append((self.states[state.cords[0]-1][state.cords[1]], self.probabilities[state.type]['DOWN']['UP'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1]+1], self.probabilities[state.type]['DOWN']['UP_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1] -1], self.probabilities[state.type]['DOWN']['UP_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]], self.probabilities[state.type]['DOWN']['DOWN'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]+1], self.probabilities[state.type]['DOWN']['DOWN_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]-1], self.probabilities[state.type]['DOWN']['DOWN_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]+1], self.probabilities[state.type]['DOWN']['RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]-1], self.probabilities[state.type]['DOWN']['LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]], self.probabilities[state.type]['DOWN']['NOOP'], state.r))
                
            if action == Action.RIGHT:

                    result.append((self.states[state.cords[0]][state.cords[1]+1], self.probabilities[state.type][action.name][a.name], self.states[state.cords[0]][state.cords[1]+1].r))

                    # result.append((self.states[state.cords[0]-1][state.cords[1]], self.probabilities[state.type]['RIGHT']['UP'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1]+1], self.probabilities[state.type]['RIGHT']['UP_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1] -1], self.probabilities[state.type]['RIGHT']['UP_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]], self.probabilities[state.type]['RIGHT']['DOWN'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]+1], self.probabilities[state.type]['RIGHT']['DOWN_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]-1], self.probabilities[state.type]['RIGHT']['DOWN_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]+1], self.probabilities[state.type]['RIGHT']['RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]-1], self.probabilities[state.type]['RIGHT']['LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]], self.probabilities[state.type]['RIGHT']['NOOP'], state.r))
                
            if action == Action.LEFT:
                    
                    result.append((self.states[state.cords[0]][state.cords[1]-1], self.probabilities[state.type][action.name][a.name], self.states[state.cords[0]][state.cords[1]-1].r))

                    # result.append((self.states[state.cords[0]-1][state.cords[1]], self.probabilities[state.type]['LEFT']['UP'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1]+1], self.probabilities[state.type]['LEFT']['UP_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1] -1], self.probabilities[state.type]['LEFT']['UP_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]], self.probabilities[state.type]['LEFT']['DOWN'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]+1], self.probabilities[state.type]['LEFT']['DOWN_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]-1], self.probabilities[state.type]['LEFT']['DOWN_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]+1], self.probabilities[state.type]['LEFT']['RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]-1], self.probabilities[state.type]['LEFT']['LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]], self.probabilities[state.type]['LEFT']['NOOP'], state.r))
                
            if action == Action.UP_LEFT:
        
                result.append((self.states[state.cords[0]-1][state.cords[1]-1], self.probabilities[state.type][action.name][a.name], self.states[state.cords[0]-1][state.cords[1]-1].r))

                    # result.append((self.states[state.cords[0]-1][state.cords[1]], self.probabilities[state.type]['UP_LEFT']['UP'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1]+1], self.probabilities[state.type]['UP_LEFT']['UP_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1] -1], self.probabilities[state.type]['UP_LEFT']['UP_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]], self.probabilities[state.type]['UP_LEFT']['DOWN'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]+1], self.probabilities[state.type]['UP_LEFT']['DOWN_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]-1], self.probabilities[state.type]['UP_LEFT']['DOWN_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]+1], self.probabilities[state.type]['UP_LEFT']['RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]-1], self.probabilities[state.type]['UP_LEFT']['LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]], self.probabilities[state.type]['UP_LEFT']['NOOP'], state.r))
                
            if action == Action.UP_RIGHT:


                result.append((self.states[state.cords[0]-1][state.cords[1] + 1], self.probabilities[state.type][action.name][a.name], self.states[state.cords[0]-1][state.cords[1]+1].r))


                    # result.append((self.states[state.cords[0]-1][state.cords[1]], self.probabilities[state.type]['UP_RIGHT']['UP'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1]+1], self.probabilities[state.type]['UP_RIGHT']['UP_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1] -1], self.probabilities[state.type]['UP_RIGHT']['UP_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]], self.probabilities[state.type]['UP_RIGHT']['DOWN'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]+1], self.probabilities[state.type]['UP_RIGHT']['DOWN_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]-1], self.probabilities[state.type]['UP_RIGHT']['DOWN_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]+1], self.probabilities[state.type]['UP_RIGHT']['RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]-1], self.probabilities[state.type]['UP_RIGHT']['LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]], self.probabilities[state.type]['UP_RIGHT']['NOOP'], state.r))
                
            if action == Action.DOWN_LEFT:
    
                result.append((self.states[state.cords[0]+1][state.cords[1] -1], self.probabilities[state.type][action.name][a.name], self.states[state.cords[0]+1][state.cords[1]-1].r))

                    # result.append((self.states[state.cords[0]-1][state.cords[1]], self.probabilities[state.type]['DOWN_LEFT']['UP'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1]+1], self.probabilities[state.type]['DOWN_LEFT']['UP_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1] -1], self.probabilities[state.type]['DOWN_LEFT']['UP_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]], self.probabilities[state.type]['DOWN_LEFT']['DOWN'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]+1], self.probabilities[state.type]['DOWN_LEFT']['DOWN_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]-1], self.probabilities[state.type]['DOWN_LEFT']['DOWN_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]+1], self.probabilities[state.type]['DOWN_LEFT']['RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]-1], self.probabilities[state.type]['DOWN_LEFT']['LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]], self.probabilities[state.type]['DOWN_LEFT']['NOOP'], state.r))
                
            if action == Action.DOWN_RIGHT:

                result.append((self.states[state.cords[0]+1][state.cords[1]+1], self.probabilities[state.type][action.name][a.name], self.states[state.cords[0]+1][state.cords[1]+1].r))
               
                    # result.append((self.states[state.cords[0]-1][state.cords[1]], self.probabilities[state.type]['DOWN_RIGHT']['UP'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1]+1], self.probabilities[state.type]['DOWN_RIGHT']['UP_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1] -1], self.probabilities[state.type]['DOWN_RIGHT']['UP_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]], self.probabilities[state.type]['DOWN_RIGHT']['DOWN'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]+1], self.probabilities[state.type]['DOWN_RIGHT']['DOWN_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]-1], self.probabilities[state.type]['DOWN_RIGHT']['DOWN_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]+1], self.probabilities[state.type]['DOWN_RIGHT']['RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]-1], self.probabilities[state.type]['DOWN_RIGHT']['LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]], self.probabilities[state.type]['DOWN_RIGHT']['NOOP'], state.r))
                
            if action == Action.NOOP:

                result.append((self.states[state.cords[0]][state.cords[1]], self.probabilities[state.type][action.name][a.name], self.states[state.cords[0]][state.cords[1]].r))

                    # result.append((self.states[state.cords[0]-1][state.cords[1]], self.probabilities[state.type]['NOOP']['UP'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1]+1], self.probabilities[state.type]['NOOP']['UP_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]-1][state.cords[1] -1], self.probabilities[state.type]['NOOP']['UP_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]], self.probabilities[state.type]['NOOP']['DOWN'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]+1], self.probabilities[state.type]['NOOP']['DOWN_RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]+1][state.cords[1]-1], self.probabilities[state.type]['NOOP']['DOWN_LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]+1], self.probabilities[state.type]['NOOP']['RIGHT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]-1], self.probabilities[state.type]['NOOP']['LEFT'], state.r))
                    # result.append((self.states[state.cords[0]][state.cords[1]], self.probabilities[state.type]['NOOP']['NOOP'], state.r))
                
        return result
        
    
    def get_actions(self, state):
        actions = []
        if state.cords[0] - 1 >= 0:
            actions.append(Action.UP)
        if state.cords[0] + 1 <= self.grid_height - 1:
            actions.append(Action.DOWN)
        if state.cords[1] - 1 >= 0:
            actions.append(Action.LEFT)
        if state.cords[1] + 1 <= self.grid_width - 1:
            actions.append(Action.RIGHT)
        if state.cords[0] - 1 >= 0 and state.cords[1] - 1 >= 0:
            actions.append(Action.UP_LEFT)
        if state.cords[0] - 1 >= 0 and state.cords[1] + 1 <= self.grid_width - 1:
            actions.append(Action.UP_RIGHT)
        if state.cords[0] + 1 <= self.grid_height - 1 >= 0 and state.cords[1] - 1 >= 0:
            actions.append(Action.DOWN_LEFT)
        if state.cords[0] + 1 <= self.grid_height - 1 >= 0 and state.cords[1] + 1 <= self.grid_width - 1:
            actions.append(Action.DOWN_RIGHT)
        
        return actions
        

    def is_End(self, state, target):
        if state == target:
            return True
        return False
    
    def valueIteration(self, target, gamma, coverage_amount):
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                self.states[row][col].v = 0
                converge = False

        def Q(state, action):
            return sum( prob*(reward + gamma*newState.v) \
                for newState, prob, reward in self.succProbReward(state, action ))

        while not converge:
            diff = 0
            for row in range(self.grid_height):
                for col in range(self.grid_width):

                    temp = self.states[row][col].v
                    self.states[row][col].v = max(Q(self.states[row][col], action) for action in self.get_actions(self.states[row][col]))
                    diff = max(diff, abs(temp - self.states[row][col].v))
            
            if diff < coverage_amount:
                converge = True
        
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                if self.is_End(self.states[row][col], target):
                    self.states[row][col].pi = Action.NOOP
                else:   
                    sums = ((Q(self.states[row][col], action), action) for action in self.get_actions(self.states[row][col]))     
                    # a = max(sums , key= lambda tup: tup[0])
                    # for s in sums:
                    #     print('sums = ', s)

                    # print(a)
                    # print('done--------------------------')
                    self.states[row][col].pi = max(sums , key= lambda tup: tup[0])[1]

    # def print_stuff(self):
    #     for s in self.states:
    #         print(s, s.v, s.pi)


if __name__ == '__main__':
    data = Agent().play()
    print("FINISH : ", data)
