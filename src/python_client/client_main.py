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
    last_diamond = None
    last_cord = ()
    actions = [
        Action.DOWN,
        Action.DOWN_LEFT,
        Action.DOWN_RIGHT,
        Action.LEFT,
        Action.RIGHT,
        Action.NOOP,
        Action.UP,
        Action.UP_LEFT,
        Action.UP_RIGHT,
    ]

    def __init__(self):
        super().__init__()

        self.states = [
            [None for _ in range(self.grid_width)] for _ in range(self.grid_height)
        ]
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                self.states[row][col] = Node((row, col), -1)

    def do_turn(self) -> Action:
        agent = self.get_agent()
        if self.is_End(agent):
            self.run = False
        self.update_grid()

        if not self.run:
            if len(self.diamonds) == 0:
                return Action.NOOP

            self.get_reward()
            self.valueIteration(0.8, 1e-3)
            print("agent = ", agent.cords)
            self.print_stuff()

            self.run = True

        self.get_policy()
        return agent.pi

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
                elif "G" in self.grid[i][j] and "g" not in self.collected_keys:
                    self.states[i][j].door = "G"
                    self.states[i][j].is_door = True
                elif "R" in self.grid[i][j] and "r" not in self.collected_keys:
                    self.states[i][j].door = "R"
                    self.states[i][j].is_door = True
                elif "Y" in self.grid[i][j] and "y" not in self.collected_keys:
                    self.states[i][j].door = "Y"
                    self.states[i][j].is_door = True

                # get keys
                elif "g" in self.grid[i][j] and (i, j) not in self.keys:
                    self.states[i][j].key = "g"
                    self.states[i][j].type = "slider"
                    self.keys.append((i, j))
                elif "r" in self.grid[i][j] and (i, j) not in self.keys:
                    self.states[i][j].key = "r"
                    self.states[i][j].type = "slider"
                    self.keys.append((i, j))
                elif "y" in self.grid[i][j] and (i, j) not in self.keys:
                    self.states[i][j].key = "y"
                    self.states[i][j].type = "slider"
                    self.keys.append((i, j))

                # get diamonds
                elif "1" in self.grid[i][j] and self.states[i][j] not in self.diamonds:
                    self.states[i][j].type = "slider"
                    self.states[i][j].diamond = "1"
                    self.diamonds.append(self.states[i][j])
                elif "2" in self.grid[i][j] and self.states[i][j] not in self.diamonds:
                    self.states[i][j].type = "slider"
                    self.states[i][j].diamond = "2"
                    self.diamonds.append(self.states[i][j])
                elif "3" in self.grid[i][j] and self.states[i][j] not in self.diamonds:
                    self.states[i][j].type = "slider"
                    self.states[i][j].diamond = "3"
                    self.diamonds.append(self.states[i][j])
                elif "4" in self.grid[i][j] and self.states[i][j] not in self.diamonds:
                    self.states[i][j].type = "slider"
                    self.states[i][j].diamond = "4"
                    self.diamonds.append(self.states[i][j])

    def diamond_score(self, state):
        if self.last_diamond == None:
            if state.diamond == "1":
                return 50
            else:
                return 0
        elif self.last_diamond == "1":
            if state.diamond == "1":
                return 50
            elif state.diamond == "2":
                return 200
            elif state.diamond == "3":
                return 100
            else:
                return 0

        elif self.last_diamond == "2":
            if state.diamond == "1":
                return 100
            elif state.diamond == "2":
                return 50
            elif state.diamond == "3":
                return 200
            else:
                return 100

        elif self.last_diamond == "3":
            if state.diamond == "1":
                return 50
            elif state.diamond == "2":
                return 100
            elif state.diamond == "3":
                return 50
            else:
                return 200
        else:
            if state.diamond == "1":
                return 250
            elif state.diamond == "2":
                return 50
            elif state.diamond == "3":
                return 100
            else:
                return 50

    def get_reward(self):
        for row in range(self.grid_height):
            for col in range(self.grid_width):

                self.states[row][col].r = -0.03

                if self.states[row][col].is_wired:
                    self.states[row][col].r += -1

                elif self.states[row][col].is_wall:
                    self.states[row][col].r += -1000

                elif self.states[row][col] in self.diamonds:
                    a = self.diamond_score(self.states[row][col])
                    self.states[row][col].r += a

                elif self.states[row][col].is_door:
                    has_key = False
                    for k in self.collected_keys:
                        if k.upper() == self.states[row][col].door:
                            has_key = True
                    if not has_key:
                        self.states[row][col].r += -1000
                    else:
                        self.states[row][col].r += 20

                elif self.states[row][col].cords in self.keys:
                    self.states[row][col].r += 100

    def succProbReward(self, state, action):

        i = state.cords[0]
        j = state.cords[1]
        result = []
        if not state.is_door and not state.is_wall and state not in self.diamonds:
            for a in self.actions:

                if a == Action.UP:
                    if i != 0 and not self.states[i - 1][j].is_wall:
                        result.append(
                            (
                                self.states[state.cords[0] - 1][state.cords[1]],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )
                    else:
                        result.append(
                            (
                                self.states[state.cords[0]][state.cords[1]],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )

                elif a == Action.DOWN:
                    if i != self.grid_height - 1 and not self.states[i + 1][j].is_wall:
                        result.append(
                            (
                                self.states[state.cords[0] + 1][state.cords[1]],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )
                    else:
                        result.append(
                            (
                                self.states[state.cords[0]][state.cords[1]],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )

                elif a == Action.RIGHT:
                    if j != self.grid_width - 1 and not self.states[i][j + 1].is_wall:
                        result.append(
                            (
                                self.states[state.cords[0]][state.cords[1] + 1],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )
                    else:
                        result.append(
                            (
                                self.states[state.cords[0]][state.cords[1]],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )

                elif a == Action.LEFT:
                    if j != 0 and not self.states[i][j - 1].is_wall:
                        result.append(
                            (
                                self.states[state.cords[0]][state.cords[1] - 1],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )
                    else:
                        result.append(
                            (
                                self.states[state.cords[0]][state.cords[1]],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )

                elif a == Action.UP_LEFT:
                    if i != 0 and j != 0 and not self.states[i - 1][j - 1].is_wall:
                        result.append(
                            (
                                self.states[state.cords[0] - 1][state.cords[1] - 1],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )
                    else:
                        result.append(
                            (
                                self.states[state.cords[0]][state.cords[1]],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )

                elif a == Action.UP_RIGHT:
                    if (
                        i != 0
                        and j != self.grid_width - 1
                        and not self.states[i - 1][j + 1].is_wall
                    ):
                        result.append(
                            (
                                self.states[state.cords[0] - 1][state.cords[1] + 1],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )
                    else:
                        result.append(
                            (
                                self.states[state.cords[0]][state.cords[1]],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )

                elif a == Action.DOWN_LEFT:
                    if (
                        i != self.grid_height - 1
                        and j != 0
                        and not self.states[i + 1][j - 1].is_wall
                    ):
                        result.append(
                            (
                                self.states[state.cords[0] + 1][state.cords[1] - 1],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )
                    else:
                        result.append(
                            (
                                self.states[state.cords[0]][state.cords[1]],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )

                elif a == Action.DOWN_RIGHT:
                    if (
                        i != self.grid_height - 1
                        and j != self.grid_width - 1
                        and not self.states[i + 1][j + 1].is_wall
                    ):
                        result.append(
                            (
                                self.states[state.cords[0] + 1][state.cords[1] + 1],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )
                    else:
                        result.append(
                            (
                                self.states[state.cords[0]][state.cords[1]],
                                self.probabilities[state.type][action.name][a.name],
                                state.r,
                            )
                        )

                elif a == Action.NOOP:
                    result.append(
                        (
                            self.states[state.cords[0]][state.cords[1]],
                            self.probabilities[state.type][action.name][a.name],
                            state.r,
                        )
                    )
        else:
            result.append((self.states[state.cords[0]][state.cords[1]], 1, state.r))

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
        if state.cords[0] + 1 <= self.grid_height - 1 and state.cords[1] - 1 >= 0:
            actions.append(Action.DOWN_LEFT)
        if (
            state.cords[0] + 1 <= self.grid_height - 1
            and state.cords[1] + 1 <= self.grid_width - 1
        ):
            actions.append(Action.DOWN_RIGHT)

        return actions

    def is_End(self, state):
        if state in self.diamonds:
            self.last_diamond = state.diamond
            self.diamonds.remove(state)
            self.last_cord = ()
            return True
        elif state.cords in self.keys:
            if (
                self.states[state.cords[0]][state.cords[1]].key
                not in self.collected_keys
            ):
                self.collected_keys.append(
                    self.states[state.cords[0]][state.cords[1]].key
                )
            self.keys.remove(state.cords)
            self.last_cord = ()
            return True
        return False

    def valueIteration(self, gamma, coverage_amount):
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                self.states[row][col].v = 0
        converge = False

        def Q(state, action):
            s = 0
            for item in self.succProbReward(state, action):
                s += item[0].v * item[1]
            return s

        while not converge:
            diff = 0
            for row in range(self.grid_height):
                for col in range(self.grid_width):
                    temp = self.states[row][col].v
                    self.states[row][col].v = self.states[row][col].r + gamma * max(
                        Q(self.states[row][col], action)
                        for action in self.get_actions(self.states[row][col])
                    )
                    diff = max(diff, abs(temp - self.states[row][col].v))

            if diff < coverage_amount:
                converge = True

    def get_policy(self):

        agent_obj = self.get_agent()
        agent = agent_obj.cords
        action = Action.NOOP
        max_val = -1000000
        c = ()
        for row in range(agent[0] - 1, agent[0] + 2):
            for col in range(agent[1] - 1, agent[1] + 2):
                if (
                    row != -1
                    and col != -1
                    and col != self.grid_width
                    and row != self.grid_height
                ):
                    if max_val < self.states[row][col].v:
                        if (
                            self.get_action(agent, (row, col))
                            in self.get_actions(agent_obj)
                            and (row, col) != self.last_cord
                        ):
                            action = self.get_action(agent, (row, col))
                            max_val = self.states[row][col].v
                            c = (row, col)
        if agent != c:
            self.last_cord = agent
        agent_obj.pi = action

    def get_action(self, agent, s):

        if agent[0] > s[0]:
            if agent[1] > s[1]:
                return Action.UP_LEFT
            elif agent[1] < s[1]:
                return Action.UP_RIGHT
            else:
                return Action.UP
        elif agent[0] < s[0]:
            if agent[1] > s[1]:
                return Action.DOWN_LEFT
            elif agent[1] < s[1]:
                return Action.DOWN_RIGHT
            else:
                return Action.DOWN
        else:
            if agent[1] < s[1]:
                return Action.RIGHT
            elif agent[1] > s[1]:
                return Action.LEFT
            else:
                return Action.NOOP

    def print_stuff(self):
        ds = []
        for d in self.diamonds:
            ds.append(d.cords)

        print("diamonds", ds)
        for i in range(self.grid_width):
            print("\t", i, end="")
        print()
        for i in range(self.grid_height):
            print(i, end="\t")
            for j in range(self.grid_width):
                print(f"{self.states[i][j].v : .2f}", end="\t")
            print()
        print()
        print("-----------------------------------------------------------")


if __name__ == "__main__":
    data = Agent().play()
    print("FINISH : ", data)
