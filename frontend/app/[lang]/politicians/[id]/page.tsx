import Link from 'next/link';
import type { Metadata } from 'next';
import { Landmark, Building2, Crown, Award, MapPin, Briefcase, Calendar, ChevronLeft, ShieldCheck } from 'lucide-react';
import { getDictionary, Locale } from '../../../../lib/dictionary';
import { fetchPoliticianById, fetchPopularPoliticians, fetchPoliticianIntelligence } from '../../../../lib/api';
import { notFound } from 'next/navigation';
import PoliticianAvatar from '../../../../components/PoliticianAvatar';
import ElectoralVoteShareChart from '../../../../components/ElectoralVoteShareChart';
import AreaDemographicsCard from '../../../../components/AreaDemographicsCard';
import AnalyticsPanel from '../../../../components/AnalyticsPanel';


const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://politicianstracker.in';

export async function generateStaticParams() {
  const politicians = await fetchPopularPoliticians(100);
  const params: { lang: Locale; id: string }[] = [];

  for (const pol of politicians) {
    const slugOrId = pol.slug || String(pol.id);
    params.push({ lang: 'en', id: slugOrId });
    params.push({ lang: 'kn', id: slugOrId });
  }

  return params;
}

export async function generateMetadata({
  params: { lang, id },
}: {
  params: { lang: Locale; id: string };
}): Promise<Metadata> {
  const pol = await fetchPoliticianById(id, lang);

  if (!pol) {
    return {
      title: 'Politician Not Found | Karnataka Legislative Tracker',
      description: 'The requested politician profile could not be located in the official database.',
    };
  }

  const isKn = lang === 'kn';
  const name = isKn && pol.full_name_kn ? pol.full_name_kn : pol.full_name_en;
  const partyStr = pol.party_name ? ` (${pol.party_name})` : '';
  const constStr = pol.parliamentary_constituency || pol.constituency?.name || pol.constituency_name || 'Karnataka';
  const roleStr = pol.is_union_minister
    ? (pol.union_title || 'Union Minister')
    : pol.is_minister
    ? (pol.minister_title || 'Cabinet Minister')
    : pol.representative_type?.startsWith('mp')
    ? 'Lok Sabha MP'
    : 'MLA';

  const assets = pol.financial_declarations?.[0];
  const worthStr = assets ? ` | Net Worth: ₹${(Number(assets.total_assets) / 10000000).toFixed(1)} Cr` : '';

  const title = isKn
    ? `${name}${partyStr} - ${constStr} ${roleStr} ಆಸ್ತಿ ಮತ್ತು ವಿವರಗಳು`
    : `${name}${partyStr} - ${constStr} ${roleStr}${worthStr} | Affidavits & Net Worth`;

  const description = isKn
    ? `${name} (${constStr} ಕ್ಷೇತ್ರ). ಒಟ್ಟು ಆಸ್ತಿ: ₹${assets ? (Number(assets.total_assets) / 10000000).toFixed(1) : 0} ಕೋಟಿ. ಸ್ವೀಕೃತ ಶಪಥಪತ್ರಗಳು, ಕ್ರಿಮಿನಲ್ ಪ್ರಕರಣಗಳು, ಮತ್ತು ಸಚಿವರ ಮಾಹಿತಿ.`
    : `Verified public profile of ${name}, ${roleStr} representing ${constStr}${partyStr}. Declared assets: ₹${assets ? (Number(assets.total_assets) / 10000000).toFixed(1) : 0} Cr, liabilities, criminal records, and executive career timeline.`;

  return {
    title,
    description,
    keywords: [
      name,
      `${name} net worth`,
      `${name} assets`,
      `${name} constituency`,
      `${name} party`,
      `${name} affidavit`,
      `${constStr} MLA`,
      `Karnataka ${roleStr}`,
    ],
    alternates: {
      canonical: `${SITE_URL}/${lang}/politicians/${id}`,
      languages: {
        en: `${SITE_URL}/en/politicians/${id}`,
        kn: `${SITE_URL}/kn/politicians/${id}`,
      },
    },
    openGraph: {
      title,
      description,
      url: `${SITE_URL}/${lang}/politicians/${id}`,
      siteName: 'Karnataka Legislative Tracker',
      type: 'profile',
      images: [
        {
          url: pol.photo_url || `${SITE_URL}/og-image.jpg`,
          width: 800,
          height: 800,
          alt: name,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [pol.photo_url || `${SITE_URL}/og-image.jpg`],
    },
  };
}

export const revalidate = 300; // ISR 5 minutes

export default async function PoliticianProfile({
  params: { lang, id },
}: {
  params: { lang: Locale; id: string };
}) {
  const dict = await getDictionary(lang);
  const pol = await fetchPoliticianById(id, lang);
  const intelligence = await fetchPoliticianIntelligence(id, lang);

  if (!pol) {
    notFound();
  }

  const name = lang === 'kn' && pol.full_name_kn ? pol.full_name_kn : pol.full_name_en;
  const bio = pol.biography;
  const assets = pol.financial_declarations?.[0];

  // Schema.org Person & GovernmentService Data for Google Search Knowledge Card Snippets
  const sameAsLinks = [
    pol.social_media?.facebook,
    pol.social_media?.twitter,
    pol.social_media?.instagram,
    pol.social_media?.youtube,
    pol.social_media?.linkedin,
    pol.social_media?.website,
  ].filter(Boolean);

  const jsonLdPerson: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name: pol.full_name_en,
    alternateName: pol.full_name_kn || undefined,
    description: pol.biography ? pol.biography.substring(0, 300) : `${pol.full_name_en} is an elected public representative in Karnataka, India.`,
    image: pol.photo_url || undefined,
    birthDate: pol.date_of_birth || undefined,
    gender: pol.gender || undefined,
    nationality: { '@type': 'Country', name: 'India' },
    jobTitle: pol.is_union_minister
      ? pol.union_title || 'Union Minister'
      : pol.is_minister
      ? pol.minister_title || 'Cabinet Minister'
      : pol.representative_type?.startsWith('mp')
      ? 'Member of Parliament'
      : 'Member of Legislative Assembly',
    worksFor: {
      '@type': 'GovernmentOrganization',
      name: pol.representative_type?.startsWith('mp') ? 'Parliament of India' : 'Karnataka Legislative Assembly',
    },
    memberOf: pol.party_name ? { '@type': 'PoliticalParty', name: pol.party_name } : undefined,
    address: pol.constituency_name
      ? { '@type': 'PostalAddress', addressLocality: pol.constituency_name, addressRegion: 'Karnataka', addressCountry: 'IN' }
      : undefined,
    knowsAbout: [
      'Karnataka Politics',
      'Indian Legislature',
      pol.constituency_name ? `${pol.constituency_name} Constituency` : null,
      pol.portfolio ? pol.portfolio : null,
    ].filter(Boolean),
    sameAs: sameAsLinks.length > 0 ? sameAsLinks : undefined,
    url: `${SITE_URL}/${lang}/politicians/${id}`,
  };

  const jsonLdBreadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: 'Home',
        item: `${SITE_URL}/${lang}`,
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: 'Directory',
        item: `${SITE_URL}/${lang}/politicians`,
      },
      {
        '@type': 'ListItem',
        position: 3,
        name: name,
        item: `${SITE_URL}/${lang}/politicians/${id}`,
      },
    ],
  };

  return (
    <div>
      {/* Schema.org Structured Data Injection */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdPerson) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdBreadcrumb) }}
      />

      {/* Header */}
      <div className="profile-header">
        <div className="container">
          <Link href={`/${lang}/politicians`} style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '4px', marginBottom: '16px', fontWeight: 500 }}>
            <ChevronLeft size={14} /> Back to Representatives Directory
          </Link>
          <div className="profile-info">
            <PoliticianAvatar photoUrl={pol.photo_url} name={name} size={90} />
            <div className="profile-details">
              <h1 style={{ fontSize: '1.8rem', fontWeight: 700, letterSpacing: '-0.02em' }}>{name}</h1>
              <div className="profile-meta" style={{ marginTop: '8px', gap: '8px' }}>
                {pol.is_union_minister && (
                  <span className="badge" style={{ background: '#f8fafc', color: '#475569', border: '1px solid #cbd5e1', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <Crown size={13} /> {pol.union_title || 'Union Cabinet Minister'}
                  </span>
                )}
                {pol.is_minister && !pol.is_union_minister && (
                  <span className="badge" style={{ background: '#f8fafc', color: '#334155', border: '1px solid #cbd5e1', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <Award size={13} /> {pol.minister_title || 'State Cabinet Minister'}
                  </span>
                )}
                {pol.representative_type?.startsWith('mp') ? (
                  <span className="badge" style={{ background: '#f8fafc', color: '#1e3a8a', border: '1px solid #cbd5e1', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <Landmark size={13} /> {pol.representative_type === 'mp_rs' ? 'Rajya Sabha MP' : 'Lok Sabha MP'}
                  </span>
                ) : (
                  <span className="badge" style={{ background: '#f8fafc', color: '#475569', border: '1px solid #e2e8f0', fontWeight: 500, display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <Building2 size={13} /> Assembly MLA
                  </span>
                )}
                {pol.party_name && <span className="badge badge-party">{pol.party_name}</span>}
                {pol.parliamentary_constituency ? (
                  <span className="badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                    <MapPin size={13} /> {pol.parliamentary_constituency}
                  </span>
                ) : (
                  pol.constituency?.name && (
                    <span className="badge" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                      <MapPin size={13} /> {pol.constituency.name}
                    </span>
                  )
                )}
                {pol.district_name && <span className="badge">{pol.district_name}</span>}
              </div>
            </div>
          </div>

          <div className="stat-grid">
            <div className="stat-box glass-panel">
              <div className="stat-value" style={{ color: 'var(--text-primary)' }}>{pol.terms_as_mla || 0}</div>
              <div className="stat-label">Times MLA</div>
            </div>
            <div className="stat-box glass-panel">
              <div className="stat-value" style={{ color: 'var(--text-primary)' }}>{pol.terms_as_mp || 0}</div>
              <div className="stat-label">Times MP</div>
            </div>
            <div className="stat-box glass-panel">
              <div className="stat-value">{pol.age || 'N/A'}</div>
              <div className="stat-label">{dict.politician.age}</div>
            </div>
            <div className="stat-box glass-panel">
              <div className="stat-value">
                {assets ? `₹${(Number(assets.total_assets) / 10000000).toFixed(1)} Cr` : 'N/A'}
              </div>
              <div className="stat-label">{dict.politician.netWorth}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container">
        <div className="profile-content">
          <div className="main-column">
            {/* Biography */}
            <section className="dashboard-section glass-panel">
              <h2>Biography</h2>
              {bio ? (
                <div className="bio-content"><p>{bio}</p></div>
              ) : (
                <p className="empty-state">No biography available yet.</p>
              )}
            </section>

            {/* Visual Electoral & Executive Career Timeline */}
            <section className="dashboard-section glass-panel">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ background: '#f1f5f9', color: '#475569', padding: '8px', borderRadius: '10px' }}>
                    <Briefcase size={20} />
                  </div>
                  <div>
                    <h2 style={{ margin: 0, fontSize: '1.25rem' }}>Electoral & Political Career Timeline</h2>
                    <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                      Track record across Assembly, Parliament, and Cabinet offices ({pol.terms_as_mla || 0} MLA terms • {pol.terms_as_mp || 0} MP terms)
                    </p>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <span style={{ background: '#f0fdf4', color: '#166534', border: '1px solid #dcfce7', fontSize: '0.72rem', fontWeight: 600, padding: '3px 8px', borderRadius: '12px' }}>
                    ● Active Tenure
                  </span>
                </div>
              </div>

              {pol.career_timeline && pol.career_timeline.length > 0 ? (
                <div style={{ position: 'relative', paddingLeft: '24px', borderLeft: '2px dashed #cbd5e1', marginLeft: '8px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  {pol.career_timeline.map((item, idx) => (
                    <div key={idx} style={{ position: 'relative' }}>
                      {/* Timeline Dot Node */}
                      <div
                        style={{
                          position: 'absolute',
                          left: '-31px',
                          top: '4px',
                          width: '14px',
                          height: '14px',
                          borderRadius: '50%',
                          background: item.is_current ? '#10b981' : '#6366f1',
                          border: '3px solid #ffffff',
                          boxShadow: item.is_current ? '0 0 0 4px rgba(16, 185, 129, 0.25)' : '0 0 0 3px rgba(99, 102, 241, 0.15)',
                        }}
                      />

                      {/* Card Content */}
                      <div
                        style={{
                          background: item.is_current ? '#f8fafc' : '#ffffff',
                          border: item.is_current ? '1.5px solid #10b981' : '1px solid #e2e8f0',
                          borderRadius: '12px',
                          padding: '16px',
                          boxShadow: 'var(--shadow-sm)',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px', marginBottom: '6px' }}>
                          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: item.is_current ? '#047857' : '#4f46e5', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                            <Calendar size={13} /> {item.year}
                          </span>
                          <span
                            style={{
                              background: item.is_current ? '#ecfdf5' : '#f1f5f9',
                              color: item.is_current ? '#065f46' : '#475569',
                              border: '1px solid ' + (item.is_current ? '#a7f3d0' : '#e2e8f0'),
                              fontSize: '0.72rem',
                              fontWeight: 600,
                              padding: '2px 8px',
                              borderRadius: '12px',
                            }}
                          >
                            {item.badge}
                          </span>
                        </div>

                        <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 6px 0' }}>
                          {item.role_title}
                        </h3>

                        {item.portfolio && (
                          <p style={{ fontSize: '0.85rem', color: '#475569', margin: '0 0 8px 0', lineHeight: '1.4' }}>
                            <strong>Portfolio:</strong> {item.portfolio}
                          </p>
                        )}

                        <div style={{ display: 'flex', gap: '12px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                          {item.constituency && (
                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                              <MapPin size={12} /> {item.constituency}
                            </span>
                          )}
                          {item.party && (
                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
                              <ShieldCheck size={12} /> {item.party}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ padding: '16px', background: '#f8fafc', borderRadius: '10px', fontSize: '0.88rem', color: '#64748b' }}>
                  Single term parliamentary/assembly tenure recorded for {name}.
                </div>
              )}
            </section>

            {/* Union Cabinet Portfolio Card */}
            {pol.is_union_minister && (
              <section className="dashboard-section glass-panel" style={{ borderLeft: '4px solid var(--text-muted)', background: 'var(--bg-hover)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Crown size={20} color="var(--text-secondary)" />
                  <h2 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--text-primary)' }}>Union Cabinet & Central Ministries</h2>
                </div>
                <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  {pol.union_title || 'Union Cabinet Minister'}
                </div>
                {pol.union_portfolio && (
                  <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.5', margin: 0 }}>
                    <strong>Central Ministries Handled:</strong> {pol.union_portfolio}
                  </p>
                )}
              </section>
            )}

            {/* State Cabinet Portfolio Card */}
            {pol.is_minister && !pol.is_union_minister && (
              <section className="dashboard-section glass-panel" style={{ borderLeft: '4px solid var(--text-muted)', background: 'var(--bg-hover)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Award size={20} color="var(--text-secondary)" />
                  <h2 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--text-primary)' }}>State Executive Office & Portfolio</h2>
                </div>
                <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px' }}>
                  {pol.minister_title || 'Cabinet Minister of Karnataka'}
                </div>
                {pol.portfolio && (
                  <p style={{ color: '#475569', fontSize: '0.95rem', lineHeight: '1.5', margin: 0 }}>
                    <strong>Departments Handled:</strong> {pol.portfolio}
                  </p>
                )}
              </section>
            )}

            {/* Official ECI Candidate Vote Share Visual Analytics */}
            {pol.electoral_performance && (
              <ElectoralVoteShareChart data={pol.electoral_performance} candidateName={name} lang={lang} />
            )}

            {/* Financials with Visual Asset Progress Bars */}
            {pol.financial_declarations && pol.financial_declarations.length > 0 && (
              <section className="dashboard-section glass-panel">
                <h2>{lang === 'kn' ? 'ಆಸ್ತಿ ಮತ್ತು ಸಾಲದ ಪ್ರಮಾಣಪತ್ರ' : 'Financial Declarations'}</h2>
                {pol.financial_declarations.map((decl) => {
                  const assetsNum = Number(decl.total_assets) || 0;
                  const liabNum = Number(decl.total_liabilities) || 0;
                  const maxVal = Math.max(assetsNum, liabNum, 1);
                  const assetWidth = Math.min(100, (assetsNum / maxVal) * 100);
                  const liabWidth = Math.min(100, (liabNum / maxVal) * 100);

                  return (
                    <div key={decl.id} className="financial-card" style={{ marginBottom: '16px' }}>
                      <div className="fin-year">{decl.declaration_year} {lang === 'kn' ? 'ಚುನಾವಣಾ ಅಫಿಡವಿಟ್' : 'Election Affidavit'}</div>
                      
                      {/* Assets Visual Bar */}
                      <div style={{ marginTop: '8px', marginBottom: '8px' }}>
                        <div className="fin-row" style={{ marginBottom: '4px' }}>
                          <span>{lang === 'kn' ? 'ಒಟ್ಟು ಆಸ್ತಿ' : 'Total Assets'}</span>
                          <span className="text-green" style={{ fontWeight: 700 }}>₹{(assetsNum / 10000000).toFixed(2)} {lang === 'kn' ? 'ಕೋಟಿ' : 'Cr'}</span>
                        </div>
                        <div style={{ height: '6px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${assetWidth}%`, height: '100%', background: '#10b981', borderRadius: '3px' }} />
                        </div>
                      </div>

                      {/* Liabilities Visual Bar */}
                      <div style={{ marginBottom: '8px' }}>
                        <div className="fin-row" style={{ marginBottom: '4px' }}>
                          <span>{lang === 'kn' ? 'ಒಟ್ಟು ಸಾಲಗಳು' : 'Total Liabilities'}</span>
                          <span className="text-red" style={{ fontWeight: 700 }}>₹{(liabNum / 10000000).toFixed(2)} {lang === 'kn' ? 'ಕೋಟಿ' : 'Cr'}</span>
                        </div>
                        <div style={{ height: '6px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${liabWidth}%`, height: '100%', background: '#ef4444', borderRadius: '3px' }} />
                        </div>
                      </div>

                      {decl.declaration_url && (
                        <a href={decl.declaration_url} target="_blank" rel="noopener noreferrer" className="source-link" style={{ display: 'block', marginTop: '8px', fontSize: '0.8rem' }}>
                          {lang === 'kn' ? 'MyNeta ಯಲ್ಲಿ ಪ್ರಮಾಣಪತ್ರ ವೀಕ್ಷಿಸಿ →' : 'View Affidavit on MyNeta →'}
                        </a>
                      )}
                    </div>
                  );
                })}
              </section>
            )}

            {/* Legal Records */}
            {pol.legal_records && pol.legal_records.length > 0 && (
              <section className="dashboard-section glass-panel">
                <h2>Declared Legal Cases ({pol.legal_records.length})</h2>
                <p style={{ fontSize: '0.8rem', fontStyle: 'italic', color: '#64748b', marginBottom: '16px', padding: '12px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '6px' }}>
                  Declared legal cases are based on election affidavit disclosures and do not by themselves establish guilt or conviction.
                </p>
                <div className="legal-list">
                  {pol.legal_records.map((record) => (
                    <div key={record.id} className="legal-card">
                      <div className="legal-header">
                        <span className="legal-status">{record.case_status_display}</span>
                        <span className="legal-year">{record.fir_date ? record.fir_date.substring(0, 4) : ''}</span>
                      </div>
                      <p className="legal-desc">{lang === 'kn' ? record.description_kn : record.description_en}</p>
                      {record.ipc_sections && record.ipc_sections.length > 0 && (
                        <div className="ipc-tags">
                          {record.ipc_sections.map((ipc, i) => (
                            <span key={i} className="ipc-tag">{ipc}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Analytics Suite */}
            {intelligence && (
              <>
                <AnalyticsPanel
                  data={intelligence}
                  financials={pol.financial_declarations}
                  career={pol.career_timeline}
                />

              </>
            )}

            {/* Official Census Area & Religion Demographics Profile */}
            {pol.area_demographics && (
              <AreaDemographicsCard data={pol.area_demographics} lang={lang} />
            )}

            {/* News */}
            {pol.public_records && pol.public_records.length > 0 && (
              <section className="dashboard-section glass-panel">
                <h2>News & Public Records</h2>
                <div className="records-list">
                  {pol.public_records.map((record) => (
                    <div key={record.id} className="record-card">
                      <div className="record-header">
                        <span className="record-type">{record.record_type_display}</span>
                        <span className="record-date">{record.event_date || ''}</span>
                      </div>
                      <h3>{lang === 'kn' ? record.title_kn : record.title_en}</h3>
                      <p>{lang === 'kn' ? record.summary_kn : record.summary_en}</p>
                      {record.source_url && (
                        <a href={record.source_url} target="_blank" rel="noopener noreferrer" className="source-link">
                          Source →
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>

          <div className="sidebar-column">
            {/* Social */}
            {pol.social_media && Object.values(pol.social_media).some(v => v) && (
              <section className="dashboard-section glass-panel">
                <h2>Links</h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {pol.social_media.twitter && <a href={pol.social_media.twitter} target="_blank" rel="noopener noreferrer" className="source-link">Twitter →</a>}
                  {pol.social_media.facebook && <a href={pol.social_media.facebook} target="_blank" rel="noopener noreferrer" className="source-link">Facebook →</a>}
                  {pol.social_media.website && <a href={pol.social_media.website} target="_blank" rel="noopener noreferrer" className="source-link">Website →</a>}
                </div>
              </section>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}