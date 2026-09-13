(() => {
  "use strict";
  const content = window.PSR_CONTENT;
  document.getElementById("hosting-note").textContent = content.hosting.statusDescription;
  document.getElementById("example-caveat").textContent = content.example.briefCaveat;
  document.getElementById("instructions-source").textContent = window.PSR_REFERENCE.instructions;
  document.getElementById("topics-source").textContent = JSON.stringify(window.PSR_REFERENCE.topics, null, 2);
  document.getElementById("instruction-fingerprint").textContent = "Generic project instruction reference—not an installer, evaluation or new runtime acceptance.";
  const theme = document.getElementById("theme-toggle");
  const labelTheme = () => {
    const dark = document.documentElement.dataset.theme === "dark";
    theme.textContent = dark ? "Light theme" : "Dark theme";
    theme.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
  };
  labelTheme();
  theme.addEventListener("click", () => {
    document.documentElement.dataset.theme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    labelTheme();
  });
  const viewer = document.getElementById("image-viewer");
  const canvas = document.getElementById("viewer-canvas");
  const zoom = document.getElementById("viewer-zoom");
  let priorOverflow = "";
  document.querySelectorAll("figure.screenshot").forEach(figure => {
    const caption = figure.querySelector("figcaption");
    const link = document.createElement("a");
    link.className = "full-size-link";
    link.textContent = "Open full-size image ↗";
    link.href = figure.querySelector("a.image-link").getAttribute("href");
    caption.append(link);
  });
  document.querySelectorAll("a.image-link, a.full-size-link").forEach(link => {
    link.addEventListener("click", event => {
      if (!viewer.showModal || event.button !== 0 || event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) return;
      event.preventDefault();
      const figure = link.closest("figure");
      const image = new Image();
      image.src = link.href;
      image.alt = figure.querySelector("img").alt;
      canvas.replaceChildren(image);
      canvas.classList.remove("actual-size");
      zoom.textContent = "Actual size";
      zoom.setAttribute("aria-pressed", "false");
      document.getElementById("viewer-caption").textContent = figure.querySelector("figcaption").textContent;
      document.getElementById("viewer-file").href = link.href;
      priorOverflow = document.documentElement.style.overflow;
      document.documentElement.style.overflow = "hidden";
      viewer.showModal();
      canvas.scrollTo(0, 0);
    });
  });
  zoom.addEventListener("click", () => {
    const actual = canvas.classList.toggle("actual-size");
    zoom.setAttribute("aria-pressed", String(actual));
    zoom.textContent = actual ? "Fit to width" : "Actual size";
    canvas.focus();
  });
  document.getElementById("viewer-close").addEventListener("click", () => viewer.close());
  viewer.addEventListener("close", () => { document.documentElement.style.overflow = priorOverflow; });
  viewer.addEventListener("click", event => { if (event.target === viewer) viewer.close(); });
  document.querySelectorAll("[data-copy]").forEach(button => {
    button.addEventListener("click", async () => {
      const source = document.getElementById(button.dataset.copy);
      try {
        await navigator.clipboard.writeText(source.textContent);
        button.textContent = "Copied";
      } catch {
        const range = document.createRange();
        range.selectNodeContents(source);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
      }
      document.getElementById("copy-status").textContent = "Generic project reference copied or selected.";
    });
  });
})();
