import time
import heapq


class AStarSearch:

    def scan_deadlock (self, width, height, mapData, itemsData, targets):
        target = set(targets)
        deadlock_spaces = set()

        for row in range(height):
            for col in range(width):
                if mapData[row][col] in ("#", 1) or (row,col) in target:
                    continue

                up = (row == 0) or mapData[row-1][col] in ("#", 1)
                down = (row == height - 1) or mapData [row + 1][col] in ("#", 1)
                left = (col == 0) or mapData[row][col-1] in ("#", 1)
                right = (col == width-1) or mapData[row][col+1] in ("#", 1)

                if (up and left) or (up and right) or (down and left) or (down and right):
                    deadlock_spaces.add((row,col))
        return deadlock_spaces

    def start_game(self, width, height, mapData, itemsData):
        player = next(
            ((row, col) for row, cells in enumerate(itemsData)
             for col, cell in enumerate(cells) if cell == "@" ),
            (0, 0),
        )
        boxes = sorted((row, col) for row in range(height) for col in range(width) if itemsData[row][col] == "$")
        targets = [(row, col) for row in range(height) for col in range(width) if mapData[row][col] == "."]

        deadlock_spaces = self.scan_deadlock(width, height, mapData, itemsData, targets)
        return player, tuple(boxes), tuple(targets), deadlock_spaces

    def manhattan_distance(self, boxes, targets):
        hx = 0

        for box in boxes:
            if targets:
                dist = min (abs (box[0] - target[0]) + abs (box[1] - target[1]) for target in targets)
            hx += dist
        return hx

    def a_star (self, width, height, mapData, itemsData):

        player, boxes, targets, deadlock_spaces = self.start_game(width, height, mapData, itemsData)

        g = 0
        h = self.manhattan_distance(boxes, targets)
        f = g + h

        open_list = []
        closed_list = {}

        initial_hash = (player, boxes)
        heapq.heappush(open_list, (f, g, player, boxes, ""))
        closed_list[initial_hash] = g

        target = set(targets)
        possible_moves = [(-1,0, "U"), (1,0, "D"), (0,-1,"L"), (0,1,"R")]

        while open_list:
            f, g, playerpos, boxespos, path = heapq.heappop(open_list)

            if set(boxespos) == target:
                print(f"Total Moves: {len(path)}")
                return path

            boxes_set = set(boxespos)


            for dr, dc, move_char in possible_moves:
                nr, nc = playerpos[0] + dr, playerpos[1] + dc

                if not (0 <= nr < height and 0 <= nc < width) or mapData[nr][nc] in ("#",1):
                    continue

                next_boxes = list(boxespos)

                if (nr, nc) in boxes_set:
                    box_nr, box_nc = nr + dr, nc + dc

                    if not (0 <= box_nr < height and 0 <= box_nc < width) or mapData[box_nr][box_nc] in ("#", 1) or (box_nr, box_nc) in boxes_set:
                        continue

                    if (box_nr, box_nc) in deadlock_spaces:
                        continue

                    next_boxes.remove((nr, nc))
                    next_boxes.append((box_nr, box_nc))

                next_boxes = tuple(sorted(next_boxes))
                next_player = (nr, nc)
                next_state_hash= (next_player, next_boxes)
                next_g = g + 1
                next_h = self.manhattan_distance (next_boxes, targets)
                next_f = next_g + next_h

                if next_state_hash not in closed_list or next_g < closed_list[next_state_hash]:
                    closed_list[next_state_hash] = next_g

                    heapq.heappush(open_list, (next_f, next_g, next_player, next_boxes, path + move_char))
        return ""

    


            




        

