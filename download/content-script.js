(function () {
    const originalPushState = history.pushState;
    const originalReplaceState = history.replaceState;

    function triggerUrlChange() {
        const event = new Event("urlchange");
        window.dispatchEvent(event);
    }

    history.pushState = function (...args) {
        originalPushState.apply(this, args);
        triggerUrlChange();
    }

    history.replaceState = function (...args) {
        originalReplaceState.apply(this, args);
        triggerUrlChange();
    }

    window.addEventListener("popstate", triggerUrlChange);
})();

function createButton(label, onClickHandler) {
    const button = document.createElement("button");
    button.textContent = label;
    button.className = "custom-button";
    button.addEventListener("click", onClickHandler);
    return button;
}

function createToggleSwitch(onToggle, labelText) { // Modified to accept labelText
    const toggleContainer = document.createElement("div");
    toggleContainer.className = "toggle-container";

    const toggleLabel = document.createElement("label");
    toggleLabel.className = "toggle-label";

    const toggleInput = document.createElement("input");
    toggleInput.type = "checkbox";
    toggleInput.className = "toggle-input";

    const toggleSlider = document.createElement("span");
    toggleSlider.className = "toggle-slider";

    const toggleText = document.createElement("span");
    toggleText.textContent = labelText; // Use parameter
    toggleText.className = "toggle-text";

    toggleLabel.appendChild(toggleInput);
    toggleLabel.appendChild(toggleSlider);
    toggleContainer.appendChild(toggleLabel);
    toggleContainer.appendChild(toggleText);

    toggleInput.addEventListener("change", () => {
        onToggle(toggleInput.checked);
    });

    return toggleContainer;
}

function svg_icon(is_success) {
    if (is_success) {
        return `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M9 16.2l-3.5-3.5-1.4 1.4 4.9 4.9 12-12-1.4-1.4z"/>
            </svg>`;
    } else {
        return `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M18.3 5.71L12 12.01 5.7 5.71 4.29 7.12 10.59 12.42 4.29 18.71 5.7 20.13 12 13.83 18.3 20.13 19.71 18.71 13.41 12.42 19.71 7.12z"/>
            </svg>`;
    }
}

function showNotification(is_success) {
    const existingNotification = document.querySelector(".notification");
    if (existingNotification) {
        existingNotification.remove(); // Remove old notification if present
    }

    // Create notification container
    const notification = document.createElement("div");
    notification.className = `notification ${is_success ? "success" : "failure"}`;

    // Add an icon
    const icon = document.createElement("span");
    icon.className = "notification-icon";
    icon.innerHTML = svg_icon(is_success);
    notification.appendChild(icon);

    // Add message text
    const text = document.createElement("span");
    text.textContent = is_success ? "Done!" : "Failed.";
    notification.appendChild(text);

    // Add notification to the body
    document.body.appendChild(notification);

    // Remove notification after the animation
    setTimeout(() => {
        notification.remove();
    }, 3000); // Match the duration of the CSS animation
}

function showAnimation(is_success) {
    const animation = document.createElement("div");
    animation.className = is_success ? "success-animation" : "failure-animation";
    animation.textContent = is_success ? "Done!" : "Failed.";
    document.body.appendChild(animation);

    setTimeout(() => animation.remove(), 3000);
}

function sendPostRequest(url, videoUrl, localDownload) { // Add parameter
    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
            url: videoUrl,
            local_download: localDownload // Include in payload
        })
    })
    .then((response) => {
        if (response.ok) {
            showNotification(true);
        } else {
            showNotification(false);
        }
    })
    .catch(() => {
        showNotification(false);
    });
}

function addControls() {
    if (document.getElementById("send-url-buttons")) return;

    const aboveTheFoldContainer = document.getElementById("above-the-fold");
    if (!aboveTheFoldContainer) return;

    let useDistantServer = false;
    let localDownload = false; // New state variable

    // Create toggles
    const distantToggle = createToggleSwitch(
        (isDistant) => { useDistantServer = isDistant; },
        "Use Distant Server"
    );
    const localToggle = createToggleSwitch(
        (isLocal) => { localDownload = isLocal; },
        "Download Locally"
    );

    const audioButton = createButton(
        "Audio",
        () => {
            const youtubeUrl = window.location.href;
            const endpoint = useDistantServer
                ? "http://distant-server:12498/audio"
                : "http://localhost:12498/audio";
            sendPostRequest(
                endpoint,
                youtubeUrl,
                localDownload // Pass the state
            );
        }
    );

    const videoButton = createButton(
        "Video",
        () => {
            const youtubeUrl = window.location.href;
            const endpoint = useDistantServer
                ? "http://distant-server:12498/video"
                : "http://localhost:12498/video";
            sendPostRequest(
                endpoint,
                youtubeUrl,
                localDownload // Pass the state
            );
        }
    );

    const controlContainer = document.createElement("div");
    controlContainer.id = "send-url-buttons";
    controlContainer.className = "control-container";
    controlContainer.appendChild(audioButton);
    controlContainer.appendChild(videoButton);
    controlContainer.appendChild(distantToggle);
    controlContainer.appendChild(localToggle); // Add new toggle

    aboveTheFoldContainer.parentNode.insertBefore(controlContainer, aboveTheFoldContainer);

    observer.disconnect();
}

function observeAboveTheFold() {
    const observer = new MutationObserver((_, obs) => {
        const aboveTheFoldContainer = document.getElementById("above-the-fold");
        if (aboveTheFoldContainer) {
            addControls();
            obs.disconnect(); // Stop observing once the target container is found
        }
    });

    // Start observing changes in the document body
    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
}

// Initialize the script with a smaller div
observeAboveTheFold();