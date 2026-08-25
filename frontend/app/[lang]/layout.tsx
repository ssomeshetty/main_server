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
    default: "Karnataka Legislative & Parliamentary Tracker | Verified Representative Database",
    template: "%s | Karnataka Legislative Tracker",
  },
  description: "Official public database & asset intelligence for Karnataka State Assembly MLAs, Lok Sabha MPs, and tracked Rajya Sabha members representing Karnataka. Sworn affidavits, financial declarations, declared legal cases & portfolio disclosures.",
  keywords: [
    "Karnataka Politicians",
    "Karnataka MLAs",
    "Karnataka MPs",
    "Lok Sabha Karnataka 2024",
    "Karnataka Assembly 2023",
    "Karnataka Cabinet Ministers",
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
    title: "Karnataka Legislative & Parliamentary Tracker | Official Database",
    description: "Verified public records, asset disclosures, legal records, and portfolios of tracked Karnataka MLAs and MPs.",
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
    description: "Verified public records & financial declarations of tracked Karnataka MLAs & MPs.",
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
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+Kannada:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <Navbar lang={params.lang} />
        <main>{children}</main>
        <Footer lang={params.lang} />
      </body>
    </html>
  );
}
