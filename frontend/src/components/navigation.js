export function calculatePath(start, destination) {
    const graph = {
        'Building A': ['Building B', 'Field'],
        'Building B': ['Building A', 'Building C', 'Parking Lot'],
        'Building C': ['Building B'],
        'Field': ['Building A', 'Parking Lot'],
        'Parking Lot': ['Building B', 'Field']
    };

    const visited = new Set();
    const path = [];

    function dfs(current) {
        if (current === destination) {
            path.push(current);
            return true;
        }

        visited.add(current);

        for (const neighbor of graph[current]) {
            if (!visited.has(neighbor)) {
                if (dfs(neighbor)) {
                    path.push(current);
                    return true;
                }
            }
        }

        return false;
    }

    if (dfs(start)) {
        return path.reverse();
    } else {
        return null; // No path found
    }
}