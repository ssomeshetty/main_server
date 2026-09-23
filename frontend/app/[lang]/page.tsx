import Link from 'next/link';
import type { Metadata } from 'next';
import { Search, Landmark, Building2, Crown, MapPin } from 'lucide-react';
import { getDictionary, Locale } from '../../lib/dictionary';

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://politicianstracker.in';

export async function generateMetadata({
  params: { lang },
}: {
  params: { lang: Locale };
}): Promise<Metadata> {
  const isKn = lang === 'kn';

  const title = isKn
    ? 'ಕರ್ನಾಟಕ ಶಾಸಕರು ಮತ್ತು ಸಂಸದರ ಆಸ್ತಿ ಹಾಗೂ ಸಾರ್ವಜನಿಕ ದಾಖಲೆಗಳ ಅಧಿಕೃತ ಮಾಹಿತಿ | ಕರ್ನಾಟಕ ಶಾಸಕರ ಟ್ರ್ಯಾಕರ್'
    : 'Karnataka Legislative & Parliamentary Directory | 224 MLAs & 28 Lok Sabha MPs';

  const description = isKn
    ? 'ಕರ್ನಾಟಕದ 224 ವಿಧಾನಸಭಾ ಶಾಸಕರು ಮತ್ತು 28 ಲೋಕಸಭಾ ಸಂಸದರ ಸಮಗ್ರ ಸಾರ್ವಜನಿಕ ಮಾಹಿತಿ. ಅಧಿಕೃತ ಆಸ್ತಿ ವಿವರಗಳು, ಶೈಕ್ಷಣಿಕ ಮಾಹಿತಿಗಳು ಮತ್ತು ಕ್ರಿಮಿನಲ್ ಪ್ರಕರಣಗಳು.'
    : 'Public records and declared disclosures for all 224 Karnataka MLAs and 28 Lok Sabha Members of Parliament. Search sworn affidavits, asset declarations, and portfolios.';

  return {
    title,
    description,
    alternates: {
      canonical: `${SITE_URL}/${lang}`,
      languages: {
        en: `${SITE_URL}/en`,
        kn: `${SITE_URL}/kn`,
      },
    },
    openGraph: {
      title,
      description,
      url: `${SITE_URL}/${lang}`,
      siteName: 'Karnataka Legislative Tracker',
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
    },
  };
}

export const revalidate = 300; // ISR 5 minutes

