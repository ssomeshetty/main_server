'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { PoliticianSummary } from '../../../lib/api';
import { Locale } from '../../../lib/dictionary';
import { ShieldCheck, Briefcase, Award, ArrowRight, CheckCircle2, UserCheck, Sparkles, Building2 } from 'lucide-react';
import PoliticianAvatar from '../../../components/PoliticianAvatar';

interface Props {
  ministers: PoliticianSummary[];
  lang: Locale;
}

export default function CabinetFilterGrid({ ministers, lang }: Props) {
  const isKn = lang === 'kn';
  const [activeCategory, setActiveCategory] = useState<string>('all');

  const categories = [
    { id: 'all', nameEn: 'All Ministries', nameKn: 'ಎಲ್ಲಾ ಸಚಿವಾಲಯಗಳು', icon: '🏛️' },
    { id: 'cm_deputy', nameEn: 'Executive Leadership (CM & Dy CM)', nameKn: 'ಮುಖ್ಯಮಂತ್ರಿ & ಉಪ ಮುಖ್ಯಮಂತ್ರಿ', icon: '👑' },
    { id: 'infra_it', nameEn: 'Infrastructure, PWD & IT/BT', nameKn: 'ಮೂಲಸೌಕರ್ಯ, ಲೋಕೋಪಯೋಗಿ & IT/BT', icon: '🏗️' },
    { id: 'finance_rev', nameEn: 'Finance, Revenue & Law', nameKn: 'ಹಣಕಾಸು, ಕಂದಾಯ & ಕಾನೂನು', icon: '💰' },
    { id: 'health_edu', nameEn: 'Health, Education & Welfare', nameKn: 'ಆರೋಗ್ಯ, ಶಿಕ್ಷಣ & ಕಲ್ಯಾಣ', icon: '🏥' },
    { id: 'energy_trans', nameEn: 'Energy, Water & Transport', nameKn: 'ಇಂಧನ, ನೀರಾವರಿ & ಸಾರಿಗೆ', icon: '⚡' },
    { id: 'home', nameEn: 'Home Affairs & Internal Security', nameKn: 'ಗೃಹ ಇಲಾಖೆ & ಪೊಲೀಸ್', icon: '🛡️' },
    { id: 'union', nameEn: 'Union Cabinet (Central Govt)', nameKn: 'ಕೇಂದ್ರ ಸಚಿವರು (ಭಾರತ ಸರ್ಕಾರ)', icon: '🇮🇳' },
  ];

  const filterMinisters = () => {
    if (activeCategory === 'all') return ministers;
    
    if (activeCategory === 'cm_deputy') {
      return ministers.filter(m => m.minister_type === 'cm' || m.minister_type === 'deputy_cm');
    }
    
    if (activeCategory === 'infra_it') {
      return ministers.filter(m => {
        const p = (m.portfolio || '').toLowerCase();
        const t = (m.minister_title || '').toLowerCase();
        return p.includes('it') || p.includes('public works') || p.includes('industries') || p.includes('infrastructure') || t.includes('public works') || t.includes('it');
      });
    }

    if (activeCategory === 'finance_rev') {
      return ministers.filter(m => {
        const p = (m.portfolio || '').toLowerCase();
        const t = (m.minister_title || '').toLowerCase();
        return p.includes('finance') || p.includes('revenue') || p.includes('law') || t.includes('finance') || t.includes('revenue') || t.includes('law');
      });
    }

    if (activeCategory === 'health_edu') {
      return ministers.filter(m => {
        const p = (m.portfolio || '').toLowerCase();
        const t = (m.minister_title || '').toLowerCase();
        return p.includes('health') || p.includes('medical') || p.includes('food') || t.includes('health') || t.includes('medical') || t.includes('food');
      });
    }

    if (activeCategory === 'energy_trans') {
      return ministers.filter(m => {
        const p = (m.portfolio || '').toLowerCase();
        const t = (m.minister_title || '').toLowerCase();
        return p.includes('energy') || p.includes('transport') || p.includes('irrigation') || p.includes('water') || t.includes('energy') || t.includes('transport') || t.includes('water');
      });
    }

    if (activeCategory === 'home') {
      return ministers.filter(m => {
        const p = (m.portfolio || '').toLowerCase();
        const t = (m.minister_title || '').toLowerCase();
        return p.includes('home') || t.includes('home');
      });
    }

    if (activeCategory === 'union') {
      return ministers.filter(m => m.is_union_minister);
    }

    return ministers;
  };

  const filtered = filterMinisters();

  return (
    <div>
      {/* Category Tabs */}
      <div
        className="hide-scrollbar"
        style={{
          display: 'flex',
          gap: '10px',
          overflowX: 'auto',
          paddingBottom: '12px',
          marginBottom: '24px',
          scrollBehavior: 'smooth',
          WebkitOverflowScrolling: 'touch',
          scrollSnapType: 'x mandatory',
        }}
      >
        {categories.map((cat) => {
          const isActive = activeCategory === cat.id;
          return (
            <button
              key={cat.id}
              type="button"
              onClick={() => setActiveCategory(cat.id)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                borderRadius: '10px',
                fontSize: '0.85rem',
                fontWeight: 700,
                whiteSpace: 'nowrap',
                border: 'none',
                cursor: 'pointer',
                background: isActive ? '#0f172a' : '#ffffff',
                color: isActive ? '#ffffff' : '#475569',
                boxShadow: isActive ? '0 2px 6px rgba(15, 23, 42, 0.16)' : '0 1px 2px rgba(15, 23, 42, 0.04)',
                transition: 'all 0.15s ease',
                scrollSnapAlign: 'start',
              }}
            >
              <span>{cat.icon}</span>
              <span>{isKn ? cat.nameKn : cat.nameEn}</span>
            </button>
          );
        })}
      </div>

      {/* Results Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
          {isKn ? 'ಸಚಿವರ ಪಟ್ಟಿ' : 'Executive Leadership Directory'} ({filtered.length})
        </h2>
        <span style={{ fontSize: '0.82rem', color: '#64748b' }}>
          {isKn ? 'ಪೂರ್ಣ ಪ್ರೊಫೈಲ್ ವೀಕ್ಷಿಸಲು ನಾಯಕರ ಕಾರ್ಡ್ ಕ್ಲಿಕ್ ಮಾಡಿ' : 'Click any minister card to view full accountability analysis'}
        </span>
      </div>

      {/* Grid of Minister Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 350px), 1fr))',
          gap: '20px',
        }}
      >
        {filtered.map((m) => {
          const isUnion = m.is_union_minister;
          const title = isUnion ? (m.union_title || m.minister_title) : m.minister_title;
          const portfolio = isUnion ? (m.union_portfolio || m.portfolio) : m.portfolio;

          return (
            <div
              key={m.id}
              style={{
                background: '#ffffff',
                borderRadius: '12px',
                border: '1px solid #e2e8f0',
                padding: '20px',
                boxShadow: '0 1px 3px rgba(15, 23, 42, 0.03)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease',
              }}
            >
              <div>
                {/* Header: Photo + Name + Role Badge */}
                <div style={{ display: 'flex', gap: '14px', alignItems: 'flex-start', marginBottom: '14px' }}>
                  <PoliticianAvatar
                    photoUrl={m.photo_url}
                    name={m.name}
                    size={64}
                  />

                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', marginBottom: '4px' }}>
                      <span
                        style={{
                          background: m.minister_type === 'cm' ? '#eff6ff' : isUnion ? '#fef3c7' : '#ecfdf5',
                          color: m.minister_type === 'cm' ? '#1d4ed8' : isUnion ? '#b45309' : '#047857',
                          border: `1px solid ${m.minister_type === 'cm' ? '#bfdbfe' : isUnion ? '#fde68a' : '#a7f3d0'}`,
                          padding: '2px 8px',
                          borderRadius: '6px',
                          fontSize: '0.72rem',
                          fontWeight: 700,
                        }}
                      >
                        {m.minister_type === 'cm'
                          ? (isKn ? 'ಮುಖ್ಯಮಂತ್ರಿಗಳು' : 'CHIEF MINISTER')
                          : m.minister_type === 'deputy_cm'
                          ? (isKn ? 'ಉಪ ಮುಖ್ಯಮಂತ್ರಿಗಳು' : 'DEPUTY CM')
                          : isUnion
                          ? (isKn ? 'ಕೇಂದ್ರ ಸಚಿವರು' : 'UNION MINISTER')
                          : (isKn ? 'ಸಂಪುಟ ಸಚಿವರು' : 'CABINET MINISTER')}
                      </span>

                      {m.party_name && (
                        <span style={{ fontSize: '0.72rem', fontWeight: 600, color: '#64748b', background: '#f8fafc', padding: '2px 8px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                          {m.party_name}
                        </span>
                      )}
                    </div>

                    <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#0f172a', margin: '0 0 2px 0' }}>
                      {m.name}
                    </h3>

                    <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                      {m.constituency_name || m.parliamentary_constituency || (isKn ? 'ಕರ್ನಾಟಕ ಕ್ಷೇತ್ರ' : 'Karnataka Representative')}
                    </div>
                  </div>
                </div>

                {/* Ministry Title */}
                {title && (
                  <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f172a', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Briefcase size={15} color="#2563eb" />
                    <span>{title}</span>
                  </div>
                )}

                {/* Official Portfolio Allocation Box */}
                <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '16px' }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '4px' }}>
                    {isKn ? 'ಇಲಾಖೆಯ ಜವಾಬ್ದಾರಿಗಳು (Portfolio):' : 'Executive Portfolio Allocations:'}
                  </div>
                  <div style={{ fontSize: '0.82rem', color: '#334155', lineHeight: '1.45', fontWeight: 500 }}>
                    {portfolio || (isKn ? 'ಅಧಿಕೃತ ಸರ್ಕಾರಿ ಇಲಾಖೆ ಜವಾಬ್ದಾರಿಗಳು' : 'Official State Department Allocations')}
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <Link
                href={`/${lang}/politicians/${m.slug || m.id}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  background: '#0f172a',
                  color: '#ffffff',
                  padding: '10px 16px',
                  borderRadius: '8px',
                  fontSize: '0.82rem',
                  fontWeight: 700,
                  textDecoration: 'none',
                  transition: 'background 0.15s ease',
                }}
              >
                <span>{isKn ? 'ಸಂಪೂರ್ಣ ಆಸ್ತಿ & ಸಾರ್ವಜನಿಕ ವಿವರ ವೀಕ್ಷಿಸಿ' : 'View Full Public Record Profile'}</span>
                <ArrowRight size={15} />
              </Link>
            </div>
          );
        })}
      </div>
    </div>
  );
}
