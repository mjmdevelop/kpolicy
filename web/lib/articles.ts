import { promises as fs } from "fs";
import path from "path";

export interface Article {
  id: string;
  title: string;
  summary: string;
  link: string;
  source: string;
  lean: number;
  side: "left" | "center" | "right";
  extreme: boolean;
  extreme_dir: "left" | "right" | null;
  pubDate: string;
}

export interface ArticleData {
  updated: string;
  count: number;
  articles: Article[];
}

let cache: ArticleData | null = null;

export async function getArticleData(): Promise<ArticleData> {
  if (cache) return cache;
  const file = path.join(process.cwd(), "public", "data", "articles.json");
  try {
    const raw = await fs.readFile(file, "utf-8");
    cache = JSON.parse(raw) as ArticleData;
  } catch {
    cache = { updated: "", count: 0, articles: [] };
  }
  return cache;
}

export function formatDate(iso: string): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return new Intl.DateTimeFormat("ko-KR", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Seoul",
  }).format(d);
}
