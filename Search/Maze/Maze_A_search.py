import heapq

class Node:
    def __init__(self, state, parent=None, action=None, g=0, h=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g  # cost from start
        self.h = h  # estimated cost to goal

    def f(self):
        return self.g + self.h

    def __lt__(self, other):  # for heapq
        return self.f() < other.f()


class PriorityQueueFrontier:
    def __init__(self):
        self.elements = []

    def add(self, node):
        heapq.heappush(self.elements, (node.f(), node))

    def contains_state(self, state):
        return any(node.state == state for _, node in self.elements)

    def empty(self):
        return len(self.elements) == 0

    def remove(self):
        if self.empty():
            raise Exception("Empty frontier")
        return heapq.heappop(self.elements)[1]


class Maze:
    def __init__(self, filename):
        with open(filename, "r") as file:
            contents = file.read()

        if contents.count("A") != 1:
            raise Exception("Maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("Maze must have exactly one goal")

        self.contents = contents.splitlines()
        self.height = len(self.contents)
        self.width = max(len(line) for line in self.contents)

        self.start = None
        self.goal = None
        for i in range(self.height):
            for j in range(self.width):
                if self.contents[i][j] == "A":
                    self.start = (i, j)
                elif self.contents[i][j] == "B":
                    self.goal = (i, j)

        self.solution = None
        self.path_cost = 0

    def print(self):
        solution = self.solution[1] if self.solution else []

        for i in range(self.height):
            for j in range(self.width):
                if (i, j) in solution and self.contents[i][j] == " ":
                    print("*", end="")
                else:
                    print(self.contents[i][j], end="")
            print()
        print("Path cost:", self.path_cost)

    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1)),
        ]
        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width:
                if self.contents[r][c] == " " or self.contents[r][c] == "B":
                    result.append((action, (r, c)))
        return result

    def heuristic(self, state):
        # Manhattan distance
        return abs(state[0] - self.goal[0]) + abs(state[1] - self.goal[1])

    def solve(self):
        start_node = Node(state=self.start, g=0, h=self.heuristic(self.start))
        frontier = PriorityQueueFrontier()
        frontier.add(start_node)
        explored = set()

        while not frontier.empty():
            node = frontier.remove()

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            explored.add(node.state)
            self.path_cost += 1

            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in explored:
                    g = node.g + 1
                    h = self.heuristic(state)
                    child = Node(state=state, parent=node, action=action, g=g, h=h)
                    frontier.add(child)


# Usage:
maze = Maze("Maze.txt")
maze.solve()
maze.print()
