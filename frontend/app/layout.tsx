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
  title: "LinkBay-CMS - L'Armaiolo delle Agenzie Digitali",
  description: "Gestione multi-tenant, marketplace, automazione: il tuo arsenale per conquistare infinite nicchie di mercato.",
  keywords: "CMS, multi-tenant, marketplace, e-commerce, agenzie digitali, LinkBay",
  authors: [{ name: "Alessio Quagliara" }],
  openGraph: {
    type: "website",
    locale: "it_IT",
    url: "https://linkbay-cms.com",
    siteName: "LinkBay-CMS",
    title: "LinkBay-CMS - L'Armaiolo delle Agenzie Digitali",
    description: "Gestione multi-tenant, marketplace, automazione: il tuo arsenale per conquistare infinite nicchie di mercato.",
    images: [
      {
        url: "/stretch-logo-std.png",
        width: 1200,
        height: 630,
        alt: "LinkBay-CMS",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "LinkBay-CMS - L'Armaiolo delle Agenzie Digitali",
    description: "Gestione multi-tenant, marketplace, automazione: il tuo arsenale per conquistare infinite nicchie di mercato.",
    images: ["/stretch-logo-std.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="it">
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
