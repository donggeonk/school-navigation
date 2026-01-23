class Node:
    def __init__(self, name, coordinates):
        self.name = name
        self.coordinates = coordinates  # Now in pixels (x, y)
        self.connections = []

    def add_connection(self, node):
        if node not in self.connections:
            self.connections.append(node)
            node.connections.append(self)

class SchoolMap:
    def __init__(self):
        self.nodes = {}
        self.create_map()

    def create_map(self):
        # Coordinates are now in pixels - adjust these to match your actual school layout
        # Canvas is 800x600, so position buildings accordingly
        
        main_entrance = Node("Main Entrance", (400, 50))
        soccer_field = Node("Soccer Field", (80, 120))
        elementary_school = Node("Elementary School", (280, 120))
        play_spaces = Node("Play Spaces", (150, 220))
        cafeteria = Node("Cafeteria", (400, 200))
        lower_hill = Node("Lower Hill", (600, 200))
        middle_school = Node("Middle School", (150, 320))
        secondary_library = Node("Secondary Library", (400, 320))
        performing_arts = Node("Performing Arts", (620, 320))
        high_school = Node("High School", (280, 420))
        outdoor_field = Node("Outdoor Field", (500, 420))
        g_building = Node("G Building", (150, 520))
        bus_area = Node("Bus Area", (500, 520))

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
            "Outdoor Field": outdoor_field,
            "G Building": g_building,
            "Bus Area": bus_area
        }

        # Backend connections (not displayed, only for pathfinding)
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
        
        performing_arts.add_connection(outdoor_field)
        
        high_school.add_connection(outdoor_field)
        high_school.add_connection(g_building)
        
        outdoor_field.add_connection(bus_area)
        
        g_building.add_connection(bus_area)

    def get_node(self, name):
        return self.nodes.get(name)

    def get_connections(self, name):
        node = self.get_node(name)
        return [connection.name for connection in node.connections] if node else []