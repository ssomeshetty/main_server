'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import { Vote, ShieldCheck, CheckCircle2, TrendingUp, Users, FileText } from 'lucide-react';
import { ElectoralPerformance } from '../lib/api';

interface Props {
  data: ElectoralPerformance;
  candidateName: string;
  lang?: 'en' | 'kn';
}

export default function ElectoralVoteShareChart({ data, candidateName, lang: propLang }: Props) {
  const params = useParams();
  const routeLang = params?.lang as 'en' | 'kn';
  const isKn = (propLang || routeLang) === 'kn';

  const winnerPct = data.vote_percentage || 0;
  const runnerPct = data.runner_up_vote_pct || 0;
  const totalPolled = data.total_votes_polled || (data.votes_secured + data.runner_up_votes);
  const evmPct = totalPolled > 0 ? ((data.evm_votes / data.votes_secured) * 100).toFixed(1) : '99.5';
  const postalPct = totalPolled > 0 ? ((data.postal_votes / data.votes_secured) * 100).toFixed(1) : '0.5';

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
              <Vote size={18} />
            </span>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', margin: 0, letterSpacing: '-0.01em' }}>
              {isKn ? 'ಚುನಾವಣಾ ಫಲಿತಾಂಶ ಮತ್ತು ಮತ ಹಂಚಿಕೆ ವರದಿ' : 'Official Election Results & Vote Share Visuals'}
            </h3>
          </div>
          <p style={{ fontSize: '0.82rem', color: '#64748b', margin: 0 }}>
            {data.election_year} {isKn ? (data.election_type === 'lok_sabha' ? 'ಲೋಕಸಭಾ ಸಾರ್ವತ್ರಿಕ ಚುನಾವಣೆ' : 'ಕರ್ನಾಟಕ ವಿಧಾನಸಭಾ ಚುನಾವಣೆ') : (data.election_type === 'lok_sabha' ? 'Lok Sabha General Election' : 'Karnataka Assembly Election')} — {data.constituency_name}
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
          <ShieldCheck size={14} color="#16a34a" /> {isKn ? 'ECI ಅಧಿಕೃತ ಫಲಿತಾಂಶ' : 'ECI VERIFIED RESULT'}
        </span>
      </div>

      {/* Citizen Plain Language Summary Banner */}
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
          <strong>{isKn ? 'ಫಲಿತಾಂಶದ ಸಾರಾಂಶ:' : 'Election Result Summary:'}</strong>{' '}
          {isKn
            ? `${data.election_year} ರ ${data.constituency_name} ಕ್ಷೇತ್ರದ ಚುನಾವಣೆಯಲ್ಲಿ ${candidateName} (${data.party_name}) ಅವರು ಒಟ್ಟು ${data.votes_secured.toLocaleString('kn-IN')} ಮತಗಳನ್ನು (${winnerPct}%) ಪಡೆದು, ಎರಡನೇ ಸ್ಥಾನದ ${data.runner_up_name} ಅವರಿಗಿಂತ +${data.margin_votes.toLocaleString('kn-IN')} ಮತಗಳ ಅಂತರದಿಂದ ಗೆದ್ದಿದ್ದಾರೆ.`
            : `In the ${data.election_year} election for ${data.constituency_name}, ${candidateName} (${data.party_name}) won by securing ${data.votes_secured.toLocaleString('en-IN')} votes (${winnerPct}%), leading runner-up ${data.runner_up_name} by a margin of +${data.margin_votes.toLocaleString('en-IN')} votes.`}
        </div>
      </div>

      {/* Key Metric Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '12px',
          marginBottom: '20px',
        }}
      >
        <div style={{ background: '#ffffff', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
            {isKn ? 'ಪಡೆದ ಒಟ್ಟು ಮತಗಳು' : 'Votes Secured'}
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', marginTop: '4px' }}>
            {isKn ? data.votes_secured.toLocaleString('kn-IN') : data.votes_secured.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '0.78rem', color: '#16a34a', fontWeight: 600, marginTop: '2px', display: 'flex', alignItems: 'center', gap: '3px' }}>
            <TrendingUp size={12} /> {winnerPct}% {isKn ? 'ಮತಗಳ ಪಾಲು' : 'Vote Share'}
          </div>
        </div>

        <div style={{ background: '#ffffff', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
            {isKn ? 'ಗೆಲುವಿನ ಮತಗಳ ಅಂತರ' : 'Victory Margin'}
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#2563eb', marginTop: '4px' }}>
            +{isKn ? data.margin_votes.toLocaleString('kn-IN') : data.margin_votes.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '2px' }}>
            {isKn ? 'ಎದುರಾಳಿಗಿಂತ ಮುನ್ನಡೆ' : 'Lead Over Opponent'}
          </div>
        </div>

        <div style={{ background: '#ffffff', padding: '14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
            {isKn ? 'ಒಟ್ಟು ಚಲಾವಣೆಯಾದ ಮತಗಳು' : 'Total Polled Turnout'}
          </div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', marginTop: '4px' }}>
            {isKn ? data.total_votes_polled.toLocaleString('kn-IN') : data.total_votes_polled.toLocaleString('en-IN')}
          </div>
          <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '2px' }}>
            {isKn ? 'ಕ್ಷೇತ್ರದ ಒಟ್ಟು ಚಲಾವಣೆಯಾದ ಮತಗಳು' : 'Total Registered Electors'}
          </div>
        </div>
      </div>

      {/* Visual Candidate Performance Bar Graph */}
      <div style={{ marginBottom: '20px', background: '#f8fafc', padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
        <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f172a', marginBottom: '14px', textTransform: 'uppercase', letterSpacing: '0.02em' }}>
          {isKn ? 'ಅಭ್ಯರ್ಥಿಗಳ ಮತ ಹಂಚಿಕೆ ಹೋಲಿಕೆ' : 'Candidate Performance vs Runner-Up (Visual Comparison)'}
        </h4>

        {/* Winner Bar */}
        <div style={{ marginBottom: '14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
            <span style={{ color: '#0f172a', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={14} color="#16a34a" />
              <strong>{candidateName}</strong> ({data.party_name}){' '}
              <span style={{ background: '#ecfdf5', color: '#15803d', border: '1px solid #a7f3d0', padding: '2px 6px', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 700 }}>
                {isKn ? 'ವಿಜೇತರು' : 'WINNER'}
              </span>
            </span>
            <span style={{ color: '#15803d', fontWeight: 700 }}>
              {isKn ? data.votes_secured.toLocaleString('kn-IN') : data.votes_secured.toLocaleString('en-IN')} ({winnerPct}%)
            </span>
          </div>
          <div style={{ height: '10px', background: '#e2e8f0', borderRadius: '5px', overflow: 'hidden' }}>
            <div style={{ width: `${winnerPct}%`, height: '100%', background: '#16a34a', borderRadius: '5px' }} />
          </div>
        </div>

        {/* Runner-Up Bar */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
            <span style={{ color: '#475569' }}>
              {data.runner_up_name} ({data.runner_up_party})
            </span>
            <span style={{ color: '#64748b' }}>
              {isKn ? data.runner_up_votes.toLocaleString('kn-IN') : data.runner_up_votes.toLocaleString('en-IN')} ({runnerPct}%)
            </span>
          </div>
          <div style={{ height: '10px', background: '#e2e8f0', borderRadius: '5px', overflow: 'hidden' }}>
            <div style={{ width: `${runnerPct}%`, height: '100%', background: '#64748b', borderRadius: '5px' }} />
          </div>
        </div>
      </div>

      {/* EVM vs Postal Breakdown */}
      <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', background: '#ffffff', padding: '12px 16px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '0.82rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
          <FileText size={15} color="#2563eb" />
          <div>
            <strong style={{ color: '#0f172a' }}>{isKn ? 'EVM ಚಲಾವಣೆಯಾದ ಮತಗಳು:' : 'EVM Polled:'}</strong>{' '}
            {isKn ? data.evm_votes.toLocaleString('kn-IN') : data.evm_votes.toLocaleString('en-IN')} ({evmPct}%)
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
          <Users size={15} color="#7c3aed" />
          <div>
            <strong style={{ color: '#0f172a' }}>{isKn ? 'ಅಂಚೆ ಮತಗಳು (Postal):' : 'Postal Votes:'}</strong>{' '}
            {isKn ? data.postal_votes.toLocaleString('kn-IN') : data.postal_votes.toLocaleString('en-IN')} ({postalPct}%)
          </div>
        </div>
      </div>
    </div>
  );
}
