(function () {
  document.querySelectorAll(".toast-item").forEach(function (el) {
    setTimeout(function () {
      el.style.opacity = "0";
      el.style.transition = "opacity .4s";
      setTimeout(function () { el.remove(); }, 400);
    }, 4000);
  });
})();
