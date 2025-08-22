// === helpers ===
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
  return '';
}

async function fetchJsonOrReload(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const ct = (res.headers.get('content-type') || '').toLowerCase();
  if (!ct.includes('application/json')) {
    // Сервер неожиданно вернул HTML (редирект/шаблон). На всякий случай обновим страницу.
    console.warn('Expected JSON, got', ct);
    const txt = await res.text(); // чтобы не висел body stream
    window.location.reload();
    throw new Error('Non-JSON response, reloading');
  }
  return await res.json();
}

// === AJAX Like ===
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('[data-like-btn]');
  if (!btn) return;

  e.preventDefault();
  if (btn.disabled) return; // защита
  btn.disabled = true;

  const url = btn.getAttribute('data-url');
  const csrftoken = getCookie('csrftoken');

  try {
    const data = await fetchJsonOrReload(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'X-Requested-With': 'XMLHttpRequest',
      },
    });

    const icon = btn.querySelector('i');
    const countSpan = btn.querySelector('[data-like-count]');
    if (data.liked) {
      icon.classList.remove('bi-heart');
      icon.classList.add('bi-heart-fill');
    } else {
      icon.classList.remove('bi-heart-fill');
      icon.classList.add('bi-heart');
    }
    if (countSpan) countSpan.textContent = data.likes_count;
  } catch (err) {
    console.error(err);
  } finally {
    btn.disabled = false;
  }
});

// === AJAX Add Comment (корневой) ===
document.addEventListener('submit', async (e) => {
  const form = e.target.closest('form[data-ajax-comment]');
  if (!form) return;

  e.preventDefault();
  const csrftoken = getCookie('csrftoken');
  const url = form.getAttribute('action');
  const btn = form.querySelector('button[type="submit"], button:not([type])');
  if (btn && btn.disabled) return;
  if (btn) btn.disabled = true;

  const formData = new FormData(form);
  try {
    const data = await fetchJsonOrReload(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: formData
    });

    const list = document.querySelector('[data-comments]');
    if (list && data.rendered_html) {
      list.insertAdjacentHTML('beforeend', data.rendered_html);
    }
    const textarea = form.querySelector('textarea[name="text"]');
    if (textarea) textarea.value = '';
  } catch (err) {
    console.error(err);
  } finally {
    if (btn) btn.disabled = false;
  }
});

// === AJAX Reply (ответ на комментарий) ===
document.addEventListener('submit', async (e) => {
  const form = e.target.closest('form[data-ajax-reply]');
  if (!form) return;

  e.preventDefault();
  const csrftoken = getCookie('csrftoken');
  const url = form.getAttribute('action');
  const btn = form.querySelector('button[type="submit"], button:not([type])');
  if (btn && btn.disabled) return;
  if (btn) btn.disabled = true;

  const formData = new FormData(form);
  try {
    const data = await fetchJsonOrReload(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: formData
    });

    const block = form.closest('[data-replies]') || document.querySelector('[data-comments]');
    if (block && data.rendered_html) {
      block.insertAdjacentHTML('beforeend', data.rendered_html);
    }
    const textarea = form.querySelector('textarea[name="text"]');
    if (textarea) textarea.value = '';
  } catch (err) {
    console.error(err);
  } finally {
    if (btn) btn.disabled = false;
  }
});