export default async function Home({
  params: { lang },
}: {
  params: { lang: Locale };
}) {
  const dict = await getDictionary(lang);

  const jsonLdWebSite = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'Karnataka Legislative Tracker',
    url: `${SITE_URL}/${lang}`,
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${SITE_URL}/${lang}/politicians?search={search_term_string}`,
      },
      'query-input': 'required name=search_term_string',
    },
  };

  const jsonLdOrg = {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'Karnataka Legislative Assembly & Parliamentary Information System',
    alternateName: 'Karnataka Legislative Tracker',
    url: `${SITE_URL}/${lang}`,
    sameAs: ['https://myneta.info', 'https://kla.kar.nic.in'],
  };

  return (
    <div>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdWebSite) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdOrg) }}
      />

      {/* Authoritative Header Hero */}
      <section style={{ background: '#ffffff', color: '#0f172a', padding: '56px 0 48px', borderBottom: '1px solid #cbd5e1' }}>
        <div className="container" style={{ textAlign: 'center', maxWidth: '860px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '4px 12px', borderRadius: '4px', background: '#f1f5f9', border: '1px solid #cbd5e1', color: '#475569', fontSize: '0.78rem', fontWeight: 600, letterSpacing: '0.04em', textTransform: 'uppercase', marginBottom: '16px' }}>
            <Landmark size={14} color="#475569" /> {lang === 'kn' ? 'ಸಾರ್ವಜನಿಕ ಶಾಸಕಾಂಗ ಮಾಹಿತಿ ಭಂಡಾರ' : 'PUBLIC LEGISLATIVE DATA REPOSITORY'}
          </div>
          
          <h1 style={{ fontSize: '2.3rem', fontWeight: 800, letterSpacing: '-0.02em', lineHeight: '1.25', marginBottom: '12px', color: '#0f172a' }}>
            {lang === 'kn' ? 'ಕರ್ನಾಟಕ ಶಾಸಕಾಂಗ ಟ್ರ್ಯಾಕರ್' : 'Karnataka Legislative Tracker'}
          </h1>
          
          <p style={{ fontSize: '1.05rem', color: '#475569', lineHeight: '1.6', marginBottom: '32px', fontWeight: 400 }}>
            {lang === 'kn'
              ? <>ಕರ್ನಾಟಕವನ್ನು ಪ್ರತಿನಿಧಿಸುವ <strong>224 ವಿಧಾನಸಭಾ ಶಾಸಕರು</strong> ಮತ್ತು <strong>28 ಲೋಕಸಭಾ ಸಂಸದರ</strong> ಅಧಿಕೃತ ಆಸ್ತಿ ಘೋಷಣೆಗಳು, ಶಪಥಪತ್ರಗಳು ಮತ್ತು ಚುನಾವಣಾ ಮಾಹಿತಿ.</>
              : <>Financial affidavits, asset disclosures, and electoral background records for <strong>224 Assembly MLAs</strong> and <strong>28 Lok Sabha MPs</strong> representing Karnataka.</>}
          </p>

          {/* Clean High-Contrast Search Bar */}
          <form method="GET" action={`/${lang}/politicians`} className="hero-search-form">
            <div className="hero-search-container">
              <Search className="hero-search-icon" size={18} />
              <input
                type="text"
                name="search"
                placeholder={lang === 'kn' ? 'ಹೆಸರಿನಿಂದ ಶಾಸಕರನ್ನು ಹುಡುಕಿ...' : 'Search representative by name...'}
                className="hero-search-input"
              />
              <button type="submit" className="btn btn-primary hero-search-btn">
                {lang === 'kn' ? 'ಹುಡುಕಿ' : 'Search'}
              </button>
            </div>
          </form>

          {/* Clean Navigation Shortcuts */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '12px', flexWrap: 'wrap', fontSize: '0.85rem' }}>
            <span style={{ color: '#64748b' }}>{lang === 'kn' ? 'ತ್ವರಿತ ಲಿಂಕ್‌ಗಳು:' : 'Quick Directories:'}</span>
            <Link href={`/${lang}/politicians?type=mp`} style={{ color: '#1e3a8a', fontWeight: 600, textDecoration: 'none' }}>
              {lang === 'kn' ? 'ಲೋಕಸಭಾ ಸಂಸದರು (28)' : 'Lok Sabha MPs (28)'}
            </Link>
            <span style={{ color: '#cbd5e1' }}>•</span>
            <Link href={`/${lang}/politicians?type=union_minister`} style={{ color: '#1e3a8a', fontWeight: 600, textDecoration: 'none' }}>
              {lang === 'kn' ? 'ಕೇಂದ್ರ ಸಚಿವರು' : 'Union Ministers'}
            </Link>
            <span style={{ color: '#cbd5e1' }}>•</span>
            <Link href={`/${lang}/analytics`} style={{ color: '#1e3a8a', fontWeight: 600, textDecoration: 'none' }}>
              {lang === 'kn' ? 'ಆಸ್ತಿ ವಿಶ್ಲೇಷಣೆ' : 'Financial Asset Audit'}
            </Link>
          </div>
        </div>
      </section>

      {/* Institutional Key Metrics Grid */}
      <section className="container" style={{ marginTop: '32px', marginBottom: '40px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 220px), 1fr))', gap: '16px' }}>
          
          <div className="dashboard-section" style={{ padding: '20px', borderRadius: '8px', background: '#ffffff', border: '1px solid var(--border-subtle)', boxShadow: 'var(--shadow-sm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Assembly MLAs</span>
              <Building2 size={18} color="#475569" />
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' }}>224</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>16th Karnataka Assembly</div>
          </div>

          <div className="dashboard-section" style={{ padding: '20px', borderRadius: '8px', background: '#ffffff', border: '1px solid var(--border-subtle)', boxShadow: 'var(--shadow-sm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Lok Sabha MPs</span>
              <Landmark size={18} color="#475569" />
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' }}>28</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>18th Lok Sabha (2024–29)</div>
          </div>

          <div className="dashboard-section" style={{ padding: '20px', borderRadius: '8px', background: '#ffffff', border: '1px solid var(--border-subtle)', boxShadow: 'var(--shadow-sm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Union Cabinet</span>
              <Crown size={18} color="#475569" />
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' }}>5</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Union Ministers from KA</div>
          </div>

          <div className="dashboard-section" style={{ padding: '20px', borderRadius: '8px', background: '#ffffff', border: '1px solid var(--border-subtle)', boxShadow: 'var(--shadow-sm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>Districts</span>
              <MapPin size={18} color="#475569" />
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a' }}>31</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Administrative Districts</div>
          </div>

        </div>
      </section>

      {/* No individual politicians lists are shown on the homepage per design specification */}
    </div>
  );
}
