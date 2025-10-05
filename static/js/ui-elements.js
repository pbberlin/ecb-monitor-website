/* Demo data & behaviors in modern vanilla JS (no build step) */

const state = {
  cards: [
    { id: 1, title: "Adaptive Layout", tag: "design", date: "2025-09-20", excerpt: "Mobile-first grid using CSS minmax and Pico containers.", liked: false },
    { id: 2, title: "Accessible Colors", tag: "design", date: "2025-08-12", excerpt: "Brand palette mapped to Pico variables with AA contrast.", liked: false },
    { id: 3, title: "Microinteractions", tag: "dev", date: "2025-09-10", excerpt: "IntersectionObserver for subtle reveal-on-scroll.", liked: true },
    { id: 4, title: "Command Palette", tag: "dev", date: "2025-07-01", excerpt: "⌘K / Ctrl+K quick actions without dependencies.", liked: false },
  ],
};

const qs = (sel, root=document) => root.querySelector(sel);
const qsa = (sel, root=document) => Array.from(root.querySelectorAll(sel));

function init() {
  renderYear();
  mountCards();
  wireSorting();
  wireFilters();
  wireSearch();
  wireLikes();
  wireDialogs();
  wireToasts();
  wireThemeToggle();
  wireCommandPalette();
  wireScrollTop();
  revealOnScroll();
}
document.addEventListener("DOMContentLoaded", init);

/* Footer year */
function renderYear() {
  const now = new Date();
  qs("#year").textContent = now.getFullYear();
}

/* Cards */
function mountCards() {
  const grid = qs("#cardGrid");
  grid.innerHTML = "";
  for (let i = 0; i < state.cards.length; i += 1) {
    const c = state.cards[i];
    const article = document.createElement("article");
    article.className = "card";
    article.dataset.tag = c.tag;
    article.dataset.title = c.title.toLowerCase();
    article.dataset.date = c.date;
    article.innerHTML = `
      <header>
        <h4>${c.title}</h4>
      </header>
      <p>${c.excerpt}</p>
      <footer class="meta">
        <span class="tag">${c.tag}</span>
        <time  datetime="${c.date}">${new Date(c.date).toLocaleDateString()}</time>
        <!-- <button class="like" aria-pressed="${c.liked}" aria-label="Like">❤</button> -->
      </footer>
    `;
    grid.appendChild(article);
  }
}

function sortCards(mode) {
  const dir = mode.includes("Desc") ? -1 : 1;
  const by = mode.startsWith("title") ? "title" : "date";
  state.cards.sort((a,b) => {
    if (by === "title") {
      return a.title.localeCompare(b.title) * dir;
    } else {
      return (new Date(a.date) - new Date(b.date)) * dir;
    }
  });
  mountCards();
  wireLikes();
  applyFilters();
  applySearch();
}

function wireSorting() {
  const select = qs("#sortSelect");
  select.addEventListener("change", (e) => sortCards(e.target.value));
}

function wireFilters() {
  const boxes = [qs("#tagDesign"), qs("#tagDev")];
  for (let i = 0; i < boxes.length; i += 1) {
    boxes[i].addEventListener("change", applyFilters);
  }
}

function applyFilters() {
  const active = new Set();
  if (qs("#tagDesign").checked) { active.add("design"); }
  if (qs("#tagDev").checked) { active.add("dev"); }
  const cards = qsa("#cardGrid .card");
  for (let i = 0; i < cards.length; i += 1) {
    const el = cards[i];
    const show = active.has(el.dataset.tag);
    el.style.display = show ? "" : "none";
  }
}

function wireSearch() {
  const input = qs("#globalSearch");
  if (!input) { return; }
  input.addEventListener("input", applySearch);
}

function applySearch() {
  const input = qs("#globalSearch");
  const term = (input && input.value || "").trim().toLowerCase();
  const cards = qsa("#cardGrid .card");
  for (let i = 0; i < cards.length; i += 1) {
    const el = cards[i];
    const inTitle = el.dataset.title.includes(term);
    const visible = el.style.display !== "none";
    el.style.opacity = inTitle && visible ? "1" : inTitle ? "1" : "0.35";
  }
}

