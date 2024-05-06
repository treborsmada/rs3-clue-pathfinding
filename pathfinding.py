from mapsection import *
import queue as qqueue
from itertools import count

move_list = ["walk", "surge", "bd", "bd_surge", "surge_bd", "bd_escape", "escape_bd", "surge_walk", "bd_walk",
             "escape_walk"]


class State:
    def __init__(self, pos: tuple, direction: int, secd: int = 0, scd: int = 0, ecd: int = 0, bdcd: int = 0,
                 wait_time: int = 0):
        self.pos = pos
        self.direction = direction
        self.secd = secd
        self.scd = scd
        self.ecd = ecd
        self.bdcd = bdcd
        self.wait_time = wait_time

    def __eq__(self, other):
        if isinstance(other, State):
            return self.pos == other.pos and self.direction == other.direction and self.secd == other.secd \
                and self.scd == other.scd and self.ecd == other.ecd and self.bdcd == other.bdcd \
                and self.wait_time == other.wait_time
        return False

    def __hash__(self):
        return hash((self.pos, self.direction, self.secd, self.scd, self.ecd, self.bdcd, self.wait_time))

    def update(self):
        new_secd = self.secd
        new_scd = self.scd
        new_ecd = self.ecd
        new_bdcd = self.bdcd
        new_wait_time = self.wait_time
        if not new_secd == 0:
            new_secd = new_secd - 1
        if not new_scd == 0:
            new_scd = new_scd - 1
        if not new_ecd == 0:
            new_ecd = new_ecd - 1
        if not new_bdcd == 0:
            new_bdcd = new_bdcd - 1
        if not new_wait_time == 0:
            new_wait_time = new_wait_time - 1
        return State(self.pos, self.direction, new_secd, new_scd, new_ecd, new_bdcd, new_wait_time)

    def move(self, x: int, y: int, direction: int):
        return State((x, y), direction, self.secd, self.scd, self.ecd, self.bdcd, self.wait_time)

    def surge(self, map_section: MapSection):
        new_pos = map_section.surge_range(self.pos[0], self.pos[1], self.direction)
        if new_pos is None:
            return None
        if self.secd == 0:
            if self.scd < 2:
                return State(new_pos, self.direction, 17, 2, 17, self.bdcd, self.wait_time)
            else:
                return State(new_pos, self.direction, 17, self.scd, 17, self.bdcd, self.wait_time)
        elif self.scd == 0:
            if self.secd < 2:
                return State(new_pos, self.direction, 2, 17, 2, self.bdcd, self.wait_time)
            else:
                return State(new_pos, self.direction, self.secd, 17, self.ecd, self.bdcd, self.wait_time)
        else:
            print(self.pos)
            raise Exception("Surge is on cooldown")

    def escape(self, map_section: MapSection):
        new_pos = map_section.escape_range(self.pos[0], self.pos[1], self.direction)
        if new_pos is None:
            return None
        if self.secd == 0:
            if self.ecd < 2:
                return State(new_pos, self.direction, 17, 17, 2, self.bdcd, self.wait_time)
            else:
                return State(new_pos, self.direction, 17, 17, self.ecd, self.bdcd, self.wait_time)
        elif self.ecd == 0:
            if self.secd < 2:
                return State(new_pos, self.direction, 2, 2, 17, self.bdcd, self.wait_time)
            else:
                return State(new_pos, self.direction, self.secd, self.scd, 17, self.bdcd, self.wait_time)
        else:
            print(self.pos)
            raise Exception("Escape is on cooldown")

    def bd(self, x: int, y: int, direction: int):
        if self.bdcd == 0:
            return State((x, y), direction, self.secd, self.scd, self.ecd, 17, self.wait_time)

    def can_bd(self):
        return self.bdcd == 0

    def can_surge(self):
        return self.secd == 0 or self.scd == 0

    def can_escape(self):
        return self.secd == 0 or self.ecd == 0

    def min_cd(self):
        cds = [(self.secd, "se"), (self.scd, "s"), (self.ecd, "e"), (self.bdcd, "bd")]
        cds = sorted(cds, key=lambda tup: tup[0])
        return cds[0]


def reconstruct_path(cameFrom: dict, current: State):
    total_path = [current]
    moves = []
    while current in cameFrom:
        current, move = cameFrom[current]
        total_path = [current] + total_path
        if len(moves) == 0 or move == "walk" or move == "wait":
            moves = [move] + moves
        else:
            moves[0] = move + " " + moves[0]
    return total_path, moves


