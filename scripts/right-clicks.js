document.addEventListener("DOMContentLoaded", () => {
    // Create menu container
    const contextMenu = document.createElement("div");
    contextMenu.id = "context-menu";

    // Title element
    const menuTitle = document.createElement("div");
    menuTitle.id = "menu-title";
    contextMenu.appendChild(menuTitle);

    // Create button container
    const buttonContainer = document.createElement("div");
    buttonContainer.id = "button-container";

    let wikiButton = initializeWikiButton(buttonContainer);
    let skipButton = initializeSkipButton(buttonContainer);
    let cancelButton = initializeCancelButton(buttonContainer);

    // Append to menu and body
    contextMenu.appendChild(buttonContainer);
    document.body.appendChild(contextMenu);

    // === LONG TOUCH/RIGHT CLICK EVENT ===
    const showContextMenu = (event) => {
        let node = event.target.closest(".node");
        if (!node) return;
        event.preventDefault(); // Prevent default browser menu

        // Update title
        menuTitle.textContent = node.title || "Unknown Item";

        // Configure Wiki Button
        let wikiLink = node.dataset.wikiLink;
        if (wikiLink) {
            wikiButton.style.display = "block";
            wikiButton.onclick = () => {
                window.open(wikiLink, "_blank");
                contextMenu.style.display = "none";
            };
        } else {
            wikiButton.style.display = "none";
        }
        
        // Configure Skip Button
        skipButton.onclick = () => {
            const currentState = parseInt(node.dataset.state);

            if (currentState === 2 && node.dataset.prevState !== undefined) {
                // Restore previous state
                node.dataset.state = node.dataset.prevState;
                delete node.dataset.prevState;
            } else {
                // Save current state and mark as skipped
                node.dataset.prevState = currentState;
                node.dataset.state = 2;
            }
        
            contextMenu.style.display = "none";
            updateNodeVisualState(node);
            saveNodeState(node);
        }

        // Configure Cancel Button
        cancelButton.onclick = () => {
            contextMenu.style.display = "none";
        };

        // Position and show menu
        renderContextMenu(contextMenu, event);
    }
    // Right click event
    document.addEventListener("contextmenu", showContextMenu);

    const touchduration = 600; //length of time we want the user to touch before we do something
    const onlongtouch = (e) => {
        timer = null;
        showContextMenu(e); // Call the context menu function
    };
    let timer;

    const chart = document.getElementById('chart-container') || document.getElementById('chart-container-bare-bones') || document.querySelector('.chart'); // last resort

    chart.addEventListener("touchstart", (e) => !timer ? timer = setTimeout(() => onlongtouch(e), touchduration) : null, false);
    chart.addEventListener("touchend", () => timer ? timer = clearTimeout(timer) : null, false);

    // === CLICK OUTSIDE TO CLOSE ===
    document.addEventListener("click", (event) => {
        if (!contextMenu.contains(event.target)) {
            contextMenu.style.display = "none";
        }
    });
});

function initializeWikiButton(buttonContainer) {
    const wikiButton = document.createElement("button");
    wikiButton.id = "wiki-button";
    wikiButton.classList.add("menu-button");

    const whiteText = document.createElement("span");
    whiteText.classList.add("left-text");
    whiteText.textContent = "Go to ";

    const orangeText = document.createElement("span");
    orangeText.classList.add("right-text");
    orangeText.textContent = "Wiki";

    wikiButton.appendChild(whiteText);
    wikiButton.appendChild(orangeText);
    buttonContainer.appendChild(wikiButton);
    return wikiButton;
}

function initializeSkipButton(buttonContainer) {
    const skipButton = document.createElement("button");
    skipButton.id = "skip-button";
    skipButton.classList.add("menu-button");

    const whiteText = document.createElement("span");
    whiteText.classList.add("left-text");
    whiteText.textContent = "Mark as ";

    const orangeText = document.createElement("span");
    orangeText.classList.add("right-text");
    orangeText.textContent = "Skipped";

    skipButton.appendChild(whiteText);
    skipButton.appendChild(orangeText);
    buttonContainer.appendChild(skipButton);
    return skipButton;
}

function initializeCancelButton(buttonContainer) {
    const cancelButton = document.createElement("button");
    cancelButton.id = "cancel-button";
    cancelButton.classList.add("menu-button");

    const cancelText = document.createElement("span");
    cancelText.classList.add("left-text");
    cancelText.textContent = "Cancel";

    cancelButton.appendChild(cancelText);
    buttonContainer.appendChild(cancelButton);
    return cancelButton;
}


function renderContextMenu(contextMenu, event) {
    // Ensure menu is temporarily visible to get accurate dimensions
    contextMenu.style.display = "block";
    contextMenu.style.visibility = "hidden"; // Prevents flickering

    const menuWidth = contextMenu.offsetWidth;
    const menuHeight = contextMenu.offsetHeight;
    const maxX = document.documentElement.clientWidth; // Use clientWidth for accurate screen width without scrollbars
    const maxY = window.innerHeight + window.scrollY; // User height + how far we scrolled down to figure out the bottom edge

    let posX = event.pageX - menuWidth / 2; // Center menu horizontally at cursor
    let posY = event.pageY; // Keep top edge at cursor position

    // Right edge overflow: Shift left if menu overflows the screen
    if (posX + menuWidth > maxX) {
        posX = maxX - menuWidth; // Stick to right edge
    }
    // Left edge overflow: Shift right if menu goes off-screen
    if (posX < 0) {
        posX = 0;
    }
    // Bottom edge overflow: Move menu upwards if needed
    if (posY + menuHeight > maxY) {
        posY = maxY - menuHeight;
    }
    // Top edge overflow: Ensure the menu is always visible
    if (posY < window.scrollY) {
        posY = window.scrollY;
    }

    // Apply computed position
    contextMenu.style.top = `${posY}px`;
    contextMenu.style.left = `${posX}px`;
    contextMenu.style.visibility = "visible"; // Now show menu properly
}

