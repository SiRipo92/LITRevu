// Id-agnostic image upload UI: works with any Django form field id.
// Scopes behavior to each [data-image-upload-section] so multiple forms can coexist.
document.addEventListener("DOMContentLoaded", () => {
  const sections = document.querySelectorAll("[data-image-upload-section]");
  if (!sections.length) return;

  sections.forEach((section) => {
    const input = section.querySelector('input[type="file"]');
    const fileInfo = section.querySelector("[data-file-info]");
    const fileName = section.querySelector("[data-file-name]");
    const uploadLabel = section.querySelector("[data-upload-label]");
    const removeBtn = section.querySelector("[data-remove-file]");
    const deleteFlag = section.querySelector("[data-delete-flag]");
    const currentImage = section.querySelector("[data-current-image]");

    if (!input || !uploadLabel || !removeBtn) return;

    // Wire the label to the actual input id
    if (input.id) uploadLabel.htmlFor = input.id;

    // If there's already an image (editing mode), disable upload & show remove
    if (currentImage) {
      uploadLabel.classList.add("opacity-60", "cursor-not-allowed");
      uploadLabel.removeAttribute("for"); // clicking label shouldn't open picker while an image exists
      removeBtn.classList.remove("hidden");
    }

    // New file selection
    input.addEventListener("change", () => {
      if (input.files && input.files[0]) {
        const file = input.files[0];
        if (fileInfo && fileName) {
          fileName.textContent = file.name;
          fileInfo.classList.remove("hidden");
        }
        removeBtn.classList.remove("hidden");
        uploadLabel.classList.add("opacity-60", "cursor-not-allowed");
        uploadLabel.removeAttribute("for");
        if (deleteFlag) deleteFlag.value = "false"; // reset if user re-selects
      }
    });

    // Delete / clear selection or existing image
    removeBtn.addEventListener("click", () => {
      // clear chosen file
      input.value = "";
      // mark delete flag (for server-side removal if an image already existed)
      if (deleteFlag) deleteFlag.value = "true";
      // remove preview if present
      if (currentImage) currentImage.remove();
      // hide filename
      if (fileInfo) fileInfo.classList.add("hidden");
      removeBtn.classList.add("hidden");
      // re-enable the upload label to open picker again
      uploadLabel.classList.remove("opacity-60", "cursor-not-allowed");
      if (input.id) uploadLabel.htmlFor = input.id;
    });
  });
});
