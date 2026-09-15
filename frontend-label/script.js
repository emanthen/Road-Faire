// ============================================================
// Aperture — record label landing page
// Vanilla JS, no framework: one page, precise scroll physics,
// doesn't need anything heavier.
// ============================================================

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// ---------- CATALOGUE DATA (fictional label, internally consistent) ----------
const RELEASES = [
  { code: "AP001", title: "Low Static", artist: "Vela Kern", format: "LP", year: "2023" },
  { code: "AP002", title: "Vaulted", artist: "Ossian Dry", format: "EP", year: "2023" },
  { code: "AP003", title: "Marrow I", artist: "Marrow", format: "12\"", year: "2024" },
  { code: "AP004", title: "Half-Light Chorus", artist: "Vela Kern", format: "LP", year: "2024" },
  { code: "AP005", title: "Sund Drift", artist: "Kepler Sund", format: "EP", year: "2024" },
  { code: "AP006", title: "Dry Season", artist: "Ossian Dry", format: "EP", year: "2025" },
  { code: "AP007", title: "Marrow II", artist: "Marrow", format: "12\"", year: "2025" },
  { code: "AP008", title: "Vance Interior", artist: "Noor Vance", format: "LP", year: "2025" },
  { code: "AP009", title: "Kern Archive Vol. 1", artist: "Vela Kern", format: "LP", year: "2026" },
  { code: "AP010", title: "Sund Line", artist: "Kepler Sund", format: "EP", year: "2026" },
];

// ============================================================
// 0. MOBILE NAV — the links list had no way to open below 720px
// ============================================================
function initNavToggle() {
  const toggle = document.getElementById("navToggle");
  const links = document.getElementById("navLinks");
  if (!toggle || !links) return;

  function close() {
    toggle.setAttribute("aria-expanded", "false");
    links.classList.remove("is-open");
  }

  toggle.addEventListener("click", () => {
    const isOpen = links.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(isOpen));
  });

  links.addEventListener("click", (e) => {
    if (e.target.tagName === "A") close();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") close();
  });
}

// ============================================================
// 1. PORTAL HERO — scroll-position-driven, therefore reversible
// ============================================================
function initHero() {
  const hero = document.getElementById("hero");
  const stage = hero.querySelector(".hero__stage");
  if (!hero || !stage) return;

  let ticking = false;

  function update() {
    ticking = false;
    const rect = hero.getBoundingClientRect();
    const scrollable = hero.offsetHeight - window.innerHeight;
    const scrolled = -rect.top;
    const progress = Math.min(1, Math.max(0, scrolled / scrollable));
    stage.style.setProperty("--p", progress.toFixed(4));
  }

  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(update);
    }
  }

  if (!prefersReducedMotion) {
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    update();
  }
}

// ============================================================
// 2. STATEMENT IMAGE — drifts and rotates with its own scroll progress
// ============================================================
function initStatementDrift() {
  if (prefersReducedMotion) return;
  const section = document.querySelector(".statement");
  const image = document.querySelector(".statement__image");
  if (!section || !image) return;

  let ticking = false;

  function update() {
    ticking = false;
    const rect = section.getBoundingClientRect();
    const total = rect.height + window.innerHeight;
    const traveled = window.innerHeight - rect.top;
    const progress = Math.min(1, Math.max(0, traveled / total));
    const drift = (progress - 0.5) * 60; // px, drifts up then settles
    const rotate = (progress - 0.5) * 22; // deg
    image.style.transform = `translateY(${drift}px) rotate(${rotate}deg)`;
  }

  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(update);
    }
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  update();
}

