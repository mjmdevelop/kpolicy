# sources.py — 언론사 RSS 목록 + 정치 성향(논조) 매핑 + 극좌/극우 보정 키워드
#
# ⚠️ 중요 안내
#   - 아래 lean 값은 "언론사별 편집 논조에 대한 통념(미디어 바이어스 차트류)"을
#     참고한 *분류 기준*일 뿐, 절대적 사실이 아닙니다.
#   - 이 파일 하나만 수정하면 전체 분류 결과가 바뀝니다. 자유롭게 조정하세요.
#   - 사이트에는 반드시 "출처 기준 자동 분류 / 참고용" 디스클레이머가 노출됩니다.
#
# lean 척도 (-2 ~ +2)
#   -2 : 진보 강 (극좌 후보군)
#   -1 : 진보
#    0 : 중도 / 통신사
#   +1 : 보수
#   +2 : 보수 강 (극우 후보군)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

# 각 언론사: name(표기명), lean(성향 점수), rss(정치 섹션 피드 우선, 여러 개면 순서대로 시도)
SOURCES = [
    # ── 진보 계열 ──────────────────────────────────────────────
    {
        "name": "오마이뉴스",
        "lean": -2,
        "rss": ["http://rss.ohmynews.com/rss/politics.xml",
                "http://rss.ohmynews.com/rss/ohmynews.xml"],
    },
    {
        "name": "한겨레",
        "lean": -1,
        "rss": ["https://www.hani.co.kr/rss/politics/",
                "https://www.hani.co.kr/rss/"],
    },
    {
        "name": "경향신문",
        "lean": -1,
        "rss": ["https://www.khan.co.kr/rss/rssdata/politic_news.xml",
                "https://www.khan.co.kr/rss/rssdata/total_news.xml"],
    },
    # ── 중도 / 통신사 ─────────────────────────────────────────
    {
        "name": "연합뉴스",
        "lean": 0,
        "rss": ["https://www.yna.co.kr/rss/politics.xml",
                "https://www.yna.co.kr/rss/news.xml"],
    },
    {
        "name": "서울신문",
        "lean": 0,
        "rss": ["https://www.seoul.co.kr/xml/rss/rss_politics.xml"],
    },
    # ── 보수 계열 ──────────────────────────────────────────────
    {
        "name": "세계일보",
        "lean": 1,
        "rss": ["https://www.segye.com/Articles/RSSList/segye_politic.xml"],
    },
    {
        "name": "동아일보",
        "lean": 1,
        "rss": ["https://rss.donga.com/politics.xml",
                "https://rss.donga.com/total.xml"],
    },
    {
        "name": "조선일보",
        "lean": 2,
        "rss": ["https://www.chosun.com/arc/outboundfeeds/rss/?outputType=xml"],
    },
]

# ── 극좌 / 극우 보정 키워드 ───────────────────────────────────
#   출처 성향(lean)이 한쪽으로 치우친 기사 중, 아래 키워드가 제목/요약에
#   포함되면 "극단(extreme)" 후보로 강조 표시합니다.
#   ⚠️ 어디까지나 휴리스틱입니다. 정치적으로 민감한 표현이니 직접 검토·수정하세요.
EXTREME_LEFT_KEYWORDS = [
    "검찰독재", "검찰개혁", "적폐", "토착왜구", "친일", "내란", "윤석열 퇴진",
    "정권 심판", "특검", "탄핵",
]
EXTREME_RIGHT_KEYWORDS = [
    "종북", "주사파", "좌파독재", "부정선거", "반국가세력", "빨갱이",
    "자유우파", "척결", "이재명 심판", "방탄",
]

# 정치 기사 필터(섹션 RSS가 아닌 전체 RSS를 쓸 때 노이즈 제거용)
POLITICS_HINT_KEYWORDS = [
    "대통령", "국회", "여당", "야당", "與", "野", "민주당", "국민의힘", "정부",
    "장관", "의원", "총리", "청와대", "용산", "특검", "탄핵", "대선", "총선",
    "개혁신당", "조국혁신당", "정의당", "한동훈", "이재명", "외교", "안보",
]
