import heapq
import time
from collections import deque


class AStarSearch:
    DIRECTIONS = [(-1, 0, "u"), (1, 0, "d"), (0, -1, "l"), (0, 1, "r")]
    TIME_LIMIT = 14 # total thinking time, stays under the 15 second limit 
    A_STAR_TIME = 1.5 # thinking time for A* before switching to GBFS
    greedy = False # True makes the search ignore path cost and only follow the heuristic (GBFS)

# pulls a box backwards from every target using bfs
# the number of pulls to reach a space is the least number of pushes needed to bring a box from that space to the target

    def scan_push_distances(self, width, height, walls, targets):
        push_distances = {} # stores the distances of every space for each target

        for target in targets: # put a box on the target
            distances = {target: 0}
            queue = deque([target])

            while queue: # pull the box
                row, col = queue.popleft()

                for new_row, new_col, char in self.DIRECTIONS:
                    new_box = (row - new_row, col - new_col) # former position of the box before
                    player = (row - 2 * new_row, col - 2 * new_col) # player position for pushing the box
                    if not (0 <= new_box[0] < height and 0 <= new_box[1] < width) or new_box in walls:
                        continue
                    if not (0 <= player[0] < height and 0 <= player[1] < width) or player in walls:
                        continue
                    if new_box not in distances:
                        distances[new_box] = distances[(row, col)] + 1
                        queue.append(new_box)

            push_distances[target] = distances
        return push_distances

# this function scans deadlock spaces 
# using backwards bfs 

    def scan_deadlock (self, width, height, walls, push_distances):
        deadlock_spaces = set()
        for row in range(height):
            for col in range (width):
                pos = (row,col)
                if pos not in walls and all(pos not in distances for distances in push_distances.values()):
                    deadlock_spaces.add(pos)
        return deadlock_spaces


# this function builds the starting locations of the crates, player and goal

    def start_game(self, width, height, mapData, itemsData):
        player = None
        crates = set()
        walls = set()
        targets = set()


        for row in range(height):
            for col in range(width):
                item = itemsData[row][col]
                map = mapData[row][col]

                if item =="@":
                    player = (row, col)
                elif item == "$":
                    crates.add((row,col))

                if map == "#":
                    walls.add((row,col))
                elif map == ".":
                    targets.add((row,col))
        crates_hash = tuple(sorted(crates))

        self.push_distances = self.scan_push_distances(width, height, walls, targets)
        deadlock_spaces = self.scan_deadlock(width, height, walls, self.push_distances)

        # stores the distance from each space to its nearest target so the heuristic doesn't have to search for it every time
        self.nearest_target = {
            (row, col): min((distances.get((row, col), float("inf")) for distances in self.push_distances.values()), default=float("inf"))
            for row in range(height)
            for col in range(width)
        }

        return player, crates_hash, targets, walls, deadlock_spaces

# computes the heuristic using the push distances instead of the manhattan distance so that the walls are taken into account
# every crate needs to reach a target and every target needs a crate, so the bigger of the two totals is used
# every push moves a crate by only one space

    def push_distance(self, crates):
        if crates in self.heuristic_cache:
            return self.heuristic_cache[crates]

        crate_total = 0 # stores the total of the distances from each crate to its nearest target
        for crate in crates:
            crate_total += self.nearest_target[crate]

        target_total = 0 # stores the total of the distances from each target to its nearest crate
        for distances in self.push_distances.values():
            target_total += min(distances.get(crate, float("inf")) for crate in crates)

        total_distance = max(crate_total, target_total)
        self.heuristic_cache[crates] = total_distance
        return total_distance

# finds every space the player can walk to without pushing a crate using bfs
# each space stores the space before it and the move used, so the walking path can be rebuilt

    def reachable(self, player, crates_set, walls):
        parents = {player: None}
        queue = deque([player])

        while queue:
            current = queue.popleft()
            for row, col, move in self.DIRECTIONS:
                next_space = (current[0] + row, current[1] + col)
                if next_space in parents or next_space in walls or next_space in crates_set:
                    continue
                parents[next_space] = (current, move)
                queue.append(next_space)
        return parents

# rebuilds the walking path to a space by following the stored spaces backwards

    def walking_path(self, parents, space):
        path = []
        while parents[space] is not None:
            space, move = parents[space]
            path.append(move)
        path.reverse()
        return "".join(path)

# checks if the pushed crate is stuck in a 2x2 block of walls and crates
# it is a deadlock unless all of them are on targets

    def is_frozen(self, crate, crates_set, walls, targets):
        row, col = crate
        for row_offset in (-1, 0):
            for col_offset in (-1, 0):
                block = [(row + row_offset + r, col + col_offset + c) for r in (0, 1) for c in (0, 1)]
                if all(space in walls or space in crates_set for space in block):
                    if any(space in crates_set and space not in targets for space in block):
                        return True
        return False

# rebuilds the whole solution by following the states back to the start

    def build_path(self, came_from, state_hash):
        moves = []
        while came_from[state_hash] is not None:
            state_hash, step = came_from[state_hash]
            moves.append(step)
        moves.reverse()
        return "".join(moves)


