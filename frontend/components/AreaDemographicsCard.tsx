'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import { PieChart, Landmark, ShieldCheck, Users, BookOpen, UserCheck } from 'lucide-react';
import { AreaDemographics } from '../lib/api';

interface Props {
  data: AreaDemographics;
  lang?: 'en' | 'kn';
}

export default function AreaDemographicsCard({ data, lang: propLang }: Props) {
  const params = useParams();
  const routeLang = params?.lang as 'en' | 'kn';
  const isKn = (propLang || routeLang) === 'kn';

  const rel = data.religion_composition;

  const religions = [
    { labelEn: 'Hindu', labelKn: 'ಹೂಂದು', pct: rel.hindu_pct, color: '#d97706' },
    { labelEn: 'Muslim', labelKn: 'ಮುಸ್ಲಿಂ', pct: rel.muslim_pct, color: '#059669' },
    { labelEn: 'Christian', labelKn: 'ಕ್ರಿಶ್ಚಿಯನ್', pct: rel.christian_pct, color: '#2563eb' },
    { labelEn: 'Jain', labelKn: 'ಜೈನ', pct: rel.jain_pct, color: '#7c3aed' },
    { labelEn: 'Buddhist', labelKn: 'ಬೌದ್ಧ', pct: rel.buddhist_pct, color: '#0891b2' },
    { labelEn: 'Sikh', labelKn: 'ಸಿಖ್', pct: rel.sikh_pct, color: '#e11d48' },
  ];

  const topReligion = [...religions].sort((a, b) => b.pct - a.pct)[0];

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: '12px',
        border: '1px solid #e2e8f0',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(15, 23, 42, 0.03)',
        marginBottom: '24px',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '20px',
          paddingBottom: '16px',
          borderBottom: '1px solid #f1f5f9',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '8px',
                background: '#0f172a',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <PieChart size={18} />
            </span>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', margin: 0, letterSpacing: '-0.01em' }}>
              {isKn ? 'ಕ್ಷೇತ್ರದ ಜನಸಂಖ್ಯಾ ಅಂಕಿಅಂಶಗಳ ವರದಿ' : 'Constituency Demographics Profile'}
            </h3>
          </div>
          <p style={{ fontSize: '0.82rem', color: '#64748b', margin: 0 }}>
            {isKn ? `ಅಧಿಕೃತ ಜನಗಣತಿ — ${data.constituency_name} (${data.district_name} ಜಿಲ್ಲೆ)` : `Official Census Baseline — ${data.constituency_name} (${data.district_name} District)`}
          </p>
        </div>
        <span
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: '#f8fafc',
            color: '#334155',
            border: '1px solid #e2e8f0',
            padding: '6px 12px',
            borderRadius: '8px',
            fontSize: '0.78rem',
            fontWeight: 600,
          }}
        >
          <ShieldCheck size={14} color="#16a34a" /> {isKn ? 'ಜನಗಣತಿ ದೃಢೀಕರಿಸಲ್ಪಟ್ಟಿದೆ' : 'VERIFIED CENSUS BASELINE'}
        </span>
      </div>

      {/* Demographic Summary Banner */}
      <div
        style={{
          background: '#f8fafc',
          border: '1px solid #e2e8f0',
          borderRadius: '8px',
          padding: '14px 16px',
          marginBottom: '20px',
        }}
      >
        <div style={{ fontSize: '0.85rem', color: '#334155', lineHeight: '1.5' }}>
          <strong>{isKn ? 'ಜನಸಂಖ್ಯೆಯ ಸಾರಾಂಶ:' : 'Demographic Summary:'}</strong>{' '}
          {isKn
            ? `${data.constituency_name} ಕ್ಷೇತ್ರದಲ್ಲಿ ಒಟ್ಟು ${data.population ? data.population.toLocaleString('kn-IN') : 'N/A'} ಜನಸಂಖ್ಯೆ ಇದ್ದು, ${topReligion.labelKn} ಸಮುದಾಯ (${topReligion.pct.toFixed(1)}%) ದೊಡ್ಡ ಗುಂಪಾಗಿದೆ. ಸಾಕ್ಷರತಾ ಪ್ರಮಾಣ ${data.literacy_rate}% ಮತ್ತು ಲಿಂಗಾನುಪಾತ ${data.sex_ratio} ಆಗಿದೆ.`
            : `In ${data.constituency_name}, out of a census population of ${data.population ? data.population.toLocaleString('en-IN') : 'N/A'} residents, ${topReligion.labelEn} (${topReligion.pct.toFixed(1)}%) forms the largest baseline community. Area literacy rate is ${data.literacy_rate}% with a sex ratio of ${data.sex_ratio}.`}
        </div>
      </div>

      {/* Key Metric Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
          gap: '12px',
          marginBottom: '20px',
        }}
      >
        <div style={{ background: '#ffffff', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Users size={13} /> {isKn ? 'ಒಟ್ಟು ಜನಸಂಖ್ಯೆ' : 'Area Population'}
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a', marginTop: '4px' }}>
            {data.population ? (isKn ? data.population.toLocaleString('kn-IN') : data.population.toLocaleString('en-IN')) : 'N/A'}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>{isKn ? 'ಜನಗಣತಿ ಲೆಕ್ಕಾಚಾರ' : 'Census Count'}</div>
        </div>

        <div style={{ background: '#ffffff', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <BookOpen size={13} /> {isKn ? 'ಸಾಕ್ಷರತಾ ಪ್ರಮಾಣ' : 'Literacy Rate'}
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a', marginTop: '4px' }}>
            {data.literacy_rate}%
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>{isKn ? 'ಅಕ್ಷರಸ್ಥ ನಾಗರಿಕರು' : 'Literate Citizens'}</div>
        </div>

        <div style={{ background: '#ffffff', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <UserCheck size={13} /> {isKn ? 'ಲಿಂಗಾನುಪಾತ' : 'Sex Ratio'}
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a', marginTop: '4px' }}>
            {data.sex_ratio}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>{isKn ? 'ಪ್ರತಿ ೧೦೦೦ ಪುರುಷರಿಗೆ ಮಹಿಳೆಯರು' : 'Females / 1k Males'}</div>
        </div>

        <div style={{ background: '#ffffff', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Landmark size={13} /> {isKn ? 'ಕ್ಷೇತ್ರದ ವರ್ಗ' : 'Seat Category'}
          </div>
          <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#0f172a', marginTop: '4px', textTransform: 'uppercase' }}>
            {data.constituency_type === 'sc' ? (isKn ? 'SC ಮೀಸಲು' : 'SC Reserved') : data.constituency_type === 'st' ? (isKn ? 'ST ಮೀಸಲು' : 'ST Reserved') : (isKn ? 'ಸಾಮಾನ್ಯ' : 'General')}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>{isKn ? 'ECI ವರ್ಗೀಕರಣ' : 'ECI Category'}</div>
        </div>
      </div>

      {/* Visual Proportional Stacked Progress Chart */}
      <div style={{ marginBottom: '20px', background: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
        <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f172a', marginBottom: '14px', textTransform: 'uppercase', letterSpacing: '0.02em' }}>
          {isKn ? 'ಜನಸಂಖ್ಯೆಯ ವಿಂಗಡಣೆ (ಶೇಕಡಾವಾರು)' : 'Demographic Population Composition (% Share)'}
        </h4>

        {/* Stacked Chart Bar */}
        <div style={{ height: '12px', width: '100%', background: '#e2e8f0', borderRadius: '6px', overflow: 'hidden', display: 'flex', marginBottom: '16px' }}>
          {religions.map((r) => (
            r.pct > 0 ? (
              <div
                key={r.labelEn}
                style={{ width: `${r.pct}%`, height: '100%', background: r.color }}
                title={`${isKn ? r.labelKn : r.labelEn}: ${r.pct.toFixed(1)}%`}
              />
            ) : null
          ))}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
          {religions.map((r) => (
            <div key={r.labelEn} style={{ background: '#ffffff', padding: '10px 12px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', fontWeight: 700, marginBottom: '4px' }}>
                <span style={{ color: '#334155' }}>{isKn ? r.labelKn : r.labelEn}</span>
                <span style={{ color: '#0f172a' }}>{r.pct.toFixed(1)}%</span>
              </div>
              <div style={{ height: '6px', background: '#f1f5f9', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: `${Math.min(100, r.pct)}%`, height: '100%', background: r.color, borderRadius: '3px' }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
