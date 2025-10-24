console.log('posts.js loaded');

document.addEventListener('DOMContentLoaded', () => {
  /* ===== CSRF helpers ===== */
  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
  }
  function getCsrf() {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : getCookie('csrftoken');
  }
  async function postForm(url, form) {
    const data = new FormData(form);
    const res  = await fetch(url, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrf() },
      body: data
    });
    const json = await res.json().catch(() => ({}));
    return { ok: res.ok, json, res };
  }

  /* ===== Create post (list page) ===== */
  const createForm = document.querySelector('#create-form');
  if (createForm && !createForm.dataset.boundExternal) {
    createForm.dataset.boundExternal = '1';
    createForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const { ok, json } = await postForm(createForm.action, createForm);
      if (!ok) {
        alert('Failed to create post: ' + JSON.stringify(json));
        return;
      }
      if (json && typeof json.html === 'string') {
        const feed = document.getElementById('feed');
        if (!feed) return;
        // remove empty text if present
        document.getElementById('feed-empty')?.remove();

        const tpl = document.createElement('template');
        tpl.innerHTML = json.html.trim();
        feed.prepend(tpl.content.firstElementChild);
        createForm.reset();
      } else {
        window.location.reload(); // fallback
      }
    });
  }

  /* ===== Like toggle (list & detail) ===== */
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.btn-like');
    if (!btn) return;
    const id = btn.dataset.id;
    const res = await fetch(`/posts/api/${id}/like-toggle/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrf() }
    });
    const j = await res.json().catch(() => ({}));
    if (res.ok) {
      const span = btn.querySelector('[data-like-count]');
      if (span) span.textContent = j.count ?? span.textContent;
      btn.classList.toggle('btn-outline-primary', !j.liked);
      btn.classList.toggle('btn-primary', j.liked);
    } else {
      alert('Failed to like.');
    }
  });

  /* ===== Delete post (list page) ===== */
  document.addEventListener('click', async (e) => {
    const del = e.target.closest('.btn-del, .btn-delete-post');
    if (!del) return;
    e.preventDefault();
    if (!confirm('Delete this post?')) return;
    const id = del.dataset.id;
    const res = await fetch(`/posts/api/${id}/delete/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrf() }
    });
    if (res.ok) {
      document.getElementById(`post-${id}`)?.remove();
      const feed = document.getElementById('feed');
      if (feed && !feed.querySelector('.post-card')) {
        const p = document.createElement('p');
        p.id = 'feed-empty';
        p.className = 'muted';
        p.textContent = 'No posts yet.';
        feed.appendChild(p);
      }
    } else {
      alert('Failed to delete');
    }
  });

  /* ===== Comments (detail page) ===== */

  // If a legacy template inserted an "empty" row, remove it once we add a real comment.
  function removeEmptyCommentsIfAny() {
    const list = document.getElementById('comment-list');
    if (!list) return;
    const empty =
      list.querySelector('#empty-comments') ||
      list.querySelector('[data-empty]') ||
      list.querySelector('.empty-comments') ||
      list.querySelector('.list-group-item.text-muted');
    if (empty) empty.remove();
  }

  const commentForm = document.querySelector('#comment-form');
  if (commentForm) {
    // create comment
    commentForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = commentForm.querySelector('input[name="body"]');
      const body  = (input?.value || '').trim();
      if (!body) return;

      const { ok, json } = await postForm(commentForm.action, commentForm);
      if (!ok) {
        alert('Failed to comment: ' + JSON.stringify(json));
        return;
      }

      const list = document.getElementById('comment-list');
      if (!list) return;

      removeEmptyCommentsIfAny();

      const li  = document.createElement('li');
      li.className = 'list-group-item d-flex justify-content-between align-items-start';
      li.id = `c-${json.id}`;
      li.innerHTML = `
        <div><strong>@${json.author}</strong> — ${json.body}</div>
        <button class="btn btn-sm btn-outline-danger btn-del-comment" data-id="${json.id}">Delete</button>
      `;
      list.appendChild(li);
      commentForm.reset();
    });

    // delete comment (do NOT re-add any placeholder)
    document.addEventListener('click', async (e) => {
      const btn = e.target.closest('.btn-del-comment');
      if (!btn) return;
      const id = btn.dataset.id;
      const res = await fetch(`/posts/api/comment/${id}/delete/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() }
      });
      if (!res.ok) {
        alert('Failed to delete comment.');
        return;
      }
      document.getElementById(`c-${id}`)?.remove();
      // Intentionally do nothing else: no placeholder should appear.
    });
  }
});