# A* orders the frontier by f = g + h
# GBFS orders it by h, and states with the same h are broken by the cheaper cost g

    def priority(self, g, h):
        if self.greedy:
            return (h, g)
        return g + h

# checks if a state can never be solved, used by other searches to add their own deadlock checks

    def is_dead_state(self, parents, crates_set):
        return False

# extra next states made of several pushes at once, used by other searches to add their own macro moves

    def macro_pushes(self, player, crates_set, parents, walls, targets, deadlock_spaces):
        return []

# runs A* first since it finds the shortest solutions,
# then switches to GBFS for the remaining time if A* takes too long

    def a_star (self, width, height, mapData, itemsData):
        start_time = time.perf_counter()

        # initialize the map and items
        player, crates, targets, walls, deadlock_spaces = self.start_game(width, height, mapData, itemsData)
        if player is None or len(crates) != len(targets):
            return ""
        self.heuristic_cache = {}

        self.greedy = False
        path = self.search(player, crates, targets, walls, deadlock_spaces, start_time + self.A_STAR_TIME)
        if path is None: # A* ran out of time
            self.greedy = True
            path = self.search(player, crates, targets, walls, deadlock_spaces, start_time + self.TIME_LIMIT)
        return path or ""

# the search loop shared by A* and GBFS
# returns the solution, "" if there is no solution, or None if it ran out of time

    def search(self, player, crates, targets, walls, deadlock_spaces, deadline):
        g = 0 # cost, counts every move of the player (walking and pushing)
        h = self.push_distance(crates) # heuristic
        f = self.priority(g, h) # heuristic function

        frontier= [] # open list, stores the frontier notes
        visited= {} # stores the cheapest cost found for each state
        closed = {} # closed list, stores every space of the player areas already expanded for each crate layout
        came_from = {} # stores the previous state and the moves taken to get to each state
        counter = 0 # breaks ties between states with the same f and h

        initial_hash = (player, crates) # stores the state data as a hash key
        heapq.heappush(frontier, (f, h, counter, g, player, crates)) # push the starting state
        visited[initial_hash] = g # map the initial cost to the starting state
        came_from[initial_hash] = None

        while frontier:
            if time.perf_counter() > deadline: # stop if the bot is thinking for too long
                return None

            f, h, _, g, current_player, current_crates = heapq.heappop(frontier) # pop the state and mark it as the current state
            current_hash = (current_player, current_crates)
            if g > visited[current_hash]: # skip the state if a cheaper way to it was found
                continue

            # the player standing anywhere in the same area counts as the same state,
            # so skip it if the area of the player was already expanded with these crates
            closed_spaces = closed.setdefault(current_crates, set())
            if current_player in closed_spaces:
                continue

            crates_set = set(current_crates)
            parents = self.reachable(current_player, crates_set, walls)
            closed_spaces.update(parents)

            if crates_set == targets: # if the goal has been reached
                return self.build_path(came_from, current_hash)
            if self.is_dead_state(parents, crates_set): # skip states that can never be solved
                continue

            next_states = self.macro_pushes(current_player, crates_set, parents, walls, targets, deadlock_spaces)

            # every push the player can walk to is a next state
            for crate in current_crates:
                for row, col, move in self.DIRECTIONS:
                    stand = (crate[0] - row, crate[1] - col) # the player has to stand behind the crate
                    crate_new = (crate[0] + row, crate[1] + col) # where the crate ends up

                    # check if the player can get behind the crate, and prune walls, crates and deadlocks
                    if stand not in parents:
                        continue
                    if crate_new in walls or crate_new in crates_set or crate_new in deadlock_spaces:
                        continue

                    # update the list of crate coordinates
                    next_crates_set = set(crates_set)
                    next_crates_set.remove(crate)
                    next_crates_set.add(crate_new)
                    if self.is_frozen(crate_new, next_crates_set, walls, targets):
                        continue

                    # convert it back to a tuple
                    next_crates = tuple(sorted(next_crates_set))
                    # new player position will be where the crate was
                    next_player = crate
                    if next_crates in closed and next_player in closed[next_crates]:
                        continue

                    walk = self.walking_path(parents, stand)
                    next_states.append((next_player, next_crates, walk + move))

            for next_player, next_crates, moves in next_states:
                # get the new state and heuristic function
                next_h = self.push_distance(next_crates)
                if next_h == float("inf"):
                    continue
                next_g = g + len(moves)
                next_f = self.priority(next_g, next_h)
                next_state_hash = (next_player, next_crates)

                # if the next state hasn't been visited or if there is a cheaper cost going towards it
                if next_state_hash not in visited or next_g < visited[next_state_hash]:
                    visited[next_state_hash] = next_g # mark the new cost
                    came_from[next_state_hash] = (current_hash, moves)

                    counter += 1
                    heapq.heappush(frontier, (next_f, next_h, counter, next_g, next_player, next_crates)) # push the new state to the frontier
        return ""