/* Likes */
function wireLikes() {
  const btns = qsa(".like");
  for (let i = 0; i < btns.length; i += 1) {
    btns[i].addEventListener("click", (e) => {
      const btn = e.currentTarget;
      const pressed = btn.getAttribute("aria-pressed") === "true";
      btn.setAttribute("aria-pressed", String(!pressed));
      // optional toast
      toast(pressed ? "Removed like" : "Liked ♥");
    });
  }
}


/* Dialogs */
function wireDialogs() {
  document.addEventListener("click", (e) => {
    const t = e.target;
    if (t.matches("[data-target]")) {
      const dlg = qs("#" + t.getAttribute("data-target"));
      if (dlg) { dlg.showModal(); }
    }
    if (t.matches("[data-close]")) {
      const dialog = t.closest("dialog");
      if (dialog) { dialog.close(); }
    }
  });
}

/* Toasts */
function wireToasts() {
  const btn = qs("#toastBtn");
  if (!btn) { return; }
  btn.addEventListener("click", () => toast("Saved!"));
}

function toast(msg) {
  const toaster = qs("#toaster");
  const el = document.createElement("div");
  el.role = "status";
  el.className = "toast glass";
  el.textContent = msg;
  toaster.appendChild(el);
  setTimeout(() => { el.classList.add("show"); }, 10);
  setTimeout(() => {
    el.classList.remove("show");
    setTimeout(() => el.remove(), 300);
  }, 2200);
}

/* Theme toggle with storage + system respect */
function wireThemeToggle() {
  const root = document.documentElement;
  const btn = qs("#themeToggle");
  const stored = localStorage.getItem("theme");
  if (stored) {
    root.setAttribute("data-theme", stored);
  } else {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    root.setAttribute("data-theme", prefersDark ? "dark" : "light");
  }
  btn.addEventListener("click", () => {
    const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
  });
}

/* Command palette */
function wireCommandPalette() {
  const dialog = qs("#cmdPalette");
  const input = qs("#cmdInput");
  const list = qs("#cmdList");
  function open() {
    dialog.showModal();
    input.value = "";
    input.focus();
  }
  function close() { dialog.close(); }
  function filter() {
    const term = input.value.toLowerCase();
    const items = qsa("li", list);
    for (let i = 0; i < items.length; i += 1) {
      const el = items[i];
      const match = el.textContent.toLowerCase().includes(term);
      el.style.display = match ? "" : "none";
    }
  }
  document.addEventListener("keydown", (e) => {
    const isMac = navigator.platform.toUpperCase().includes("MAC");
    if ((isMac && e.metaKey && e.key.toLowerCase() === "k") || (!isMac && e.ctrlKey && e.key.toLowerCase() === "k")) {
      e.preventDefault();
      open();
    }
    if (e.key === "Escape" && dialog.open) { close(); }
  });
  qs("#cmdk").addEventListener("click", open);
  input.addEventListener("input", filter);
  list.addEventListener("click", (e) => {
    const li = e.target.closest("li");
    if (!li) { return; }
    const action = li.dataset.action;
    if (action && action.startsWith("goto:")) {
      const target = action.split(":")[1];
      location.hash = target;
    } else if (action === "theme") {
      qs("#themeToggle").click();
    } else if (action === "search") {
      const search = qs("#globalSearch");
      if (search) { search.focus(); }
    }
    close();
  });
  qsa("[data-close]", dialog).forEach(el => el.addEventListener("click", (e) => { e.preventDefault(); close(); }));
}

/* Scroll-to-top button */
function wireScrollTop() {
  const btn = qs("#scrollTop");
  function onScroll() {
    const y = window.scrollY || document.documentElement.scrollTop;
    if (y > 480) {
      btn.classList.add("show");
    } else {
      btn.classList.remove("show");
    }
  }
  btn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  document.addEventListener("scroll", onScroll);
  onScroll();
}

/* Reveal-on-scroll */
function revealOnScroll() {
  const items = qsa(".reveal");
  const io = new IntersectionObserver((entries) => {
    for (let i = 0; i < entries.length; i += 1) {
      const entry = entries[i];
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        io.unobserve(entry.target);
      }
    }
  }, { threshold: 0.12 });
  for (let i = 0; i < items.length; i += 1) {
    io.observe(items[i]);
  }
}
