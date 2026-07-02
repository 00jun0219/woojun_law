/* =====================================================================
   blog.js — 칼럼 섹션 공용 스크립트
   (index.html 스크립트에서 nav 스크롤·reveal·모바일메뉴·모달·Formspree
    제출 로직 이식. body 끝에서 로드되어 DOM 준비 후 실행.)
   함수는 인라인 onclick에서 호출되므로 전역 스코프 유지.
   ===================================================================== */

(function () {
  const nav = document.getElementById('main-nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 40);
    });
  }

  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
    }, { threshold: 0.1 });
    reveals.forEach(el => observer.observe(el));
  }

  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
})();

function toggleMobile() { document.getElementById('mobile-menu').classList.toggle('open'); }
function closeMobile() { document.getElementById('mobile-menu').classList.remove('open'); }

function openModal() {
  document.getElementById('modal-overlay').classList.add('active');
  document.body.style.overflow = 'hidden';
}
function closeModal() {
  const overlay = document.getElementById('modal-overlay');
  if (overlay) overlay.classList.remove('active');
  document.body.style.overflow = '';
}
function handleOverlayClick(e) { if (e.target === e.currentTarget) closeModal(); }

async function handleSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('.form-submit');
  const action = form.getAttribute('action');

  if (!action) {
    alert('상담 신청이 완료되었습니다.\n빠른 시일 내로 연락드리겠습니다.');
    closeModal();
    form.reset();
    return;
  }

  const originalText = submitBtn.textContent;
  submitBtn.textContent = '전송 중...';
  submitBtn.disabled = true;
  try {
    const response = await fetch(action, {
      method: 'POST',
      body: new FormData(form),
      headers: { 'Accept': 'application/json' }
    });
    if (response.ok) {
      alert('상담 신청이 완료되었습니다.\n빠른 시일 내로 연락드리겠습니다.');
      form.reset();
      closeModal();
    } else {
      alert('문제가 발생했습니다. 잠시 후 다시 시도해주세요.');
    }
  } catch (err) {
    alert('네트워크 오류입니다. 잠시 후 다시 시도해주세요.');
  } finally {
    submitBtn.textContent = originalText;
    submitBtn.disabled = false;
  }
}

/* 칼럼 허브 카테고리 필터 (진행적 향상 — JS 없어도 전체 카드 노출) */
function filterPosts(category, btn) {
  document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
  if (btn) btn.classList.add('active');
  document.querySelectorAll('.post-card').forEach(card => {
    const match = category === 'all' || card.getAttribute('data-category') === category;
    card.style.display = match ? '' : 'none';
  });
}
