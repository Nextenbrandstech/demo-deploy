document.addEventListener("DOMContentLoaded", function () {
    // Define the URL for the API endpoint
    const apiUrl = "/backend/api/jiomart_insights/";

    // Fetch the data from the API
    fetch(apiUrl)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json(); // Parse the JSON response
        })
        .then((data) => {
            // Display the message in the UI
            const messageContainer = document.getElementById("message-container");
            messageContainer.textContent = data.message; // Display the message
        })
        .catch((error) => {
            console.error("Error fetching data:", error);
            const messageContainer = document.getElementById("message-container");
            messageContainer.textContent = "Failed to load insights. Please try again later.";
        });
});