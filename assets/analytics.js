/* =====================================================================
   analytics.js — GA4 + 상담 전환 클릭 이벤트 (모든 페이지 <head>에서 async 로드)
   GA4: 계정 "법률사무소 청무" / 속성 "chung-mu.com" (556086578)
   ※ 사건부 앱 속성(G-2TVTBR5R18)과 혼동 금지.
   이벤트: phone_call_click / kakao_click / consult_click
           파라미터 link_location (+ GA4 자동 page_location) — 전화번호·개인정보는 넣지 않는다.
   ===================================================================== */

(function () {
  var GA_ID = 'G-BHZWEFSN4L';

  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
  document.head.appendChild(s);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  gtag('js', new Date());
  gtag('config', GA_ID);

  // 버튼 위치: float / header / footer / faq / 그 외는 소속 section의 id·class
  function where(a) {
    if (a.closest('.float-btns')) return 'float';
    if (a.closest('#main-nav, #mobile-menu')) return 'header';
    if (a.closest('footer')) return 'footer';
    if (a.closest('.faq-section, .faq')) return 'faq';
    if (a.closest('.cta-section, .post-cta')) return 'cta';
    var sec = a.closest('section');
    return sec ? (sec.id || sec.classList[0] || 'section') : 'body';
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var ev;
    if (href.indexOf('tel:') === 0) ev = 'phone_call_click';
    else if (/(open|pf)\.kakao\.com/.test(href)) ev = 'kakao_click';
    else if (/consult-chungmu\.vercel\.app/.test(href) ||
             /openModal/.test(a.getAttribute('onclick') || '')) ev = 'consult_click';
    if (!ev) return;
    // 페이지 경로는 GA4가 모든 이벤트에 page_location으로 자동 기록(보고서 '페이지 경로' 측정기준).
    // gtag.js는 page_path 파라미터를 버리고, 전송은 기본이 beacon이라 transport_type 불필요.
    gtag('event', ev, { link_location: where(a) });
  }, true);
})();
