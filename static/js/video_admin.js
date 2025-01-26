document.addEventListener("DOMContentLoaded", function () {
    const videoInput = document.querySelector("#id_video"); // Adjust selector to match the "Video" field
    const nameInput = document.querySelector("#id_name"); // Adjust selector to match the "Name" field

    if (videoInput && nameInput) {
        videoInput.addEventListener("change", function () {
            const fileName = videoInput.files[0]?.name || ""; // Get the file name
            const baseName = fileName.split(".").slice(0, -1).join("."); // Remove the file extension
            nameInput.value = baseName; // Set the name input value
        });
    }
});
