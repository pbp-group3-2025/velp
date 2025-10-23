// static/js/report.js

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return decodeURIComponent(parts.pop().split(';').shift());
}
const csrftoken = getCookie('csrftoken');

const modal = document.getElementById('reportModal');
const form = document.getElementById('reportForm');
const feedback = document.getElementById('reportFeedback');
const submitBtn = document.getElementById('reportSubmitBtn');

const modeInput = document.getElementById('report-mode');
const modalTitle = document.getElementById('reportModalTitle');

const contentTypeInput = document.getElementById('report-content-type');
const objectIdInput = document.getElementById('report-object-id');
const targetTypeInput = document.getElementById('report-target-type');

const reasonSelect = document.getElementById('report-reason');
const detailsTextarea = document.getElementById('report-details');

function openModal() {
  feedback.classList.add('hidden');
  feedback.textContent = '';
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}
function closeModal() {
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}

// Event delegation for open/close + mode switching
if (modal && form) {
  document.addEventListener('click', (e) => {
    const createBtn = e.target.closest('[data-open-report]');
    const closeBtn  = e.target.closest('[data-close-report]');
    const editBtn   = e.target.closest('[data-edit-report]');

    if (createBtn) {
      // CREATE mode
      modeInput.value = 'create';
      modalTitle.textContent = 'Report content';
      form.action = form.dataset.createAction || form.action; // default points to create URL in template
      reasonSelect.value = 'inappropriate';
      detailsTextarea.value = '';

      contentTypeInput.value = createBtn.dataset.ctId;
      objectIdInput.value    = createBtn.dataset.objectId;
      targetTypeInput.value  = createBtn.dataset.targetType;
      openModal();
    }

    if (editBtn) {
      // EDIT mode
      modeInput.value = 'edit';
      modalTitle.textContent = 'Edit your report';
      form.action = editBtn.dataset.reportAction; // /reports/update/<id>/

      // For EDIT, we don't need content_type/object_id/target_type (ignored by update view)
      contentTypeInput.value = '';
      objectIdInput.value    = '';
      targetTypeInput.value  = '';

      // Prefill existing values
      reasonSelect.value   = editBtn.dataset.reportReason || 'inappropriate';
      detailsTextarea.value = editBtn.dataset.reportDetails || '';
      openModal();
    }

    if (closeBtn) {
      closeModal();
    }
  });

  // Submit handler covers both create and edit
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    submitBtn.disabled = true;
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken },
        body: new FormData(form),
      });
      const data = await res.json();

      feedback.classList.remove('hidden');
      if (res.ok && data.ok) {
        feedback.classList.remove('text-red-600');
        feedback.classList.add('text-green-600');
        feedback.textContent = data.message || (modeInput.value === 'edit' ? 'Report updated.' : 'Report submitted.');
        setTimeout(() => { closeModal(); form.reset(); location.reload(); }, 700);
      } else {
        feedback.classList.remove('text-green-600');
        feedback.classList.add('text-red-600');
        feedback.textContent = data.message || 'Failed to process.';
      }
    } catch {
      feedback.classList.remove('hidden');
      feedback.classList.add('text-red-600');
      feedback.textContent = 'Network error. Please try again.';
    } finally {
      submitBtn.disabled = false;
    }
  });
}
