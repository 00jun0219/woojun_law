# 새 칼럼을 허브(column/index.html)·홈 최근칼럼(index.html)·사이트맵(sitemap.xml)에 등록한다.
# 칼럼 페이지(column/<slug>/index.html)는 먼저 만들어 둘 것. 이 스크립트는 등록만 한다.
#
# 사용: python tools/add-column.py <slug> "<제목>" "<허브 요약(2~3문장)>" "<홈 요약(1~2문장)>" [YYYY-MM-DD]
# 검증: 실행 후 `python tools/add-column.py --check` 로 JSON-LD 파싱·첫 항목 확인.
import io, json, re, sys, datetime, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB, HOME, SITEMAP = "column/index.html", "index.html", "sitemap.xml"


def read(p): return io.open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, s): io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n").write(s)


def jsonld(s):
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    return json.loads(m.group(1))


def check():
    d = jsonld(read(HUB))
    bc = next(x for x in d["@graph"] if x["@type"] == "BreadcrumbList")["itemListElement"]
    il = next(x for x in d["@graph"] if x["@type"] == "CollectionPage")["mainEntity"]["itemListElement"]
    assert [x["position"] for x in bc] == [1, 2], bc
    assert [x["position"] for x in il] == list(range(1, len(il) + 1)), "ItemList 번호 불연속"
    print("breadcrumb ok / ItemList", len(il), "items, #1 =", il[0]["url"])
    cards = len(re.findall(r'<a class="post-card', read(HUB)))
    assert cards == len(il), f"허브 카드 {cards} != ItemList {len(il)}"
    print("hub cards =", cards)
    print("home cards =", len(re.findall(r'<a class="hc-card', read(HOME))))
    print("sitemap urls =", read(SITEMAP).count("<url>"))


def add(slug, title, excerpt, excerpt_short, date):
    url = f"https://chung-mu.com/column/{slug}/"
    dot = date.replace("-", ".")
    assert os.path.exists(os.path.join(ROOT, "column", slug, "index.html")), "칼럼 페이지가 없음"

    # 1) 허브: 카드 + ItemList (반드시 "@type": "ItemList" 뒤의 itemListElement에만 삽입)
    s = read(HUB)
    assert url not in s, "이미 등록됨"
    card = (f'      <a class="post-card reveal" href="/column/{slug}/" data-category="칼럼">\n'
            f'        <div class="post-card-top">\n          <span class="cat-badge cat-column">칼럼</span>\n'
            f'          <span class="post-card-date">{dot}</span>\n        </div>\n'
            f'        <div class="post-card-title">{title}</div>\n'
            f'        <div class="post-card-excerpt">{excerpt}</div>\n'
            f'        <div class="post-card-more">자세히 보기 →</div>\n      </a>\n')
    s = s.replace("      <!-- POSTS: 최신순 -->\n", "      <!-- POSTS: 최신순 -->\n" + card, 1)
    a = s.index('"@type": "ItemList"')
    b = s.index('"itemListElement": [\n', a) + len('"itemListElement": [\n')
    c = s.index("\n          ]", b)
    n = [1]
    def renum(m): n[0] += 1; return f'"position": {n[0]}'
    block = re.sub(r'"position": \d+', renum, s[b:c])
    item = (f'            {{\n              "@type": "ListItem",\n              "position": 1,\n'
            f'              "url": "{url}",\n              "name": "{title}"\n            }},\n')
    s = s[:b] + item + block + s[c:]
    write(HUB, s)

    # 2) 홈: 최근 칼럼 4장 — 맨 앞 삽입, 마지막 제거, reveal-delay 재부여
    s = read(HOME)
    st = s.index('<div class="home-column-grid">'); en = s.index('<div class="home-column-cta reveal">')
    cards = re.findall(r'      <a class="hc-card[^\n]*\n(?:.*?\n)*?      </a>\n', s[st:en])
    new = (f'      <a class="hc-card reveal" href="/column/{slug}/">\n        <div class="hc-card-top">\n'
           f'          <span class="hc-badge">칼럼</span>\n          <span class="hc-date">{dot}</span>\n        </div>\n'
           f'        <div class="hc-title">{title}</div>\n        <div class="hc-excerpt">{excerpt_short}</div>\n'
           f'        <div class="hc-more">자세히 보기 →</div>\n      </a>\n')
    kept = [new] + cards[:3]
    out = [re.sub(r'class="hc-card reveal[^"]*"', 'class="hc-card reveal"' if i == 0 else f'class="hc-card reveal reveal-delay-{i}"', c, count=1)
           for i, c in enumerate(kept)]
    s = s[:st] + '<div class="home-column-grid">\n' + "".join(out) + "    </div>\n" + s[en:]
    write(HOME, s)

    # 3) 사이트맵: 첫 칼럼 항목 앞에 삽입 + 허브 lastmod 갱신
    s = read(SITEMAP)
    entry = (f"  <url>\n    <loc>{url}</loc>\n    <lastmod>{date}</lastmod>\n"
             f"    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>\n")
    first = s.index("  <url>\n    <loc>https://chung-mu.com/column/")
    hub_end = s.index("</url>", first) + len("</url>\n")  # 첫 항목은 허브(/column/) → 그 다음에 삽입
    s = s[:hub_end] + entry + s[hub_end:]
    s = re.sub(r'(<loc>https://chung-mu.com/column/</loc>\s*<lastmod>)[\d-]+', r'\g<1>' + date, s)
    write(SITEMAP, s)
    print("registered:", slug)
    check()


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        check()
    elif len(sys.argv) >= 5:
        add(*sys.argv[1:5], sys.argv[5] if len(sys.argv) > 5 else datetime.date.today().isoformat())
    else:
        print(__doc__ or open(__file__, encoding="utf-8").read().split("import")[0])
