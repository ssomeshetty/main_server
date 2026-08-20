import Link from 'next/link';
import type { Metadata } from 'next';
import { getDictionary, Locale } from '../../../lib/dictionary';
import { fetchAnalyticsData } from '../../../lib/api';

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://politicianstracker.in';

export async function generateMetadata({
  params: { lang },
}: {
  params: { lang: Locale };
}): Promise<Metadata> {
  const isKn = lang === 'kn';

  const title = isKn
    ? 'ಕರ್ನಾಟಕ ಶಾಸಕಾಂಗ ಅಂಕಿ-ಅಂಶಗಳು ಮತ್ತು ಶಾಸಕರ ಒಟ್ಟು ಆಸ್ತಿ ಆಡಿಟ್'
    : 'Karnataka Assembly Analytics & Wealth Leaderboard | Assets & Demographics Audit';

  const description = isKn
    ? 'ಕರ್ನಾಟಕದ ಶಾಸಕರ ಒಟ್ಟು ಆಸ್ತಿ, ಸಾಲಗಳು, ಪಕ್ಷಗಳ ಸೀಟುಗಳ ಹಂಚಿಕೆ, ಮತ್ತು ವಯೋಮಾನದ ಅಂಕಿ-ಅಂಶ ವಿಶ್ಲೇಷಣೆ.'
    : 'Analytical breakdown of declared assets, liabilities, party seat shares, age demographics, and education profile of all 224 Karnataka MLAs.';

  return {
    title: `${title} | Karnataka Legislative Tracker`,
    description,
    alternates: {
      canonical: `${SITE_URL}/${lang}/analytics`,
      languages: {
        en: `${SITE_URL}/en/analytics`,
        kn: `${SITE_URL}/kn/analytics`,
      },
    },
    openGraph: {
      title: `${title} | Karnataka Legislative Tracker`,
      description,
      url: `${SITE_URL}/${lang}/analytics`,
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

export default async function AnalyticsPage({
  params: { lang },
}: {
  params: { lang: Locale };
}) {
  const dict = await getDictionary(lang);
  const data = await fetchAnalyticsData(lang);

  if (!data) {
    return (
      <div className="container" style={{ padding: '60px 0', textAlign: 'center' }}>
        <h2>Analytics Data Unavailable</h2>
        <p>Could not load analytics dataset. Please check backend server status.</p>
      </div>
    );
  }

  const { summary, top_richest, top_indebted, party_distribution, age_demographics, education_demographics } = data;
  const maxPartySeats = Math.max(...party_distribution.map((p) => p.seats), 1);
  const maxAgeCount = Math.max(...age_demographics.map((a) => a.count), 1);
  const maxEduCount = Math.max(...education_demographics.map((e) => e.count), 1);

  // Schema.org Dataset
  const jsonLdDataset = {
    '@context': 'https://schema.org',
    '@type': 'Dataset',
    name: '16th Karnataka Legislative Assembly Assets & Demographics Dataset',
    description: 'Comprehensive financial disclosures, declared net worth, criminal records, and demographics of Karnataka MLAs.',
    url: `${SITE_URL}/${lang}/analytics`,
    license: 'https://creativecommons.org/licenses/by/4.0/',
    provider: {
      '@type': 'GovernmentOrganization',
      name: 'Karnataka Legislative Tracker',
    },
  };

  return (
    <div className="container" style={{ paddingBottom: '60px' }}>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdDataset) }}
      />

      {/* Header */}
      <div className="page-header" style={{ margin: '30px 0 36px', textAlign: 'left', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '24px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '4px 12px', borderRadius: '4px', background: '#f1f5f9', border: '1px solid #cbd5e1', color: '#475569', fontSize: '0.8rem', fontWeight: 600, letterSpacing: '0.5px', textTransform: 'uppercase', marginBottom: '12px' }}>
          16th Karnataka Legislative Assembly Data Audit
        </div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 700, margin: '0 0 10px 0', color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
          {dict.analytics.title}
        </h1>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '850px', margin: 0, fontSize: '0.95rem', lineHeight: '1.6' }}>
          {dict.analytics.subtitle}
        </p>
      </div>

      {/* Hero Metric Summary Cards */}
      <div className="metrics-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '36px' }}>
        <div className="stat-card glass-panel" style={{ padding: '20px', borderRadius: '12px', background: 'var(--surface-color)', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              {dict.analytics.summaryAssets}
            </span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="1" x2="12" y2="23"></line>
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            ₹{(summary.total_assembly_assets_cr / 1000).toFixed(2)}k Cr
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: '4px' }}>
            Combined Declared Net Assets
          </div>
        </div>

        <div className="stat-card glass-panel" style={{ padding: '20px', borderRadius: '12px', background: 'var(--surface-color)', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              {dict.analytics.summaryLiabilities}
            </span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            ₹{(summary.total_assembly_liabilities_cr / 1000).toFixed(2)}k Cr
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: '4px' }}>
            Combined Declared Liabilities
          </div>
        </div>

        <div className="stat-card glass-panel" style={{ padding: '20px', borderRadius: '12px', background: 'var(--surface-color)', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              {dict.analytics.summaryAge}
            </span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
            </svg>
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            {summary.average_age} yrs
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: '4px' }}>
            Assembly Average Age
          </div>
        </div>

        <div className="stat-card glass-panel" style={{ padding: '20px', borderRadius: '12px', background: 'var(--surface-color)', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              {dict.analytics.summaryLegal}
            </span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
            {summary.total_legal_cases}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', marginTop: '4px' }}>
            Sworn Affidavits IPC Counts
          </div>
        </div>
      </div>

      {/* Main Financial Ranking Section */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 450px), 1fr))', gap: '24px', marginBottom: '36px' }}>
        
        {/* Top 10 Declared Assets */}
        <section className="glass-panel" style={{ padding: '24px', borderRadius: '14px', background: 'var(--surface-color)', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', borderBottom: '1px solid var(--border-color)', paddingBottom: '14px' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
              {dict.analytics.topRichest}
            </h2>
            <span style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: '4px', background: '#f0fdf4', color: '#166534', border: '1px solid #dcfce7', fontWeight: 600 }}>
              Declared Assets
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {top_richest.map((pol) => (
              <Link
                key={pol.id}
                href={`/${lang}/politicians/${pol.slug}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  textDecoration: 'none',
                  color: 'inherit',
                  transition: 'all 0.15s ease',
                }}
                className="leaderboard-card"
              >
                <div style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '50%',
                  background: pol.rank <= 3 ? 'var(--accent-primary)' : 'rgba(0,0,0,0.04)',
                  color: pol.rank <= 3 ? '#fff' : 'var(--text-secondary)',
                  fontWeight: 700,
                  fontSize: '0.75rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  {pol.rank}
                </div>

                <div style={{ width: '38px', height: '38px', borderRadius: '50%', overflow: 'hidden', flexShrink: 0, background: 'var(--surface-hover)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}>
                  {pol.photo_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={pol.photo_url} alt={pol.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    pol.name.charAt(0)
                  )}
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {pol.name}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', display: 'flex', gap: '6px', alignItems: 'center', marginTop: '2px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>{pol.party}</span>
                    <span>•</span>
                    <span>{pol.constituency}</span>
                  </div>
                </div>

                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{ fontWeight: 700, color: '#166534', fontSize: '0.95rem' }}>
                    ₹{pol.total_assets_cr.toLocaleString()} Cr
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>
                    Debt: ₹{pol.total_liabilities_cr} Cr
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Top 10 Declared Liabilities */}
        <section className="glass-panel" style={{ padding: '24px', borderRadius: '14px', background: 'var(--surface-color)', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', borderBottom: '1px solid var(--border-color)', paddingBottom: '14px' }}>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>
              {dict.analytics.topIndebted}
            </h2>
            <span style={{ fontSize: '0.75rem', padding: '3px 8px', borderRadius: '4px', background: '#fef2f2', color: '#991b1b', border: '1px solid #fee2e2', fontWeight: 600 }}>
              Declared Liabilities
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {top_indebted.map((pol) => (
              <Link
                key={pol.id}
                href={`/${lang}/politicians/${pol.slug}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  textDecoration: 'none',
                  color: 'inherit',
                  transition: 'all 0.15s ease',
                }}
                className="leaderboard-card"
              >
                <div style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '50%',
                  background: '#fef2f2',
                  color: '#991b1b',
                  border: '1px solid #fee2e2',
                  fontWeight: 700,
                  fontSize: '0.75rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  {pol.rank}
                </div>

                <div style={{ width: '38px', height: '38px', borderRadius: '50%', overflow: 'hidden', flexShrink: 0, background: 'var(--surface-hover)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}>
                  {pol.photo_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={pol.photo_url} alt={pol.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    pol.name.charAt(0)
                  )}
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {pol.name}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)', display: 'flex', gap: '6px', alignItems: 'center', marginTop: '2px' }}>
                    <span style={{ fontWeight: 600, color: 'var(--accent-primary)' }}>{pol.party}</span>
                    <span>•</span>
                    <span>{pol.constituency}</span>
                  </div>
                </div>

                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                  <div style={{ fontWeight: 700, color: '#991b1b', fontSize: '0.95rem' }}>
                    ₹{pol.total_liabilities_cr.toLocaleString()} Cr
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>
                    Assets: ₹{pol.total_assets_cr} Cr
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

      </div>

      {/* Assembly Seat Distribution Section */}
      <section className="glass-panel" style={{ padding: '26px', borderRadius: '14px', background: 'var(--surface-color)', border: '1px solid var(--border-color)', marginBottom: '36px' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0 0 4px 0', color: 'var(--text-primary)' }}>
          {dict.analytics.partyDistributionTitle}
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', margin: '0 0 20px 0' }}>
          {dict.analytics.partySubtitle}
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {party_distribution.map((item) => (
            <div key={item.party_code} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.88rem', fontWeight: 600 }}>
                <span>{item.party_name} ({item.party_code})</span>
                <span style={{ color: 'var(--text-secondary)' }}>{item.seats} {dict.analytics.seats} ({item.percentage}%)</span>
              </div>
              <div style={{ height: '8px', borderRadius: '4px', background: 'var(--bg-secondary)', overflow: 'hidden' }}>
                <div
                  style={{
                    height: '100%',
                    width: `${(item.seats / maxPartySeats) * 100}%`,
                    background: item.color,
                    borderRadius: '4px',
                    transition: 'width 0.6s ease',
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Demographics & Education Breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 450px), 1fr))', gap: '24px' }}>
        
        {/* Age Demographics */}
        <section className="glass-panel" style={{ padding: '24px', borderRadius: '14px', background: 'var(--surface-color)', border: '1px solid var(--border-color)' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: '0 0 18px 0', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
            {dict.analytics.demographicsTitle}
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {age_demographics.map((item) => (
              <div key={item.bracket} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600 }}>
                  <span>Age {item.bracket}</span>
                  <span style={{ color: 'var(--text-secondary)' }}>{item.count} MLAs ({item.percentage}%)</span>
                </div>
                <div style={{ height: '8px', borderRadius: '4px', background: 'var(--bg-secondary)', overflow: 'hidden' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${(item.count / maxAgeCount) * 100}%`,
                      background: 'var(--accent-primary)',
                      borderRadius: '4px',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Education Breakdown */}
        <section className="glass-panel" style={{ padding: '24px', borderRadius: '14px', background: 'var(--surface-color)', border: '1px solid var(--border-color)' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: '0 0 18px 0', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
            {dict.analytics.educationTitle}
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {education_demographics.map((item) => (
              <div key={item.level} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600 }}>
                  <span>{item.level}</span>
                  <span style={{ color: 'var(--text-secondary)' }}>{item.count} MLAs ({item.percentage}%)</span>
                </div>
                <div style={{ height: '8px', borderRadius: '4px', background: 'var(--bg-secondary)', overflow: 'hidden' }}>
                  <div
                    style={{
                      height: '100%',
                      width: `${(item.count / maxEduCount) * 100}%`,
                      background: '#06b6d4',
                      borderRadius: '4px',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
}