// ============================================================
// 3. ONE-TIME REVEALS — never un-reveal; skipped entirely under
//    reduced motion, so that render is just the finished page.
// ============================================================
function initReveals() {
  if (prefersReducedMotion) return;
  document.documentElement.classList.add("reveal-ready");

  const targets = document.querySelectorAll("[data-reveal]");
  if (!("IntersectionObserver" in window) || targets.length === 0) {
    targets.forEach((el) => el.classList.add("is-revealed"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-revealed");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  targets.forEach((el) => observer.observe(el));
}

// ============================================================
// 4. THROWABLE CARD DECK
// ============================================================
function initDeck() {
  const deck = document.getElementById("deck");
  const dotsWrap = document.getElementById("deckDots");
  if (!deck) return;

  const VISIBLE_STACK = 5;
  let order = RELEASES.map((_, i) => i); // order[0] = top card's index into RELEASES

  // Build one DOM card per release, keyed by release index (stable across throws).
  const cardEls = RELEASES.map((release) => {
    const card = document.createElement("div");
    card.className = "deck__card";
    card.innerHTML = `
      <div>
        <span class="deck__card-code">${release.code}</span>
        <div class="deck__card-title">${release.title}</div>
        <div class="deck__card-artist">${release.artist}</div>
      </div>
      <div class="deck__card-footer">
        <span>${release.format}</span>
        <span>${release.year}</span>
      </div>
    `;
    deck.appendChild(card);
    return card;
  });

  RELEASES.forEach((_, i) => (dotsWrap.innerHTML += "<span></span>"));
  const dotEls = Array.from(dotsWrap.children);

  function stackTransform(position) {
    // Deterministic "tossed" offsets, not a straight fan.
    const dir = position % 2 === 0 ? 1 : -1;
    const x = dir * (position * 4);
    const y = position * 7;
    const rotate = dir * (position * 2.4);
    const scale = 1 - position * 0.025;
    return { x, y, rotate, scale };
  }

  function render() {
    order.forEach((releaseIndex, position) => {
      const card = cardEls[releaseIndex];
      if (position >= VISIBLE_STACK) {
        card.style.opacity = "0";
        card.style.zIndex = "0";
        card.style.pointerEvents = "none";
        return;
      }
      const { x, y, rotate, scale } = stackTransform(position);
      card.style.opacity = "1";
      card.style.zIndex = String(100 - position);
      card.style.pointerEvents = position === 0 ? "auto" : "none";
      card.style.transform = `translate(${x}px, ${y}px) rotate(${rotate}deg) scale(${scale})`;
    });
    dotEls.forEach((dot, i) => dot.classList.toggle("is-active", i === order[0]));
  }

  function throwTop(direction) {
    const topReleaseIndex = order[0];
    const card = cardEls[topReleaseIndex];
    const deckWidth = deck.offsetWidth;
    card.classList.remove("deck__card--dragging");
    card.style.transform = `translate(${direction * (deckWidth * 1.4)}px, -40px) rotate(${direction * 24}deg) scale(0.96)`;
    card.style.opacity = "0";
    setTimeout(() => {
      order.push(order.shift());
      render();
    }, 380);
  }

  // ---- Pointer drag physics ----
  let dragging = false;
  let startX = 0;
  let startY = 0;
  let dx = 0;

  deck.addEventListener("pointerdown", (e) => {
    const topReleaseIndex = order[0];
    const card = cardEls[topReleaseIndex];
    if (e.target !== card && !card.contains(e.target)) return;
    dragging = true;
    startX = e.clientX;
    startY = e.clientY;
    dx = 0;
    card.classList.add("deck__card--dragging");
    card.setPointerCapture(e.pointerId);
  });

  deck.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const topReleaseIndex = order[0];
    const card = cardEls[topReleaseIndex];
    dx = e.clientX - startX;
    const dy = e.clientY - startY;
    const rotate = dx * 0.05;
    card.style.transform = `translate(${dx}px, ${dy}px) rotate(${rotate}deg) scale(1.02)`;
  });

  function endDrag() {
    if (!dragging) return;
    dragging = false;
    const deckWidth = deck.offsetWidth;
    const threshold = deckWidth * 0.1;
    if (Math.abs(dx) > threshold) {
      throwTop(dx > 0 ? 1 : -1);
    } else {
      const topReleaseIndex = order[0];
      const card = cardEls[topReleaseIndex];
      card.classList.remove("deck__card--dragging");
      render();
    }
  }

  deck.addEventListener("pointerup", endDrag);
  deck.addEventListener("pointercancel", endDrag);

  // ---- Keyboard: usable without a mouse ----
  deck.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") {
      e.preventDefault();
      throwTop(1);
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      throwTop(-1);
    }
  });

  render();
}

// ============================================================
document.addEventListener("DOMContentLoaded", () => {
  initNavToggle();
  initHero();
  initStatementDrift();
  initReveals();
  initDeck();
});
