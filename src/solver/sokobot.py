import time
from . import aStarSearch

class SokoBot:
    def solveSokobanPuzzle(self, width, height, mapData, itemsData):
        TIME_LIMIT = 15.0
        start_time = time.time()
        solver = aStarSearch.AStarSearch()
        return solver.a_star(width, height, mapData, itemsData)

