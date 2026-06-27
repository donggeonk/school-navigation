const API_URL = '/api';
let mapData = [];
let currentPath = [];
let pathStart = '';
let pathEnd = '';
let isChatSending = false;

// const campusBoundary = [
//     [60, 180],
//     [650, 180],
//     [650, 400],
//     [60, 400]
// ];

// Map each location to its icon filename
const iconFiles = {
    "Main Entrance": "entrance.png",
    "Soccer Field": "soccer.png",
    "Elementary School": "school.png",
    "Play Spaces": "play.png",
    "Cafeteria": "cafeteria.png",
    "Lower Hill": "hill.png",
    "Middle School": "school.png",
    "Secondary Library": "library.png",
    "Performing Arts": "arts.png",
    "High School": "school.png",
    "Outdoor Field": "field.png",
    "G Building": "building.png",
    "Bus Area": "bus.png"
};

const blueprintFloors = {
    "High School": [
        { label: "B", file: "high_school_base.png" },
        { label: "1", file: "high_school.png" },
        { label: "2", file: "high_school_2.png" },
        { label: "3", file: "high_school_3.png" },
        { label: "4", file: "high_school_4.png" },
        { label: "5", file: "high_school_5.png" },
        { label: "6", file: "high_school_6.png" },
        { label: "7", file: "high_school_7.png" }
    ],
    "Middle School": [
        { label: "1", file: "middle_school.png" }
    ],
    "Elementary School": [
        { label: "1", file: "elementary_school.png" },
        { label: "2", file: "elementary_school_2.png" }
    ],
    "Cafeteria": [
        { label: "1", file: "cafeteria.png" },
        { label: "2", file: "cafeteria_2.png" },
        { label: "2-1", file: "cafeteria_2_1.png" }
    ]
};

const icons = {}; // Will store the loaded Image objects

window.addEventListener('DOMContentLoaded', async () => {
    await loadIcons(); // Preload icons before drawing
    await loadMap();
    drawMap();
});

window.addEventListener('resize', () => {
    drawMap();
});

document.getElementById('mapCanvas').addEventListener('click', (event) => {
    const clickedBuilding = getClickedBlueprintBuilding(event);

    if (clickedBuilding) {
        openBlueprintModal(clickedBuilding);
    }
});

document.getElementById('mapCanvas').addEventListener('mousemove', (event) => {
    const canvas = document.getElementById('mapCanvas');
    canvas.style.cursor = getClickedBlueprintBuilding(event) ? 'pointer' : 'default';
});

document.getElementById('mapCanvas').addEventListener('mouseleave', () => {
    document.getElementById('mapCanvas').style.cursor = 'default';
});

document.getElementById('closeModalBtn').addEventListener('click', closeBlueprintModal);

document.getElementById('blueprintModal').addEventListener('click', (event) => {
    if (event.target.id === 'blueprintModal') {
        closeBlueprintModal();
    }
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closeBlueprintModal();
    }
});

// Preload all images
async function loadIcons() {
    const promises = Object.keys(iconFiles).map(name => {
        return new Promise((resolve) => {
            const img = new Image();
            // Assuming you put the icons in frontend/src/icons/
            img.src = `/icons/${iconFiles[name]}`; 
            img.onload = () => {
                icons[name] = img;
                resolve();
            };
            img.onerror = () => {
                console.warn(`Failed to load icon for ${name}`);
                resolve(); // Resolve anyway so the app doesn't freeze
            };
        });
    });
    await Promise.all(promises);
}

function getCanvasPoint(event) {
    const canvas = document.getElementById('mapCanvas');
    const rect = canvas.getBoundingClientRect();

    return {
        x: (event.clientX - rect.left) * (canvas.width / rect.width),
        y: (event.clientY - rect.top) * (canvas.height / rect.height)
    };
}

function getBuildingHitBox(node) {
    const canvas = document.getElementById('mapCanvas');
    const scaleX = canvas.width / 800;
    const scaleY = canvas.height / 600;
    const scale = Math.min(scaleX, scaleY);
    const [mapX, mapY] = node.coordinates;
    const iconSize = 50 * scale;
    const padding = 16 * scale;
    const bgSize = iconSize + padding;
    const centerX = mapX * scaleX;
    const centerY = mapY * scaleY;

    return {
        left: centerX - bgSize / 2,
        right: centerX + bgSize / 2,
        top: centerY - bgSize / 2,
        bottom: centerY + bgSize / 2
    };
}

function getClickedBlueprintBuilding(event) {
    const point = getCanvasPoint(event);

    for (const node of mapData) {
        if (!blueprintFloors[node.name]) {
            continue;
        }

        const hitBox = getBuildingHitBox(node);
        const isInside =
            point.x >= hitBox.left &&
            point.x <= hitBox.right &&
            point.y >= hitBox.top &&
            point.y <= hitBox.bottom;

        if (isInside) {
            return node.name;
        }
    }

    return null;
}

