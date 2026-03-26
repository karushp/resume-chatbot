(function () {
  const STORAGE_KEY = 'cookie_consent';
  const banner = document.getElementById('cookie-banner');

  function hideBanner() {
    if (banner) banner.hidden = true;
  }

  function showBanner() {
    if (banner) banner.hidden = false;
  }

  function applyConsent(granted) {
    if (typeof gtag !== 'function') return;
    gtag('consent', 'update', {
      analytics_storage: granted ? 'granted' : 'denied',
    });
  }

  function accept() {
    try {
      localStorage.setItem(STORAGE_KEY, 'granted');
    } catch (_) {}
    applyConsent(true);
    hideBanner();
  }

  function reject() {
    try {
      localStorage.setItem(STORAGE_KEY, 'denied');
    } catch (_) {}
    applyConsent(false);
    hideBanner();
  }

  function init() {
    let choice = null;
    try {
      choice = localStorage.getItem(STORAGE_KEY);
    } catch (_) {}

    if (choice === null) showBanner();
    else hideBanner();

    document.getElementById('cookie-accept')?.addEventListener('click', accept);
    document.getElementById('cookie-reject')?.addEventListener('click', reject);
    document.getElementById('cookie-settings-btn')?.addEventListener('click', function (e) {
      e.preventDefault();
      showBanner();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
