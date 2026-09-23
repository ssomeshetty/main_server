import type { Metadata, Viewport } from "next";
import "../globals.css";
import Navbar from "../../components/Navbar";
import Footer from "../../components/Footer";
import { Locale } from "../../lib/dictionary";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://politicianstracker.in';

export const viewport: Viewport = {
  themeColor: '#0f172a',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
};

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Karnataka Legislative & Parliamentary Tracker | Public Representative Database",
    template: "%s | Karnataka Legislative Tracker",
  },
  description: "Public database and derived analysis for Karnataka MLAs and MPs, including sworn affidavits, financial declarations, legal records, and portfolio disclosures.",
  keywords: [
    "Karnataka Politicians",
    "Karnataka MLAs",
    "Karnataka MPs",
    "Lok Sabha Karnataka 2024",
    "Karnataka Assembly 2023",
    "Karnataka Cabinet Ministers",
    "Karnataka Politician Net Worth",
    "DK Shivakumar net worth",
    "Siddaramaiah MLA assets",
    "MyNeta Karnataka",
    "Karnataka Election Affidavits",
    "Bengaluru MLAs",
  ],
  authors: [{ name: "Karnataka Legislative Tracker" }],
  creator: "Karnataka Legislative Tracker",
  publisher: "Karnataka Legislative Tracker",
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: "website",
    locale: "en_IN",
    alternateLocale: ["kn_IN"],
    url: SITE_URL,
    siteName: "Karnataka Legislative Tracker",
    title: "Karnataka Legislative & Parliamentary Tracker | Public Database",
    description: "Public records, asset disclosures, legal records, and portfolios of Karnataka MLAs and MPs.",
    images: [
      {
        url: `${SITE_URL}/og-image.jpg`,
        width: 1200,
        height: 630,
        alt: "Karnataka Legislative & Parliamentary Tracker",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Karnataka Legislative & Parliamentary Tracker",
    description: "Public records and financial declarations of Karnataka MLAs and MPs.",
    images: [`${SITE_URL}/og-image.jpg`],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export async function generateStaticParams() {
  return [{ lang: 'en' }, { lang: 'kn' }];
}

export default function RootLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode;
  params: { lang: Locale };
}>) {
  return (
    <html lang={params.lang}>
      <body>
        <Navbar lang={params.lang} />
        <main>{children}</main>
        <Footer lang={params.lang} />
      </body>
    </html>
  );
}