function openBlueprintModal(buildingName, floorLabel = "1") {
    const modal = document.getElementById('blueprintModal');
    const floors = blueprintFloors[buildingName];

    if (!floors || floors.length === 0) {
        return false;
    }

    const selectedFloor = floors.find(floor => floor.label === floorLabel) ||
        floors.find(floor => floor.label === "1") ||
        floors[0];

    renderFloorButtons(buildingName, floors);
    showBlueprintFloor(buildingName, selectedFloor);
    modal.style.display = 'flex';
    return true;
}

function renderFloorButtons(buildingName, floors) {
    const floorControls = document.getElementById('blueprintFloorControls');
    floorControls.innerHTML = '';

    floors.forEach(floor => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'floor-button';
        button.textContent = floor.label;
        button.setAttribute('aria-label', `${buildingName} floor ${floor.label}`);
        button.addEventListener('click', () => {
            showBlueprintFloor(buildingName, floor);
        });
        floorControls.appendChild(button);
    });
}

function showBlueprintFloor(buildingName, floor) {
    const blueprintImage = document.getElementById('blueprintImage');
    const floorButtons = document.querySelectorAll('.floor-button');

    blueprintImage.src = `/blueprints/${floor.file}`;
    blueprintImage.alt = `${buildingName} floor ${floor.label} blueprint`;

    floorButtons.forEach(button => {
        button.classList.toggle('active', button.textContent === floor.label);
    });
}

function closeBlueprintModal() {
    const modal = document.getElementById('blueprintModal');
    const blueprintImage = document.getElementById('blueprintImage');
    const floorControls = document.getElementById('blueprintFloorControls');

    modal.style.display = 'none';
    blueprintImage.src = '';
    blueprintImage.alt = 'Blueprint';
    floorControls.innerHTML = '';
}

async function loadMap() {
// ...existing code...
    try {
        const response = await fetch(`${API_URL}/map`);
        mapData = await response.json();
        console.log('Map data loaded:', mapData);
    } catch (error) {
        console.error('Error loading map:', error);
    }
}

function drawMap() {
// ...existing code...
    const canvas = document.getElementById('mapCanvas');
    const ctx = canvas.getContext('2d');
    const container = canvas.parentElement;

    canvas.width = container.clientWidth - 20;
    canvas.height = container.clientHeight - 20;

    const scaleX = canvas.width / 800;
    const scaleY = canvas.height / 600;

    // Draw grass background
    ctx.fillStyle = '#c8e6c9';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw the navigation path (behind buildings)
    if (currentPath.length > 1) {
        drawNavigationPath(ctx, scaleX, scaleY);
    }

    // drawCampusBoundary(ctx, scaleX, scaleY);

    // Draw buildings/locations
    mapData.forEach(node => {
        const [x, y] = node.coordinates;
        const isStart = node.name === pathStart;
        const isEnd = node.name === pathEnd;
        drawBuilding(ctx, x * scaleX, y * scaleY, node.name, Math.min(scaleX, scaleY), isStart, isEnd);
    });
}

function drawCampusBoundary(ctx, scaleX, scaleY) {
    if (campusBoundary.length < 2) return;

    ctx.save();
    ctx.strokeStyle = '#7a7a7a';
    ctx.lineWidth = 3;
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(campusBoundary[0][0] * scaleX, campusBoundary[0][1] * scaleY);

    for (let i = 1; i < campusBoundary.length; i++) {
        ctx.lineTo(campusBoundary[i][0] * scaleX, campusBoundary[i][1] * scaleY);
    }

    ctx.closePath();
    ctx.stroke();
    ctx.restore();
}

