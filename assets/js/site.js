/* (C) PSK OG Marienheide e.V., VR/Köln 1369 */
(() => {
  const root = document.documentElement;
  root.dataset.js = "";
  let preference = "system";
  try {
    const stored = localStorage.getItem("psk-theme");
    if (["light", "dark"].includes(stored)) preference = stored;
  } catch { /* Browser storage is optional. */ }
  root.dataset.theme = preference;
  document.addEventListener("DOMContentLoaded", () => {
    const control = document.querySelector(".theme-control");
    const select = document.querySelector("#farbschema");
    select.value = preference;
    control.hidden = false;
    select.addEventListener("change", () => {
      root.dataset.theme = select.value;
      try {
        if (select.value === "system") localStorage.removeItem("psk-theme");
        else localStorage.setItem("psk-theme", select.value);
      } catch { /* Keep the selection for this page when storage is unavailable. */ }
    });
    const menu = document.querySelector(".menu-toggle");
    menu.hidden = false;
    const closeMenu = () => {
      delete root.dataset.menuOpen;
      menu.setAttribute("aria-expanded", "false");
    };
    menu.addEventListener("click", () => {
      const open = menu.getAttribute("aria-expanded") !== "true";
      menu.setAttribute("aria-expanded", String(open));
      root.toggleAttribute("data-menu-open", open);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && root.hasAttribute("data-menu-open")) {
        closeMenu();
        menu.focus();
      }
    });
    document.querySelectorAll(".site-nav a").forEach((link) => link.addEventListener("click", closeMenu));
  });
})();
