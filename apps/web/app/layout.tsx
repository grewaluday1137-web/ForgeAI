import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { Providers } from "@/components/providers";
import Script from "next/script";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "ForgeAI",
  description: "Autonomous Software Engineering Team",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <Script id="theme-script" strategy="beforeInteractive">{`
          (function() {
            try {
              var t = localStorage.getItem('forgeai-theme') || 'dark';
              var d = t === 'system' ? window.matchMedia('(prefers-color-scheme: dark)').matches : t === 'dark';
              if (d) document.documentElement.classList.add('dark');
            } catch(e) { document.documentElement.classList.add('dark'); }
          })();
        `}</Script>
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