function drawBuilding(ctx, x, y, name, scale, isStart, isEnd) {
    const iconSize = 50 * scale; // Increased from 48 to make icons larger
    const padding = 16 * scale;  // Padding around the icon
    const bgSize = iconSize + padding; // Total size of the background box
    const cornerRadius = 12 * scale; // How round the corners are

    // Draw a highlight border behind the box if it's the start or destination
    if (isStart || isEnd) {
        ctx.beginPath();
        ctx.roundRect(x - bgSize / 2 - 4, y - bgSize / 2 - 4, bgSize + 8, bgSize + 8, cornerRadius + 2);
        ctx.fillStyle = isStart ? 'rgba(67, 160, 71, 0.4)' : 'rgba(229, 57, 53, 0.4)';
        ctx.fill();
        ctx.lineWidth = 3;
        ctx.strokeStyle = isStart ? '#2e7d32' : '#b71c1c';
        ctx.stroke();
    }

    // Draw the dark green rounded rectangle background
    ctx.beginPath();
    ctx.roundRect(x - bgSize / 2, y - bgSize / 2, bgSize, bgSize, cornerRadius);
    ctx.fillStyle = '#84d988'; // Dark green color
    ctx.fill();
    
    const highlightBuildings = ["High School", "Middle School", "Cafeteria", "Elementary School"];
    
    if (highlightBuildings.includes(name)) {
        ctx.lineWidth = 3;            // clickable icons to view floorplans
        ctx.strokeStyle = '#2f85a2'; 
    } else {
        ctx.lineWidth = 2;            
        ctx.strokeStyle = '#0d3b13';
    }
    ctx.stroke();

    // Draw the icon image
    const img = icons[name];
    if (img) {
        ctx.drawImage(img, x - iconSize / 2, y - iconSize / 2, iconSize, iconSize);
    } else {
        // Fallback square if image is missing
        ctx.fillStyle = '#a5d6a7';
        ctx.fillRect(x - iconSize / 4, y - iconSize / 4, iconSize / 2, iconSize / 2);
    }

    // Label tag for start/end
    if (isStart || isEnd) {
        const tag = isStart ? 'Start' : 'Destination';
        ctx.font = `bold ${Math.max(11 * scale, 10)}px Arial`;
        const tagWidth = ctx.measureText(tag).width + 16;
        const tagHeight = 20 * scale;
        const tagY = y - bgSize / 2 - tagHeight - 10; // Positioned above the new background box

        ctx.beginPath();
        ctx.roundRect(x - tagWidth / 2, tagY, tagWidth, tagHeight, 4);
        ctx.fillStyle = isStart ? '#a5d6a7' : '#ef9a9a';
        ctx.fill();
        
        ctx.fillStyle = isStart ? '#1b5e20' : '#b71c1c';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(tag, x, tagY + tagHeight / 2);
    }

    // Building label (Text below the background box)
    ctx.fillStyle = '#333'; 
    ctx.font = `bold ${Math.max(12 * scale, 11)}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';

    const words = name.split(' ');
    const textY = y + bgSize / 2 + 6; // Position text just below the background box
    
    if (words.length > 1) {
        ctx.fillText(words[0], x, textY);
        ctx.fillText(words.slice(1).join(' '), x, textY + 14 * scale);
    } else {
        ctx.fillText(name, x, textY);
    }
}

function drawNavigationPath(ctx, scaleX, scaleY) {
    if (currentPath.length < 2) return;

    // Draw glow
    ctx.strokeStyle = 'rgba(255, 87, 34, 0.25)';
    ctx.lineWidth = 12;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    ctx.moveTo(currentPath[0][0] * scaleX, currentPath[0][1] * scaleY);
    for (let i = 1; i < currentPath.length; i++) {
        ctx.lineTo(currentPath[i][0] * scaleX, currentPath[i][1] * scaleY);
    }
    ctx.stroke();

    // Draw main path line
    ctx.strokeStyle = '#ff5722';
    ctx.lineWidth = 4;
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(currentPath[0][0] * scaleX, currentPath[0][1] * scaleY);
    for (let i = 1; i < currentPath.length; i++) {
        ctx.lineTo(currentPath[i][0] * scaleX, currentPath[i][1] * scaleY);
    }
    ctx.stroke();

    // Draw direction arrows along the path
    for (let i = 0; i < currentPath.length - 1; i++) {
        const x1 = currentPath[i][0] * scaleX;
        const y1 = currentPath[i][1] * scaleY;
        const x2 = currentPath[i + 1][0] * scaleX;
        const y2 = currentPath[i + 1][1] * scaleY;

        const dist = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
        if (dist > 30) {
            const midX = (x1 + x2) / 2;
            const midY = (y1 + y2) / 2;
            drawArrow(ctx, x1, y1, midX, midY);
        }
    }
}

function drawArrow(ctx, fromX, fromY, toX, toY) {
    const headLength = 12;
    const angle = Math.atan2(toY - fromY, toX - fromX);

    ctx.fillStyle = '#ff5722';
    ctx.beginPath();
    ctx.moveTo(toX, toY);
    ctx.lineTo(
        toX - headLength * Math.cos(angle - Math.PI / 6),
        toY - headLength * Math.sin(angle - Math.PI / 6)
    );
    ctx.lineTo(
        toX - headLength * Math.cos(angle + Math.PI / 6),
        toY - headLength * Math.sin(angle + Math.PI / 6)
    );
    ctx.closePath();
    ctx.fill();
}

// --- Navigation UI ---

const locations = [
    "Main Entrance",
    "Soccer Field",
    "Elementary School",
    "Play Spaces",
    "Cafeteria",
    "Lower Hill",
    "Middle School",
    "Secondary Library",
    "Performing Arts",
    "High School",
    "Outdoor Field",
    "G Building",
    "Bus Area"
];

function populateDropdowns() {
    const startSelect = document.getElementById("startSelect");
    const destSelect = document.getElementById("destSelect");

    locations.forEach(loc => {
        const opt1 = document.createElement("option");
        opt1.value = loc;
        opt1.textContent = loc;
        startSelect.appendChild(opt1);

        const opt2 = document.createElement("option");
        opt2.value = loc;
        opt2.textContent = loc;
        destSelect.appendChild(opt2);
    });
}

async function runNavigation(start, dest, options = {}) {
    const { showAlertOnError = true } = options;

    function handleError(message) {
        if (showAlertOnError) {
            alert(message);
        }
        return {
            success: false,
            error: message
        };
    }

    if (!start || !dest) {
        return handleError("Please select both a start and a destination.");
    }
    if (start === dest) {
        return handleError("Start and destination cannot be the same.");
    }

    try {
        const response = await fetch(
            `${API_URL}/navigate?start=${encodeURIComponent(start)}&end=${encodeURIComponent(dest)}`
        );
        const data = await response.json();

        if (data.error) {
            return handleError(data.error);
        }

        pathStart = data.start;
        pathEnd = data.end;
        currentPath = data.path;  // Array of [x, y] coordinates
        console.log('Path found:', currentPath.length, 'waypoints');
        drawMap();
        return {
            success: true
        };
    } catch (error) {
        console.error('Navigation error:', error);
        return handleError('Failed to find a path. Make sure the server is running.');
    }
}

async function applyChatNavigation(navigation) {
    if (!navigation || !navigation.start || !navigation.destination) {
        return {
            success: false,
            error: "Chatbot returned an incomplete navigation request."
        };
    }

    document.getElementById("startSelect").value = navigation.start;
    document.getElementById("destSelect").value = navigation.destination;

    return runNavigation(navigation.start, navigation.destination, {
        showAlertOnError: false
    });
}

document.getElementById("navigateBtn").addEventListener("click", async () => {
    const start = document.getElementById("startSelect").value;
    const dest = document.getElementById("destSelect").value;
    await runNavigation(start, dest);
});

// Add event listener for the Done button to clear the path
document.getElementById("doneBtn").addEventListener("click", () => {
    currentPath = [];
    pathStart = '';
    pathEnd = '';
    document.getElementById("startSelect").value = '';
    document.getElementById("destSelect").value = '';
    drawMap();
});

function appendChatMessage(text, type) {
    const chatMessages = document.getElementById("chatMessages");
    const bubble = document.createElement("div");
    bubble.className = `chat-message ${type === "user" ? "user-message" : "bot-message"}`;
    bubble.textContent = text;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setSuggestedDestination(location) {
    if (!location || !locations.includes(location)) {
        return;
    }

    document.getElementById("destSelect").value = location;
}

function applyChatBlueprint(blueprint) {
    if (!blueprint || !blueprint.building) {
        return false;
    }

    return openBlueprintModal(blueprint.building, blueprint.floor || "1");
}

async function sendChatMessage() {
    const chatInput = document.getElementById("chatInput");
    const sendButton = document.getElementById("chatSendBtn");
    const message = chatInput.value.trim();

    if (!message || isChatSending) {
        return;
    }

    appendChatMessage(message, "user");
    chatInput.value = "";
    isChatSending = true;
    sendButton.disabled = true;

    const selectedStart = document.getElementById("startSelect").value;
    const selectedDestination = document.getElementById("destSelect").value;

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message,
                start: selectedStart,
                destination: selectedDestination
            })
        });

        const data = await response.json();
        if (data.error) {
            appendChatMessage(`Error: ${data.error}`, "bot");
            return;
        }

        if (data.navigation) {
            const navigationResult = await applyChatNavigation(data.navigation);
            if (!navigationResult.success) {
                appendChatMessage(navigationResult.error, "bot");
            }
        } else if (data.suggested_destination) {
            setSuggestedDestination(data.suggested_destination);
        }

        if (data.blueprint && !applyChatBlueprint(data.blueprint)) {
            appendChatMessage("I found a blueprint request, but could not open that building or floor.", "bot");
        }

        appendChatMessage(data.message || "I could not generate a response.", "bot");
    } catch (error) {
        console.error("Chat error:", error);
        appendChatMessage("Could not reach the chatbot service.", "bot");
    } finally {
        isChatSending = false;
        sendButton.disabled = false;
    }
}

document.getElementById("chatSendBtn").addEventListener("click", sendChatMessage);
document.getElementById("chatInput").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        event.preventDefault();
        sendChatMessage();
    }
});

populateDropdowns();
