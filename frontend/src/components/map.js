class MapComponent {
    constructor() {
        this.mapElement = document.getElementById('map');
        this.startInput = document.getElementById('start-location');
        this.destinationInput = document.getElementById('destination-location');
        this.buildings = {
            building1: { x: 50, y: 50 },
            building2: { x: 150, y: 50 },
            building3: { x: 100, y: 150 },
            field: { x: 100, y: 250 },
            parkingLot: { x: 200, y: 200 }
        };
        this.connections = {
            building1: ['building2', 'field'],
            building2: ['building1', 'building3'],
            building3: ['building2', 'parkingLot'],
            field: ['building1'],
            parkingLot: ['building3']
        };
    }

    renderMap() {
        // Render buildings, field, and parking lot
        for (const [name, coords] of Object.entries(this.buildings)) {
            this.drawNode(name, coords.x, coords.y);
        }
    }

    drawNode(name, x, y) {
        const node = document.createElement('div');
        node.className = 'map-node';
        node.style.left = `${x}px`;
        node.style.top = `${y}px`;
        node.innerText = name;
        this.mapElement.appendChild(node);
    }

    drawPath(start, destination) {
        const startCoords = this.buildings[start];
        const destCoords = this.buildings[destination];

        if (startCoords && destCoords) {
            const path = document.createElement('div');
            path.className = 'navigation-line';
            path.style.left = `${startCoords.x}px`;
            path.style.top = `${startCoords.y}px`;
            path.style.width = `${destCoords.x - startCoords.x}px`;
            path.style.height = `${destCoords.y - startCoords.y}px`;
            this.mapElement.appendChild(path);
        }
    }
}

export default MapComponent;