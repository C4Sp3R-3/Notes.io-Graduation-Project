async function loadUserNotes() {
        const response = await fetch("/api/handle-note", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                action: "list",
            })
        });

        const result = await response.json();

        if (response.ok && result.notes) {
            const container = document.getElementById("pages-container");
            container.innerHTML = "";

            const sortedNotes = result.notes.slice().sort((a, b) => {
                const dateA = new Date(a.updatedAt);
                const dateB = new Date(b.updatedAt);
                return dateB - dateA;
            });

            sortedNotes.forEach(note => {
                let noteTitle = note.title;
                const div = document.createElement("div");
                div.className = "notes-page-item d-flex align-items-center px-3 py-2 mb-1";
                div.setAttribute("data-title", note.title);
                div.setAttribute("data-note-id", note.id);
                div.style.cursor = "pointer";

                div.innerHTML = `
                    <div class="d-flex align-items-center w-100 position-relative">
                        <i class="bi bi-file-earmark me-2 text-muted small"></i>
                        <span class="me-auto">${noteTitle}</span>
                        <div class="dropdown">
                            <i class="bi bi-three-dots" data-bs-toggle="dropdown" aria-expanded="false" style="cursor: pointer;"></i>
                            <ul class="dropdown-menu custom-note-dropdown shadow-sm">
                                <li>
                                    <a class="dropdown-item text-danger d-flex align-items-center delete-note" href="#">
                                        <i class="bi bi-trash me-2"></i> Delete
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>
                `;


                div.addEventListener("click", () => {
                    highlightActiveNote(note.id);
                    loadNoteIntoEditor(note.id);
                });

                // Prevent dropdown from triggering note click
                    div.querySelector(".bi-three-dots").addEventListener("click", e => e.stopPropagation());

                    // Delete note logic
                    div.querySelector(".delete-note").addEventListener("click", async (e) => {
                        e.preventDefault();
                        e.stopPropagation();


                        const res = await fetch("/api/handle-note", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                action: "delete",
                                note: { id: note.id }
                            })
                        });

                        if (res.ok) loadUserNotes();
                        else alert("Failed to delete note.");
                    });



                container.appendChild(div);
            });

            if (window.location.pathname === "/" && sortedNotes.length > 0) {
                const firstNoteDiv = container.querySelector(`[data-note-id="${sortedNotes[0].id}"]`);
                if (firstNoteDiv) firstNoteDiv.click();  // simulate user click
            } else if (window.location.pathname === "/" && sortedNotes.length === 0) {
                window.location.href = `/getting-started`;
            } else {
                const currentNoteId = window.location.pathname.replace("/", "");
                highlightActiveNote(currentNoteId); // highlight on refresh or deep-link
            }
        } else {
            console.error("Failed to load notes:", result.error);
        }
    }

    async function filterNotes(searchTerm) {
    const response = await fetch("/api/handle-note", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            action: "list",
        })
    });

    const result = await response.json();
    if (!response.ok || !result.notes) return;

    const container = document.getElementById("pages-container");
    container.innerHTML = "";

    const filteredNotes = result.notes
        .filter(note => note.title.toLowerCase().includes(searchTerm.toLowerCase()))
        .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));

    filteredNotes.forEach(note => {
        const div = document.createElement("div");
        div.className = "notes-page-item d-flex align-items-center px-3 py-2 mb-1";
        div.setAttribute("data-title", note.title);
        div.setAttribute("data-note-id", note.id);
        div.style.cursor = "pointer";

        div.innerHTML = `
            <div class="d-flex align-items-center w-100 position-relative">
                <i class="bi bi-file-earmark me-2 text-muted small"></i>
                <span class="me-auto">${note.title}</span>
                <div class="dropdown">
                    <i class="bi bi-three-dots" data-bs-toggle="dropdown" aria-expanded="false" style="cursor: pointer;"></i>
                    <ul class="dropdown-menu custom-note-dropdown shadow-sm">
                        <li>
                            <a class="dropdown-item text-danger d-flex align-items-center delete-note" href="#">
                                <i class="bi bi-trash me-2"></i> Delete
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        `;

        div.addEventListener("click", () => {
            highlightActiveNote(note.id);
            loadNoteIntoEditor(note.id);
        });

        div.querySelector(".bi-three-dots").addEventListener("click", e => e.stopPropagation());
        div.querySelector(".delete-note").addEventListener("click", async (e) => {
            e.preventDefault();
            e.stopPropagation();

            const res = await fetch("/api/handle-note", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    action: "delete",
                    note: { id: note.id }
                })
            });

            if (res.ok) filterNotes(document.getElementById("page-search").value);
            else alert("Failed to delete note.");
        });

        container.appendChild(div);
    });

    if (window.location.pathname === "/" && filteredNotes.length > 0) {
        const firstNoteDiv = container.querySelector(`[data-note-id="${filteredNotes[0].id}"]`);
        if (firstNoteDiv) firstNoteDiv.click();
    }
}

    async function loadNoteIntoEditor(noteId) {
        document.getElementById("page-search").value = '';
        const pathSegments = window.location.pathname.split('/').filter(segment => segment);
        const lastSegment = pathSegments[pathSegments.length - 1];
        if (lastSegment === "settings") window.location.href = `/${noteId}`;
        const response = await fetch("/api/handle-note", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                action: "get",
                note: { id: noteId }
            })
        });

        const result = await response.json();
        if (response.ok && result.note) {
            const contentJson = result.note.contentJson;
            const title = result.note.title;
            window.notePublicity = result.note.publicRead; // can be toggled by user
            setPublicReadChecked(window.notePublicity);


            if (window.editorjsInterop.instance) {
                await window.editorjsInterop.instance.destroy();
                window.editorjsInterop.instance = null;
            }

            history.pushState({}, "", `/${noteId}`);

            const titleInput = document.getElementById("note-title");
            if(title == "Untitled Note")
            titleInput.value = '';
            else
            titleInput.value = title;


            window.editorjsInterop.init(contentJson);
        } else {
            console.error("Failed to load note:", result.error);
        }
    }

    function highlightActiveNote(noteId) {
        document.querySelectorAll(".notes-page-item").forEach(el => {
            el.classList.remove("active", "bg-secondary-subtle");
            if (el.getAttribute("data-note-id") === noteId) {
                el.classList.add("active", "bg-secondary-subtle");
            }
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        loadUserNotes();
    });