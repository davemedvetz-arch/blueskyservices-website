// Blue Sky Services — interactivity
(function () {
  // Icons
  if (window.lucide) lucide.createIcons();

  // Year
  var y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();

  // Theme toggle
  var toggle = document.querySelector('[data-theme-toggle]');
  var root = document.documentElement;
  function readThemeCookie() {
    try {
      var m = document.cookie.match(/(?:^|;\s*)bss-theme=(dark|light)/);
      return m ? m[1] : null;
    } catch (err) { return null; }
  }
  function saveThemeCookie(value) {
    try {
      document.cookie = 'bss-theme=' + value + ';path=/;max-age=31536000;SameSite=Lax';
    } catch (err) {}
  }
  var savedTheme = readThemeCookie();
  var theme = savedTheme || (matchMedia('(prefers-color-scheme:dark)').matches ? 'dark' : 'light');
  root.setAttribute('data-theme', theme);

  function renderToggleIcon() {
    if (!toggle) return;
    toggle.innerHTML =
      theme === 'dark'
        ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
        : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    toggle.setAttribute('aria-label', 'Switch to ' + (theme === 'dark' ? 'light' : 'dark') + ' mode');
  }
  renderToggleIcon();
  if (toggle) {
    toggle.addEventListener('click', function () {
      theme = theme === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', theme);
      saveThemeCookie(theme);
      renderToggleIcon();
    });
  }

  // Header scroll state
  var header = document.getElementById('siteHeader');
  function onScroll() {
    if (window.scrollY > 40) header.classList.add('is-scrolled');
    else header.classList.remove('is-scrolled');
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // Mobile menu
  var mobileMenu = document.getElementById('mobileMenu');
  var openBtn = document.getElementById('mobileOpen');
  var closeBtn = document.getElementById('mobileClose');
  function openMenu() {
    mobileMenu.classList.add('is-open');
    openBtn.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }
  function closeMenu() {
    mobileMenu.classList.remove('is-open');
    openBtn.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }
  if (openBtn) openBtn.addEventListener('click', openMenu);
  if (closeBtn) closeBtn.addEventListener('click', closeMenu);
  mobileMenu.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', closeMenu);
  });

  // Scroll reveal
  var revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );
    revealEls.forEach(function (el) {
      io.observe(el);
    });
  } else {
    revealEls.forEach(function (el) {
      el.classList.add('is-visible');
    });
  }

  // FAQ accordion
  document.querySelectorAll('.faq-item').forEach(function (item) {
    var btn = item.querySelector('.faq-question');
    btn.addEventListener('click', function () {
      var isOpen = item.getAttribute('data-open') === 'true';
      item.setAttribute('data-open', String(!isOpen));
      btn.setAttribute('aria-expanded', String(!isOpen));
    });
  });
})();

// Contact form (static site — opens the visitor's email app with the message pre-filled)
function handleFormSubmit(e) {
  e.preventDefault();
  var form = e.target;
  var get = function (name) {
    var el = form.querySelector('[name="' + name + '"]');
    return el ? el.value.trim() : '';
  };
  var name = (get('fname') + ' ' + get('lname')).trim();
  var subject = 'Free estimate request — ' + (get('interest') || 'General inquiry');
  var bodyLines = [
    'Name: ' + name,
    'Email: ' + get('email'),
    'Phone: ' + (get('phone') || 'Not provided'),
    'Project type: ' + get('interest'),
    '',
    'Project details:',
    get('details'),
  ];
  var mailto =
    'mailto:info@blueskyservices.com?subject=' +
    encodeURIComponent(subject) +
    '&body=' +
    encodeURIComponent(bodyLines.join('\n'));
  window.location.href = mailto;
  var note = form.querySelector('.form-note');
  if (note) {
    note.innerHTML =
      'Your email app should open with your request pre-filled — just hit send. If it didn\u2019t open, email <a href="mailto:info@blueskyservices.com">info@blueskyservices.com</a> or call <a href="tel:9197430030">919-743-0030</a>.';
  }
  return false;
}
