class Node:
    def __init__(self, action= None, parent=None, state=None):
        self.action= action
        self.parent= parent
        self.state = state

class  StackFrontier:
    def __init__(self):
        self.frontier = []
    def add(self,node):
        self.frontier.append(node)
    def contains_state(self,state):
        return any(state == node.state for node in self.frontier)
    def empty(self):
        return len(self.frontier)==0
    def remove(self):
        if self.empty():
            raise Exception("Empty")
        node = self.frontier.pop()
        return node
class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception("Empty")
        node = self.frontier[0]
        self.frontier = self.frontier[1:]
        return node


class Maze:
    def __init__(self, filename):
        self.filename = filename
        with open(filename,"r") as  file:
            content = file.read()

        if content.count("A") !=1:
            raise Exception("The Maze must contain 1 starting point")
        if content.count("B") !=1:
            raise Exception("The Maze must contain 1 goal ")
        content = content.splitlines()
        self.height = len(content)
        self.width = max((len(line)) for line in content)
        self.content = content

        for i in range(self.height):
            for j in range(self.width):
                if content[i][j] == "A":
                    self.start = (i,j)
                elif content[i][j] == "B":
                    self.goal = (i, j)
        self.solution = None
        self.path_cost = 0

    def print(self):
        solution = []
        if self.solution is not None:
            solution = self.solution[1]  # list of coordinates

        for i in range(self.height):
            for j in range(self.width):
                if (i, j) in solution and self.content[i][j] == " ":
                    print("*", end="")
                else:
                    print(self.content[i][j], end="")
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
        for action, (r,c) in candidates:
            try:
                if self.content[r][c] == " " or  self.content[r][c] == "B":
                    result.append((action, (r,c)))
            except IndexError:
                continue
        return result

    def GbfsFrontier(self,gbfs,h,child_pair):
        for i in range(len(gbfs)):
            if gbfs[i][1]>h:
                gbfs.insert(i,child_pair)
                return gbfs
        gbfs.append(child_pair)
        return gbfs
    
    def Heuristic(self,state):
        goal_x, goal_y = self.goal
        x, y = state
        return abs(goal_x - x) + abs(goal_y - y)

    def solve(self):
        node = Node(action=None, state= self.start, parent=None)
        frontier = StackFrontier()
        frontier.add(node)
        explored = set()

        while True:
            if frontier.empty():
                raise Exception("No solution")
            node = frontier.remove()
            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return
            gbfs = []
            explored.add(node.state)
            self.path_cost += 1
            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in explored:
                    child = Node(parent=node, action=action, state=state)
                    h = self.Heuristic(child.state)
                    gbfs = self.GbfsFrontier(gbfs,h,(child,h))
                if gbfs:
                    frontier.add(gbfs[0][0])



maze = Maze("Maze.txt")
maze.solve()
maze.print()


