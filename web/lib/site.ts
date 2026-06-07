// site.ts — 빌드 시점 환경변수(NEXT_PUBLIC_SIDE)로 좌/우 사이트를 분기
//
// 같은 코드베이스를 Vercel에 두 번 배포하고, 프로젝트별 환경변수만 다르게
// 설정하면 "좌(진보) 사이트"와 "우(보수) 사이트" 두 개가 만들어집니다.
//
//   프로젝트 A: NEXT_PUBLIC_SIDE=left   NEXT_PUBLIC_SISTER_URL=https://<우측사이트>
//   프로젝트 B: NEXT_PUBLIC_SIDE=right  NEXT_PUBLIC_SISTER_URL=https://<좌측사이트>

export type Side = "left" | "right";

export interface SiteConfig {
  side: Side;
  brand: string;
  tagline: string;
  accent: string;       // 메인 강조색
  accentSoft: string;   // 옅은 배경색
  extremeLabel: string; // 극단 섹션 라벨
  sisterLabel: string;  // 자매 사이트로 가는 안내 문구
  sisterUrl: string;
}

const RAW_SIDE = (process.env.NEXT_PUBLIC_SIDE ?? "left").toLowerCase();
export const SIDE: Side = RAW_SIDE === "right" ? "right" : "left";

const CONFIGS: Record<Side, SiteConfig> = {
  left: {
    side: "left",
    brand: "정치 좌편향 뉴스 모음",
    tagline: "진보 성향 매체의 정치 기사를 한곳에",
    accent: "#1d4ed8",
    accentSoft: "#eff6ff",
    extremeLabel: "강성 / 극좌 추정 기사",
    sisterLabel: "보수 성향 기사 모음 보기 →",
    sisterUrl: process.env.NEXT_PUBLIC_SISTER_URL ?? "#",
  },
  right: {
    side: "right",
    brand: "정치 우편향 뉴스 모음",
    tagline: "보수 성향 매체의 정치 기사를 한곳에",
    accent: "#b91c1c",
    accentSoft: "#fef2f2",
    extremeLabel: "강성 / 극우 추정 기사",
    sisterLabel: "진보 성향 기사 모음 보기 →",
    sisterUrl: process.env.NEXT_PUBLIC_SISTER_URL ?? "#",
  },
};

export const site: SiteConfig = CONFIGS[SIDE];
