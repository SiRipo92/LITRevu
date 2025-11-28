/**
 * auth_forms.js
 * Handles:
 *   - Password visibility toggle
 *   - Registration + logout toast triggers
 * (Generic toasts are handled in toast.js)
 */


// ===============================
// 1. Password visibility toggle
// ===============================

function initPasswordToggles() {
  const buttons = document.querySelectorAll("[data-password-toggle]");

  buttons.forEach((button) => {
    const targetSelector = button.getAttribute("data-target");
    if (!targetSelector) {
      return;
    }

    const input = document.querySelector(targetSelector);
    if (!input) {
      return;
    }

    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();

      const makeVisible = input.type === "password";
      input.type = makeVisible ? "text" : "password";

      const iconShow = button.querySelector("[data-eye-show]");
      const iconHide = button.querySelector("[data-eye-hide]");

      if (iconShow && iconHide) {
        // When visible: hide open-eye, show closed-eye
        iconShow.classList.toggle("hidden", makeVisible);
        iconHide.classList.toggle("hidden", !makeVisible);
      }
    });
  });
}

// Attach once the DOM is ready
document.addEventListener("DOMContentLoaded", initPasswordToggles);


// ===============================
// 2. Registration + Logout Toasters Only
// ===============================

(function handleAuthToasts() {
  const url = new URL(window.location);
  const params = url.searchParams;

  // Registration
  if (params.get("registered") === "1") {
    const username = params.get("u") || "";
    const msg = username
      ? `Compte créé pour ${username}. Vous pouvez maintenant vous connecter.`
      : "Compte créé. Vous pouvez maintenant vous connecter.";

    window.toast.showToast({ message: msg, type: "success" });

    params.delete("registered");
    params.delete("u");
    window.history.replaceState({}, "", url);
  }

  // Logout
  if (params.get("logout") === "1") {
    window.toast.showToast({
      message: "Vous avez été déconnecté(e).",
      type: "info"
    });

    params.delete("logout");
    window.history.replaceState({}, "", url);
  }
})();