/**
 * auth_forms.js
 * Handles:
 *   - Password show/hide toggles
 *   - Generic toast helper (a11y-aware)
 *   - Registration + Logout toasts via URL query params
 */

 // ================================
// 0) Small utilities
// ================================

function getToastRoot() {
  return document.getElementById("toast-root");
}

function sanitize(text) {
  // Simple guard to avoid injecting raw HTML
  const div = document.createElement("div");
  div.textContent = String(text == null ? "" : text);
  return div.textContent;
}

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
/**
 * 2) Reusable toast helper (a11y-aware)
 *
 * showToast({
 *   message: string,
 *   type?: "success" | "info" | "error",  // default: "info"
 *   timeoutMs?: number                     // default: 5000
 * })
 */
// ================================

function showToast({ message, type = "info", timeoutMs = 5000 } = {}) {
  const root = getToastRoot();
  if (!root) return;

  const palette = {
    success: {
      container: "bg-green-50 border-green-200 text-green-800",
    },
    info: {
      container: "bg-blue-50 border-blue-200 text-blue-800",
    },
    error: {
      container: "bg-red-50 border-red-200 text-red-800",
    },
  };

  const styles = palette[type] || palette.info;

  const div = document.createElement("div");
  div.setAttribute("role", "alert"); // announce this specific toast
  div.className =
    "inline-block pointer-events-auto px-4 py-3 mb-2 rounded-lg border " +
  `${styles.container} shadow text-base`;

  // Keep content text-only for safety
  div.textContent = sanitize(message);

  // Insert & auto-dismiss
  root.appendChild(div);
  if (timeoutMs > 0) {
    setTimeout(() => {
      if (div && div.parentNode === root) div.remove();
    }, timeoutMs);
  }

  return div; // useful for testing
}

// Expose a controlled test hook (optional)
if (!window.__auth_toast__) {
  window.__auth_toast__ = { showToast };
}

// ================================
// 3) Query-param driven toasts
//    - Registration (?registered=1&u=username)
//    - Logout (?logout=1)
// ================================

(function handleQueryParamToasts() {
  const url = new URL(window.location);
  const params = url.searchParams;

  // Registration success
  if (params.get("registered") === "1") {
    const username = sanitize(params.get("u") || "");
    const message = username
      ? `Compte créé pour ${username}. Vous pouvez maintenant vous connecter.`
      : "Compte créé. Vous pouvez maintenant vous connecter.";

    showToast({ message, type: "success", timeoutMs: 5000 });

    // Clean URL
    params.delete("registered");
    params.delete("u");
    window.history.replaceState({}, "", url);
  }

  // Logout info
  if (params.get("logout") === "1") {
    showToast({ message: "Vous avez été déconnecté(e).", type: "info", timeoutMs: 5000 });

    // Clean URL
    params.delete("logout");
    window.history.replaceState({}, "", url);
  }
})();