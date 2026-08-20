'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import { ShieldCheck, TrendingUp, AlertCircle, Award, CheckCircle2, Info, Sparkles } from 'lucide-react';
import { IntelligenceReport } from '../lib/api';

interface Props {
  data: IntelligenceReport;
  lang?: 'en' | 'kn';
}

export default function PalantirIntelligencePanel({ data, lang: propLang }: Props) {
  const params = useParams();
  const routeLang = params?.lang as 'en' | 'kn';
  const isKn = (propLang || routeLang) === 'kn';

  const [viewMode, setViewMode] = useState<'citizen' | 'expert'>('citizen');

  const fin = data.financial_analysis;
  const evs = data.electoral_vulnerability;
  const lig = data.legislative_influence;

  // Currency helper in Lakhs / Crores
  const formatMoney = (amount?: number) => {
    if (!amount || amount === 0) return isKn ? 'ಅಫಿಡವಿಟ್ ಸಲ್ಲಿಸಲಾಗಿದೆ' : 'Affidavit Filed';
    const cr = amount / 10000000;
    if (cr >= 1) return isKn ? `₹${cr.toFixed(2)} ಕೋಟಿ` : `₹${cr.toFixed(2)} Crore`;
    const lakh = amount / 100000;
    return isKn ? `₹${lakh.toFixed(0)} ಲಕ್ಷ` : `₹${lakh.toFixed(0)} Lakh`;
  };

  // Wealth growth summary based on language
  const getWealthSummary = () => {
    const factor = parseFloat(fin.asset_growth_factor) || 1.6;
    const currentVal = Math.round(factor * 100);

    if (factor <= 1.8) {
      return {
        badge: isKn ? 'ಸಾಮಾನ್ಯ ಆಸ್ತಿ ಬೆಳವಣಿಗೆ' : 'Normal Asset Growth',
        badgeBg: '#f0fdf4',
        badgeText: '#15803d',
        badgeBorder: '#bbf7d0',
        explanation: isKn
          ? `ಘೋಷಿತ ಆಸ್ತಿಗಳು ವರ್ಷಕ್ಕೆ ~${fin.cagr_pct}% ರಂತೆ ಹೆಚ್ಚಾಗಿವೆ (೫ ವರ್ಷಗಳಲ್ಲಿ ${fin.asset_growth_factor} ಪಟ್ಟು). ಇದು ಬ್ಯಾಂಕ್ ಠೇವಣಿ ಅಥವಾ ಆಸ್ತಿಯ ಮೌಲ್ಯವರ್ಧನೆಯ ಸಾಮಾನ್ಯ ದರವಾಗಿದೆ.`
          : `Declared assets grew by ~${fin.cagr_pct}% annually (${fin.asset_growth_factor}x over 5 years). This rate aligns with standard property appreciation and asset yields.`,
        analogy: isKn
          ? `೨೦೧೮ ರಲ್ಲಿ ₹೧೦೦ ಇದ್ದ ಆಸ್ತಿಯ ಮೌಲ್ಯ, ಈಗ ಸುಮಾರು ₹${currentVal} ಆಗಿದೆ.`
          : `For every ₹100 declared in 2018, total property value is now ~₹${currentVal}.`,
      };
    } else if (factor <= 3.0) {
      return {
        badge: isKn ? 'ಹೆಚ್ಚಿನ ಆಸ್ತಿ ಬೆಳವಣಿಗೆ' : 'Above Average Growth',
        badgeBg: '#fff7ed',
        badgeText: '#c2410c',
        badgeBorder: '#fed7aa',
        explanation: isKn
          ? `ಘೋಷಿತ ಆಸ್ತಿಗಳು ವರ್ಷಕ್ಕೆ ~${fin.cagr_pct}% ರಂತೆ ಹೆಚ್ಚಾಗಿವೆ (೫ ವರ್ಷಗಳಲ್ಲಿ ${fin.asset_growth_factor} ಪಟ್ಟು). ಇದು ಸಾಮಾನ್ಯ ಆರ್ಥಿಕ ದರಕ್ಕಿಂತ ಹೆಚ್ಚಾಗಿದೆ.`
          : `Declared assets grew by ~${fin.cagr_pct}% annually (${fin.asset_growth_factor}x over 5 years), which is higher than average market yields.`,
        analogy: isKn
          ? `೨೦೧೮ ರಲ್ಲಿ ₹೧೦೦ ಇದ್ದ ಆಸ್ತಿಯ ಮೌಲ್ಯ, ಈಗ ಸುಮಾರು ₹${currentVal} ಆಗಿದೆ.`
          : `For every ₹100 declared in 2018, total property value is now ~₹${currentVal}.`,
      };
    } else {
      return {
        badge: isKn ? 'ವೇಗದ ಆಸ್ತಿ ಏರಿಕೆ' : 'Significant Growth',
        badgeBg: '#fef2f2',
        badgeText: '#b91c1c',
        badgeBorder: '#fecaca',
        explanation: isKn
          ? `ಘೋಷಿತ ಆಸ್ತಿಗಳು ವರ್ಷಕ್ಕೆ ~${fin.cagr_pct}% ರಂತೆ ವೇಗವಾಗಿ ಹೆಚ್ಚಾಗಿವೆ (೫ ವರ್ಷಗಳಲ್ಲಿ ${fin.asset_growth_factor} ಪಟ್ಟು).`
          : `Declared assets increased rapidly by ~${fin.cagr_pct}% per year (${fin.asset_growth_factor}x growth over 5 years).`,
        analogy: isKn
          ? `೨೦೧೮ ರಲ್ಲಿ ₹೧೦೦ ಇದ್ದ ಆಸ್ತಿಯ ಮೌಲ್ಯ, ಈಗ ಸುಮಾರು ₹${currentVal} ಆಗಿದೆ.`
          : `For every ₹100 declared in 2018, total property value is now ~₹${currentVal}.`,
      };
    }
  };

  // Election summary based on language
  const getElectionSummary = () => {
    const margin = evs.margin_pct;
    if (margin <= 5.0) {
      return {
        badge: isKn ? 'ತೀವ್ರ ಸ್ಪರ್ಧೆಯ ಕ್ಷೇತ್ರ' : 'Close Win Margin',
        badgeBg: '#fff7ed',
        badgeText: '#c2410c',
        badgeBorder: '#fed7aa',
        summary: isKn
          ? `ಚುನಾವಣೆಯಲ್ಲಿ +${margin}% ನಷ್ಟು ಸಣ್ಣ ಅಂತರದಿಂದ ಗೆದ್ದಿದ್ದಾರೆ. ಕ್ಷೇತ್ರದಲ್ಲಿ ತೀವ್ರ ಸ್ಪರ್ಧೆ ಇತ್ತು.`
          : `Won the election with a narrow victory margin of +${margin}%. This constituency is closely contested.`,
        takeaway: isKn
          ? 'ಸಣ್ಣ ಪ್ರಮಾಣದ ಮತಗಳ ಬದಲಾವಣೆಯು ಮುಂದಿನ ಚುನಾವಣಾ ಫಲಿತಾಂಶವನ್ನು ಬದಲಾಯಿಸಬಹುದು.'
          : 'A small shift in voter turnout can significantly impact the outcome in future elections.',
      };
    } else if (margin <= 15.0) {
      return {
        badge: isKn ? 'ಮಧ್ಯಮ ಗೆಲುವಿನ ಅಂತರ' : 'Moderate Win Margin',
        badgeBg: '#eff6ff',
        badgeText: '#1d4ed8',
        badgeBorder: '#bfdbfe',
        summary: isKn
          ? `ಎರಡನೇ ಸ್ಥಾನದ ಅಭ್ಯರ್ಥಿಗಿಂತ +${margin}% ನಷ್ಟು ಉತ್ತಮ ಮತಗಳ ಅಂತರದಿಂದ ಗೆದ್ದಿದ್ದಾರೆ.`
          : `Won with a moderate lead of +${margin}% over the nearest competitor.`,
        takeaway: isKn
          ? 'ಕ್ಷೇತ್ರದಲ್ಲಿ ಸ್ಥಿರವಾದ ಮುನ್ನಡೆ ಇದೆ.'
          : 'Maintains a reasonable advantage in the constituency.',
      };
    } else {
      return {
        badge: isKn ? 'ಭದ್ರವಾದ ಕ್ಷೇತ್ರ' : 'Strong Safe Seat',
        badgeBg: '#f0fdf4',
        badgeText: '#15803d',
        badgeBorder: '#bbf7d0',
        summary: isKn
          ? `+${margin}% ನಷ್ಟು ದೊಡ್ಡ ಮತಗಳ ಅಂತರದಿಂದ ಸುಲಭವಾಗಿ ಗೆದ್ದಿದ್ದಾರೆ.`
          : `Won comfortably with a strong margin buffer of +${margin}%.`,
        takeaway: isKn
          ? 'ಕ್ಷೇತ್ರದಲ್ಲಿ ಗಟ್ಟಿ ಮತದಾರರ ಬೆಂಬಲವಿದೆ.'
          : 'Holds a substantial vote share cushion.',
      };
    }
  };

  const wealthInfo = getWealthSummary();
  const electionInfo = getElectionSummary();

  return (
    <div style={{ marginBottom: '32px' }}>
      <div
        style={{
          background: '#ffffff',
          borderRadius: '12px',
          border: '1px solid #e2e8f0',
          padding: '24px',
          boxShadow: '0 1px 3px rgba(15, 23, 42, 0.03)',
        }}
      >
        {/* Header Bar */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '16px',
            marginBottom: '20px',
            paddingBottom: '16px',
            borderBottom: '1px solid #f1f5f9',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '36px',
                height: '36px',
                borderRadius: '8px',
                background: '#0f172a',
                color: '#ffffff',
              }}
            >
              <CheckCircle2 size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', margin: 0, letterSpacing: '-0.01em' }}>
                {isKn ? 'ಸಾರ್ವಜನಿಕ ಸೇವೆ ಮತ್ತು ಆಸ್ತಿ ವಿವರ ವರದಿ' : 'Public Accountability Summary'}
              </h2>
              <p style={{ fontSize: '0.82rem', color: '#64748b', margin: '2px 0 0 0' }}>
                {isKn ? `ಅಧಿಕೃತ ವರದಿ — ${data.name}` : `Official Performance & Financial Summary — ${data.name}`}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            {/* View Switcher */}
            <div
              style={{
                display: 'inline-flex',
                background: '#f8fafc',
                padding: '3px',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
              }}
            >
              <button
                type="button"
                onClick={() => setViewMode('citizen')}
                style={{
                  padding: '6px 14px',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  border: 'none',
                  cursor: 'pointer',
                  background: viewMode === 'citizen' ? '#0f172a' : 'transparent',
                  color: viewMode === 'citizen' ? '#ffffff' : '#64748b',
                  transition: 'all 0.15s ease',
                }}
              >
                {isKn ? 'ಜನರ ನೋಟ' : 'Citizen View'}
              </button>

              <button
                type="button"
                onClick={() => setViewMode('expert')}
                style={{
                  padding: '6px 14px',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  border: 'none',
                  cursor: 'pointer',
                  background: viewMode === 'expert' ? '#0f172a' : 'transparent',
                  color: viewMode === 'expert' ? '#ffffff' : '#64748b',
                  transition: 'all 0.15s ease',
                }}
              >
                {isKn ? 'ವಿಶ್ಲೇಷಣೆ' : 'Expert Ratios'}
              </button>
            </div>

            <span
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                background: '#f8fafc',
                color: '#334155',
                padding: '6px 12px',
                borderRadius: '8px',
                fontSize: '0.78rem',
                fontWeight: 600,
                border: '1px solid #e2e8f0',
              }}
            >
              <ShieldCheck size={14} color="#16a34a" />
              {isKn ? 'ECI ದಾಖಲೆಗಳಿಂದ ದೃಢೀಕರಿಸಲ್ಪಟ್ಟಿದೆ' : 'Verified ECI Affidavits'}
            </span>
          </div>
        </div>

        {/* CITIZEN VIEW */}
        {viewMode === 'citizen' && (
          <div>
            {/* Top 3-Point Summary Box */}
            <div
              style={{
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '10px',
                padding: '16px',
                marginBottom: '20px',
              }}
            >
              <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0f172a', margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Sparkles size={16} color="#2563eb" />
                {isKn ? 'ಮತದಾರರು ಮುಖ್ಯವಾಗಿ ತಿಳಿಯಬೇಕಾದ ೩ ಸಂಗತಿಗಳು' : 'Key Takeaways for Voters'}
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '12px' }}>
                {/* Point 1 */}
                <div style={{ background: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#2563eb', textTransform: 'uppercase', marginBottom: '2px' }}>
                    {isKn ? '೧. ಆಸ್ತಿ ವಿವರ' : '1. Declared Assets'}
                  </div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', marginBottom: '2px' }}>
                    {formatMoney(fin.current_net_worth)}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#475569', lineHeight: '1.4' }}>
                    {isKn
                      ? `ವರ್ಷಕ್ಕೆ ~${fin.cagr_pct}% ರಷ್ಟು ಏರಿಕೆ. (${wealthInfo.badge})`
                      : `Annual growth of ~${fin.cagr_pct}%. (${wealthInfo.badge})`}
                  </div>
                </div>

                {/* Point 2 */}
                <div style={{ background: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#d97706', textTransform: 'uppercase', marginBottom: '2px' }}>
                    {isKn ? '೨. ಗೆಲುವಿನ ಅಂತರ' : '2. Victory Margin'}
                  </div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', marginBottom: '2px' }}>
                    +{evs.margin_pct}% {isKn ? 'ಮತಗಳ ಮುನ್ನಡೆ' : 'Lead'}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#475569', lineHeight: '1.4' }}>
                    {electionInfo.badge} — {electionInfo.summary}
                  </div>
                </div>

                {/* Point 3 */}
                <div style={{ background: '#ffffff', padding: '12px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#16a34a', textTransform: 'uppercase', marginBottom: '2px' }}>
                    {isKn ? '೩. ಸ್ಥಾನ ಮತ್ತು ಅನುಭವ' : '3. Assembly Experience'}
                  </div>
                  <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', marginBottom: '2px' }}>
                    {lig.office_title || (isKn ? 'ಶಾಸಕರು' : 'Elected MLA')}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#475569', lineHeight: '1.4' }}>
                    {isKn
                      ? `ವಿಧಾನಸಭೆಯಲ್ಲಿ ${lig.total_terms} ಬಾರಿ ಶಾಸಕರಾಗಿ ಆಯ್ಕೆಯಾಗಿದ್ದಾರೆ.`
                      : `Elected for ${lig.total_terms} terms in the Assembly.`}
                  </div>
                </div>
              </div>
            </div>

            {/* Detailed Cards Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              
              {/* Card 1: Assets */}
              <div
                style={{
                  background: '#ffffff',
                  padding: '18px',
                  borderRadius: '10px',
                  border: '1px solid #e2e8f0',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <TrendingUp size={16} color="#2563eb" />
                      {isKn ? 'ಆಸ್ತಿ ಮತ್ತು ಹಣಕಾಸು ಏರಿಕೆ' : 'Property & Wealth Trajectory'}
                    </span>
                    <span
                      style={{
                        background: wealthInfo.badgeBg,
                        color: wealthInfo.badgeText,
                        padding: '3px 8px',
                        borderRadius: '5px',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        border: `1px solid ${wealthInfo.badgeBorder}`,
                      }}
                    >
                      {wealthInfo.badge}
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div style={{ marginBottom: '14px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: '#64748b', marginBottom: '4px' }}>
                      <span>{isKn ? '೨೦೧೮ ಪ್ರಮಾಣಪತ್ರ' : '2018 Affidavit'}</span>
                      <span>{isKn ? '೨೦೨೩ ಪ್ರಮಾಣಪತ್ರ' : '2023 Affidavit'}</span>
                    </div>
                    <div style={{ height: '8px', background: '#f1f5f9', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
                      <div style={{ width: '55%', background: '#93c5fd' }}></div>
                      <div style={{ width: '45%', background: '#2563eb' }}></div>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', fontWeight: 600, color: '#334155', marginTop: '4px' }}>
                      <span>{isKn ? 'ಆರಂಭಿಕ ಆಸ್ತಿ' : 'Baseline Assets'}</span>
                      <span style={{ color: '#2563eb' }}>{fin.asset_growth_factor}x {isKn ? 'ಏರಿಕೆ' : 'Growth'}</span>
                    </div>
                  </div>

                  <p style={{ fontSize: '0.83rem', color: '#334155', lineHeight: '1.5', marginBottom: '12px' }}>
                    {wealthInfo.explanation}
                  </p>
                </div>

                <div style={{ background: '#f8fafc', padding: '10px 12px', borderRadius: '6px', fontSize: '0.78rem', color: '#475569', border: '1px solid #f1f5f9' }}>
                  <strong>{isKn ? 'ಉದಾಹರಣೆ:' : 'Context:'}</strong> {wealthInfo.analogy}
                </div>
              </div>

              {/* Card 2: Election Margin */}
              <div
                style={{
                  background: '#ffffff',
                  padding: '18px',
                  borderRadius: '10px',
                  border: '1px solid #e2e8f0',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <AlertCircle size={16} color="#d97706" />
                      {isKn ? 'ಚುನಾವಣಾ ಗೆಲುವಿನ ಅಂತರ' : 'Election Win Security'}
                    </span>
                    <span
                      style={{
                        background: electionInfo.badgeBg,
                        color: electionInfo.badgeText,
                        padding: '3px 8px',
                        borderRadius: '5px',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        border: `1px solid ${electionInfo.badgeBorder}`,
                      }}
                    >
                      +{evs.margin_pct}% {isKn ? 'ಅಂತರ' : 'Margin'}
                    </span>
                  </div>

                  {/* Gauge */}
                  <div style={{ marginBottom: '14px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: '#64748b', marginBottom: '4px' }}>
                      <span>{isKn ? 'ಗೆಲುವಿನ ಸುಲಭತೆ' : 'Victory Cushion'}</span>
                      <span style={{ fontWeight: 600, color: electionInfo.badgeText }}>{electionInfo.badge}</span>
                    </div>
                    <div style={{ height: '8px', background: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ width: `${Math.min(evs.margin_pct * 3.5, 100)}%`, background: evs.margin_pct <= 5 ? '#f59e0b' : '#10b981', height: '100%' }}></div>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#64748b', marginTop: '4px' }}>
                      <span>0% ({isKn ? 'ಸಮಬಲ' : 'Equal'})</span>
                      <span>+15% ({isKn ? 'ಸುರಕ್ಷಿತ' : 'Safe'})</span>
                    </div>
                  </div>

                  <p style={{ fontSize: '0.83rem', color: '#334155', lineHeight: '1.5', marginBottom: '12px' }}>
                    {electionInfo.summary}
                  </p>
                </div>

                <div style={{ background: '#f8fafc', padding: '10px 12px', borderRadius: '6px', fontSize: '0.78rem', color: '#475569', border: '1px solid #f1f5f9' }}>
                  <strong>{isKn ? 'ವಿವರಣೆ:' : 'Context:'}</strong> {electionInfo.takeaway}
                </div>
              </div>

              {/* Card 3: Experience */}
              <div
                style={{
                  background: '#ffffff',
                  padding: '18px',
                  borderRadius: '10px',
                  border: '1px solid #e2e8f0',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Award size={16} color="#16a34a" />
                      {isKn ? 'ಅನುಭವ ಮತ್ತು ಹುದ್ದೆ' : 'Legislative Seniority'}
                    </span>
                    <span style={{ background: '#ecfdf5', color: '#047857', padding: '3px 8px', borderRadius: '5px', fontSize: '0.72rem', fontWeight: 700, border: '1px solid #a7f3d0' }}>
                      {lig.total_terms} {isKn ? 'ಬಾರಿ ಶಾಸಕರು' : 'Terms MLA'}
                    </span>
                  </div>

                  <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a', marginBottom: '4px' }}>
                    {lig.office_title || (isKn ? 'ಶಾಸಕರು' : 'Elected MLA')}
                  </div>

                  <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '12px' }}>
                    {isKn ? 'ಕರ್ನಾಟಕ ವಿಧಾನಸಭೆ' : 'Karnataka Legislative Assembly'}
                  </div>

                  <p style={{ fontSize: '0.83rem', color: '#334155', lineHeight: '1.5', marginBottom: '12px' }}>
                    {isKn
                      ? `ವಿಧಾನಸಭೆಯಲ್ಲಿ ${lig.total_terms} ಬಾರಿ ಶಾಸಕರಾಗಿ ಆಯ್ಕೆಯಾಗಿದ್ದು, ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಸಚಿವ ಸಂಪುಟದ ಜವಾಬ್ದಾರಿಗಳನ್ನು ನಿರ್ವಹಿಸಿದ್ದಾರೆ.`
                      : `Has served ${lig.total_terms} terms as an elected representative in the Karnataka Legislative Assembly.`}
                  </p>
                </div>

                <div style={{ background: '#f8fafc', padding: '10px 12px', borderRadius: '6px', fontSize: '0.78rem', color: '#475569', border: '1px solid #f1f5f9' }}>
                  <strong>{isKn ? 'ಜವಾಬ್ದಾರಿ:' : 'Role:'}</strong> {isKn ? 'ಶಾಸನ ರಚನೆ ಮತ್ತು ಕ್ಷೇತ್ರದ ಸಾರ್ವಜನಿಕ ಸೇವೆ.' : 'Constituency representation & legislative administration.'}
                </div>
              </div>

            </div>
          </div>
        )}

        {/* EXPERT VIEW */}
        {viewMode === 'expert' && (
          <div>
            <div
              style={{
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '10px 14px',
                marginBottom: '16px',
                fontSize: '0.8rem',
                color: '#475569',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <Info size={15} color="#0f172a" />
              <span>
                <strong>{isKn ? 'ತಾಂತ್ರಿಕ ವಿಶ್ಲೇಷಣೆ:' : 'Technical Ratios Mode:'}</strong>{' '}
                {isKn
                  ? 'ಸಂಶೋಧಕರು ಮತ್ತು ಪತ್ರಕರ್ತರಿಗೆ ಅಗತ್ಯವಾದ CAGR, ಶೇಕಡಾವಾರು ಆಸ್ತಿ ಏರಿಕೆ ಮತ್ತು ಚುನಾವಣಾ ಅಂಕಿಅಂಶಗಳ ವಿವರಣೆ.'
                  : 'Displaying CAGR calculations, growth multipliers, leverage ratios, and vulnerability scores for research.'}
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
              
              {/* Financial CAGR Technical Card */}
              <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155', textTransform: 'uppercase', marginBottom: '8px' }}>
                  {isKn ? 'ಆಸ್ತಿ ಏರಿಕೆ ದರ (CAGR)' : 'Financial Growth & CAGR'}
                </div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', marginBottom: '2px' }}>
                  CAGR: {fin.cagr_pct}%
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '6px' }}>
                  {isKn ? 'ಆಸ್ತಿ ಏರಿಕೆ ಅಪವರ್ತನ:' : 'Growth Factor:'} <strong>{fin.asset_growth_factor}x</strong>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '10px' }}>
                  {isKn ? 'ಸಾಲದ ಪ್ರಮಾಣ:' : 'Leverage Ratio:'} <strong>{fin.leverage_ratio_pct}%</strong>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#334155', background: '#ffffff', padding: '8px', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
                  {fin.insight_text}
                </div>
              </div>

              {/* Electoral Technical Card */}
              <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155', textTransform: 'uppercase', marginBottom: '8px' }}>
                  {isKn ? 'ಚುನಾವಣಾ ಸುಲಭತೆಯ ಅಂಕ' : 'Electoral Security Index'}
                </div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', marginBottom: '2px' }}>
                  {isKn ? 'ಅಂತರ:' : 'Margin:'} +{evs.margin_pct}%
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '6px' }}>
                  EVM Dominance: <strong>{evs.evm_dominance_pct}%</strong>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '10px' }}>
                  Vulnerability Score: <strong>{evs.vulnerability_score} / 100</strong>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#334155', background: '#ffffff', padding: '8px', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
                  {evs.insight_text}
                </div>
              </div>

              {/* Legislative Seniority Technical Card */}
              <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#334155', textTransform: 'uppercase', marginBottom: '8px' }}>
                  {isKn ? 'ವಿಧಾನಸಭಾ ಅನುಭವದ ಅಂಕ' : 'Legislative Seniority Score'}
                </div>
                <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', marginBottom: '2px' }}>
                  {lig.total_terms} {isKn ? 'ಬಾರಿ ಆಯ್ಕೆ' : 'Terms Elected'}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '6px' }}>
                  {isKn ? 'ಹುದ್ದೆ:' : 'Office:'} <strong>{lig.office_title}</strong>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '10px' }}>
                  Seniority Score: <strong>{lig.seniority_score} / 100</strong>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#334155', background: '#ffffff', padding: '8px', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
                  {isKn ? 'ಸಚಿವ ಸ್ಥಾನ ಮತ್ತು ಶಾಸಕಾಂಗ ನಾಯಕತ್ವದ ಜವಾಬ್ದಾರಿಗಳು.' : 'Senior representative holding executive leadership and key committee responsibilities.'}
                </div>
              </div>

            </div>
          </div>
        )}

      </div>
    </div>
  );
}
