# 새 칼럼을 허브(column/index.html)·홈 최근칼럼(index.html)·사이트맵(sitemap.xml)에 등록한다.
# 칼럼 페이지(column/<slug>/index.html)는 먼저 만들어 둘 것. 이 스크립트는 등록만 한다.
#
# 사용: python tools/add-column.py <slug> "<제목>" "<허브 요약(2~3문장)>" "<홈 요약(1~2문장)>" [YYYY-MM-DD]
# 검증: 실행 후 `python tools/add-column.py --check` 로 JSON-LD 파싱·첫 항목 확인.
# 썸네일: 등록 후 커버 이미지를 추가했으면 `python tools/add-column.py --thumbs` 로 홈 카드 썸네일 재동기화.
# 피드: 등록 시 feed.xml(RSS)을 칼럼 JSON-LD에서 통째로 재생성한다. 수동 재생성은 `--feed`.
# 색인 알림: push·라이브 반영 **후** `python tools/add-column.py --ping <slug> [...]` (IndexNow → 네이버·Bing).
#           slug 없이 `--ping`이면 사이트맵 전체 URL을 보낸다.
import io, json, re, sys, datetime, os, glob, urllib.request
from email.utils import format_datetime
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB, HOME, SITEMAP, FEED = "column/index.html", "index.html", "sitemap.xml", "feed.xml"
NL = chr(10)
INDEXNOW_KEY = "2cd5b9db8eee988f3732f3bcefff2f53"  # 루트 <key>.txt 와 같아야 한다


def read(p): return io.open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, s): io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="\n").write(s)


def jsonld(s):
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    return json.loads(m.group(1))


# 홈 카드 썸네일: 칼럼 og:image가 자기 폴더의 이미지(커버)면 그 사진, 아니면 분야색 패널
THUMB_TONE = {"형사": "criminal", "민사": "civil", "부동산": "realestate", "가사·상속": "family", "엔터테인먼트·IP": "ip"}


def thumb(slug):
    page = read(f"column/{slug}/index.html")
    m = re.search(r'<meta property="og:image" content="https://chung-mu\.com(/column/' + re.escape(slug) + r'/[^"]+)"', page)
    if m:
        return f'        <div class="hc-thumb"><img src="{m.group(1)}" alt="" loading="lazy" /></div>\n'
    post = next((x for x in jsonld(page)["@graph"] if x["@type"] in ("BlogPosting", "NewsArticle")), {})
    sec = post.get("articleSection", "칼럼")
    return f'        <div class="hc-thumb hc-thumb-{THUMB_TONE.get(sec, "etc")}"><span>{sec}</span></div>\n'


def sync_thumbs():
    s = read(HOME)
    s = re.sub(r'        <div class="hc-thumb[^\n]*\n', '', s)
    s = re.sub(r'(      <a class="hc-card[^"]*" href="/column/([^/"]+)/">\n)', lambda m: m.group(1) + thumb(m.group(2)), s)
    write(HOME, s)
    print("home thumbs =", s.count('<div class="hc-thumb'))


def feed():
    posts = []
    for f in glob.glob(os.path.join(ROOT, "column", "*", "index.html")):
        p = next(x for x in jsonld(io.open(f, encoding="utf-8").read())["@graph"] if x["@type"] in ("BlogPosting", "NewsArticle"))
        posts.append(p)
    posts.sort(key=lambda p: (p["datePublished"], p["url"]), reverse=True)
    rfc = lambda d: format_datetime(datetime.datetime.fromisoformat(d[:10] + "T09:00:00+09:00"))
    head = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">', "  <channel>",
            "    <title>칼럼 | 변호사 최우준 · 법률사무소 청무</title>", "    <link>https://chung-mu.com/column/</link>",
            '    <atom:link href="https://chung-mu.com/feed.xml" rel="self" type="application/rss+xml" />',
            "    <description>변호사 최우준(법률사무소 청무)의 법률 칼럼</description>", "    <language>ko</language>",
            f"    <lastBuildDate>{rfc(posts[0]['datePublished'])}</lastBuildDate>"]
    items = [line for p in posts for line in (
        "    <item>", f"      <title>{escape(p['headline'])}</title>", f"      <link>{p['url']}</link>",
        f"      <guid>{p['url']}</guid>", f"      <pubDate>{rfc(p['datePublished'])}</pubDate>",
        f"      <category>{escape(p.get('articleSection', '칼럼'))}</category>",
        f"      <description>{escape(p.get('description', ''))}</description>", "    </item>")]
    write(FEED, NL.join(head + items + ["  </channel>", "</rss>", ""]))
    print("feed items =", len(posts))


def ping(slugs):
    urls = [f"https://chung-mu.com/column/{x}/" for x in slugs] or re.findall(r"<loc>([^<]+)</loc>", read(SITEMAP))
    body = json.dumps({"host": "chung-mu.com", "key": INDEXNOW_KEY, "keyLocation": f"https://chung-mu.com/{INDEXNOW_KEY}.txt",
                       "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", body, {"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=20) as r:  # 200/202 = 접수. 4xx는 HTTPError로 올라온다
        print("IndexNow", r.status, "/", len(urls), "urls")


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
    home = read(HOME)
    print("home cards =", len(re.findall(r'<a class="hc-card', home)), "/ thumbs =", home.count('<div class="hc-thumb'))
    print("sitemap urls =", read(SITEMAP).count("<url>"))
    n = read(FEED).count("<item>")
    assert n == len(il), f"피드 {n} != ItemList {len(il)} (--feed 로 재생성)"
    print("feed items =", n)


def add(slug, title, excerpt, excerpt_short, date):
    url = f"https://chung-mu.com/column/{slug}/"
    dot = date.replace("-", ".")
    assert os.path.exists(os.path.join(ROOT, "column", slug, "index.html")), "칼럼 페이지가 없음"
    assert "/assets/analytics.js" in read(f"column/{slug}/index.html"), "<head>에 GA4 analytics.js 누락"

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
    new = (f'      <a class="hc-card reveal" href="/column/{slug}/">\n' + thumb(slug) + '        <div class="hc-card-top">\n'
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
    feed()
    print("registered:", slug)
    check()


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        check()
    elif sys.argv[1:] == ["--thumbs"]:
        sync_thumbs()
    elif sys.argv[1:] == ["--feed"]:
        feed()
    elif sys.argv[1:2] == ["--ping"]:
        ping(sys.argv[2:])
    elif len(sys.argv) >= 5:
        add(*sys.argv[1:5], sys.argv[5] if len(sys.argv) > 5 else datetime.date.today().isoformat())
    else:
        print(__doc__ or open(__file__, encoding="utf-8").read().split("import")[0])
