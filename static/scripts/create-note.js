async function newNote() {


        const response = await fetch("/api/handle-note", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                action: "create",
                note: {
                    //title: "",
                    contentJson: "",
                }
            })
        });

        if (!response.ok) {
            const error = await response.json();
            alert("Failed to save note: " + error.error);
            return;
        }

        const result = await response.json();
        const noteId = result.note.id;
        loadNoteIntoEditor(noteId);
        loadUserNotes();
        highlightActiveNote(noteId)
    }