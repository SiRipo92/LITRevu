// ===============================
// Toast Root & Sanitizer
// ===============================

function getToastRoot() {
  return document.getElementById("toast-root");
}

function sanitize(text) {
  const div = document.createElement("div");
  div.textContent = String(text || "");
  return div.textContent;
}

// ===============================
// Toast Display Function
// ===============================

function showToast({ message, type = "info", timeoutMs = 5000 } = {}) {
  const root = getToastRoot();
  if (!root) return;

  const palette = {
    success: { classes: "bg-green-50 border-green-200 text-green-800" },
    info:    { classes: "bg-blue-50 border-blue-200 text-blue-800" },
    error:   { classes: "bg-red-50 border-red-200 text-red-800" },
  };

  const { classes } = palette[type] || palette.info;

  const div = document.createElement("div");
  div.setAttribute("role", "alert");
  div.className = `inline-block px-4 py-3 mb-2 rounded-lg border shadow ${classes}`;
  div.textContent = sanitize(message);

  root.appendChild(div);

  if (timeoutMs > 0) {
    setTimeout(() => div.remove(), timeoutMs);
  }

  return div;
}

// Expose globally to the whole site
window.toast = { showToast };


// ===============================================
// NEW: Global Query-Param Toast Loader (ALL pages)
// ===============================================

(function handleGenericToastParams() {
  const url = new URL(window.location);
  const params = url.searchParams;

  const msg = params.get("toast_msg");
  const type = params.get("toast_type");

  if (msg) {
    showToast({
      message: msg,
      type: type || "info",
      timeoutMs: 5000
    });

    // Clean URL
    params.delete("toast_msg");
    params.delete("toast_type");
    window.history.replaceState({}, "", url);
  }
})();