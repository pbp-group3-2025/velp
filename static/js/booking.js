console.log("---------- booking.js LOADED ----------");

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("booking-form");
    if (!form) return;

    const errorBox = document.getElementById("ajax-errors");
    const submitBtn = form.querySelector("button[type=submit]");

    form.addEventListener("submit", async function (e) {
        e.preventDefault();

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.dataset.origText = submitBtn.innerText;
            submitBtn.innerText = "Booking...";
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

            if (data.non_field_error) {
                errorBox.innerHTML = `<div style="color:red;">${data.non_field_error}</div>`;
            }

            if (data.errors) {
                let html = "";
                for (const [field, msgs] of Object.entries(data.errors)) {
                    html += `<div style="color:red;"><strong>${field}:</strong> ${msgs}</div>`;
                }
                errorBox.innerHTML = html;
            }

            if (!data.ok && !data.errors && !data.non_field_error) {
                errorBox.innerHTML = `<div style="color:red;">Unknown error occurred.</div>`;
            }

        } catch (err) {
            if (errorBox) errorBox.innerHTML = `<div style="color:red;">Network error: ${err.message}</div>`;
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerText = submitBtn.dataset.origText || "Create Booking";
            }
        }
    });
});
