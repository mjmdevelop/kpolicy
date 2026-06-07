import { site } from "@/lib/site";
import { getArticleData, formatDate, type Article } from "@/lib/articles";

export const revalidate = 1800; // 30분마다 재생성 (ISR)

function ArticleCard({ a, extreme = false }: { a: Article; extreme?: boolean }) {
  return (
    <a
      className={`card${extreme ? " extreme-card" : ""}`}
      href={a.link}
      target="_blank"
      rel="noopener noreferrer"
    >
      <p className="card-title">{a.title}</p>
      {a.summary && <p className="card-summary">{a.summary}</p>}
      <div className="card-meta">
        <span className="badge-outline">{a.source}</span>
        <span>{formatDate(a.pubDate)}</span>
        {extreme && <span className="badge">강성 표현 감지</span>}
      </div>
    </a>
  );
}

export default async function Home() {
  const data = await getArticleData();
  const mine = data.articles.filter((a) => a.side === site.side);
  const extremes = mine.filter((a) => a.extreme && a.extreme_dir === site.side);
  const rest = mine.filter((a) => !(a.extreme && a.extreme_dir === site.side));

  return (
    <>
      <header className="header">
        <div className="header-inner">
          <h1 className="brand">{site.brand}</h1>
          <p className="tagline">{site.tagline}</p>
          <p className="disclaimer">
            ⓘ 이 사이트는 사람이 아닌 <b>자동 분류 시스템</b>이 운영합니다. 각 기사의 분류는
            기사를 작성한 <b>언론사의 평소 논조(통념상 좌/우 성향)</b>를 기준으로 자동
            배정되며, 제목·요약에 등장하는 표현으로 &ldquo;강성/극단&rdquo; 여부를
            보조 판별합니다. 이는 해당 언론사·기자·기사에 대한 단정적 평가가 아니며,
            개별 기사의 실제 논조와 다를 수 있습니다. 본문은 게재하지 않으며 제목과
            요약 후 원문 링크로 연결합니다 (저작권은 각 언론사에 있습니다).
          </p>
        </div>
      </header>

      <main className="container">
        {extremes.length > 0 && (
          <section>
            <h2 className="section-title">
              <span className="badge">{site.extremeLabel}</span>
              <span style={{ fontWeight: 400, fontSize: 13, color: "var(--fg-muted)" }}>
                제목·요약의 표현을 기준으로 자동 추출 ({extremes.length}건)
              </span>
            </h2>
            {extremes.map((a) => (
              <ArticleCard key={a.id} a={a} extreme />
            ))}
          </section>
        )}

        <section>
          <h2 className="section-title">
            전체 기사
            <span style={{ fontWeight: 400, fontSize: 13, color: "var(--fg-muted)" }}>
              ({rest.length}건 · 최신순)
            </span>
          </h2>
          {rest.length === 0 && extremes.length === 0 ? (
            <p className="empty">아직 수집된 기사가 없습니다. 잠시 후 다시 확인해 주세요.</p>
          ) : (
            rest.map((a) => <ArticleCard key={a.id} a={a} />)
          )}
        </section>

        <footer className="footer">
          <p>
            마지막 업데이트:{" "}
            {data.updated ? formatDate(data.updated) : "정보 없음"} (Asia/Seoul)
          </p>
          <p>
            본 사이트는 각 언론사의 RSS 피드에서 제목·요약·링크만 수집하여 표시하며,
            기사 본문을 게재하지 않습니다. 분류 기준과 소스 목록은 공개되어 있으며
            언제든 조정될 수 있습니다. 특정 진영을 대변하거나 특정 매체를 비방할
            목적이 없으며, 다양한 시각의 기사를 한곳에서 비교해 볼 수 있도록 돕기
            위한 참고용 아카이브입니다.
          </p>
        </footer>
      </main>
    </>
  );
}
