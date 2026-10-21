from src.solver.ida_star import AStarSearch


class SokoBot:
    def solveSokobanPuzzle(self, width, height, mapData, itemsData):
        return AStarSearch().a_star(width, height, mapData, itemsData)
