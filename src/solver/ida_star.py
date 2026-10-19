import time

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
                if self._is_deadlock(destination, goals, walls):
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
    def _is_deadlock(self, box, goals, walls):
        if box in goals:
            return False

        row, column = box
        up = (row-1, column) in walls
        down = (row+1, column) in walls
        left = (row, column-1) in walls
        right = (row, column+1) in walls

        return (up or down) and (left or right)
