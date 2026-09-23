import React from 'react';
import Link from 'next/link';
import { Metadata } from 'next';
import { ShieldCheck, Landmark, Briefcase, Award, ArrowRight, UserCheck, CheckCircle2 } from 'lucide-react';
import { fetchPoliticians, PoliticianSummary } from '../../../lib/api';
import { Locale } from '../../../lib/dictionary';
import CabinetFilterGrid from './CabinetFilterGrid';

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://politicianstracker.in';

export const revalidate = 300; // ISR 5 minutes — cabinet data changes rarely

export async function generateMetadata({ params }: { params: { lang: Locale } }): Promise<Metadata> {
  const isKn = params.lang === 'kn';
  const title = isKn
    ? 'ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಸಚಿವ ಸಂಪುಟ ಮತ್ತು ಸಚಿವಾಲಯಗಳು | Karnataka Cabinet Ministers & Portfolios'
    : 'Karnataka Cabinet Ministers & Portfolios | Executive Ministry Directory | Legislative Tracker';
  const description = isKn
    ? 'ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಮುಖ್ಯಮಂತ್ರಿಗಳು, ಉಪ ಮುಖ್ಯಮಂತ್ರಿಗಳು ಮತ್ತು ಸಚಿವರ ಅಧಿಕೃತ ಸಚಿವಾಲಯಗಳು, ಆಸ್ತಿ ವಿವರಗಳು ಮತ್ತು ಜವಾಬ್ದಾರಿಗಳು.'
    : 'Public directory of Karnataka Cabinet Ministers, portfolio allocations, executive responsibilities, and public accountability metrics sourced from cited records.';

  return {
    title,
    description,
    alternates: {
      canonical: `${SITE_URL}/${params.lang}/cabinet`,
      languages: {
        en: `${SITE_URL}/en/cabinet`,
        kn: `${SITE_URL}/kn/cabinet`,
      },
    },
    openGraph: {
      title,
      description,
      url: `${SITE_URL}/${params.lang}/cabinet`,
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

export default async function CabinetPage({ params }: { params: { lang: Locale } }) {
  const lang = params.lang || 'en';
  const isKn = lang === 'kn';

  // Fetch State Ministers
  const stateRes = await fetchPoliticians({ lang, is_minister: true, page: 1 });
  const stateMinisters = stateRes.results || [];

  // Fetch Union Ministers from Karnataka
  const unionRes = await fetchPoliticians({ lang, is_union_minister: true, page: 1 });
  const unionMinisters = unionRes.results || [];

  // Merge unique ministers
  const allMinistersMap = new Map<number, PoliticianSummary>();
  [...stateMinisters, ...unionMinisters].forEach((m) => {
    allMinistersMap.set(m.id, m);
  });
  const allMinisters = Array.from(allMinistersMap.values());

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 16px' }}>
      
      {/* Page Header Banner */}
      <div
        style={{
          background: '#ffffff',
          borderRadius: '14px',
          border: '1px solid #e2e8f0',
          padding: '32px 28px',
          marginBottom: '28px',
          boxShadow: '0 1px 3px rgba(15, 23, 42, 0.03)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span
                style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '10px',
                  background: '#0f172a',
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Landmark size={22} />
              </span>
              <div>
                <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f172a', margin: 0, letterSpacing: '-0.02em' }}>
                  {isKn ? 'ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಸಚಿವ ಸಂಪುಟ' : 'Karnataka Executive Cabinet & Portfolios'}
                </h1>
                <p style={{ fontSize: '0.88rem', color: '#64748b', margin: '3px 0 0 0' }}>
                  {isKn ? 'ಸರ್ಕಾರದ ಪ್ರಮುಖ ಸಚಿವಾಲಯಗಳು ಮತ್ತು ಸಚಿವರ ಜವಾಬ್ದಾರಿಗಳ ಪಟ್ಟಿ' : 'Government Ministry Directory & Executive Department Allocations'}
                </p>
              </div>
            </div>

            <p style={{ fontSize: '0.92rem', color: '#334155', lineHeight: '1.6', maxWidth: '820px', marginTop: '12px', marginBottom: 0 }}>
              {isKn
                ? 'ಕರ್ನಾಟಕ ಸರ್ಕಾರದ ಮುಖ್ಯಮಂತ್ರಿಗಳು, ಉಪ ಮುಖ್ಯಮಂತ್ರಿಗಳು, ಸಂಪುಟ ಸಚಿವರು ಮತ್ತು ಕೇಂದ್ರ ಸಚಿವರ ಅಧಿಕೃತ ಸಚಿವಾಲಯಗಳು. ಸಾರ್ವಜನಿಕ ಸೇವೆಗಳು, ಮೂಲಸೌಕರ್ಯ, ಕೃಷಿ, ಇಂಧನ ಮತ್ತು ಕಂದಾಯ ಇಲಾಖೆಗಳನ್ನು ನಿರ್ವಹಿಸುವ ನಾಯಕರ ವಿವರ ಇಲ್ಲಿದೆ.'
                : 'Explore executive government leadership in Karnataka. View cited portfolio allocations, department responsibilities, public records, and declared assets for Cabinet Ministers and Executive Representatives.'}
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                background: '#f8fafc',
                color: '#16a34a',
                border: '1px solid #bbf7d0',
                padding: '8px 14px',
                borderRadius: '8px',
                fontSize: '0.8rem',
                fontWeight: 700,
              }}
            >
              <ShieldCheck size={16} />
              {isKn ? 'ಮೂಲ ಉಲ್ಲೇಖಿತ ಸರ್ಕಾರಿ ದಾಖಲೆಗಳು' : 'CITED GOVERNMENT RECORDS'}
            </span>

            <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
              {isKn ? 'ಮೂಲ: karnataka.gov.in & ECI' : 'Source: karnataka.gov.in & ECI Affidavits'}
            </span>
          </div>
        </div>
      </div>

      {/* Interactive Cabinet Filter Grid Component */}
      <CabinetFilterGrid ministers={allMinisters} lang={lang} />

    </div>
  );
}
