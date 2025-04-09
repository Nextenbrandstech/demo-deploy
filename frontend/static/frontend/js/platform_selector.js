document.addEventListener("DOMContentLoaded", function () {
    // Select the form and the dropdown
    const form = document.querySelector("form");
    const platformSelect = document.getElementById("platform");

    // Attach an event listener to the form's submit event
    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent the default form submission behavior

        // Get the selected platform
        const selectedPlatform = platformSelect.value;

        // Redirect based on the selected platform
        if (selectedPlatform === "flipkart") {
            window.location.href = "/frontend/fk_insights/";
        } 
        else if (selectedPlatform === "amazon") {
            window.location.href = "/frontend/amz_insights/";
        } 
        else if (selectedPlatform === "d2c") {
            window.location.href = "/frontend/d2c_insights/";
        }
        else if (selectedPlatform === "meesho") {
            window.location.href = "/frontend/meesho_insights/";
        }
        else if (selectedPlatform === "jiomart") {
            window.location.href = "/frontend/jiomart_insights/";
        }
        else {
            alert("Invalid platform selected. Please try again."); // Optional error handling
        }
    });
});
