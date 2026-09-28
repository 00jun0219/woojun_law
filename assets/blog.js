/* =====================================================================
   blog.js — 전 페이지 공용 스크립트 (홈·소개·업무분야·칼럼·개인정보)
   nav 스크롤·reveal·모바일메뉴·상담 모달·Formspree 제출.
   body 끝에서 로드되어 DOM 준비 후 실행.
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
    }, { threshold: 0.1, rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(el => observer.observe(el));
  }

  const hamburger = document.getElementById('hamburger');
  if (hamburger) hamburger.setAttribute('aria-expanded', 'false');

  // 폼 결과 안내 영역 (alert 대신) — 스크린리더가 읽도록 role=status
  const form = document.getElementById('contactForm');
  if (form) {
    const status = document.createElement('p');
    status.className = 'form-status';
    status.setAttribute('role', 'status');
    form.appendChild(status);
  }

  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
})();

function setMobile(open) {
  document.getElementById('mobile-menu').classList.toggle('open', open);
  const hamburger = document.getElementById('hamburger');
  if (hamburger) hamburger.setAttribute('aria-expanded', String(open));
}
function toggleMobile() { setMobile(!document.getElementById('mobile-menu').classList.contains('open')); }
function closeMobile() { setMobile(false); }

let modalOpener = null;
function openModal() {
  modalOpener = document.activeElement;
  document.getElementById('modal-overlay').classList.add('active');
  document.body.style.overflow = 'hidden';
  const first = document.getElementById('name');
  if (first) setTimeout(() => first.focus(), 50);
}
function closeModal() {
  const overlay = document.getElementById('modal-overlay');
  if (!overlay || !overlay.classList.contains('active')) return;
  overlay.classList.remove('active');
  document.body.style.overflow = '';
  const status = overlay.querySelector('.form-status');
  if (status) { status.textContent = ''; status.className = 'form-status'; }
  if (modalOpener && modalOpener.focus) modalOpener.focus();
}
function handleOverlayClick(e) { if (e.target === e.currentTarget) closeModal(); }

async function handleSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('.form-submit');
  const status = form.querySelector('.form-status');
  const originalText = submitBtn.textContent;
  submitBtn.textContent = '전송 중...';
  submitBtn.disabled = true;
  status.textContent = '';
  status.className = 'form-status';
  try {
    const response = await fetch(form.action, {
      method: 'POST',
      body: new FormData(form),
      headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) throw new Error(response.status);
    form.reset();
    status.className = 'form-status ok';
    status.textContent = '상담 신청이 접수되었습니다. 빠른 시일 내로 연락드리겠습니다.';
  } catch (err) {
    status.className = 'form-status err';
    status.textContent = '전송에 실패했습니다. 잠시 후 다시 시도하시거나 전화(0507-1379-6089)로 연락해 주세요.';
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
