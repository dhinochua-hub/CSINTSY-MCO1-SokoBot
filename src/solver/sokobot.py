import time
from . import aStarSearch


class SokoBot:
    def solveSokobanPuzzle(self, width, height, mapData, itemsData):

        solver = aStarSearch.AStarSearch()
        return solver.a_star(width, height, mapData, itemsData)
