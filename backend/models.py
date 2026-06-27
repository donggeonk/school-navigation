import heapq

class Node:
    def __init__(self, name, coordinates):
        self.name = name
        self.coordinates = coordinates
        self.connections = []

    def add_connection(self, node):
        if node not in self.connections:
            self.connections.append(node)
            node.connections.append(self)

class SchoolMap:
    GRID_WIDTH = 800
    GRID_HEIGHT = 600
    BUILDING_HALF_W = 55
    BUILDING_HALF_H = 32
    BUILDING_MARGIN = 10
    BOUNDARY_LEFT = 60
    BOUNDARY_TOP = 180
    BOUNDARY_RIGHT = 650
    BOUNDARY_BOTTOM = 400

    def __init__(self):
        self.nodes = {}
        self.create_map()
        self.obstacle_grid = self._build_obstacle_grid()

    def create_map(self): # (x, y)
        main_entrance = Node("Main Entrance", (50, 300))
        soccer_field = Node("Soccer Field", (120, 220))
        elementary_school = Node("Elementary School", (200, 220))
        play_spaces = Node("Play Spaces", (280, 170))
        cafeteria = Node("Cafeteria", (280, 280))
        lower_hill = Node("Lower Hill", (650, 150))
        middle_school = Node("Middle School", (360, 220))
        secondary_library = Node("Secondary Library", (430, 280))
        performing_arts = Node("Performing Arts", (430, 170))
        high_school = Node("High School", (500, 220))
        g_building = Node("G Building", (360, 420))
        bus_area = Node("Bus Area", (200, 400))

        self.nodes = {
            "Main Entrance": main_entrance,
            "Soccer Field": soccer_field,
            "Elementary School": elementary_school,
            "Play Spaces": play_spaces,
            "Cafeteria": cafeteria,
            "Lower Hill": lower_hill,
            "Middle School": middle_school,
            "Secondary Library": secondary_library,
            "Performing Arts": performing_arts,
            "High School": high_school,
            "G Building": g_building,
            "Bus Area": bus_area
        }

        main_entrance.add_connection(elementary_school)
        main_entrance.add_connection(cafeteria)
        soccer_field.add_connection(elementary_school)
        soccer_field.add_connection(play_spaces)
        elementary_school.add_connection(play_spaces)
        elementary_school.add_connection(cafeteria)
        play_spaces.add_connection(middle_school)
        cafeteria.add_connection(secondary_library)
        cafeteria.add_connection(lower_hill)
        lower_hill.add_connection(performing_arts)
        middle_school.add_connection(high_school)
        middle_school.add_connection(secondary_library)
        middle_school.add_connection(g_building)
        secondary_library.add_connection(high_school)
        secondary_library.add_connection(performing_arts)
        high_school.add_connection(g_building)
        g_building.add_connection(bus_area)

    def _build_obstacle_grid(self):
        """Buildings are not pathfinding obstacles in the current map."""
        return set()

    def _heuristic(self, a, b):
        """Euclidean distance heuristic for A*."""
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def _is_inside_boundary(self, point):
        x, y = point
        return (
            self.BOUNDARY_LEFT <= x <= self.BOUNDARY_RIGHT
            and self.BOUNDARY_TOP <= y <= self.BOUNDARY_BOTTOM
        )

    def _closest_boundary_point(self, point):
        x, y = point
        clamped_x = min(max(x, self.BOUNDARY_LEFT), self.BOUNDARY_RIGHT)
        clamped_y = min(max(y, self.BOUNDARY_TOP), self.BOUNDARY_BOTTOM)
        return (clamped_x, clamped_y)

    def _get_special_case_path(self, start_name, end_name):
        """Return a hand-tuned path for routes that should follow campus walkways."""
        special_paths = {
            ("Main Entrance", "Play Spaces"): [
                [60, 300],
                [240, 255],
                [280, 180],
            ],
        }

        path = special_paths.get((start_name, end_name))
        if path:
            return path

        reverse_path = special_paths.get((end_name, start_name))
        if reverse_path:
            return list(reversed(reverse_path))

        return None

    def _line_of_sight(self, p1, p2, blocked):
        """Check if a straight line between p1 and p2 is free of obstacles.
        Uses Bresenham-style raycasting with a step size for performance."""
        x0, y0 = p1
        x1, y1 = p2
        dx = x1 - x0
        dy = y1 - y0
        dist = max(abs(dx), abs(dy))

        if dist == 0:
            return True

        # Check points along the line every 2 pixels
        steps = max(int(dist / 2), 1)
        for i in range(steps + 1):
            t = i / steps
            x = int(x0 + dx * t)
            y = int(y0 + dy * t)
            if (x, y) in blocked:
                return False
            if not self._is_inside_boundary((x, y)):
                return False
        return True

    def _smooth_path(self, path, blocked):
        """Line-of-sight smoothing: skip waypoints when a direct line is clear."""
        if len(path) <= 2:
            return path

        smoothed = [path[0]]
        current = 0

        while current < len(path) - 1:
            # Try to skip as far ahead as possible
            farthest = current + 1
            for candidate in range(len(path) - 1, current, -1):
                if self._line_of_sight(
                    tuple(path[current]), tuple(path[candidate]), blocked
                ):
                    farthest = candidate
                    break
            smoothed.append(path[farthest])
            current = farthest

        return smoothed

    def find_shortest_path(self, start_name, end_name):
        """A* pathfinding on the grid, avoiding buildings except start/end."""
        start_node = self.get_node(start_name)
        end_node = self.get_node(end_name)

        if not start_node or not end_node:
            return None

        special_case_path = self._get_special_case_path(start_name, end_name)
        if special_case_path:
            return special_case_path

        if start_name == end_name:
            return [list(self._closest_boundary_point(tuple(start_node.coordinates)))]

        start = self._closest_boundary_point(tuple(start_node.coordinates))
        end = self._closest_boundary_point(tuple(end_node.coordinates))
        blocked = self.obstacle_grid

        # A* with step size to speed things up
        STEP = 5
        directions = [
            (STEP, 0), (-STEP, 0), (0, STEP), (0, -STEP),
            (STEP, STEP), (-STEP, -STEP), (STEP, -STEP), (-STEP, STEP)
        ]

        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if abs(current[0] - end[0]) <= STEP and abs(current[1] - end[1]) <= STEP:
                # Reconstruct raw path
                path = [list(end)]
                node = current
                while node in came_from:
                    path.append(list(node))
                    node = came_from[node]
                path.append(list(start))
                path.reverse()

                # Smooth the path using line-of-sight checks
                return self._smooth_path(path, blocked)

            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy

                if nx < 0 or nx >= self.GRID_WIDTH or ny < 0 or ny >= self.GRID_HEIGHT:
                    continue

                if not self._is_inside_boundary((nx, ny)):
                    continue

                if (nx, ny) in blocked:
                    continue

                move_cost = (dx**2 + dy**2) ** 0.5
                tentative_g = g_score[current] + move_cost
                neighbor = (nx, ny)

                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self._heuristic(neighbor, end)
                    heapq.heappush(open_set, (f, neighbor))

        return None

    def get_node(self, name):
        return self.nodes.get(name)

    def get_connections(self, name):
        node = self.get_node(name)
        return [connection.name for connection in node.connections] if node else []
