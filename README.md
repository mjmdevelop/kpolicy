# 정치 뉴스 좌/우 모음 사이트

언론사 RSS에서 정치 기사의 **제목·요약·원문 링크**만 수집해, 출처(언론사)의
평소 논조를 기준으로 **좌(진보) 사이트**와 **우(보수) 사이트** 두 곳에 나눠
보여주는 프로젝트입니다. 제목·요약에 자극적 표현이 감지된 기사는
"강성/극단 추정 기사" 섹션에 별도로 모아 보여줍니다.

⚠️ **분류는 100% 자동(휴리스틱)이며 절대적 사실이 아닙니다.** 사이트 본문에도
이 점을 명시하는 디스클레이머가 항상 노출됩니다.

## 구조

```
policy/
├── sources.py      ← 언론사 RSS 목록 + 성향(lean) 매핑 + 극좌/극우 키워드
├── collector.py    ← RSS 수집 → 분류 → web/public/data/articles.json 저장
├── data/           ← 수집 시점별 아카이브 (articles_YYYYMMDD_HHMM.json)
└── web/            ← Next.js 앱 (좌/우 두 사이트가 같은 코드베이스를 공유)
    ├── lib/site.ts     ← NEXT_PUBLIC_SIDE 값으로 브랜드/색상/필터 분기
    ├── lib/articles.ts ← articles.json 로딩 + 타입
    └── app/page.tsx    ← 메인 페이지 (해당 side 기사 + 강성 섹션)
```

## 분류 방식 (저작권 안전 + API 비용 없음)

1. **출처 매핑**: `sources.py`의 `lean` 값(-2~+2)으로 좌/중도/우를 결정
   - `-2,-1` → 좌(left), `0` → 중도(center), `+1,+2` → 우(right)
2. **강성/극단 보정**: lean과 무관하게, 제목·요약에 `EXTREME_LEFT_KEYWORDS` /
   `EXTREME_RIGHT_KEYWORDS` 키워드가 있으면 `extreme: true`로 표시
   - ⚠️ "성향이 강한 매체 = 극단 매체"로 단정하지 않습니다. 반드시 실제
     문구를 근거로만 표시합니다 (collector.py의 `detect_extreme` 참고)
3. 본문은 절대 저장·게재하지 않으며, 제목+요약(180자 이내)+원문 링크만 보관

매핑·키워드는 모두 `sources.py` 한 파일에 모여 있으니, 특정 언론사를
추가/삭제하거나 lean 값·키워드를 조정하려면 그 파일만 고치면 됩니다.

## 로컬에서 실행하기

### 1) 데이터 수집

```bash
cd policy
python collector.py
```

`web/public/data/articles.json`에 결과가 저장됩니다 (Next.js가 빌드 시 읽음).

### 2) 웹 개발 서버

```bash
cd policy/web
npm install

# 좌측 사이트로 보기
NEXT_PUBLIC_SIDE=left  npm run dev

# 우측 사이트로 보기 (다른 포트 권장: PORT=3001 npm run dev)
NEXT_PUBLIC_SIDE=right npm run dev
```

(PowerShell에서는 `$env:NEXT_PUBLIC_SIDE="left"; npm run dev` 형태로 설정)

## Vercel에 "두 개의 별도 사이트"로 배포하기

같은 GitHub 저장소를 **Vercel 프로젝트 2개**로 각각 연결하고, 프로젝트별
환경변수만 다르게 주면 됩니다 (코드 중복 없이 운영 가능).

| 설정 | 프로젝트 A (좌측) | 프로젝트 B (우측) |
|---|---|---|
| Root Directory | `policy/web` | `policy/web` |
| `NEXT_PUBLIC_SIDE` | `left` | `right` |

두 사이트는 서로를 언급하거나 링크하지 않으며, 완전히 독립된 매체로 보이도록
의도적으로 분리되어 있습니다.

## 데이터 자동 갱신

`collector.py`를 주기적으로 실행해 `articles.json`을 새로 만들고 커밋·푸시하면,
Vercel이 재배포되면서 최신 기사로 갱신됩니다. (페이지 자체도 ISR로 30분마다
재생성되므로, 데이터 파일이 갱신되면 비교적 빨리 반영됩니다.)

기존 `aipicklab` 프로젝트의 `scheduler.py` / `auto_scheduler.py`처럼 Windows
작업 스케줄러나 cron으로 `python collector.py && git add -A && git commit ... && git push`를
주기 실행하면 완전 자동화할 수 있습니다.

## 면책 / 운영 원칙

- 특정 진영을 옹호하거나 특정 매체·인물을 비방할 목적이 없는 **참고용 아카이브**입니다.
- 모든 페이지에 "자동 분류이며 절대적 평가가 아니다"라는 디스클레이머를 노출합니다.
- 기사 본문을 게재하지 않고 항상 원문 링크로 연결해 언론사 저작권을 존중합니다.
- 분류 기준(`sources.py`)은 비공개로 숨기지 않고 코드로 공개되어 있어 누구나 검증할 수 있습니다.