def walk_path(start: tuple, end: tuple, map_section: MapSection) -> list:
    path = [start]
    if start == end:
        return path
    visited = {start}
    queue = [path]
    while queue:
        path = queue.pop(0)
        node = path[-1]
        adj = map_section.walk_range(node[0], node[1])[0]
        for tile in adj:
            if tile not in visited:
                new_path = list(path)
                new_path.append(tile)
                queue.append(new_path)
                visited.add(tile)
                if tile == end:
                    return new_path


def a_star_end_buffer(start_state: State, end: tuple, map_section: MapSection, heuristic) -> tuple:
    unique = count()
    queue = qqueue.PriorityQueue()
    queue.put((0, next(unique), start_state))
    g_score = dict()
    g_score[start_state] = 0
    came_from = dict()
    count_num = 0
    heuristic_data = np.load("HeuristicData/l_infinity_cds.npy")
    while not queue.empty():
        current_node = queue.get()[2]
        count_num += 1
        # check if at end
        if end[0] - 1 <= current_node.pos[0] <= end[0] + 1 and end[1] - 1 <= current_node.pos[1] <= end[1] + 1:
            print(count_num)
            return reconstruct_path(came_from, current_node)
        # wait
        tentative_g_score = g_score[current_node] + 1
        next_node = current_node.update()
        if next_node not in g_score or tentative_g_score < g_score[next_node]:
            came_from[next_node] = current_node, "wait"
            g_score[next_node] = tentative_g_score
            f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
            queue.put((f_score, -next(unique), next_node))
        # walk
        walk_adj = map_section.walk_range(current_node.pos[0], current_node.pos[1])
        for i in range(len(walk_adj[0])):
            next_node = current_node.move(walk_adj[0][i][0], walk_adj[0][i][1], walk_adj[1][i])
            next_node = next_node.update()
            if next_node not in g_score or tentative_g_score < g_score[next_node]:
                came_from[next_node] = current_node, "walk"
                g_score[next_node] = tentative_g_score
                f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
                queue.put((f_score, -next(unique), next_node))
        # surge
        tentative_g_score = g_score[current_node]
        if current_node.can_surge():
            next_node = current_node.surge(map_section)
            if next_node is not None:
                if next_node not in g_score or g_score[current_node] < g_score[next_node]:
                    came_from[next_node] = current_node, "surge"
                    g_score[next_node] = tentative_g_score
                    f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
                    queue.put((f_score, -next(unique), next_node))
        # bladed dive
        if current_node.can_bd():
            bd_adj = map_section.bd_range(current_node.pos[0], current_node.pos[1])
            for i in range(len(bd_adj[0])):
                next_node = current_node.bd(bd_adj[0][i][0], bd_adj[0][i][1], bd_adj[1][i])
                if next_node not in g_score or tentative_g_score < g_score[next_node]:
                    came_from[next_node] = current_node, "bd"
                    g_score[next_node] = tentative_g_score
                    f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
                    queue.put((f_score, -next(unique), next_node))
        # escape
        if current_node.can_escape():
            next_node = current_node.escape(map_section)
            if next_node is not None:
                if next_node not in g_score or tentative_g_score < g_score[next_node]:
                    came_from[next_node] = current_node, "escape"
                    g_score[next_node] = tentative_g_score
                    f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
                    queue.put((f_score, -next(unique), next_node))

def a_star_end_buffer_se_tick_loss(start_state: State, end: tuple, map_section: MapSection, heuristic) -> tuple:
    unique = count()
    queue = qqueue.PriorityQueue()
    queue.put((0, next(unique), start_state))
    g_score = dict()
    g_score[start_state] = 0
    came_from = dict()
    heuristic_data = np.load("HeuristicData/l_infinity_cds.npy")
    while not queue.empty():
        current_node = queue.get()[2]
        # check if at end
        if end[0] - 1 <= current_node.pos[0] <= end[0] + 1 and end[1] - 1 <= current_node.pos[1] <= end[1] + 1:
            return reconstruct_path(came_from, current_node)
        # wait
        tentative_g_score = g_score[current_node] + 1
        next_node = current_node.update()
        if next_node not in g_score or tentative_g_score < g_score[next_node]:
            came_from[next_node] = current_node, "wait"
            g_score[next_node] = tentative_g_score
            f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
            queue.put((f_score, -next(unique), next_node))
        # walk
        walk_adj = map_section.walk_range(current_node.pos[0], current_node.pos[1])
        for i in range(len(walk_adj[0])):
            next_node = current_node.move(walk_adj[0][i][0], walk_adj[0][i][1], walk_adj[1][i])
            next_node = next_node.update()
            if next_node not in g_score or tentative_g_score < g_score[next_node]:
                came_from[next_node] = current_node, "walk"
                g_score[next_node] = tentative_g_score
                f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
                queue.put((f_score, -next(unique), next_node))
        # surge
        if current_node.can_surge():
            next_node = current_node.surge(map_section)
            if next_node is not None:
                next_node = next_node.update()
                if next_node not in g_score or g_score[current_node] < g_score[next_node]:
                    came_from[next_node] = current_node, "surge"
                    g_score[next_node] = tentative_g_score
                    f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
                    queue.put((f_score, -next(unique), next_node))
        # escape
        if current_node.can_escape():
            next_node = current_node.escape(map_section)
            if next_node is not None:
                next_node = next_node.update()
                if next_node not in g_score or tentative_g_score < g_score[next_node]:
                    came_from[next_node] = current_node, "escape"
                    g_score[next_node] = tentative_g_score
                    f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
                    queue.put((f_score, -next(unique), next_node))
        # bladed dive
        tentative_g_score = g_score[current_node]
        if current_node.can_bd():
            bd_adj = map_section.bd_range(current_node.pos[0], current_node.pos[1])
            for i in range(len(bd_adj[0])):
                next_node = current_node.bd(bd_adj[0][i][0], bd_adj[0][i][1], bd_adj[1][i])
                if next_node not in g_score or tentative_g_score < g_score[next_node]:
                    came_from[next_node] = current_node, "bd"
                    g_score[next_node] = tentative_g_score
                    f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
                    queue.put((f_score, -next(unique), next_node))

