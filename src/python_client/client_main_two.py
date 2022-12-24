from itertools import permutations
import random
from base import BaseAgent, Action
from MainClass import Node
import numpy as np

class Agent(BaseAgent):

  DIAMOND_SCORES = {
        '01': 50,
        '02': 0,
        '03': 0,
        '04': 0,
        '11': 50,
        '12': 200,
        '13': 100,
        '14': 0,
        '21': 100,
        '22': 50,
        '23': 200,
        '24': 100,
        '31': 50,
        '32': 100,
        '33': 50,
        '34': 200,
        '41': 250,
        '42': 50,
        '43': 100,
        '44': 50,
    }

  states = []
  diamonds = []
  keys = []
  collected_keys = []
  run = False
  target = None
  q_values =[]
  total_actions = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT, Action.UP_LEFT, Action.UP_RIGHT, Action.DOWN_LEFT, Action.DOWN_RIGHT, Action.NOOP]
  last_diamond = '0'
  combo = ''
  combo_value = 0

  def __init__(self):
      super().__init__()

      self.states = [[None for _ in range(self.grid_width)] for _ in range(self.grid_height)]
      self.q_values = np.zeros((self.grid_height, self.grid_width, 9))

      for row in range(self.grid_height):
          for col in range(self.grid_width):
              self.states[row][col] = Node((row, col), 0)

  
  def do_turn(self) -> Action:

      agent = self.get_agent()
      row_index, column_index = agent.cords[0], agent.cords[1]
      self.update_grid()

      if agent.cords in self.keys:
          self.collected_keys.append(agent)
      if agent.cords in self.diamonds:
        agent.diamond = ''
      

      if len(self.diamonds) == 0:
        print('2')
        return Action.NOOP


      distance = self.get_reward()
      self.q_learning(row_index, column_index, distance)
    #   print(self.q_values[0,0])
    #   print('2')
      self.run = True
    #   for row in range(self.grid_height):
    #     print()
    #     for col in range(self.grid_width):
    #         if self.states[3][0].r != -101:
    #             print(self.states[row][col].r, end=",")
    #   print()
    #   print("|||||||||||")
            
        
    #   for i in range(len(best_actions)-1):
    #     print(best_actions[i])
    #     return best_actions[i]
      return self.get_shortest_path(row_index, column_index)

        




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
                #   print('g')
                  self.states[i][j].key = 'g'
                  self.states[i][j].type = 'slider'
                  self.keys.append((i,j))
              elif 'r' in self.grid[i][j] and (i,j) not in self.keys:
                #   print('r')
                  self.states[i][j].key = 'r'
                  self.states[i][j].type = 'slider'
                  self.keys.append((i,j))
              elif 'y' in self.grid[i][j] and (i,j) not in self.keys:
                #   print('y')
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
  
  def get_actions(self, row_index, column_index):
      actions = []
      if row_index - 1 >= 0:
          actions.append(Action.UP)
      if row_index + 1 <= self.grid_height - 1:
          actions.append(Action.DOWN)
      if column_index - 1 >= 0:
          actions.append(Action.LEFT)
      if column_index + 1 <= self.grid_width - 1:
          actions.append(Action.RIGHT)
      if row_index - 1 >= 0 and column_index - 1 >= 0:
          actions.append(Action.UP_LEFT)
      if row_index - 1 >= 0 and column_index + 1 <= self.grid_width - 1:
          actions.append(Action.UP_RIGHT)
      if row_index + 1 <= self.grid_height - 1 >= 0 and column_index - 1 >= 0:
          actions.append(Action.DOWN_LEFT)
      if row_index + 1 <= self.grid_height - 1 >= 0 and column_index + 1 <= self.grid_width - 1:
          actions.append(Action.DOWN_RIGHT)

      actions.append(Action.NOOP)
      
      return actions

  def get_reward(self,):
    for row in range(self.grid_height):
      for col in range(self.grid_width):
        # D = 1
        # D2 = 2
        # dx = abs(self.states[row][col].cords[0] - goal.cords[0])
        # dy = abs(self.states[row][col].cords[1] - goal.cords[1])
        self.states[row][col].r =  -0.04

        if self.states[row][col].is_wired:
          self.states[row][col].r = self.states[row][col].r - 0.1

        elif self.states[row][col].is_door:
        #   print('1')
          has_key = False
          rowNum = [-1, 0, 0, 1, 1, -1, 1, -1]
          colNum = [0, -1, 1, 0, 1, -1, -1, 1]
          for k in self.collected_keys:
            # print(k)
            if k.key.upper() == self.states[row][col].door:
              has_key = True
              self.states[row][col].r += 20
              for i in range(8):
                if row + rowNum[i] >= 0 and row + rowNum[i] <= self.grid_height -1 and col + colNum[i] >= 0 and col + colNum[i] <= self.grid_width -1:
                    self.states[row + rowNum[i]][col + colNum[i]].r += 0
              
          if not has_key:
            self.states[row][col].r = self.states[row][col].r - 2

        elif self.states[row][col].is_wall:
            self.states[row][col].r = self.states[row][col].r - 2

        elif self.states[row][col].key:
            self.states[row][col].r = self.states[row][col].r + 20

        # elif self.states[row][col].diamond == '1' or self.states[row][col].diamond == '2' or self.states[row][col].diamond == '3' or self.states[row][col].diamond == '4':
        #     self.states[row][col].r = self.states[row][col].r + 40
        nearest_diamond, distance = self.get_distance()

        goal, goal_type = self.get_near_diamonds() 
        selected_perm, max_score = self.cluster_max_score(goal_type)
        x = 0
        if len(goal_type) != 0:
            for i in selected_perm:
                for j in goal:
                    if i == j.diamond:
                        j.r = (len(selected_perm)*400 - x)/(distance)
                        # print('g')
                        x += 130
        else:
            nearest_diamond.r = 180
            
    return distance
        
    # goal.r = 1

    
  def get_near_diamonds(self):
        agent = self.get_agent()
        x ,y = agent.cords[0], agent.cords[1]
        near_diamonds = []
        near_diamonds_type =[]
        for i in range(len(self.diamonds)):
            if self.diamonds[i].cords[0] <= x+2 and self.diamonds[i].cords[0] >= x-2 and self.diamonds[i].cords[1] <= y+2 and self.diamonds[i].cords[1] >= y-2:
                near_diamonds_type.append(self.diamonds[i].diamond)
                near_diamonds.append(self.diamonds[i])


        return near_diamonds , near_diamonds_type

  def cluster_max_score(self, goal):
        perm = list(permutations(goal))  
        my_max = 0
        selected_perm = []
        for j in perm:
            s = 0
            for i in range(len(j) - 1):
                if str(j[i][0]) + str(j[i+1][0]) in list(self.DIAMOND_SCORES.keys()):
                    s = s + self.DIAMOND_SCORES[str(j[i][0]) + str(j[i+1][0])]
            if s >= my_max:
                my_max = s
                selected_perm = j
                
        return selected_perm, my_max

  def get_distance(self):
        '''implemented with diagonal distance as the heuristic function'''
        agent = self.get_agent()
        x ,y = agent.cords[0], agent.cords[1]
        D = 1
        D2 = 2
        distance = 2**32
        nearest_diamond =''
        for i in range(len(self.diamonds)):  
            dx = abs(x - self.diamonds[i].cords[0])
            dy = abs(y - self.diamonds[i].cords[1])
            tmp = D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)
            if tmp < distance:
                distance = tmp
                nearest_diamond = self.diamonds[i]
                # print(nearest_diamond.cords)
                
        return nearest_diamond, distance


