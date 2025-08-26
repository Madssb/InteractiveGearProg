/**
 * Global storage for item and node data.
 * - `itemsData`: Maps item names to their metadata (e.g., image source, wiki link).
 * - `nodegroups`: Stores ordered lists of nodes as defined in sequence.json.
 */
let itemsData = {};
let nodegroups = [];

/** Define a cache version to invalidate outdated stored charts */
const CACHE_VERSION = "1.4.2"; // Update this whenever you make a major update
const ITEMS_PATH = "data/generated/items.json";
const SEQUENCE_PATH = "data/sequence.json";


/**
 * Sanitizes a string to create a safe HTML element ID.
 */
function sanitizeId(name) {
    return name.replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').toLowerCase();
}

/**
 * Creates a node element representing an item.
 */
function handle_item(node) {
    let nodeDiv = document.createElement("div");
    nodeDiv.classList.add("node");

    let itemData = itemsData[node];
    if (!itemData) {
        console.warn(`Missing data for item: ${node}`);
        return null;
    }
    let img = document.createElement("img");
    img.src = itemData.imgUrl; // Ensures correct path
    img.alt = node;
    nodeDiv.title = node;
    nodeDiv.id = sanitizeId(node);
    nodeDiv.appendChild(img);
    nodeDiv.dataset.wikiLink = itemData.wikiUrl;
    return nodeDiv;
}

/**
 * Creates a node element representing a skill milestone.
 */
function handle_skill(node) {
    let parts = node.split(" ");
    let lvlNum = parts[0];
    let skillName = parts[1];
    
    
    let nodeDiv = document.createElement("div");
    nodeDiv.classList.add("node");
    let itemData = itemsData[skillName];
    if (!itemData) {
        console.warn(`Missing data for item: ${node}`);
    }

    let skillDiv = document.createElement("div");
    skillDiv.classList.add("skill");

    let img = document.createElement("img");
    img.src = itemData.imgUrl; // Ensures correct path

    let span = document.createElement("span");
    span.textContent = lvlNum;

    skillDiv.appendChild(img);
    skillDiv.appendChild(span);
    nodeDiv.alt = `Get ${lvlNum} ${skillName}`;
    nodeDiv.title = `Get ${lvlNum} ${skillName}`;
    nodeDiv.id = "lvl-" + sanitizeId(node);
    nodeDiv.appendChild(skillDiv);
    nodeDiv.dataset.wikiLink = itemData.wikiUrl;

    return nodeDiv;
}


/**
 * Renders the progression chart and caches it in localStorage.
 */
function renderChart(chartContainer) {
    if (!chartContainer) {
        console.error("No valid chart container provided.");
        return;
    }

    chartContainer.innerHTML = "";

    for (let nodegroup of nodegroups) {
        let nodeGroupDiv = document.createElement("div");
        nodeGroupDiv.classList.add("node-group");

        for (let node of nodegroup) {
            let nodeDiv = !isNaN(node.charAt(0)) ? handle_skill(node) : handle_item(node);
            if (nodeDiv) nodeGroupDiv.appendChild(nodeDiv);
        }

        chartContainer.appendChild(nodeGroupDiv);

        if (nodegroup !== nodegroups[nodegroups.length - 1]) {
            let arrowDiv = document.createElement("div");
            arrowDiv.classList.add("arrow");
            arrowDiv.textContent = "→";
            chartContainer.appendChild(arrowDiv);
        }
    }

    localStorage.setItem("cachedChart", chartContainer.innerHTML);
    localStorage.setItem("cacheVersion", CACHE_VERSION); // Store the cache version
}

/**
 * Initializes the chart by checking for cached content.
 */
async function loadChart() {
    let chartContainer = document.getElementById("chart-container");
    if (!chartContainer) {
        console.error("No element with ID 'chart-container' found.");
        return Promise.reject("Chart container not found");
    }

    let cachedChart = localStorage.getItem("cachedChart");
    let cachedVersion = localStorage.getItem("cacheVersion");

    try {
        if (cachedChart && cachedVersion === CACHE_VERSION) {
            chartContainer.innerHTML = cachedChart;
            console.log("Cached chart loaded successfully.");
            return;
        } else {
            throw new Error("Cache outdated or missing"); // Forces a fallback
        }
    } catch (error) {
        console.warn("Cache load failed:", error);
        console.log("Fetching fresh data...");

        try {
            const [items, sequence] = await Promise.all([
                fetch(ITEMS_PATH).then(res => res.json()),
                fetch(SEQUENCE_PATH).then(res => res.json())
            ]);
            itemsData = items;
            nodegroups = Object.values(sequence);
            renderChart(chartContainer);
        } catch (error) {
            console.error("Error loading JSON:", error);
        }
    }
}

/**
 * Saves and restores node states in localStorage.
 */
function saveNodeState(node) {
    let savedStates = JSON.parse(localStorage.getItem("sharedNodeStates")) || {}; // Use shared storage key
    savedStates[node.id] = parseInt(node.dataset.state);
    localStorage.setItem("sharedNodeStates", JSON.stringify(savedStates)); // Store under shared key
}

function updateNodeVisualState(node) {
    node.classList.remove("state-0", "state-1", "state-2");
    let state = parseInt(node.dataset.state);
    node.classList.add(`state-${state}`);
}

function initializeNodeStates() {
    let chartContainer = document.getElementById("chart-container");
    if (!chartContainer) return;

    let savedStates = JSON.parse(localStorage.getItem("sharedNodeStates")) || {}; // Load from shared storage

    chartContainer.addEventListener("click", (event) => {
        let node = event.target.closest(".node");
        if (!node) return;

        let currentState = parseInt(node.dataset.state) || 0;
        let nextState = currentState === 1 ? 0 : 1;
        node.dataset.state = nextState;

        updateNodeVisualState(node);
        saveNodeState(node); // Save state under shared key
    });

    for (let nodeId in savedStates) {
        let node = document.getElementById(nodeId);
        if (node) {
            node.dataset.state = savedStates[nodeId];
            updateNodeVisualState(node);
        }
    }
}


/**
 * Prevents dragging images within the chart container.
 */
function preventDragging() {
    document.querySelector("#chart-container").addEventListener("dragstart", (event) => {
        if (event.target.tagName === "IMG") {
            event.preventDefault();
        }
    });
}

/**
 * Initializes the application.
 */
async function init() {
    await loadChart();
    initializeNodeStates();
    preventDragging();
}

// Start rendering when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", init);
