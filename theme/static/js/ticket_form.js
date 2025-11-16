// Adds a button to remove any uploaded image files in form and disables/enables the download button
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("id_image");
    const fileInfo = document.getElementById("file-info");
    const fileName = document.getElementById("file-name");
    const uploadLabel = document.getElementById("upload-label");
    const removeBtn = document.getElementById("remove-file");

    if (!input || !uploadLabel || !removeBtn) return;

    // === Detect if editing mode has an existing image ===
    const currentImage = document.getElementById("current-image");
    if (currentImage) {
        // Disable upload when an image already exists
        uploadLabel.classList.add("opacity-60", "cursor-not-allowed");
        uploadLabel.removeAttribute("for");

        // Show delete button to allow image removal
        removeBtn.classList.remove("hidden");
    }

    // === Handle new file selection ===
    input.addEventListener("change", () => {
        if (input.files && input.files[0]) {
            const file = input.files[0];
            fileName.textContent = file.name;

            // Show filename + delete button
            fileInfo.classList.remove("hidden");
            removeBtn.classList.remove("hidden");

            // Disable upload button once a file is chosen
            uploadLabel.classList.add("opacity-60", "cursor-not-allowed");
            uploadLabel.removeAttribute("for");
        }
    });

    // === Handle image deletion ===
    removeBtn.addEventListener("click", () => {
        input.value = "";
        const deleteFlag = document.getElementById("delete_existing_image");
        if (deleteFlag) deleteFlag.value = "true";

        // Remove existing image preview if present
        if (currentImage) currentImage.remove();

        // Hide filename + reset buttons
        fileInfo.classList.add("hidden");
        removeBtn.classList.add("hidden");

        // Re-enable upload button
        uploadLabel.classList.remove("opacity-60", "cursor-not-allowed");
        uploadLabel.setAttribute("for", "id_image");
    });
});
