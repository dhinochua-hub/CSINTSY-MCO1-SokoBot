import time


class SokoBot:
    def solveSokobanPuzzle(self, width, height, mapData, itemsData):
        TIME_LIMIT = 15.0 # time limit stated in the specifications
        startTime = time.time()

        try:
            targets = set() # create a set of target positions
            walls = set() # create a set of the walls
            for y in range(height):
                for x in range(width):
                    if mapData[y][x] == '.': # check for target symbol
                        targets.add((y,x))
                    elif mapData[y][x] == '#': # check for wall symbol
                        walls.add((y,x)) 
                        
            player = None # unknown player position
            crates = []
            for y in range(height):
                for x in range(width):
                    if itemsData[y][x] == '@': # check for player symbol
                        player = (y,x) # store position of player
                    elif itemsData[y][x] == '$': # check for crate symbol
                        crates.append((y,x)) # add crate position
            initialCrates = tuple(sorted(crates)) # store initial position

            MOVES = ((0, 1), (1, 0), (0, -1), (-1, 0)) # movement offsets
            MOVE_CHARS = {(0, 1): 'r', (1, 0): 'd', (0, -1): 'l', (-1, 0): 'u'} # translated moves

            # NOTE: state[0] is player state and state[1] is crate state
            def isGoal(state): 
                return set(state[1] == targets) # check if crate set is in the target set
            
            def doMove(state, move):
                dy, dx = move
                py, px = state[0] # player coords
                ny, nx = py+dy, px+dx # new coords
                
                if not (0 <= ny < height and 0 <= nx < width): # check for bounds
                    return None
                if (ny, nx) in walls: # check for wall
                    return None
                
                crateSet = set(state[1]) # take crateSet from state

                if (ny, nx) in crateSet:
                    cy, cx = ny + dy, nx + dx # new crate coords with movement/push offset
                    if not (0 <= cy < height and 0 <= cx < width): # check for bounds
                        return None
                    if (cy, cx) in walls:
                        return None
                    if (cy, cx) in crateSet: # check if blocked by another crate
                        return None

                    crateSet.remove((ny, nx)) # remove crate from the cell
                    crateSet.add((cy, cx)) # move it to new position

                updatedCrates = tuple(sorted(crateSet)) # store updated crate state
                return ((ny, nx), updatedCrates) # return tuple of new states

            def dfsID(depthLimit): # main algorithm
                start = (player, initialCrates) # starting state
                stack = [(start), []] # state and path
                visited = {start} # set of visited states

                while stack:
                    if time.time() - startTime > TIME_LIMIT: # check if out of time
                        return None # return no solution if bot was thinking for too long :(

                    state, path = stack.pop()

                    if isGoal(state): # check if solution found
                        return path 

                    if len(path) < depthLimit: # only do til depth limit
                        for move in MOVES:
                            child = doMove(state, move) # next move
                            if child is not None and not visited: # if valid move and not yet visited
                                visited.add(child)
                                stack.append((child, path+[MOVE_CHARS[move]])) # add the new state and built path
                                
                return None # did not find solution



                            
        except Exception as ex:
            print(ex)
            
        return "lrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlr"

    