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
                            
        except Exception as ex:
            print(ex)
            
        return "lrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlrlr"