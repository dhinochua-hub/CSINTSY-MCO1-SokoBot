import heapq
from collections import deque


class AStarSearch:
    DIRECTIONS = [(-1, 0, "u"), (1, 0, "d"), (0, -1, "l"), (0, 1, "r")]

# this function scans deadlock spaces (corners)
# using backwards bfs

    def scan_deadlock (self, width, height, walls, targets):
        visited_boxes = set()
        queue = deque()

        for target in targets: # put a box on every goal
            visited_boxes.add(target)
            queue.append(target)
        
        while queue: #pull the boxes
            row, col = queue.popleft()

            for new_row, new_col, char in self.DIRECTIONS:
                new_box = (row - new_row, col - new_col) # former position of the box before
                player = (row - 2 * new_row, col - 2 * new_col) # player position for pushing the box
                if not (0 <= new_box[0] < height and 0 <= new_box[0] < width) or new_box in walls:
                    continue
                if not (0 <= player[0] < height and 0 <= player[0] < width) or player in walls:
                    continue
                if new_box not in visited_boxes:
                    visited_boxes.add(new_box)
                    queue.append(new_box)

        deadlock_spaces = set()
        for row in range(height):
            for col in range (width):
                pos = (row,col)
                if pos not in walls and pos not in visited_boxes:
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

        deadlock_spaces = self.scan_deadlock(width, height, walls, targets)

        return player, crates_hash, targets, walls, deadlock_spaces

# this function computes the manhattan distance_cole using the zip function -> parallels x and y coordinates and packs it into 2 tuples
    def manhattan_distance(self, crates, targets):
        total_distance = 0 # stores the total of the minimum distance_coles between the crates and targets

        for crate in crates:
            if targets:
                total_distance += min (sum (abs(x-y) for x, y in zip(crate, target)) for target in targets) # check the manhattan distance_cole for every target and get the minimum distance_cole(nearest target)
        return total_distance
            

    def a_star (self, width, height, mapData, itemsData):

        # initialize the map and items
        player, crates, targets, walls, deadlock_spaces = self.start_game(width, height, mapData, itemsData)

        g = 0 # cost
        h = self.manhattan_distance(crates, targets) # heuristic
        f = g + h # heuristic function

        frontier= [] # open list, stores the frontier notes
        visited= {} # closted list, stores the visited nodes

        initial_hash = (player, crates) # stores the state data as a hash key
        heapq.heappush(frontier, (f, g, player, crates, "")) # push the starting state
        visited[initial_hash] = g # map the initial cost to the starting state

        while frontier:
            f, g, current_player, current_crates, path = heapq.heappop(frontier) # pop the state and mark it as the current state
            crates_set = set(current_crates) 

            if crates_set == targets: # if the goal has been reached
                print(f"Total Moves: {len(path)}")
                return path

            # find the next positions you can move into (next states)
            for row, col, move in self.DIRECTIONS:
                new_row, new_col = current_player[0] + row, current_player[1] + col

                # check out of bounds or if the path leads to a wall
                if not (0 <= new_row < height and 0 <= new_col < width) or (new_row, new_col) in walls:
                    continue

                next_crates = set(current_crates)

                # if the incoming path has a box on it, push it to the next tile by 1 step
                if (new_row, new_col) in crates_set:
                    crate_new_row, crate_new_col = new_row + row, new_col + col

                    # check out of bounds again and prune the deadlock

                    if not (0 <= crate_new_row < height and 0 <= crate_new_col < width) or (crate_new_row, crate_new_col) in crates_set or (crate_new_row, crate_new_col) in walls or (crate_new_row, crate_new_col) in deadlock_spaces:
                        continue

                    # update the list of box coordinates 
                    next_crates.remove((new_row, new_col))
                    next_crates.add((crate_new_row, crate_new_col))

                # convert it back to a tuple 
                next_crates = tuple(sorted(next_crates))
                # new player position will be in the tile before the new box position
                next_player = (new_row, new_col)

                # get the new state and heuristic function
                next_state_hash= (next_player, next_crates)
                next_g = g + 1
                next_h = self.manhattan_distance(next_crates, targets)
                next_f = next_g + next_h

                # if the next state hasn't been visited or if there is a cheaper cost going towards it
                if next_state_hash not in visited or next_g < visited[next_state_hash]:
                    visited[next_state_hash] = next_g # mark the new cost

                    heapq.heappush(frontier, (next_f, next_g, next_player, next_crates, path + move)) # push the new state to the frontier
        return ""

    


            




        
