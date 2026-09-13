# 칼럼 페이지 작성 스펙 (에이전트용)

`column/<slug>/index.html` 한 편을 만드는 규격. 등록(허브·홈·사이트맵)은 `tools/add-column.py`가 따로 처리하므로 **이 문서는 페이지 작성만 다룬다.**

## 0. 먼저 할 일

**가장 가까운 기존 칼럼 한 편을 통째로 복제해서 내용만 바꾼다.** 새 마크업을 발명하지 말 것.

권장 원본:
- 절차 해설형 → `column/payment-order/index.html`
- 제도 총론형 → `column/juvenile-protection-cases/index.html`

헤더 nav / 모바일 메뉴 / footer / float-btns / 상담 모달 / 폰트·CSS 인클루드는 **100% 동일**하다. 손대지 말고 그대로 둔다.

## 1. 바꿔야 하는 것 (빠짐없이)

### `<head>`
`<title>` · `description` · `keywords` · `canonical` · `og:*` / `twitter:*` 전 세트(제목·설명·url) · `article:published_time`.

- `article:section`은 **항상 `"칼럼"` 고정** (글의 형식). JSON-LD의 `articleSection`과 다른 값이다.
- `theme-color`는 `#2D665C` 그대로.
- `og:image`는 원본 칼럼 값을 그대로 두되, 히어로 이미지를 만들지 않으므로 **`column/<slug>/cover.jpg`를 가리키게 바꾸지 말 것** (파일이 없으면 깨진다).

### body
- breadcrumb 마지막 `<span>` — 링크 없는 짧은 제목
- `article-meta` 날짜 — `<time datetime="YYYY-MM-DD">YYYY년 M월 D일</time>`
- `<h1 class="article-title">`
- `article-byline`은 그대로 (`글 · 변호사 최우준 (법률사무소 청무)`)
- `<div class="post-body">` 본문 전체
- `post-cta` 문구
- `post-related` 링크 2~4개
- `back-to-hub`는 그대로

### JSON-LD (`@graph` 3객체)
1. `BreadcrumbList` — 3단계, position 1~3
2. `BlogPosting` — `headline` · `description` · `datePublished`/`dateModified` · `url` · `mainEntityOfPage` · `keywords` · **`articleSection`(법률 분야: 형사 / 민사 / 부동산 / 가사·상속 / 엔터테인먼트·IP)**
   `author`/`publisher`는 `@id` 참조이므로 **절대 건드리지 말 것**
3. `FAQPage` — 본문 "자주 묻는 질문" 섹션과 **1:1 정확히 대응**

## 2. 본문 문체 — 블로그와 다르다

블로그(`naver-blog/posts/<slug>/paste.html`)는 검색용 Q&A 구조다. **칼럼은 읽히는 글이다.** 같은 주제를 다루되 **문장을 재사용하지 말고 새로 쓴다** (검색엔진 중복 콘텐츠 회피).

| | 블로그 | 칼럼 |
|---|---|---|
| 도입 | 정의문 즉답 | `<blockquote>` — 상담실에서 실제로 듣는 질문이나 장면 |
| 소제목 | 질문형("~인가요?") | 서술형 명제("~입니다", "~가 갈리는 지점") |
| 전개 | 섹션별 독립 완결 | 앞뒤가 이어지는 서사 |
| 톤 | 정보 전달 | 판단과 관점, 실무에서 본 것 |

구조: `<blockquote>` 도입 → `<h2>` 소제목 5~7개 + `<p>`/`<ul><li>` → `<h2>자주 묻는 질문</h2>` (FAQ 2~3개) → 면책 문구.

면책은 인라인 스타일 그대로:
`<p style="margin-top:2.5rem; font-size:0.86rem; color:var(--warm-gray-light);">※ 이 글은 일반적인 정보 제공을 …`

본문 클래스는 `post-body` 안의 기본 태그(`h2`, `p`, `ul`, `li`, `strong`, `blockquote`)만 쓴다. 커스텀 클래스를 만들지 말 것.

## 3. 콘텐츠 원칙 (절대 위반 금지)

- **블로그 본문에 있는 조문·사실만 쓴다.** 판례번호·조문·수치를 새로 만들어 넣지 말 것. 블로그에서 의도적으로 뺀 것(개정 취약 수치 등)은 칼럼에서도 뺀다.
- 변호사 광고규정: 단정·과장 금지("무조건 무죄", "100% 승소"). 현실적 분석 톤.
- **'청하' 명칭 사용 금지.** 사무소명은 '법률사무소 청무', 담당자는 '최우준 변호사'.

## 4. 하지 말 것

- `column/index.html`, 루트 `index.html`, `sitemap.xml`, `llms.txt` **수정 금지.** 등록은 메인이 `add-column.py`로 순차 처리한다. 동시에 건드리면 파일이 깨진다.
- `tools/add-column.py` 실행 금지.
- 다른 slug 폴더 건드리지 말 것.
- 이미지 파일 생성 금지.

## 5. 보고

파일 전문을 붙여넣지 말고 아래만 보고한다:
제목 / `articleSection` 값 / `<h2>` 소제목 목록 / FAQ 질문 목록 / 본문 글자 수 /
`post-related` 링크 대상 / 블로그에서 가져온 조문 목록 /
그리고 **add-column.py에 넘길 인자 3개**: 제목, 허브 요약(2~3문장), 홈 요약(1~2문장).
