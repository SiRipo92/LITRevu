// Accessible mobile menu with smooth staged animations
(function () {
  const burgerBtn  = document.getElementById('burgerBtn');
  const burgerIcon = document.getElementById('burgerIcon');
  const closeIcon  = document.getElementById('closeIcon');
  const overlay    = document.getElementById('mobileOverlay');
  const drawer     = document.getElementById('mobileMenu');
  const body       = document.body;

  if (!burgerBtn || !overlay || !drawer || !burgerIcon || !closeIcon) return;

  // Match the HTML durations you chose:
  // If you used defaults: 300 / 500. If you used arbitrary: 250 / 400.
  const OVERLAY_MS = 300; // 250 if you used duration-[250ms]
  const DRAWER_MS  = 500; // 400 if you used duration-[400ms]
  const STAGGER_MS = 100; // start drawer a bit after overlay begins

  let previousFocus = null;

  const focusableSelectors = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])'
  ];
  const getFocusable = () => drawer.querySelectorAll(focusableSelectors.join(','));

  function reflow(el) { void el.offsetHeight; }
  function show(el)   { el.classList.remove('hidden'); reflow(el); }
  function hide(el)   { el.classList.add('hidden'); }

  function isOpen() {
    return burgerBtn.getAttribute('aria-expanded') === 'true';
  }

  function onDocumentClick(e) {
    if (!drawer.contains(e.target) && e.target !== burgerBtn && !burgerBtn.contains(e.target)) {
      closeMenu();
    }
  }

  function onKeydown(e) {
    if (e.key === 'Escape') {
      e.preventDefault();
      closeMenu();
      return;
    }
    if (e.key === 'Tab') {
      const focusables = Array.from(getFocusable());
      if (!focusables.length) return;
      const first = focusables[0];
      const last  = focusables[focusables.length - 1];
      const active = document.activeElement;

      if (e.shiftKey) {
        if (active === first || !drawer.contains(active)) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (active === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }
  }

  function openMenu() {
    previousFocus = document.activeElement;
    // Lock scroll
    body.classList.add('overflow-hidden');

    // Stage 1: fade in overlay
    show(overlay);
    overlay.classList.remove('opacity-0');

    // Stage 2: slide+fade in drawer after a short stagger
    setTimeout(() => {
      show(drawer);
      drawer.classList.remove('translate-x-full');
      drawer.classList.remove('opacity-0');
    }, STAGGER_MS);

    // ARIA + icon cross-fade
    burgerBtn.setAttribute('aria-expanded', 'true');
    burgerBtn.setAttribute('aria-label', 'Fermer le menu');

    burgerIcon.classList.add('opacity-0');
    closeIcon.classList.remove('hidden');
    requestAnimationFrame(() => closeIcon.classList.remove('opacity-0'));
    setTimeout(() => burgerIcon.classList.add('hidden'), 200);

    // Focus management & traps
    const focusables = getFocusable();
    if (focusables.length) focusables[0].focus();

    document.addEventListener('keydown', onKeydown);
    overlay.addEventListener('click', closeMenu);
    document.addEventListener('click', onDocumentClick, true);
  }

  function closeMenu() {
    // Slide+fade out drawer
    drawer.classList.add('translate-x-full');
    drawer.classList.add('opacity-0');

    // After drawer finishes, hide it and fade overlay out
    setTimeout(() => {
      hide(drawer);
      overlay.classList.add('opacity-0');

      setTimeout(() => {
        hide(overlay);
        body.classList.remove('overflow-hidden');
      }, OVERLAY_MS);
    }, DRAWER_MS);

    // ARIA + icon cross-fade back
    burgerBtn.setAttribute('aria-expanded', 'false');
    burgerBtn.setAttribute('aria-label', 'Ouvrir le menu');

    closeIcon.classList.add('opacity-0');
    setTimeout(() => {
      closeIcon.classList.add('hidden');
      burgerIcon.classList.remove('hidden');
      requestAnimationFrame(() => burgerIcon.classList.remove('opacity-0'));
    }, 200);

    // Restore focus & remove traps
    if (previousFocus && typeof previousFocus.focus === 'function') {
      previousFocus.focus();
    }
    document.removeEventListener('keydown', onKeydown);
    overlay.removeEventListener('click', closeMenu);
    document.removeEventListener('click', onDocumentClick, true);
  }

  burgerBtn.addEventListener('click', () => (isOpen() ? closeMenu() : openMenu()));
})();