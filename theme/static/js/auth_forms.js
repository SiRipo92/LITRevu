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

function togglePassword(fieldId, button) {
  const input = document.getElementById(fieldId);
  if (!input) return;

  const isHidden = input.type === "password";
  input.type = isHidden ? "text" : "password";

  button.innerHTML = isHidden
    ? `<svg ... eye-off ...></svg>`
    : `<svg ... eye-on ...></svg>`;
}

window.togglePassword = togglePassword;


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