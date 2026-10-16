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

  // ── Notification bell ──
  (function () {
    var bellBtn = document.getElementById("notifBellBtn");
    var badge = document.getElementById("notifBadge");
    var body = document.getElementById("notifDropdownBody");
    var markReadBtn = document.getElementById("notifMarkReadBtn");
    if (!bellBtn || !body) return;

    var MARK_READ_URL = bellBtn.closest(".dropdown")
      ? "" : "";
    // Find URLs from the page context
    var notifApiUrl = document.querySelector('meta[name="notif-api-url"]');
    var markReadUrl = document.querySelector('meta[name="notif-mark-read-url"]');
    if (notifApiUrl) notifApiUrl = notifApiUrl.getAttribute("content");
    if (markReadUrl) markReadUrl = markReadUrl.getAttribute("content");

    function timeAgo(iso) {
      try {
        var d = new Date(iso);
        var now = new Date();
        var diff = Math.floor((now - d) / 1000);
        if (diff < 60) return diff + "s";
        if (diff < 3600) return Math.floor(diff / 60) + "m";
        if (diff < 86400) return Math.floor(diff / 3600) + "h";
        return Math.floor(diff / 86400) + "d";
      } catch (e) { return ""; }
    }

    function renderNotifications(data) {
      // Badge
      if (data.unread_count > 0) {
        badge.textContent = data.unread_count > 99 ? "99+" : data.unread_count;
        badge.classList.remove("d-none");
      } else {
        badge.classList.add("d-none");
      }
      // Body
      if (!data.notifications.length) {
        body.innerHTML = '<p class="notif-empty">' +
          (bellBtn.getAttribute("data-no-notif") || "No notifications") +
          "</p>";
        return;
      }
      var html = "";
      data.notifications.forEach(function (n) {
        var cls = n.is_read ? "read" : "unread";
        var href = "#";
        html += '<a class="notif-item ' + cls + '" href="' + href + '">';
        html += '<span class="notif-dot"></span>';
        html += '<span class="notif-msg">' + escapeHtml(n.message);
        html += '<span class="notif-time">' + timeAgo(n.created_at) + "</span>";
        html += "</span></a>";
      });
      body.innerHTML = html;
    }

    function escapeHtml(s) {
      var div = document.createElement("div");
      div.appendChild(document.createTextNode(s));
      return div.innerHTML;
    }

    function fetchNotifications() {
      if (!notifApiUrl) return;
      fetch(notifApiUrl, { credentials: "same-origin" })
        .then(function (r) { return r.json(); })
        .then(renderNotifications)
        .catch(function () {});
    }

    // Fetch on page load, then every 60s
    fetchNotifications();
    setInterval(fetchNotifications, 60000);

    // Mark all read
    if (markReadBtn && markReadUrl) {
      markReadBtn.addEventListener("click", function (e) {
        e.preventDefault();
        fetch(markReadUrl, {
          method: "POST",
          credentials: "same-origin",
          headers: { "X-CSRFToken": getCsrfToken() },
        })
          .then(function () { fetchNotifications(); })
          .catch(function () {});
      });
    }

    function getCsrfToken() {
      var m = document.querySelector("[name=csrfmiddlewaretoken]");
      if (m) return m.value;
      var c = document.cookie.match(/csrftoken=([^;]+)/);
      return c ? c[1] : "";
    }
  })();

  // Adobe Connect FAQ accordion
  document.addEventListener("click", function (e) {
    var question = e.target.closest(".adobe-faq-question");
    if (!question) return;
    var item = question.closest(".adobe-faq-item");
    if (!item) return;
    var faq = item.closest(".adobe-faq");
    if (faq) {
      faq.querySelectorAll(".adobe-faq-item").forEach(function (other) {
        if (other !== item) other.classList.remove("open");
      });
    }
    item.classList.toggle("open");
  });
})();
