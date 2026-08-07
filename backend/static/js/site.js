(function () {
  var THEME_KEY = "hef-ui-theme";

  function getRoot() {
    return document.documentElement;
  }

  function applyTheme(theme) {
    var dark = theme === "dark";
    var root = getRoot();
    root.setAttribute("data-bs-theme", dark ? "dark" : "light");
    root.classList.toggle("theme-dark", dark);
    if (document.body) {
      document.body.classList.toggle("theme-dark", dark);
    }

    var btn = document.getElementById("themeToggleBtn");
    if (!btn) return;
    var moon = btn.querySelector(".theme-icon-moon");
    var sun = btn.querySelector(".theme-icon-sun");
    if (moon) {
      if (dark) moon.classList.add("d-none");
      else moon.classList.remove("d-none");
    }
    if (sun) {
      if (dark) sun.classList.remove("d-none");
      else sun.classList.add("d-none");
    }
    btn.setAttribute("aria-pressed", dark ? "true" : "false");
  }

  function currentTheme() {
    return getRoot().getAttribute("data-bs-theme") === "dark" ? "dark" : "light";
  }

  function toggleTheme() {
    var next = currentTheme() === "dark" ? "light" : "dark";
    try {
      localStorage.setItem(THEME_KEY, next);
    } catch (e) { /* ignore */ }
    applyTheme(next);
  }

  function initTheme() {
    var saved = null;
    try {
      saved = localStorage.getItem(THEME_KEY);
    } catch (e) { /* ignore */ }
    applyTheme(saved === "dark" || saved === "light" ? saved : "light");
  }

  // Toasts
  document.querySelectorAll(".toast-item").forEach(function (el) {
    setTimeout(function () {
      el.style.opacity = "0";
      el.style.transition = "opacity .4s";
      setTimeout(function () { el.remove(); }, 400);
    }, 4000);
  });

  initTheme();

  // Delegation so it works even if navbar is re-rendered
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("#themeToggleBtn, [data-theme-toggle]");
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    toggleTheme();
  });
})();
