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
})();
