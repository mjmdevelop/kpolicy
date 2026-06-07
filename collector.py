# collector.py — 정치 뉴스 RSS 수집 → 출처 성향 + 키워드 분류 → JSON 저장
#
# 사용법:
#   python collector.py
#
# 동작:
#   1) sources.py의 각 언론사 RSS를 수집 (정치 섹션 피드 우선, 실패 시 다음 URL)
#   2) 제목/요약/링크만 추출 (본문 미저장 → 저작권 안전, API 미사용)
#   3) 출처 lean으로 side(left/right/center) 결정, 키워드로 극단(extreme) 보정
#   4) web/public/data/articles.json + data/archive 에 저장
#
# 의존성: requests (이미 설치됨). RSS 파싱은 표준 라이브러리만 사용.

import sys
import json
import re
import html

# Windows 콘솔(cp949)에서도 한글/이모지 출력이 깨지지 않도록 UTF-8 강제
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.utils import parsedate_to_datetime

import requests

from sources import (
    HEADERS, SOURCES,
    EXTREME_LEFT_KEYWORDS, EXTREME_RIGHT_KEYWORDS,
    POLITICS_HINT_KEYWORDS,
)

BASE_DIR = Path(__file__).parent
WEB_DATA = BASE_DIR / "web" / "public" / "data"
ARCHIVE = BASE_DIR / "data"
WEB_DATA.mkdir(parents=True, exist_ok=True)
ARCHIVE.mkdir(parents=True, exist_ok=True)

KST = timezone(timedelta(hours=9))
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
MAX_PER_SOURCE = 40         # 언론사당 최대 기사 수
SUMMARY_LEN = 180           # 요약 최대 글자수


def clean_text(s: str) -> str:
    """HTML 태그/엔티티 제거 + 공백 정리."""
    if not s:
        return ""
    s = TAG_RE.sub(" ", s)
    s = html.unescape(s)
    s = WS_RE.sub(" ", s).strip()
    return s


def parse_date(raw: str) -> str:
    """RFC822 등 다양한 pubDate를 KST ISO 문자열로. 실패 시 빈 문자열."""
    if not raw:
        return ""
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=KST)
        return dt.astimezone(KST).isoformat()
    except Exception:
        return ""


def fetch_feed(urls):
    """여러 후보 URL을 순서대로 시도, 첫 성공 응답 텍스트 반환."""
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200 and "<item" in r.text:
                r.encoding = r.apparent_encoding or r.encoding
                return r.text, url
        except Exception as e:
            print(f"    · 실패 {url} ({str(e)[:50]})")
    return None, None


def parse_items(xml_text):
    """RSS 2.0 <item> 목록 파싱 → [{title, link, desc, pubDate}]."""
    items = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        # 깨진 XML 방어: <item>...</item> 블록 정규식 폴백
        for block in re.findall(r"<item[\s\S]*?</item>", xml_text):
            def grab(tag):
                m = re.search(rf"<{tag}[^>]*>([\s\S]*?)</{tag}>", block)
                return clean_text(m.group(1)) if m else ""
            items.append({"title": grab("title"), "link": grab("link"),
                          "desc": grab("description"), "pubDate": grab("pubDate")})
        return items

    for it in root.iter("item"):
        def t(tag):
            el = it.find(tag)
            return el.text if el is not None and el.text else ""
        items.append({
            "title": clean_text(t("title")),
            "link": (t("link") or "").strip(),
            "desc": clean_text(t("description")),
            "pubDate": t("pubDate"),
        })
    return items


def is_political(text: str) -> bool:
    return any(k in text for k in POLITICS_HINT_KEYWORDS)


def detect_extreme(text: str, side: str, lean: int):
    """(extreme: bool, extreme_dir: str|None) 반환.

    주의: '강성 매체 소속'만으로 기사를 극단으로 단정하지 않는다 — 출처 lean이
    강해도 내용이 평범할 수 있으므로, 반드시 제목/요약의 자극적 키워드 매칭을
    근거로 삼는다 (방향만 side/lean으로 정함).
    """
    if side == "left":
        hit = any(k in text for k in EXTREME_LEFT_KEYWORDS)
        return (hit, "left" if hit else None)
    if side == "right":
        hit = any(k in text for k in EXTREME_RIGHT_KEYWORDS)
        return (hit, "right" if hit else None)
    return (False, None)


def side_of(lean: int) -> str:
    if lean < 0:
        return "left"
    if lean > 0:
        return "right"
    return "center"


def collect():
    articles = []
    seen_links = set()

    for src in SOURCES:
        name, lean = src["name"], src["lean"]
        side = side_of(lean)
        print(f"[{name}] lean={lean} side={side}")
        xml_text, used = fetch_feed(src["rss"])
        if not xml_text:
            print(f"    × 모든 피드 실패, 건너뜀")
            continue
        items = parse_items(xml_text)
        added = 0
        for it in items:
            if added >= MAX_PER_SOURCE:
                break
            title, link = it["title"], it["link"]
            if not title or not link or link in seen_links:
                continue
            text = f"{title} {it['desc']}"
            # 섹션이 정치 전용이 아닐 수 있으니 힌트 키워드로 약하게 필터
            if not is_political(text):
                continue
            seen_links.add(link)
            extreme, edir = detect_extreme(text, side, lean)
            articles.append({
                "id": hashlib.md5(link.encode()).hexdigest()[:12],
                "title": title,
                "summary": it["desc"][:SUMMARY_LEN],
                "link": link,
                "source": name,
                "lean": lean,
                "side": side,
                "extreme": extreme,
                "extreme_dir": edir,
                "pubDate": parse_date(it["pubDate"]),
            })
            added += 1
        print(f"    ✓ {used}  →  {added}건")

    # 최신순 정렬
    articles.sort(key=lambda a: a["pubDate"], reverse=True)

    payload = {
        "updated": datetime.now(KST).isoformat(),
        "count": len(articles),
        "articles": articles,
    }

    out_web = WEB_DATA / "articles.json"
    out_web.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    stamp = datetime.now(KST).strftime("%Y%m%d_%H%M")
    (ARCHIVE / f"articles_{stamp}.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    left = sum(1 for a in articles if a["side"] == "left")
    right = sum(1 for a in articles if a["side"] == "right")
    center = sum(1 for a in articles if a["side"] == "center")
    ext = sum(1 for a in articles if a["extreme"])
    print("\n" + "=" * 40)
    print(f"총 {len(articles)}건  |  좌 {left} · 중도 {center} · 우 {right}  |  극단 {ext}")
    print(f"저장: {out_web}")
    print("=" * 40)


if __name__ == "__main__":
    collect()
