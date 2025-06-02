const toggle = document.getElementById('toggleSwitch');
const saveButton = document.getElementById('saveButton');
const statusText = document.getElementById('statusText');

toggle.addEventListener('change', () => {
const isEnabled = toggle.checked;

fetch("/api/update_mfa", {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify({
        enabled: isEnabled,
        })
    })
        .then(response => {
        if (!response.ok) throw new Error("Server error");
        return response.json(); // optional: parse server response
        })
        .then(data => {
        statusText.textContent = isEnabled
            ? "Status: Enabled"
            : "Status: Disabled";
        })
        .catch(error => {
        console.error("Failed to update MFA status:", error);
        statusText.textContent = "Status: Error";
        });
    });


saveButton.addEventListener('click', (event) => {
    event.preventDefault();
fetch("/api/update_user_settings", {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify({
        username : document.getElementById("usernameInput").value,
        email : document.getElementById("emailInput").value
        })
    })
        .then(response => {
        if (!response.ok) throw new Error("Server error");
        return response.json(); // optional: parse server response
        })
        .then(data => {
        console.log("Updated user settings")
        }).catch(error => {
        console.error("Failed to update user settings", error);
        });
    });
