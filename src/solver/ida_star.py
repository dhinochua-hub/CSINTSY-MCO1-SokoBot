import time
from collections import deque 
class IDAStarSolver:

    DIRECTIONS = (
        (-1, 0, "u"),
        (1, 0, "d"),
        (0, -1, "l"),
        (0, 1, "r"),
    )

    def solve(self, width, height, map_data, items_data):
        walls = {
            (row, column)
            for row in range(height)
            for column in range(width)
            if map_data[row][column] == "#"
        }
        goals = frozenset(
            (row, column)
            for row in range(height)
            for column in range(width)
            if map_data[row][column] == "."
        )
        boxes = frozenset(
            (row, column)
            for row in range(height)
            for column in range(width)
            if items_data[row][column] == "$"
        )
        player = next(
            (
                (row, column)
                for row in range(height)
                for column in range(width)
                if items_data[row][column] == "@"
            ),
            None,
        )

        if player is None or len(boxes) != len(goals) or boxes <= goals:
            return ""
        self._is_deadlock = self._is_deadlock(width, height, goals, walls)

        deadline = time.perf_counter() + 14.5
        threshold = self._heuristic(boxes, goals)
        path = []

        while time.perf_counter() < deadline:
            result = self._search(
                player, boxes, goals, walls, threshold, 0, path, set(), deadline
            )
            if result is True:
                return "".join(path)
            if result == float("inf"):
                return ""
            threshold = result
        return ""

    def _search(
        self,
        player,
        boxes,
        goals,
        walls,
        threshold,
        cost,
        path,
        active_states,
        deadline,
    ):
        if time.perf_counter() >= deadline:
            return float("inf")
        if boxes <= goals:
            return True

        estimate = cost + self._heuristic(boxes, goals)
        if estimate > threshold:
            return estimate

        state = (player, boxes)
        if state in active_states:
            return float("inf")
        active_states.add(state)

        reachable, walking_paths = self._reachable(player, boxes, walls)

        candidates = []
        for box in boxes:
            for row_delta, column_delta, direction in self.DIRECTIONS:
                stand = (box[0] - row_delta, box[1] - column_delta)
                destination = (box[0] + row_delta, box[1] + column_delta)
                if stand not in reachable:
                    continue
                if destination in walls or destination in boxes:
                    continue
                

                walking_path = walking_paths[stand]
                new_boxes = (boxes - {box}) | {destination}
                move_cost = len(walking_path) + 1
                candidates.append(
                    (
                        cost + move_cost + self._heuristic(new_boxes, goals),
                        walking_path,
                        direction,
                        box,
                        new_boxes,
                        move_cost,
                    )
                )

        candidates.sort(key=lambda candidate: candidate[0])
        next_threshold = float("inf")
        for _, walking_path, direction, box, new_boxes, move_cost in candidates:
            path.extend(walking_path)
            path.append(direction)
            result = self._search(
                box,
                frozenset(new_boxes),
                goals,
                walls,
                threshold,
                cost + move_cost,
                path,
                active_states,
                deadline,
            )
            if result is True:
                return True
            del path[-(len(walking_path) + 1) :]
            next_threshold = min(next_threshold, result)

        active_states.remove(state)
        return next_threshold

    def _reachable(self, player, boxes, walls):
        walking_paths = {player: []}
        queue = [player]
        head = 0
        while head < len(queue):
            current = queue[head]
            head += 1
            for dr, dc, direction in self.DIRECTIONS:
                next = (current[0] + dr, current[1] + dc)
                if next in walking_paths:
                    continue
                if next in walls or next in boxes:
                    continue
                walking_paths[next] = walking_paths[current] + [direction]
                queue.append(next)

        return set(walking_paths), walking_paths
            
    def _heuristic(self, boxes, goals):
        # Uses Manhattan Distance
        if not boxes or not goals:
            return 0
        total_distance = 0

        for box in boxes:
            total_distance += min(abs (box[0] - goal[0]) + abs (box[1] - goal[1])
                                    for goal in goals)
        return total_distance
    def _is_deadlock(self, height, width, goals, walls):
        visited_boxes = set()
        queue = deque()

        for goal in goals: # put a box on every goal
            visited_boxes.add(goal)
            queue.append(goal)
        
        while queue: #pull the boxes
            row, col = queue.popleft()

            for new_row, new_col, char in self.DIRECTIONS:
                new_box = (row - new_row, col - new_col) # former position of the box before it got pushed
                player = (row - 2 * new_row, col - 2 * new_col) # player position for pulling the box
                if not (0 <= new_box[0] < height and 0 <= new_box[1] < width) or new_box in walls:
                    continue
                if not (0 <= player[0] < height and 0 <= player[1] < width) or player in walls:
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