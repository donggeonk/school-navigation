const API_URL = '/api';
let mapData = [];
let currentPath = [];

window.addEventListener('DOMContentLoaded', async () => {
    await loadMap();
    drawMap();
});

// Redraw map when window is resized
window.addEventListener('resize', () => {
    drawMap();
});

async function loadMap() {
    try {
        const response = await fetch(`${API_URL}/map`);
        mapData = await response.json();
        console.log('Map data loaded:', mapData);
    } catch (error) {
        console.error('Error loading map:', error);
    }
}

function drawMap() {
    const canvas = document.getElementById('mapCanvas');
    const ctx = canvas.getContext('2d');
    const container = canvas.parentElement;
    
    // Set canvas size to fill container
    canvas.width = container.clientWidth - 20;
    canvas.height = container.clientHeight - 20;
    
    // Calculate scale based on canvas size
    // Original coordinates were designed for 800x600
    const scaleX = canvas.width / 800;
    const scaleY = canvas.height / 600;
    
    // Draw grass background
    ctx.fillStyle = '#c8e6c9';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw navigation path with arrows if exists
    if (currentPath.length > 1) {
        drawNavigationPath(ctx, scaleX, scaleY);
    }
    
    // Draw buildings/locations
    mapData.forEach(node => {
        const [x, y] = node.coordinates;
        drawBuilding(ctx, x * scaleX, y * scaleY, node.name, Math.min(scaleX, scaleY));
    });
}

function drawBuilding(ctx, x, y, name, scale) {
    const width = 110 * scale;
    const height = 65 * scale;
    
    // Building shadow
    ctx.fillStyle = 'rgba(0,0,0,0.2)';
    ctx.fillRect(x - width/2 + 4, y - height/2 + 4, width, height);
    
    // Building body
    ctx.fillStyle = '#5c6bc0';
    ctx.fillRect(x - width/2, y - height/2, width, height);
    
    // Building border
    ctx.strokeStyle = '#3949ab';
    ctx.lineWidth = 2;
    ctx.strokeRect(x - width/2, y - height/2, width, height);
    
    // Building label
    ctx.fillStyle = 'white';
    ctx.font = `bold ${Math.max(12 * scale, 11)}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    // Word wrap for long names
    const words = name.split(' ');
    if (words.length > 1) {
        ctx.fillText(words[0], x, y - 8 * scale);
        ctx.fillText(words.slice(1).join(' '), x, y + 8 * scale);
    } else {
        ctx.fillText(name, x, y);
    }
}

function drawNavigationPath(ctx, scaleX, scaleY) {
    ctx.strokeStyle = '#ff5722';
    ctx.lineWidth = 4;
    ctx.setLineDash([]);
    
    for (let i = 0; i < currentPath.length - 1; i++) {
        const node1 = mapData.find(n => n.name === currentPath[i]);
        const node2 = mapData.find(n => n.name === currentPath[i + 1]);
        
        if (node1 && node2) {
            const [x1, y1] = node1.coordinates;
            const [x2, y2] = node2.coordinates;
            
            ctx.beginPath();
            ctx.moveTo(x1 * scaleX, y1 * scaleY);
            ctx.lineTo(x2 * scaleX, y2 * scaleY);
            ctx.stroke();
            
            drawArrow(ctx, x1 * scaleX, y1 * scaleY, x2 * scaleX, y2 * scaleY);
        }
    }
}

function drawArrow(ctx, fromX, fromY, toX, toY) {
    const headLength = 15;
    const angle = Math.atan2(toY - fromY, toX - fromX);
    
    const distance = Math.sqrt((toX - fromX) ** 2 + (toY - fromY) ** 2);
    const shortenBy = 40;
    const ratio = (distance - shortenBy) / distance;
    const arrowX = fromX + (toX - fromX) * ratio;
    const arrowY = fromY + (toY - fromY) * ratio;
    
    ctx.fillStyle = '#ff5722';
    ctx.beginPath();
    ctx.moveTo(arrowX, arrowY);
    ctx.lineTo(
        arrowX - headLength * Math.cos(angle - Math.PI / 6),
        arrowY - headLength * Math.sin(angle - Math.PI / 6)
    );
    ctx.lineTo(
        arrowX - headLength * Math.cos(angle + Math.PI / 6),
        arrowY - headLength * Math.sin(angle + Math.PI / 6)
    );
    ctx.closePath();
    ctx.fill();
}

function setPath(path) {
    currentPath = path;
    drawMap();
}