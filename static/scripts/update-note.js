let autoSaveTimer = null;
let lastSavedContent = "";
let lastSavedTitle = "";

/**
 * Starts or restarts the auto-save debounce timer.
 */
function startAutoSaveTimer() {
    if (autoSaveTimer) clearTimeout(autoSaveTimer);

    autoSaveTimer = setTimeout(async () => {
        const currentContent = await window.editorjsInterop.getContent();
        const currentTitle = document.getElementById("note-title")?.value.trim() || "";

        if (
            currentContent !== lastSavedContent ||
            currentTitle !== lastSavedTitle
        ) {
            const response = await fetch("/api/handle-note", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    action: "update",
                    note: {
                        id: window.note_id, // Make sure this is globally set!
                        title: currentTitle || "Untitled Note",
                        contentJson: currentContent,
                        publicRead: window.notePublicity
                    }
                })
            });

            if (response.ok) {
                console.log("Note auto-saved");
                lastSavedContent = currentContent;
                lastSavedTitle = currentTitle;
                loadUserNotes();
            } else {
                const error = await response.json();
                console.error("Auto-save failed:", error.error || error);
            }
        }
    }, 1000); // 1-second debounce
}

// ⏳ Listen to editor and title input changes
document.addEventListener("DOMContentLoaded", () => {
    const titleInput = document.getElementById("note-title");

    if (titleInput) {
        titleInput.addEventListener("input", () => {
            startAutoSaveTimer();
        });
    }

    if (window.editorjsInterop?.instance) {
        window.editorjsInterop.instance.onChange = () => {
            startAutoSaveTimer();
        };
    }
});
