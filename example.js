(() => {
  "use strict";
  const root = document.documentElement;
  const button = document.getElementById("theme-toggle");
  const label = () => {
    const dark = root.dataset.theme === "dark";
    button.textContent = dark ? "Light theme" : "Dark theme";
    button.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
  };
  label();
  button.addEventListener("click", () => { root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark"; label(); });
  const print = document.getElementById("print-example");
  print.hidden = false;
  print.addEventListener("click", () => window.print());
  if (matchMedia("(max-width: 1000px)").matches) document.querySelector(".example-toc details").open = false;
})();
