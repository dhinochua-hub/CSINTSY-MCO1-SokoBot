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

        deadline = time.perf_counter() + 9.5
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
        queue = [player]
        paths = {player: ""}
        for current in queue:
            for row_delta, column_delta, direction in self.DIRECTIONS:
                target = (current[0] + row_delta, current[1] + column_delta)
                if target in paths or target in walls or target in boxes:
                    continue
                paths[target] = paths[current] + direction
                queue.append(target)
        return paths.keys(), paths

    def _heuristic(self, boxes, goals):
        """Return the minimum Manhattan-distance box-to-goal assignment."""
        if not boxes:
            return 0

        boxes = tuple(boxes)
        goals = tuple(goals)
        scores = {0: 0}
        for box in boxes:
            next_scores = {}
            for used_goals, score in scores.items():
                for goal_index, goal in enumerate(goals):
                    bit = 1 << goal_index
                    if used_goals & bit:
                        continue
                    mask = used_goals | bit
                    distance = abs(box[0] - goal[0]) + abs(box[1] - goal[1])
                    next_scores[mask] = min(
                        next_scores.get(mask, float("inf")),
                        score + distance,
                    )
            scores = next_scores
        return min(scores.values(), default=float("inf"))

    def _is_deadlock(self, box, goals, walls):
        if box in goals:
            return False

        row, column = box
        vertical_wall = (
            (row - 1, column) in walls or (row + 1, column) in walls
        )
        horizontal_wall = (
            (row, column - 1) in walls or (row, column + 1) in walls
        )
        if vertical_wall and not any(goal[1] == column for goal in goals):
            return True
        if horizontal_wall and not any(goal[0] == row for goal in goals):
            return True
        return vertical_wall and horizontal_wall
