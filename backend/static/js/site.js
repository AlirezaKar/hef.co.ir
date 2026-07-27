(function () {
  const shell = document.getElementById("appShell");
  const collapseBtn = document.getElementById("sidebarCollapse");
  const toggleBtn = document.getElementById("sidebarToggle");

  if (collapseBtn && shell) {
    collapseBtn.addEventListener("click", function () {
      shell.classList.toggle("collapsed");
      collapseBtn.textContent = shell.classList.contains("collapsed") ? "»" : "«";
    });
  }

  if (toggleBtn && shell) {
    toggleBtn.addEventListener("click", function () {
      shell.classList.toggle("sidebar-open");
    });
  }

  // Auto-hide toasts
  document.querySelectorAll(".toast-item").forEach(function (el) {
    setTimeout(function () {
      el.style.opacity = "0";
      el.style.transition = "opacity .4s";
      setTimeout(function () { el.remove(); }, 400);
    }, 4000);
  });

  // Report folder scan version polling — reload page when version changes
  if (window.HEF_SCAN && window.HEF_SCAN.endpoint) {
    var current = Number(window.HEF_SCAN.version || 0);
    setInterval(function () {
      fetch(window.HEF_SCAN.endpoint, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
        credentials: "same-origin",
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (typeof data.scan_version === "number" && data.scan_version !== current) {
            window.location.reload();
          }
        })
        .catch(function () { /* ignore transient errors */ });
    }, 15000);
  }
})();