def a_star(start_state: State, end: tuple, map_section: MapSection, heuristic) -> tuple:
    unique = count()
    queue = qqueue.PriorityQueue()
    queue.put((0, next(unique), start_state))
    g_score = dict()
    g_score[start_state] = 0
    came_from = dict()
    heuristic_data = np.load("HeuristicData/l_infinity_cds.npy")
    while not queue.empty():
        current_node = queue.get()[2]
        # check if at end
        if end[0] == current_node[0] and end[1] == current_node[1]:
            return reconstruct_path(came_from, current_node)
        # wait
        tentative_g_score = g_score[current_node] + 1
        next_node = current_node.update()
        if next_node not in g_score or tentative_g_score < g_score[next_node]:
            came_from[next_node] = current_node, "wait"
            g_score[next_node] = tentative_g_score
            f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
            queue.put((f_score, -next(unique), next_node))
        # walk
        walk_adj = map_section.walk_range(current_node.pos[0], current_node.pos[1])
        for i in range(len(walk_adj[0])):
            next_node = current_node.move(walk_adj[0][i][0], walk_adj[0][i][1], walk_adj[1][i])
            next_node = next_node.update()
            if next_node not in g_score or tentative_g_score < g_score[next_node]:
                came_from[next_node] = current_node, "walk"
                g_score[next_node] = tentative_g_score
                f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
                queue.put((f_score, -next(unique), next_node))
        # surge
        tentative_g_score = g_score[current_node]
        if current_node.can_surge():
            next_node = current_node.surge(map_section)
            if next_node is not None:
                if next_node not in g_score or g_score[current_node] < g_score[next_node]:
                    came_from[next_node] = current_node, "surge"
                    g_score[next_node] = tentative_g_score
                    f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
                    queue.put((f_score, -next(unique), next_node))
        # bladed dive
        if current_node.can_bd():
            bd_adj = map_section.bd_range(current_node.pos[0], current_node.pos[1])
            for i in range(len(bd_adj[0])):
                next_node = current_node.bd(bd_adj[0][i][0], bd_adj[0][i][1], bd_adj[1][i])
                if next_node not in g_score or tentative_g_score < g_score[next_node]:
                    came_from[next_node] = current_node, "bd"
                    g_score[next_node] = tentative_g_score
                    f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
                    queue.put((f_score, -next(unique), next_node))
        # escape
        if current_node.can_escape():
            next_node = current_node.escape(map_section)
            if next_node is not None:
                if next_node not in g_score or tentative_g_score < g_score[next_node]:
                    came_from[next_node] = current_node, "escape"
                    g_score[next_node] = tentative_g_score
                    f_score = tentative_g_score + heuristic(next_node, end, heuristic_data)
                    queue.put((f_score, -next(unique), next_node))

# heuristic functions
def l_infinity(state: State, end: tuple) -> float:
    distance = max(abs(state.pos[0] - end[0]), abs(state.pos[1] - end[1])) - 1
    if distance <= 0:
        return 0
    return distance / 22


def l_infinity_cds(state: State, end: tuple, data) -> float:
    distance = max(abs(state.pos[0] - end[0]), abs(state.pos[1] - end[1])) - 1
    return data[distance, state.secd, state.scd, state.ecd, state.bdcd]


def zero_heuristic(state: State, end: tuple) -> float:
    return 0
