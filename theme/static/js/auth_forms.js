/**
 * auth_forms.js
 * Handles:
 *   - Password show/hide toggles
 *   - Registration success toast messages
 */

// ================================
// 1. Password visibility toggle
// ================================

function togglePassword(fieldId, button) {
  const input = document.getElementById(fieldId);
  if (!input) return;

  const isHidden = input.type === "password";
  input.type = isHidden ? "text" : "password";

  // Update icon (swap between "eye" and "eye-off")
  button.innerHTML = isHidden
    ? `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
             stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
          <path stroke-linecap="round" stroke-linejoin="round"
                d="M3.98 8.223C6.225 5.728 9.024 4.5 12 4.5c3.6 0 6.75 2.25 9 6-2.25 3.75-5.4 6-9 6-1.17 0-2.28-.207-3.312-.582M3 3l18 18" />
        </svg>`
    : `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
             stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
          <path stroke-linecap="round" stroke-linejoin="round"
                d="M2.25 12s3.75-6.75 9.75-6.75S21.75 12 21.75 12s-3.75 6.75-9.75 6.75S2.25 12 2.25 12z" />
          <circle cx="12" cy="12" r="3" />
        </svg>`;
}

// Make function globally available to inline `onclick`
window.togglePassword = togglePassword;

// ================================
// 2. Registration toast handler
// ================================

(function showRegistrationToast() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("registered") === "1") {
    const username = params.get("u") || "";
    const toastRoot = document.getElementById("toast-root");

    if (toastRoot) {
      const div = document.createElement("div");
      div.className =
        "px-4 py-3 rounded-lg border bg-green-50 border-green-200 text-green-800 shadow";
      div.textContent = username
        ? `Compte créé pour ${username}. Vous pouvez maintenant vous connecter.`
        : "Compte créé. Vous pouvez maintenant vous connecter.";
      toastRoot.appendChild(div);

      // Clean URL (remove query params) and auto-dismiss
      const url = new URL(window.location);
      url.searchParams.delete("registered");
      url.searchParams.delete("u");
      window.history.replaceState({}, "", url);
      setTimeout(() => div.remove(), 5000);
    }
  }
})();
