console.log("---------- venue.js LOADED ----------");

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}

// Handle create and edit venue form submissions
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("venue-form");
    if (!form) return;

    const errorBox = document.getElementById("ajax-errors");
    const submitBtn = form.querySelector("button[type=submit]");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.dataset.origText = submitBtn.innerText;
            submitBtn.innerText = "Saving...";
        }

        if (errorBox) errorBox.innerHTML = "";

        const formData = new FormData(form);

        try {
            const resp = await fetch(form.action || window.location.href, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie("csrftoken")
                }
            });

            const data = await resp.json();

            if (resp.ok && data.ok) {
                if (data.redirect) {
                    window.location.href = data.redirect;
                    return;
                }
                window.location.reload();
                return;
            }

            if (data.errors) {
                let html = "";
                for (const [field, msgs] of Object.entries(data.errors)) {
                    html += `<div style="color:red;"><strong>${field}:</strong> ${msgs}</div>`;
                }
                errorBox.innerHTML = html;
            }

            if (!data.ok && !data.errors) {
                errorBox.innerHTML = `<div style="color:red;">${data.error || "Unknown error occurred."}</div>`;
            }

        } catch (err) {
            if (errorBox) errorBox.innerHTML = `<div style="color:red;">Network error: ${err.message}</div>`;
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerText = submitBtn.dataset.origText || "Save";
            }
        }
    });
});

// Handle delete venue via AJAX
document.addEventListener("DOMContentLoaded", function () {
    const deleteButtons = document.querySelectorAll(".deleteVenueBtn");
    
    deleteButtons.forEach(button => {
        button.addEventListener("click", async function (e) {
            e.preventDefault();
            
            const venueId = this.dataset.id;
            const deleteUrl = this.dataset.url;
            
            // Confirm deletion
            if (!confirm("Are you sure you want to delete this venue?")) {
                return;
            }
            
            try {
                const resp = await fetch(deleteUrl, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": getCookie("csrftoken")
                    }
                });
                
                const data = await resp.json();
                
                if (resp.ok && data.ok) {
                    if (data.redirect) {
                        window.location.href = data.redirect;
                        return;
                    }
                    window.location.reload();
                    return;
                }
                
                alert(`Error: ${data.error || "Failed to delete venue"}`);
            } catch (err) {
                alert(`Network error: ${err.message}`);
            }
        });
    });
});
