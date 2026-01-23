def get_school_map():
    # Define the nodes in the school map
    nodes = {
        "Building A": (1, 2),
        "Building B": (3, 2),
        "Building C": (2, 4),
        "Field": (2, 1),
        "Parking Lot": (4, 3)
    }
    
    # Define the connections between the nodes
    connections = {
        "Building A": ["Building B", "Field"],
        "Building B": ["Building A", "Building C"],
        "Building C": ["Building B"],
        "Field": ["Building A", "Parking Lot"],
        "Parking Lot": ["Field"]
    }
    
    return nodes, connections

def calculate_path(start, destination):
    nodes, connections = get_school_map()
    
    if start not in nodes or destination not in nodes:
        return None  # Invalid start or destination
    
    # Simple BFS to find the shortest path
    from collections import deque
    
    queue = deque([(start, [start])])
    visited = set()
    
    while queue:
        current, path = queue.popleft()
        
        if current == destination:
            return path
        
        visited.add(current)
        
        for neighbor in connections.get(current, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))
    
    return None  # No path found