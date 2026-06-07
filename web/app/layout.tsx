import type { Metadata } from "next";
import { site } from "@/lib/site";
import "./globals.css";

export const metadata: Metadata = {
  title: site.brand,
  description: site.tagline,
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body
        style={
          {
            "--accent": site.accent,
            "--accent-soft": site.accentSoft,
          } as React.CSSProperties
        }
      >
        {children}
      </body>
    </html>
  );
}
