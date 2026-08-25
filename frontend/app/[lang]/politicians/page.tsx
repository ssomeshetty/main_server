import Link from 'next/link';
import type { Metadata } from 'next';
import { Search, Filter, X, Landmark, Building2, Crown, Award, MapPin, UserCheck, ChevronLeft, CheckCircle2 } from 'lucide-react';
import { getDictionary, Locale } from '../../../lib/dictionary';
import { fetchDistricts, fetchParties, PoliticianSummary } from '../../../lib/api';
import PoliticianAvatar from '../../../components/PoliticianAvatar';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://politicianstracker.in';

export async function generateMetadata({
  params: { lang },
  searchParams,
}: {
  params: { lang: Locale };
  searchParams: { search?: string; party?: string; district?: string; minister?: string; type?: string };
}): Promise<Metadata> {
  const isKn = lang === 'kn';

  let filterTitle = isKn ? 'ಕರ್ನಾಟಕ ಜನಪ್ರತಿನಿಧಿಗಳ ಡೈರೆಕ್ಟರಿ' : 'Karnataka Legislative Representatives Directory';
  if (searchParams.search) {
    filterTitle = isKn ? `"${searchParams.search}" - ಕರ್ನಾಟಕ ಜನಪ್ರತಿನಿಧಿಗಳು` : `Search Results for "${searchParams.search}" - Karnataka Representatives`;
  } else if (searchParams.type === 'mp_ls') {
    filterTitle = isKn ? 'ಕರ್ನಾಟಕದ 28 ಲೋಕಸಭಾ ಸಂಸದರು (2024)' : 'Karnataka 28 Lok Sabha Members of Parliament (2024–29)';
  } else if (searchParams.type === 'mp_rs') {
    filterTitle = isKn ? 'ಕರ್ನಾಟಕದ ರಾಜ್ಯಸಭಾ ಸಂಸದರು' : 'Karnataka Rajya Sabha Members of Parliament';
  } else if (searchParams.type === 'union_minister') {
    filterTitle = isKn ? 'ಕರ್ನಾಟಕದ ಕೇಂದ್ರ ಸಂಪುಟ ಸಚಿವರು' : 'Union Cabinet Ministers Representing Karnataka';
  } else if (searchParams.minister === 'true') {
    filterTitle = isKn ? 'ಕರ್ನಾಟಕ ರಾಜ್ಯ ಸಂಪುಟ ಸಚಿವರು' : 'Karnataka State Cabinet Ministers';
  } else if (searchParams.type === 'mla') {
    filterTitle = isKn ? 'ಕರ್ನಾಟಕದ 224 ವಿಧಾನಸಭಾ ಶಾಸಕರು' : 'Karnataka 224 Members of Legislative Assembly (MLAs)';
  }

  const description = isKn
    ? `ಕರ್ನಾಟಕ ಶಾಸಕರು ಮತ್ತು ಸಂಸದರ ಸಂಪೂರ್ಣ ಪಟ್ಟಿ. ${filterTitle}. ಆಸ್ತಿ ಘೋಷಣೆಗಳು, ಕ್ಷೇತ್ರಗಳು ಮತ್ತು ಸಚಿವರ ವಿವರಣೆ.`
    : `Explore ${filterTitle}. Full directory of 224 Karnataka State Assembly MLAs & 28 Lok Sabha MPs. Verified affidavits, assets, legal records & constituencies.`;

  return {
    title: `${filterTitle} | Karnataka Legislative Tracker`,
    description,
    alternates: {
      canonical: `${SITE_URL}/${lang}/politicians`,
      languages: {
        en: `${SITE_URL}/en/politicians`,
        kn: `${SITE_URL}/kn/politicians`,
      },
    },
    openGraph: {
      title: `${filterTitle} | Karnataka Legislative Tracker`,
      description,
      url: `${SITE_URL}/${lang}/politicians`,
      siteName: 'Karnataka Legislative Tracker',
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title: filterTitle,
      description,
    },
  };
}

export const revalidate = 300; // ISR 5 minutes

