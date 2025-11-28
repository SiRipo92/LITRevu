// pagination.js – AJAX-enhanced pagination for feed & "Mes Posts"

(function () {
  function onClick(event) {
    const link = event.target.closest("[data-page-link]");
    if (!link) {
      return;
    }

    // Only intercept a normal left-click without modifier keys
    if (
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) {
      return;
    }

    event.preventDefault();

    const url = link.href;
    const container = document.querySelector("[data-feed-container]");

    if (!container) {
      // Fallback: if container not found, just navigate normally
      window.location.href = url;
      return;
    }

    fetch(url, {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.text();
      })
      .then((html) => {
        container.innerHTML = html;
        window.history.pushState({}, "", url);
        window.scrollTo({ top: 0, behavior: "smooth" });
      })
      .catch(() => {
        // On error, fall back to normal navigation
        window.location.href = url;
      });
  }

  document.addEventListener("click", onClick);
})();