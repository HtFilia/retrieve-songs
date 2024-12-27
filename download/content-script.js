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

function createToggleSwitch(onToggle) {
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
    toggleText.textContent = "Use Distant Server";
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

function showAnimation(is_success) {
    const animation = document.createElement("div");
    animation.className = is_success ? "success-animation" : "failure-animation";
    animation.textContent = is_success ? "Done!" : "Failed.";
    document.body.appendChild(animation);

    setTimeout(() => animation.remove(), 3000);
}

function sendPostRequest(url, videoUrl) {
    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ url: videoUrl })
    })
    .then((response) => {
        if (response.ok) {
            showAnimation(true);
        } else {
            showAnimation(false);
        }
    })
    .catch(() => {
        showAnimation(false);
    });
}

function addControls() {

    if (document.getElementById("send-url-buttons")) return;

    const aboveTheFoldContainer = document.getElementById("above-the-fold");
    if (!aboveTheFoldContainer) return;

    let useDistantServer = false;
    const toggleSwitch = createToggleSwitch((isDistant) => {
        useDistantServer = isDistant;
    });

    const audioButton = createButton(
        "Audio",
        () => {
            const youtubeUrl = window.location.href;
            const endpoint = useDistantServer
                ? "http://distant-server:12498/audio"
                : "http://localhost:12498/audio";
            sendPostRequest(
                endpoint,
                youtubeUrl
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
            youtubeUrl
        );
        }
    );

    const controlContainer = document.createElement("div");
    controlContainer.id = "send-url-buttons";
    controlContainer.className = "control-container";
    controlContainer.appendChild(audioButton);
    controlContainer.appendChild(videoButton);
    controlContainer.appendChild(toggleSwitch);

    aboveTheFoldContainer.parentNode.insertBefore(controlContainer, aboveTheFoldContainer);

    observer.disconnect();
}

function observeAboveTheFold() {
    const observer = new MutationObserver((_, obs) => {
        const aboveTheFoldContainer = document.getElementById("above-the-fold");
        if (aboveTheFoldContainer) {
            addControls();

            // Listen for custom "urlchange" events
            window.addEventListener("urlchange", handleUrlChange);

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