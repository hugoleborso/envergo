var _paq = window._paq || [];

// Track an event when a regulation main "read more" btn is clicked
window.addEventListener('load', function() {
  const showMoreBtns = document.querySelectorAll('.read-more-btn');
  showMoreBtns.forEach(btn => btn.addEventListener('click', function(evt) {
    const btn = evt.currentTarget;
    const target = btn.getAttribute('aria-controls');
    const expanded = btn.getAttribute('aria-expanded');
    const action = expanded == 'false' ? 'Expand' : 'Conceal';
    _paq.push(['trackEvent', 'Content', action, target]);
  }));
});

// Track a moulinette result page load
window.addEventListener('load', function() {
  _paq.push(['trackEvent', 'Simulation', 'Result', DEPARTMENT]);
});

// Track when a summary link is clicked
window.addEventListener('load', function() {
  const summaryLinks = document.querySelectorAll('.summary-link');
  summaryLinks.forEach(link => link.addEventListener('click', function(evt) {
    // Log the event
    const link = evt.currentTarget;
    const title = link.getAttribute('data-regulation');
    _paq.push(['trackEvent', 'Content', 'JumpToAnchor', title]);
  }));
});
