(function () {
  "use strict";

  // ====== helpers ======
  function qs(root, sel) {
    return root.querySelector(sel);
  }
  function qsa(root, sel) {
    return Array.from(root.querySelectorAll(sel));
  }
  function isElement(node) {
    return node && node.nodeType === 1;
  }

  // ====== find trigger and content ======
  var trigger =
    document.getElementById("openMainMenuTrigger") ||
    qs(document, ".js-offcanvas-trigger") ||
    document.getElementById("menu_main_div"); // last resort

  var contentRoot =
    document.getElementById("c-menu-offcanvas") ||
    document.getElementById("menu_main_div");

  if (!trigger || !contentRoot) {
    console.warn("Menu trigger or content root not found.");
    return;
  }

  // Hide original subtree from layout; we will render panels from it
  contentRoot.style.display = "none";
  contentRoot.setAttribute("aria-hidden", "true");

  // ====== build floating container ======
  var container = document.createElement("div");
  container.setAttribute("data-offcanvas", "zew");
  container.style.position = "absolute";
  container.style.top = "0";
  container.style.left = "0";
  container.style.zIndex = "9999";
  container.style.display = "none";
  container.style.fontFamily = "inherit";

  // basic look & feel
  var basePanelWidth = 280;
  var panelGap = 8;

  // panels wrapper (so we can place multiple columns)
  var panelsWrap = document.createElement("div");
  panelsWrap.style.position = "relative";
  panelsWrap.style.display = "flex";
  panelsWrap.style.alignItems = "stretch";
  panelsWrap.style.boxShadow = "0 8px 24px rgba(0,0,0,0.15)";
  panelsWrap.style.border = "1px solid rgba(0,0,0,0.1)";
  panelsWrap.style.background = "#fff";

  container.appendChild(panelsWrap);
  document.body.appendChild(container);


function normalizeList(ul) {
  // Snapshot, weil wir die DOM-Struktur ändern
  var children = Array.from(ul.childNodes);

  for (var i = 0; i < children.length; i += 1) {
    var node = children[i];

    if (!node || node.nodeType !== 1) {
      continue;
    }

    var tag = node.tagName.toLowerCase();

    // 1) Bereits korrekt
    if (tag === "li") {
      continue;
    }

    //
    if (tag === "p") {
      if (node.parentNode === ul) {

        var li = document.createElement("li");
        // Wichtig: erst LI einfügen, dann node hinein verschieben
        ul.insertBefore(li, node);
        li.appendChild(node);
      }
      continue;
    }

    // 2) Wrappe AnkER/Div/Span/P in <li>
    if (tag === "a" || tag === "div" || tag === "span") {
      if (node.parentNode === ul) {
        var li = document.createElement("li");
        // Wichtig: erst LI einfügen, dann node hinein verschieben
        ul.insertBefore(li, node);
        li.appendChild(node);
      }
      continue;
    }

    // 3) Direktes UL unter UL → an vorheriges LI hängen
    if (tag === "ul") {
      var prevLi = ul.lastElementChild && ul.lastElementChild.tagName.toLowerCase() === "li"
        ? ul.lastElementChild
        : null;

      if (prevLi) {
        prevLi.appendChild(node);
      } else {
        // WICHTIGER FIX:
        // Erst das neue LI vor "node" einfügen, dann "node" in dieses LI verschieben.
        var fakeLi = document.createElement("li");
        fakeLi.appendChild(document.createTextNode("Mehr …"));
        if (node.parentNode === ul) {
          ul.insertBefore(fakeLi, node);
          fakeLi.appendChild(node);
        } else {
          // Falls inzwischen woanders: hänge das LI einfach ans Ende und füge danach das UL ein
          ul.appendChild(fakeLi);
          fakeLi.appendChild(node);
        }
      }
      continue;
    }
  }

  // 4) Falls Struktur "LI (mit A) + folgendes UL als Geschwister" existiert:
  var fixedKids = Array.from(ul.children);
  for (var j = 0; j < fixedKids.length; j += 1) {
    var liNode = fixedKids[j];
    if (liNode.tagName.toLowerCase() !== "li") {
      continue;
    }
    var hasSub = liNode.querySelector(":scope > ul");
    if (!hasSub) {
      var next = liNode.nextElementSibling;
      if (next && next.tagName.toLowerCase() === "ul") {
        liNode.appendChild(next);
      }
    }
  }

  // 5) Rekursiv für Submenüs
  var nested = Array.from(ul.querySelectorAll(":scope > li > ul"));
  for (var k = 0; k < nested.length; k += 1) {
    normalizeList(nested[k]);
  }
}


  // ====== normalize source markup ======
  function AAAAnormalizeList(ul) {
    // Ensure direct children are <li>
    var children = Array.from(ul.childNodes);
    for (var i = 0; i < children.length; i += 1) {
      var node = children[i];
      if (!isElement(node)) {
        continue;
      }
      if (node.tagName.toLowerCase() === "li") {
        continue;
      }
      if (
        node.tagName.toLowerCase() === "a" ||
        node.tagName.toLowerCase() === "div" ||
        node.tagName.toLowerCase() === "p" ||
        node.tagName.toLowerCase() === "span"
      ) {
        var li = document.createElement("li");
        ul.insertBefore(li, node);
        li.appendChild(node);
      } else if (node.tagName.toLowerCase() === "ul") {
        // if a UL is floating directly under UL, wrap it into previous LI if possible
        var prev = liOfLastElementChild(ul);
        if (prev) {
          prev.appendChild(node);
        } else {
          var fakeLi = document.createElement("li");
          fakeLi.appendChild(document.createTextNode("Mehr …"));
          fakeLi.appendChild(node);
          ul.insertBefore(fakeLi, node);
        }
      }
    }

    // Pair an <a> followed by a <ul> as submenu inside the same <li>
    var fixedKids = Array.from(ul.children);
    for (var j = 0; j < fixedKids.length; j += 1) {
      var liNode = fixedKids[j];
      if (liNode.tagName.toLowerCase() !== "li") {
        continue;
      }
      // if this LI has an <a> as first and its next sibling (in UL scope) is a <ul>, move that <ul> inside this LI
      var sibling = liNode.nextElementSibling;
      if (sibling && sibling.tagName.toLowerCase() === "ul") {
        // move in only if current LI doesn't already contain a UL
        if (!qs(liNode, ":scope > ul")) {
          liNode.appendChild(sibling);
        }
      }
    }

    // Recurse normalize nested ULs
    var nested = qsa(ul, ":scope > li > ul");
    for (var k = 0; k < nested.length; k += 1) {
      normalizeList(nested[k]);
    }
  }

  function liOfLastElementChild(ul) {
    var lastEl = ul.lastElementChild;
    if (!lastEl) {
      return null;
    }
    if (lastEl.tagName.toLowerCase() === "li") {
      return lastEl;
    }
    return null;
  }

  // Find the first real UL inside the content root; if not found, fabricate one from anchors
  var sourceUL =
    qs(contentRoot, "nav#c-menu-offcanvas > ul") ||
    qs(contentRoot, ":scope > ul") ||
    qs(contentRoot, "ul");

  if (!sourceUL) {
    // fabricate
    sourceUL = document.createElement("ul");
    var allLinks = qsa(contentRoot, "a[href]");
    for (var z = 0; z < allLinks.length; z += 1) {
      var li = document.createElement("li");
      li.appendChild(allLinks[z].cloneNode(true));
      sourceUL.appendChild(li);
    }
  } else {
    sourceUL = sourceUL.cloneNode(true);
  }

  normalizeList(sourceUL);

  // ====== render panels on demand ======
  var openPath = []; // keeps the chain of ULs that are open (by level)

  function renderPanelsFrom(ul, level) {
    // remove panels to the right of this level
    while (panelsWrap.children.length > level) {
      panelsWrap.removeChild(panelsWrap.lastElementChild);
    }

    // create a panel for 'ul'
    var panel = document.createElement("div");
    panel.setAttribute("role", "menu");
    panel.style.minWidth = basePanelWidth + "px";
    panel.style.maxWidth = basePanelWidth + "px";
    panel.style.padding = "8px 0";
    panel.style.borderLeft = level === 0 ? "none" : "1px solid rgba(0,0,0,0.08)";
    panel.style.boxSizing = "border-box";
    panel.style.overflowY = "auto";
    panel.style.maxHeight = "70vh";

    var list = document.createElement("ul");
    list.style.listStyle = "none";
    list.style.margin = "0";
    list.style.padding = "0";

    var items = qsa(ul, ":scope > li");
    for (var i = 0; i < items.length; i += 1) {
      var li = items[i];
      var a = qs(li, ":scope > a, :scope > div > a");
      var labelNode = a ? a.cloneNode(true) : li.firstElementChild;

      var row = document.createElement("li");
      row.setAttribute("role", "none");
      row.style.margin = "0";
      row.style.padding = "0";

      var btn = document.createElement("button");
      btn.setAttribute("type", "button");
      btn.setAttribute("role", "menuitem");
      btn.style.display = "flex";
      btn.style.justifyContent = "space-between";
      btn.style.alignItems = "center";
      btn.style.width = "100%";
      btn.style.textAlign = "left";
      btn.style.border = "0";
      btn.style.background = "transparent";
      btn.style.padding = "10px 14px";
      btn.style.cursor = "pointer";
      btn.style.fontSize = "16px";
      btn.style.lineHeight = "1.3";

      // label
      var textSpan = document.createElement("span");
      if (a && a.textContent) {
        textSpan.textContent = a.textContent.trim();
      } else {
        textSpan.textContent = li.textContent.trim().replace(/\s+/g, " ").slice(0, 120);
      }
      btn.appendChild(textSpan);

      // submenu indicator
      var sub = qs(li, ":scope > ul");
      if (sub) {
        btn.setAttribute("aria-haspopup", "true");
        btn.setAttribute("aria-expanded", "false");
        var caret = document.createElement("span");
        caret.setAttribute("aria-hidden", "true");
        caret.textContent = "›";
        caret.style.marginLeft = "12px";
        btn.appendChild(caret);
      }

      // click behavior
      (function (liRef, subRef, linkRef, lvl, buttonRef) {
        btn.addEventListener("click", function (ev) {
          ev.stopPropagation();

          if (subRef) {
            // open next level
            buttonRef.setAttribute("aria-expanded", "true");
            renderPanelsFrom(subRef, lvl + 1);
            // move focus to first item of next panel
            var nextPanel = panelsWrap.children[lvl + 1];
            if (nextPanel) {
              var firstBtn = qs(nextPanel, "button[role='menuitem']");
              if (firstBtn) {
                firstBtn.focus();
              }
            }
          } else if (linkRef && linkRef.href) {
            window.location.href = linkRef.href;
          }
        });
      })(li, sub, a, level, btn);

      // hover open submenu (optional but nice)
      (function (subRef, lvl, buttonRef) {
        row.addEventListener("mouseenter", function () {
          if (subRef) {
            buttonRef.setAttribute("aria-expanded", "true");
            renderPanelsFrom(subRef, lvl + 1);
          }
        });
      })(sub, level, btn);

      row.appendChild(btn);
      list.appendChild(row);
    }

    panel.appendChild(list);
    panelsWrap.appendChild(panel);
  }

  // ====== open/close mechanics ======
  var isOpen = false;

  function positionContainer() {
    var rect = trigger.getBoundingClientRect();
    var docX = window.scrollX || window.pageXOffset;
    var docY = window.scrollY || window.pageYOffset;

    container.style.top = Math.round(rect.top + docY) + "px";
    container.style.left = Math.round(rect.right + docX + panelGap) + "px";
  }

  function openMenu() {
    positionContainer();
    container.style.display = "block";
    renderPanelsFrom(sourceUL, 0);
    isOpen = true;
    container.setAttribute("aria-hidden", "false");
    // focus first item
    var firstBtn = qs(container, "button[role='menuitem']");
    if (firstBtn) {
      firstBtn.focus();
    }
    // keyboard listener
    document.addEventListener("keydown", onKeyDown, { capture: true });
    // outside click
    setTimeout(function () {
      document.addEventListener("mousedown", onOutsideClick);
      window.addEventListener("resize", onWindowChange);
      window.addEventListener("scroll", onWindowChange, { passive: true });
    }, 0);
  }

  function closeMenu() {
    container.style.display = "none";
    isOpen = false;
    container.setAttribute("aria-hidden", "true");
    document.removeEventListener("keydown", onKeyDown, { capture: true });
    document.removeEventListener("mousedown", onOutsideClick);
    window.removeEventListener("resize", onWindowChange);
    window.removeEventListener("scroll", onWindowChange, { passive: true });
    // collapse indicators
    qsa(container, "button[aria-expanded='true']").forEach(function (b) {
      b.setAttribute("aria-expanded", "false");
    });
  }

  function onKeyDown(e) {
    if (e.key === "Escape") {
      e.preventDefault();
      closeMenu();
      trigger.focus();
      return;
    }
    // simple vertical navigation
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      var items = qsa(container, "button[role='menuitem']");
      if (items.length === 0) {
        return;
      }
      var idx = items.indexOf(document.activeElement);
      if (e.key === "ArrowDown") {
        idx = idx < 0 ? 0 : Math.min(items.length - 1, idx + 1);
      } else {
        idx = idx < 0 ? 0 : Math.max(0, idx - 1);
      }
      items[idx].focus();
      e.preventDefault();
      return;
    }
    // open submenu with ArrowRight
    if (e.key === "ArrowRight") {
      var btn = document.activeElement;
      if (btn && btn.getAttribute("aria-haspopup") === "true") {
        btn.click();
        e.preventDefault();
      }
      return;
    }
    // close to previous panel with ArrowLeft
    if (e.key === "ArrowLeft") {
      if (panelsWrap.children.length > 1) {
        panelsWrap.removeChild(panelsWrap.lastElementChild);
        var prevPanel = panelsWrap.lastElementChild;
        var focusBtn = prevPanel ? qs(prevPanel, "button[role='menuitem']") : null;
        if (focusBtn) {
          focusBtn.focus();
        }
        e.preventDefault();
      }
      return;
    }
  }

  function onOutsideClick(e) {
    if (!container.contains(e.target) && !trigger.contains(e.target)) {
      closeMenu();
    }
  }

  function onWindowChange() {
    if (!isOpen) {
      return;
    }
    positionContainer();
  }

  // ====== wire trigger ======
  // Ensure the clickable thing is the button, not the label span
  var actualTrigger =
    trigger.closest("button") ||
    trigger;

  actualTrigger.setAttribute("aria-haspopup", "true");
  actualTrigger.setAttribute("aria-expanded", "false");

  actualTrigger.addEventListener("click", function (e) {
    e.preventDefault();
    if (isOpen) {
      closeMenu();
      actualTrigger.setAttribute("aria-expanded", "false");
    } else {
      openMenu();
      actualTrigger.setAttribute("aria-expanded", "true");
    }
  });

  // Defensive: close if page hides
  document.addEventListener("visibilitychange", function () {
    if (document.hidden && isOpen) {
      closeMenu();
    }
  });
})();


document.addEventListener("DOMContentLoaded", function() {
    let headers = document.querySelectorAll(".c-accordion__tab");

    for (let i = 0; i < headers.length; i++) {
        headers[i].addEventListener("click", function() {
            let panelId = this.getAttribute("id").replace("tab", "panel");
            let panel = document.getElementById(panelId);
            console.log(` clicked ${this} - 'id-${panelId}' --- ${panel}`)

            if (panel.classList.contains("is-open")) {
                panel.classList.remove("is-open");
            } else {
                panel.classList.add("is-open");
            }
        });
        console.log(` attached ${headers[i]}`)
    }
});