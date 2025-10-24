(function () {
  // --- CSRF helpers ---
  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? decodeURIComponent(m.pop()) : null;
  }
  function getCSRFToken() {
    return (
      getCookie('csrftoken') ||
      (document.querySelector('meta[name="csrf-token"]') || {}).content ||
      ''
    );
  }
  const CSRF = getCSRFToken();

  async function postURL(url, formData) {
    const init = {
      method: 'POST',
      headers: {
        'X-CSRFToken': CSRF,
        'X-Requested-With': 'XMLHttpRequest',
      },
      credentials: 'same-origin',
    };
    if (formData instanceof FormData) {
      init.body = formData;
    } else {
      init.body = new URLSearchParams(); // empty POST body
    }
    return fetch(url, init);
  }

  // --- OPTIONAL: non-modal quick delete (if you add buttons with data-url) ---
  // Example HTML (no modal):
  // <button data-url="/community/..." data-confirm="Delete this?" class="btn btn-danger btn-sm">Delete</button>
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('button[data-url]');
    if (!btn) return;

    // If this button is a modal trigger, ignore here; the modal logic handles it
    if (btn.hasAttribute('data-bs-toggle')) return;

    const url = btn.dataset.url;
    const confirmMsg = btn.dataset.confirm || 'Are you sure?';
    if (!url) return;

    e.preventDefault();
    if (!window.confirm(confirmMsg)) return;
    try {
      const res = await postURL(url);
      if (res.ok) {
        // If the element provides a redirect target, use it; else reload
        const redirectTo = btn.dataset.redirect || '';
        if (redirectTo) window.location.assign(redirectTo);
        else window.location.reload();
      } else {
        alert('Delete failed (' + res.status + ').');
      }
    } catch (err) {
      console.error(err);
      alert('Network error while deleting.');
    }
  });

  // --- AJAX forms (create/edit group, add comment) ---
  document.addEventListener('submit', async (e) => {
    const form = e.target.closest('[data-ajax]');
    if (!form) return;

    e.preventDefault();

    const fd = new FormData(form);
    const action = form.getAttribute('action');
    const redirectTo = form.dataset.redirect || '';

    try {
      const res = await postURL(action, fd);

      if (res.ok) {
        if (redirectTo) {
          window.location.assign(redirectTo);
          return;
        }
        window.location.reload();
        return;
      }

      const ct = res.headers.get('Content-Type') || '';
      if (ct.includes('text/html')) {
        const html = await res.text();
        form.outerHTML = html; // show server-side validation errors
      } else {
        alert('Save failed (' + res.status + ').');
      }
    } catch (err) {
      console.error(err);
      alert('Network error while submitting form.');
    }
  });
})();

// --- Bootstrap confirm modal wiring ---
// Attach immediately (no DOMContentLoaded) so the handler is installed even if
// the DOMContentLoaded event already fired before this script executed.
(() => {
  const modalEl = document.getElementById('confirmModal');
  if (!modalEl) return;

  modalEl.addEventListener('show.bs.modal', (event) => {
    const button = event.relatedTarget; // the button that opened the modal
    if (!button) return;

    // In your templates, data-action is the URL to post to
    const action = button.getAttribute('data-action') || '';
    const title  = button.getAttribute('data-title')  || 'Please confirm';
    const body   = button.getAttribute('data-body')   || 'Are you sure?';

    const titleEl = modalEl.querySelector('.modal-title');
    const bodyEl  = modalEl.querySelector('.modal-body');
    if (titleEl) titleEl.textContent = title;
    if (bodyEl)  bodyEl.textContent  = body;

    const form = modalEl.querySelector('#confirmModalForm');
    if (form) form.setAttribute('action', action);
  });
})();
