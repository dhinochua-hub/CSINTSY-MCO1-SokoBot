from src.solver.ida_star import IDAStarSolver


class SokoBot:
    def solveSokobanPuzzle(self, width, height, mapData, itemsData):
        return IDAStarSolver().solve(width, height, mapData, itemsData)