#   def get_next_action(self, current_row_index, current_column_index, epsilon):
#       if np.random.random() < epsilon:
#         #   print(self.total_actions[np.argmax(self.q_values[current_row_index, current_column_index])])
#         #   print(np.argmax(self.q_values[current_row_index, current_column_index]))
#         #   print("1")
#         #   print("||||||||||||||||")
#           return self.total_actions[np.argmax(self.q_values[current_row_index, current_column_index])]
#       else:
#         #   print(self.total_actions[np.random.randint(9)])
#         #   print("2")
#         #   print("||||||||||||||||")
#           return self.total_actions[np.random.randint(9)]

  def get_next_location(self, row_index, column_index ,epsilon):

        if np.random.random() < epsilon:
        #   print(self.total_actions[np.argmax(self.q_values[current_row_index, current_column_index])])
        #   print(np.argmax(self.q_values[current_row_index, current_column_index]))
        #   print("1")
        #   print("||||||||||||||||")
            action = self.total_actions[np.argmax(self.q_values[row_index, column_index])]
        else:
        #   print(self.total_actions[np.random.randint(9)])
        #   print("2")
        #   print("||||||||||||||||")
            action = self.total_actions[np.random.randint(9)]

        actions = self.get_actions(row_index, column_index)

        # print(action)
        # print("|||||||||||")
        if action in actions:
            # print(action.value)

            if action == Action.UP:
                row_index, column_index = row_index-1, column_index

            if action == Action.DOWN:
                row_index, column_index = row_index+1, column_index

            if action == Action.RIGHT:
                row_index, column_index = row_index, column_index+1

            if action == Action.LEFT:
                row_index, column_index = row_index, column_index-1

            if action == Action.UP_LEFT:
                row_index, column_index = row_index-1, column_index-1

            if action == Action.UP_RIGHT:
                row_index, column_index = row_index-1, column_index+1

            if action == Action.DOWN_LEFT:
                row_index, column_index = row_index+1, column_index-1

            if action == Action.DOWN_RIGHT:
                row_index, column_index = row_index+1, column_index+1
            # print(row_index, column_index)
        # print(row_index, column_index)
            # print(action.value)
            return action, row_index, column_index
        else:
            return Action.NOOP, row_index, column_index
            
        

  def is_End(self, state, target):
      if state == target:
          return True
      return False

  def is_terminal_state(self, current_row_index, current_column_index):
      for row in range(self.grid_height):
        for col in range(self.grid_width):
            if row == current_row_index and col == current_column_index:
                if self.states[row][col].r < -1.8:
                    return True
                else:
                    return False
            
             


  def get_shortest_path(self, row_index, column_index ):
      terminal = self.is_terminal_state(row_index, column_index)
    
      if terminal:
        print("1")
        # print(row_index, column_index)
        # print()
        return Action.NOOP
      else:
    #   best_actions.append()

        # print(action.value)
        action, row_index, column_index = self.get_next_location(row_index, column_index, 1.) 
        # print(row_index, column_index
        return action
    #   shortest_path.append([row_index, column_index])
      

  def q_learning(self, row_index, column_index, distance):
    epsilon = 0.8
    if distance <= 2:
        epsilon = 0.85 #the percentage of time when we should take the best action (instead of a random action)
    elif distance >2 and distance < 4:
        epsilon = 0.78 #the percentage of time when we should take the best action (instead of a random action)
    elif distance >= 4 and distance < 6 :
        epsilon = 0.68 #the percentage of time when we should take the best action (instead of a random action)
    elif distance >= 6 and distance < 8 :
        epsilon = 0.45 #the percentage of time when we should take the best action (instead of a random action)
    elif distance >= 8 and distance < 10 :
        epsilon = 0.25 #the percentage of time when we should take the best action (instead of a random action)
    # print(epsilon)
    discount_factor = 0.85 #discount factor for future rewards
    learning_rate = 0.4 #the rate at which the AI agent should learn
    q_diamonds = self.diamonds

    is_frist_action = True
    old_action =''

    #run through 1000 training episodes
    for episode in range(10000):
    #   print("1")
      #get the starting location for this episode

      #continue taking actions (i.e., moving) until we reach a terminal state
      #(i.e., until we reach the item packaging area or crash into an item storage location)
    #   print(row_index, column_index)
      if len(q_diamonds) != 0:
        q_diamonds.pop(0)
      while not self.is_terminal_state(row_index, column_index) and (row_index >= 0 and row_index <= self.grid_height -1 and column_index >= 0 and column_index <= self.grid_width -1) and len(q_diamonds) != 0:
        #choose which action to take (i.e., where to move next)
        #perform the chosen action, and transition to the next state (i.e., move to the next location)
        old_row_index, old_column_index = row_index, column_index #store the old row and column indexes
        if not is_frist_action:
            old_action = action
        else:
            is_frist_action = False

        if self.states[old_row_index][old_column_index].is_door:
            self.states[old_row_index][old_column_index].r = -0.04

        action, row_index, column_index = self.get_next_location(row_index, column_index, epsilon)
        action_index = self.total_actions.index(action)
        if old_action == Action.NOOP and action == Action.NOOP:
            self.states[old_row_index][old_column_index].r -= 0
        else:
            self.states[old_row_index][old_column_index].r -= 0.02
        # print(row_index, column_index)
        # print("2")
        #receive the reward for moving to the new state, and calculate the temporal difference
        reward = self.states[row_index][column_index].r
        # print(row_index, column_index)
        # print(reward)
        old_q_value = self.q_values[old_row_index, old_column_index, action_index]
        # print(old_q_value)
        # print(row_index, column_index)
        temporal_difference = reward + (discount_factor * np.max(self.q_values[row_index, column_index])) - old_q_value
        # print(temporal_difference)
        # print("|||||||||")
        #update the Q-value for the previous state and action pair
        new_q_value = old_q_value + (learning_rate * temporal_difference)
        self.q_values[old_row_index, old_column_index, action_index] = new_q_value
        if self.states[row_index][column_index].diamond == '1' or self.states[row_index][column_index].diamond == '2' or self.states[row_index][column_index].diamond == '3' or self.states[row_index][column_index].diamond == '4':
            self.states[row_index][column_index].diamond = ''
            self.states[row_index][column_index].r = -0.04
        if self.states[row_index][column_index].key == 'y' or self.states[row_index][column_index].key == 'r' or self.states[row_index][column_index].key == 'g':
            # self.states[row_index][column_index].key = ''
            self.states[row_index][column_index].r = -0.04
        
    
    # def print_stuff(self):
    #     for s in self.states:
    #         print(s, s.v, s.pi)
if __name__ == '__main__':
  data = Agent().play()
  print("FINISH : ", data)