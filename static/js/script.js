
// ==========================
// PREVENT PAST DATE BOOKING
// ==========================
document.addEventListener("DOMContentLoaded", function () {
    const dateInput = document.querySelector('input[type="date"]');

    if (dateInput) {
        const today = new Date().toISOString().split("T")[0];
        dateInput.setAttribute("min", today);
    }
});


// ==========================
// CONFIRM DELETE ACTION
// ==========================
document.addEventListener("DOMContentLoaded", function () {
    const deleteForms = document.querySelectorAll('form[action*="delete"]');

    deleteForms.forEach(form => {
        form.addEventListener("submit", function (e) {
            const confirmDelete = confirm("Are you sure you want to delete this?");
            if (!confirmDelete) {
                e.preventDefault();
            }
        });
    });
});


// ==========================
// SIMPLE FORM VALIDATION
// ==========================
document.addEventListener("DOMContentLoaded", function () {
    const forms = document.querySelectorAll("form");

    forms.forEach(form => {
        form.addEventListener("submit", function (e) {
            const inputs = form.querySelectorAll("input[required], select[required]");

            for (let input of inputs) {
                if (!input.value.trim()) {
                    alert("Please fill all required fields");
                    e.preventDefault();
                    return;
                }
            }
        });
    });
});


// ==========================
// AUTO HIDE ALERTS (future use)
// ==========================
document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.display = "none";
        }, 3000);
    });
});