async function fetchAllPoliticians(
  lang: Locale,
  filters: { search?: string; party?: string; district?: string; minister?: string; type?: string; sort?: string }
): Promise<PoliticianSummary[]> {
  const all: PoliticianSummary[] = [];
  let url = `${API_BASE_URL}/politicians/?lang=${lang}&page_size=250`;

  if (filters.search) url += `&search=${encodeURIComponent(filters.search)}`;
  if (filters.party) url += `&party=${encodeURIComponent(filters.party)}`;
  if (filters.district) url += `&district=${encodeURIComponent(filters.district)}`;
  if (filters.minister === 'true') url += `&is_minister=true`;
  if (filters.type) url += `&type=${encodeURIComponent(filters.type)}`;

  try {
    while (url) {
      const res = await fetch(url, {
        headers: { 'Accept-Language': lang },
        cache: 'no-store',
      });
      if (!res.ok) {
        console.error(`API response not OK (${res.status}) when fetching ${url}`);
        break;
      }
      const data = await res.json();
      all.push(...(data.results || []));
      url = data.next || '';
    }
  } catch (e) {
    console.error('Failed to fetch politicians:', e);
  }

  // Sort alphabetically
  const sortMode = filters.sort || 'a-z';
  const locale = lang === 'kn' ? 'kn' : 'en';

  all.sort((a, b) => {
    if (sortMode === 'z-a') {
      return b.name.localeCompare(a.name, locale, { sensitivity: 'base' });
    }
    if (sortMode === 'party') {
      const partyA = a.party_name || '';
      const partyB = b.party_name || '';
      return partyA.localeCompare(partyB, locale) || a.name.localeCompare(b.name, locale);
    }
    // Default: A to Z
    return a.name.localeCompare(b.name, locale, { sensitivity: 'base' });
  });

  return all;
}

