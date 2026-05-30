import type { Metadata } from "next";
import localFont from "next/font/local";
import { Electrolize } from "next/font/google";
import "./globals.css";
import { Header } from "./components/Header";
import { Footer } from "./components/Footer";
import CookieConsentBanner from "./components/Cookie";

const dubai = localFont({
  src: [
    {
      path: "../public/font/Dubai-Light.ttf",
      weight: "300",
      style: "normal",
    },
    {
      path: "../public/font/Dubai-Regular.ttf",
      weight: "400",
      style: "normal",
    },
    {
      path: "../public/font/Dubai-Medium.ttf",
      weight: "500",
      style: "normal",
    },
    {
      path: "../public/font/Dubai-Bold.ttf",
      weight: "700",
      style: "normal",
    },
  ],
  variable: "--font-dubai",
  fallback: ["system-ui", "sans-serif"],
});

const electrolize = Electrolize({
  weight: "400",
  variable: "--font-electrolize",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LinkBay-CMS — Commerce infrastructure for digital agencies",
  description: "Manage all your client stores from one dashboard. White-label delivery, recurring revenue, reusable layouts, and AI assistance for agencies running multiple stores.",
  keywords: "agency CMS, white-label commerce, client store management, agency dashboard, recurring revenue, LinkBay",
  authors: [{ name: "Alessio Quagliara" }],
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://linkbay-cms.com",
    siteName: "LinkBay-CMS",
    title: "LinkBay-CMS — Commerce infrastructure for digital agencies",
    description: "Manage all your client stores from one dashboard. White-label delivery, recurring revenue, reusable layouts, and AI assistance for agencies running multiple stores.",
    images: [
      {
        url: "/logo.svg",
        width: 1200,
        height: 630,
        alt: "LinkBay-CMS",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "LinkBay-CMS — Commerce infrastructure for digital agencies",
    description: "Manage all your client stores from one dashboard. White-label delivery, recurring revenue, reusable layouts, and AI assistance for agencies running multiple stores.",
    images: ["/logo.svg"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${dubai.variable} ${electrolize.variable} antialiased font-dubai`}
      >
        <div className="min-h-screen bg-gray-50 flex flex-col">
          <Header />
          <main className="flex-1 pt-16 md:pt-20" id="top">
            {children}
          </main>
          <CookieConsentBanner />
          <Footer />
        </div>
      </body>
    </html>
  );
}
