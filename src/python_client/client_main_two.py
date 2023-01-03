from collections import deque
import random
from base import BaseAgent, Action
from MainClass import Node
import numpy as np


class Agent(BaseAgent):

    DIAMOND_SCORES = {
        "01": 50,
        "02": 0,
        "03": 0,
        "04": 0,
        "11": 50,
        "12": 200,
        "13": 100,
        "14": 0,
        "21": 100,
        "22": 50,
        "23": 200,
        "24": 100,
        "31": 50,
        "32": 100,
        "33": 50,
        "34": 200,
        "41": 250,
        "42": 50,
        "43": 100,
        "44": 50,
    }

    states = []
    diamonds = []
    keys = []
    collected_keys = []
    key_values = []
    target = None
    last_diamond = '0'
    q_values = []
    total_actions = [
        Action.UP,
        Action.DOWN,
        Action.LEFT,
        Action.RIGHT,
        Action.UP_LEFT,
        Action.UP_RIGHT,
        Action.DOWN_LEFT,
        Action.DOWN_RIGHT,
        Action.NOOP,
    ]

    def __init__(self):
        super().__init__()

        self.states = [
            [None for _ in range(self.grid_width)] for _ in range(self.grid_height)
        ]
        self.q_values = np.zeros((self.grid_height, self.grid_width, 9))

        for row in range(self.grid_height):
            for col in range(self.grid_width):
                self.states[row][col] = Node((row, col), 0)

    def do_turn(self) -> Action:

        agent = self.get_agent()
        row_index, column_index = agent.cords[0], agent.cords[1]

        if agent.cords in self.keys:
            self.collected_keys.append(agent)
            self.key_values.append(agent.key)
            self.keys.remove(agent.cords)
            self.states[row_index][column_index].key = ""

        if agent.cords in self.diamonds:
            self.last_diamond = agent.diamond
            agent.diamond = ""

        self.update_grid()
        
        if len(self.diamonds) == 0:
            return Action.NOOP

        self.get_reward()

        distance = self.positive_trace()

        self.q_learning(row_index, column_index, distance)

        return self.get_shortest_path(row_index, column_index)

    def get_agent(self):
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                if "A" in self.grid[i][j]:
                    return self.states[i][j]

    def get_target(self):
        return self.diamonds.pop(0)

    def update_grid(self):
        for i in range(self.grid_height):
            for j in range(self.grid_width):

                if "W" in self.grid[i][j]:
                    self.states[i][j].is_wall = True
                elif "*" in self.grid[i][j]:
                    self.states[i][j].is_wired = True
                    self.states[i][j].type = "barbed"
                elif "T" in self.grid[i][j]:
                    self.states[i][j].type = "teleport"

                # get doors
                elif "G" in self.grid[i][j]:
                    if "g" not in self.key_values:
                        self.states[i][j].door = "G"
                        self.states[i][j].is_door = True
                    else:
                        self.states[i][j].door = ""
                        self.states[i][j].is_door = False
                elif "R" in self.grid[i][j]:
                    if "r" not in self.key_values:
                        self.states[i][j].door = "R"
                        self.states[i][j].is_door = True
                    else:
                        self.states[i][j].door = ""
                        self.states[i][j].is_door = False
                elif "Y" in self.grid[i][j]:
                    if "y" not in self.key_values:
                        self.states[i][j].door = "Y"
                        self.states[i][j].is_door = True
                    else:
                        self.states[i][j].door = ""
                        self.states[i][j].is_door = False

                # get keys
                elif "g" in self.grid[i][j] and (i, j) not in self.keys:
                        self.states[i][j].key = "g"
                        self.states[i][j].type = "slider"
                        self.keys.append((i, j))
                        self.states[i][j].available = True

                elif "r" in self.grid[i][j] and (i, j) not in self.keys:
                    self.states[i][j].key = "r"
                    self.states[i][j].type = "slider"
                    self.keys.append((i, j))
                    self.states[i][j].available = True
                elif "y" in self.grid[i][j] and (i, j) not in self.keys:
                    self.states[i][j].key = "y"
                    self.states[i][j].type = "slider"
                    self.keys.append((i, j))
                    self.states[i][j].available = True

                # get diamonds
                elif "1" in self.grid[i][j] and self.states[i][j] not in self.diamonds:
                    self.states[i][j].type = "slider"
                    self.states[i][j].diamond = "1"
                    self.diamonds.append(self.states[i][j])
                    self.states[i][j].available = True
                elif "2" in self.grid[i][j] and self.states[i][j] not in self.diamonds:
                    self.states[i][j].type = "slider"
                    self.states[i][j].diamond = "2"
                    self.diamonds.append(self.states[i][j])
                    self.states[i][j].available = True
                elif "3" in self.grid[i][j] and self.states[i][j] not in self.diamonds:
                    self.states[i][j].type = "slider"
                    self.states[i][j].diamond = "3"
                    self.diamonds.append(self.states[i][j])
                    self.states[i][j].available = True
                elif "4" in self.grid[i][j] and self.states[i][j] not in self.diamonds:
                    self.states[i][j].type = "slider"
                    self.states[i][j].diamond = "4"
                    self.diamonds.append(self.states[i][j])
                    self.states[i][j].available = True

    def get_actions(self, row_index, column_index):
        actions = []

        if (
            row_index - 1 >= 0
            and self.states[row_index - 1][column_index].is_wall == False
        ):
            if self.states[row_index - 1][column_index].is_door:
                for k in self.collected_keys:
                    if k.key.upper() == self.states[row_index - 1][column_index].door:
                        actions.append(Action.UP)
            else:
                actions.append(Action.UP)

        if (
            row_index + 1 <= self.grid_height - 1
            and self.states[row_index + 1][column_index].is_wall == False
        ):
            if self.states[row_index + 1][column_index].is_door:
                for k in self.collected_keys:
                    if k.key.upper() == self.states[row_index + 1][column_index].door:
                        actions.append(Action.DOWN)
            else:
                actions.append(Action.DOWN)

        if (
            column_index - 1 >= 0
            and self.states[row_index][column_index - 1].is_wall == False
        ):
            if self.states[row_index][column_index - 1].is_door:
                for k in self.collected_keys:
                    if k.key.upper() == self.states[row_index][column_index - 1].door:
                        actions.append(Action.LEFT)
            else:
                actions.append(Action.LEFT)

        if (
            column_index + 1 <= self.grid_width - 1
            and self.states[row_index][column_index + 1].is_wall == False
        ):
            if self.states[row_index][column_index + 1].is_door:
                for k in self.collected_keys:
                    if k.key.upper() == self.states[row_index][column_index + 1].door:
                        actions.append(Action.RIGHT)
            else:
                actions.append(Action.RIGHT)

        if (
            row_index - 1 >= 0
            and column_index - 1 >= 0
            and self.states[row_index - 1][column_index - 1].is_wall == False
        ):
            if self.states[row_index - 1][column_index - 1].is_door:
                for k in self.collected_keys:
                    if k.key.upper() == self.states[row_index - 1][column_index - 1].door:
                        actions.append(Action.UP_LEFT)
            else:
                actions.append(Action.UP_LEFT)

        if (
            row_index - 1 >= 0
            and column_index + 1 <= self.grid_width - 1
            and self.states[row_index - 1][column_index + 1].is_wall == False
        ):
            if self.states[row_index - 1][column_index + 1].is_door:
                for k in self.collected_keys:
                    if k.key.upper() == self.states[row_index - 1][column_index + 1].door:
                        actions.append(Action.UP_RIGHT)
            else:
                actions.append(Action.UP_RIGHT)

        if (
            row_index + 1 <= self.grid_height - 1
            and column_index - 1 >= 0
            and self.states[row_index + 1][column_index - 1].is_wall == False
        ):
            if self.states[row_index + 1][column_index - 1].is_door:
                for k in self.collected_keys:
                    if k.key.upper() == self.states[row_index + 1][column_index - 1].door:
                        actions.append(Action.DOWN_LEFT)
            else:
                actions.append(Action.DOWN_LEFT)

        if (
            row_index + 1 <= self.grid_height - 1
            and column_index + 1 <= self.grid_width - 1
            and self.states[row_index + 1][column_index + 1].is_wall == False
        ):
            if self.states[row_index + 1][column_index + 1].is_door:
                for k in self.collected_keys:
                    if k.key.upper() == self.states[row_index + 1][column_index + 1].door:
                        actions.append(Action.DOWN_RIGHT)
            else:
                actions.append(Action.DOWN_RIGHT)

        actions.append(Action.NOOP)

        return actions

    def get_reward(self):
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                self.states[row][col].r = -1

                if self.states[row][col].is_wired:
                    self.states[row][col].r = -0.5

                elif self.states[row][col].is_door:
                    has_key = False
                    for k in self.collected_keys:
                        if k.key.upper() == self.states[row][col].door:
                            has_key = True
                            self.states[row][col].r = -1
                    if not has_key:
                        self.states[row][col].r = 0

                elif self.states[row][col].is_wall:
                    self.states[row][col].r = 0

                elif self.states[row][col].key:
                    self.states[row][col].r = 50


    def positive_trace(self):
        start = self.get_agent()
        row_index, column_index = start.cords[0], start.cords[1]
        dest = ""
        found = False
        while found == False:
            shortest = 1000
            for i in range(self.grid_height):
                for j in range(self.grid_width):
                    if (
                        self.states[i][j].diamond == "1"
                        or self.states[i][j].diamond == "2"
                        or self.states[i][j].diamond == "3"
                        or self.states[i][j].diamond == "4"
                        or (self.states[i][j].key == "g" and "g" not in self.key_values)
                        or (self.states[i][j].key == "r" and "r" not in self.key_values)
                        or (self.states[i][j].key == "y" and "y" not in self.key_values)
                    ) and self.states[i][j].available == True:
                        distance = self.heuristic(
                            (start.cords[0], start.cords[1]), (i, j)
                        )
                        if shortest >= distance:
                            shortest = distance
                            dest = (i, j)

            dest_cords = dest
            source = Point(row_index, column_index)
            try:
                dest = Point(dest_cords[0], dest_cords[1])
            except:
                pass

            path = self.BFS(source, dest)

            if path == -1:
                self.states[dest.x][dest.y].available = False
            else:
                found = True
                self.states[dest.x][dest.y].available = True

        path_rewards = []

        for i in range(len(path)):
            path_rewards.append(self.states[path[i].x][path[i].y].r)

        if 0 in path_rewards:
            self.states[dest_cords[0]][dest_cords[1]].r = -1
        else:
            second_diamond = self.states[dest_cords[0]][dest_cords[1]].diamond
            for i in self.DIAMOND_SCORES.keys():
                if i == self.last_diamond + second_diamond:
                    self.states[dest_cords[0]][dest_cords[1]].r = self.DIAMOND_SCORES[i]

        addition = 0
        for k in range(len(path)):
            addition += 50
            path[k] = (path[k].x, path[k].y)
            for i in range(self.grid_height):
                for j in range(self.grid_width):
                    if path[k] == (i, j):
                        self.states[i][j].r += addition
        return len(path)


    def isValid(self, row, col):
        return (
            (row >= 0)
            and (row < self.grid_height)
            and (col >= 0)
            and (col < self.grid_width)
        )

    rowNum = [-1, 0, 0, 1, 1, -1, 1, -1]
    colNum = [0, -1, 1, 0, 1, -1, -1, 1]

    def BFS(self, start, dest):

        mat = np.ones((self.grid_height, self.grid_width))
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                if self.states[i][j].is_wall == True:
                    mat[i, j] = 0
                elif self.states[i][j].is_door == True:
                    mat[i, j] = 0

        visited = [
            [False for i in range(self.grid_width)] for j in range(self.grid_height)
        ]
        visited[start.x][start.y] = True
        q = deque()
        s = queueNode(start, 0)
        q.append(s)

        while q:

            curr = q.popleft()
            pt = curr.pt
            if pt.x == dest.x and pt.y == dest.y:
                path = []
                self.getPath(curr, path)
                return path

            for i in range(8):
                row = pt.x + self.rowNum[i]
                col = pt.y + self.colNum[i]

                if self.isValid(row, col) and mat[row][col] == 1:
                    Adjcell = queueNode(Point(row, col), curr.dist + 1, curr)
                    if not visited[row][col]:
                        visited[row][col] = True
                        q.append(Adjcell)

        return -1

    def getPath(self, node, path=[]):
        if node:
            self.getPath(node.parent, path)
            path.append(node.pt)

    def heuristic(self, start, goal):
        D = 1
        D2 = 2
        dx = abs(start[0] - goal[0])
        dy = abs(start[1] - goal[1])
        return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)

    def get_next_location(self, row_index, column_index, epsilon):

        if np.random.random() < epsilon:
            action = self.total_actions[
                np.argmax(self.q_values[row_index, column_index])
            ]
        else:
            action = self.total_actions[np.random.randint(9)]

        actions = self.get_actions(row_index, column_index)

        if action in actions:

            if action == Action.UP:
                row_index, column_index = row_index - 1, column_index

            if action == Action.DOWN:
                row_index, column_index = row_index + 1, column_index

            if action == Action.RIGHT:
                row_index, column_index = row_index, column_index + 1

            if action == Action.LEFT:
                row_index, column_index = row_index, column_index - 1

            if action == Action.UP_LEFT:
                row_index, column_index = row_index - 1, column_index - 1

            if action == Action.UP_RIGHT:
                row_index, column_index = row_index - 1, column_index + 1

            if action == Action.DOWN_LEFT:
                row_index, column_index = row_index + 1, column_index - 1

            if action == Action.DOWN_RIGHT:
                row_index, column_index = row_index + 1, column_index + 1

            return action, row_index, column_index
        else:
            return Action.NOOP, row_index, column_index

    def is_terminal_state(self, current_row_index, current_column_index):
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                if row == current_row_index and col == current_column_index:
                    if self.states[row][col].r < -5:
                        return True
                    else:
                        return False

    def get_shortest_path(self, row_index, column_index):
        terminal = self.is_terminal_state(row_index, column_index)

        if terminal:
            return Action.NOOP
        else:
            action, row_index, column_index = self.get_next_location(
                row_index, column_index, 1
            )
            return action


    def q_learning(self, row_index, column_index, distance):
        epsilon = 0.9

        if distance <= 2:
            epsilon = 0.95
        elif distance > 2 and distance < 4:
            epsilon = 0.85
        elif distance >= 4 and distance < 6:
            epsilon = 0.78
        elif distance >= 6 and distance < 8:
            epsilon = 0.69
        else:
            epsilon = 0.6

        learning_rate = 0.5
        discount_factor = 0.1
        q_diamonds = self.diamonds

        for episode in range(70000):
            if len(q_diamonds) != 0:
                q_diamonds.pop(0)
            while (
                not self.is_terminal_state(row_index, column_index)
                and (
                    row_index >= 0
                    and row_index <= self.grid_height - 1
                    and column_index >= 0
                    and column_index <= self.grid_width - 1
                )
                and len(q_diamonds) != 0
            ):
                old_row_index, old_column_index = (
                    row_index,
                    column_index,
                )
                self.states[old_row_index][old_column_index].r -= 1
                action, row_index, column_index = self.get_next_location(
                    row_index, column_index, epsilon
                )
                action_index = self.total_actions.index(action)
                reward = self.states[row_index][column_index].r
                old_q_value = self.q_values[
                    old_row_index, old_column_index, action_index
                ]
                temporal_difference = (
                    reward
                    + (discount_factor * np.max(self.q_values[row_index, column_index]))
                    - old_q_value
                )

                new_q_value = old_q_value + (learning_rate * temporal_difference)
                self.q_values[
                    old_row_index, old_column_index, action_index
                ] = new_q_value
                if (
                    self.states[row_index][column_index].diamond == "1"
                    or self.states[row_index][column_index].diamond == "2"
                    or self.states[row_index][column_index].diamond == "3"
                    or self.states[row_index][column_index].diamond == "4"
                ):
                    self.states[row_index][column_index].diamond = ""
                    self.states[row_index][column_index].r = -1
                elif (
                    self.states[row_index][column_index].key == "g"
                    or self.states[row_index][column_index].key == "r"
                    or self.states[row_index][column_index].key == "y"
                ) and (self.states[row_index][column_index] in self.collected_keys):
                    self.states[row_index][column_index].r = -1


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class queueNode:
    def __init__(self, pt: Point, dist: int, parent=None):
        self.pt = pt
        self.dist = dist
        self.parent = parent


if __name__ == "__main__":
    data = Agent().play()
    print("FINISH : ", data)