export default async function PoliticiansDirectory({
  params: { lang },
  searchParams,
}: {
  params: { lang: Locale };
  searchParams: { search?: string; party?: string; district?: string; minister?: string; type?: string; sort?: string };
}) {
  const dict = await getDictionary(lang);

  const [politicians, parties, districts] = await Promise.all([
    fetchAllPoliticians(lang, searchParams),
    fetchParties(lang),
    fetchDistricts(lang),
  ]);

  const activeParty = parties.find((p) => p.id.toString() === searchParams.party);
  const activeDistrict = districts.find((d) => d.id.toString() === searchParams.district);
  const isMpLsOnly = searchParams.type === 'mp_ls';
  const isMpRsOnly = searchParams.type === 'mp_rs';
  const isMpOnly = searchParams.type === 'mp';
  const isUnionMinisterOnly = searchParams.type === 'union_minister';
  const isStateMinisterOnly = searchParams.minister === 'true';
  const isMlaOnly = searchParams.type === 'mla';

  const titleText = isMpLsOnly
    ? 'Karnataka Lok Sabha Members of Parliament (28 MPs)'
    : isMpRsOnly
    ? 'Karnataka Rajya Sabha Members of Parliament'
    : isMpOnly
    ? 'Karnataka Members of Parliament (Lok Sabha & Rajya Sabha)'
    : isUnionMinisterOnly
    ? 'Union Cabinet Ministers Representing Karnataka'
    : isStateMinisterOnly
    ? 'Karnataka State Cabinet Ministers'
    : isMlaOnly
    ? 'Karnataka Members of Legislative Assembly (MLAs)'
    : 'Karnataka Legislative Representatives Directory';

  const hasActiveFilters = Boolean(searchParams.search || searchParams.party || searchParams.district || searchParams.minister || searchParams.type);

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
        name: 'Representatives Directory',
        item: `${SITE_URL}/${lang}/politicians`,
      },
    ],
  };

  return (
    <div className="container" style={{ padding: '32px 20px 60px' }}>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLdBreadcrumb) }}
      />

      {/* Directory Title Header */}
      <div style={{ marginBottom: '28px' }}>
        <Link href={`/${lang}`} style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '4px', marginBottom: '16px', fontWeight: 600 }}>
          <ChevronLeft size={14} /> Back to Dashboard
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap', marginBottom: '8px' }}>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em', margin: 0 }}>
            {titleText}
          </h1>
          <span className="logo-badge" style={{ padding: '4px 8px' }}>
            PUBLIC REPOSITORY
          </span>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Showing <strong>{politicians.length}</strong> active representatives
          {searchParams.search && ` matching "${searchParams.search}"`}
          {activeParty && ` affiliated with ${activeParty.short_name || activeParty.name}`}
          {activeDistrict && ` representing ${activeDistrict.name} District`}
        </p>
      </div>

      {/* Directory Category Pills */}
      <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '12px', marginBottom: '20px' }}>
        <Link
          href={`/${lang}/politicians`}
          style={{
            padding: '7px 14px',
            borderRadius: '4px',
            fontSize: '0.85rem',
            fontWeight: !searchParams.type && !searchParams.minister ? 700 : 500,
            background: !searchParams.type && !searchParams.minister ? '#0f172a' : '#ffffff',
            color: !searchParams.type && !searchParams.minister ? '#ffffff' : 'var(--text-secondary)',
            border: '1px solid ' + (!searchParams.type && !searchParams.minister ? '#0f172a' : 'var(--border-subtle)'),
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap',
            textDecoration: 'none',
          }}
        >
          <UserCheck size={14} /> All Representatives
        </Link>

        <Link
          href={`/${lang}/politicians?type=mla`}
          style={{
            padding: '7px 14px',
            borderRadius: '4px',
            fontSize: '0.85rem',
            fontWeight: searchParams.type === 'mla' ? 700 : 500,
            background: searchParams.type === 'mla' ? '#0f172a' : '#ffffff',
            color: searchParams.type === 'mla' ? '#ffffff' : 'var(--text-secondary)',
            border: '1px solid ' + (searchParams.type === 'mla' ? '#0f172a' : 'var(--border-subtle)'),
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap',
            textDecoration: 'none',
          }}
        >
          <Building2 size={14} /> State MLAs (Assembly)
        </Link>

        <Link
          href={`/${lang}/politicians?type=mp_ls`}
          style={{
            padding: '7px 14px',
            borderRadius: '4px',
            fontSize: '0.85rem',
            fontWeight: searchParams.type === 'mp_ls' ? 700 : 500,
            background: searchParams.type === 'mp_ls' ? '#1e3a8a' : '#ffffff',
            color: searchParams.type === 'mp_ls' ? '#ffffff' : 'var(--text-secondary)',
            border: '1px solid ' + (searchParams.type === 'mp_ls' ? '#1e3a8a' : 'var(--border-subtle)'),
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap',
            textDecoration: 'none',
          }}
        >
          <Landmark size={14} /> Lok Sabha MPs (28)
        </Link>

        <Link
          href={`/${lang}/politicians?type=union_minister`}
          style={{
            padding: '7px 14px',
            borderRadius: '4px',
            fontSize: '0.85rem',
            fontWeight: searchParams.type === 'union_minister' ? 700 : 500,
            background: searchParams.type === 'union_minister' ? '#475569' : '#ffffff',
            color: searchParams.type === 'union_minister' ? '#ffffff' : 'var(--text-secondary)',
            border: '1px solid ' + (searchParams.type === 'union_minister' ? '#475569' : 'var(--border-subtle)'),
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap',
            textDecoration: 'none',
          }}
        >
          <Crown size={14} /> Union Ministers
        </Link>

        <Link
          href={`/${lang}/politicians?minister=true`}
          style={{
            padding: '7px 14px',
            borderRadius: '4px',
            fontSize: '0.85rem',
            fontWeight: searchParams.minister === 'true' ? 700 : 500,
            background: searchParams.minister === 'true' ? '#334155' : '#ffffff',
            color: searchParams.minister === 'true' ? '#ffffff' : 'var(--text-secondary)',
            border: '1px solid ' + (searchParams.minister === 'true' ? '#334155' : 'var(--border-subtle)'),
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            whiteSpace: 'nowrap',
            textDecoration: 'none',
          }}
        >
          <Award size={14} /> State Ministers
        </Link>
      </div>

      {/* Clean Filter Controls */}
      <form method="GET" action={`/${lang}/politicians`} className="filter-bar" style={{ marginBottom: '32px' }}>
        <div className="search-container" style={{ margin: '0', flex: '1 1 240px', maxWidth: '100%' }}>
          <Search className="search-icon" size={16} />
          <input
            type="text"
            name="search"
            className="search-input"
            placeholder="Search representative by name..."
            defaultValue={searchParams.search || ''}
          />
        </div>

        {searchParams.type && <input type="hidden" name="type" value={searchParams.type} />}
        {searchParams.minister && <input type="hidden" name="minister" value={searchParams.minister} />}

        <select
          name="party"
          className="filter-select"
          defaultValue={searchParams.party || ''}
          style={{ flex: '1 1 180px' }}
        >
          <option value="">All Political Parties</option>
          {parties.map((party) => (
            <option key={party.id} value={party.id}>
              {party.short_name || party.name}
            </option>
          ))}
        </select>

        <select
          name="district"
          className="filter-select"
          defaultValue={searchParams.district || ''}
          style={{ flex: '1 1 160px' }}
        >
          <option value="">All Districts</option>
          {districts.map((district) => (
            <option key={district.id} value={district.id}>
              {district.name}
            </option>
          ))}
        </select>

        <select
          name="sort"
          className="filter-select"
          defaultValue={searchParams.sort || 'a-z'}
          style={{ flex: '1 1 150px' }}
        >
          <option value="a-z">Sort: Name (A - Z)</option>
          <option value="z-a">Sort: Name (Z - A)</option>
          <option value="party">Sort: Political Party</option>
        </select>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <button type="submit" className="btn btn-primary" style={{ padding: '9px 18px' }}>
            <Filter size={14} /> Search
          </button>
          {hasActiveFilters && (
            <Link href={`/${lang}/politicians`} className="btn btn-secondary" title="Clear all filters">
              <X size={14} /> Clear
            </Link>
          )}
        </div>
      </form>

      {/* Candidate Grid */}
      <div className="grid">
        {politicians.map((pol) => (
          <Link href={`/${lang}/politicians/${pol.slug || pol.id}`} key={pol.id} className="card" style={{ display: 'flex', flexDirection: 'column', textDecoration: 'none' }}>
            <div className="card-header">
              <PoliticianAvatar photoUrl={pol.photo_url} name={pol.name} size={52} />
              <div style={{ flex: 1 }}>
                <h3 className="card-title" style={{ fontSize: '1rem', color: '#0f172a', fontWeight: 700 }}>
                  {pol.name}
                </h3>
                <div className="card-subtitle" style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  <MapPin size={12} />
                  {pol.representative_type?.startsWith('mp')
                    ? `MP - ${pol.parliamentary_constituency || pol.constituency_name || 'Karnataka'}`
                    : (pol.constituency_name || '—')}
                </div>
              </div>
            </div>

            {/* Union Minister Badge */}
            {pol.is_union_minister && (
              <div style={{ marginTop: '10px', marginBottom: '8px', padding: '6px 8px', borderRadius: '4px', background: '#f8fafc', border: '1px solid #e2e8f0' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Crown size={12} /> {pol.union_title || 'Union Minister'}
                </div>
              </div>
            )}

            {/* State Minister Badge */}
            {pol.is_minister && !pol.is_union_minister && (
              <div style={{ marginTop: '10px', marginBottom: '8px', padding: '6px 8px', borderRadius: '4px', background: '#f8fafc', border: '1px solid #e2e8f0' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#334155', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Award size={12} /> {pol.minister_title || 'State Cabinet Minister'}
                </div>
              </div>
            )}

            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: 'auto', paddingTop: '10px' }}>
              {pol.representative_type?.startsWith('mp') ? (
                <span className="badge badge-party">
                  Lok Sabha MP
                </span>
              ) : (
                <span className="badge">
                  Assembly MLA
                </span>
              )}
              {pol.party_name && <span className="badge">{pol.party_name}</span>}
              {pol.is_verified && (
                <span className="badge" style={{ background: '#f0fdf4', color: '#166534', border: '1px solid #dcfce7', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                  <CheckCircle2 size={11} /> Verified
                </span>
              )}
            </div>
          </Link>
        ))}
        {politicians.length === 0 && (
          <div style={{ padding: '48px 20px', textAlign: 'center', color: 'var(--text-secondary)', gridColumn: '1/-1', background: '#ffffff', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontWeight: 700, fontSize: '1.1rem', color: '#0f172a', marginBottom: '4px' }}>No representatives found</div>
            <p style={{ fontSize: '0.9rem' }}>Try adjusting your search query or clearing active filters.</p>
          </div>
        )}
      </div>
    </div>
  );
}
