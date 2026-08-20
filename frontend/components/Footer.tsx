import Link from 'next/link';
import { Landmark, ShieldCheck, ExternalLink, FileText, BarChart3, Users } from 'lucide-react';
import { getDictionary, Locale } from '../lib/dictionary';

export default async function Footer({ lang }: { lang: Locale }) {
  const dict = await getDictionary(lang);

  return (
    <footer className="footer" style={{ background: '#0f172a', color: '#94a3b8', borderTop: '1px solid rgba(255,255,255,0.1)', padding: '48px 0 32px' }}>
      <div className="container">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 240px), 1fr))', gap: '32px', marginBottom: '40px', textAlign: 'left' }}>
          
          {/* Brand Col */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#ffffff', fontWeight: 700, fontSize: '1.1rem', marginBottom: '12px' }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '6px', background: '#334155', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff' }}>
                <Landmark size={16} />
              </div>
              Karnataka Legislative Tracker
            </div>
            <p style={{ fontSize: '0.85rem', lineHeight: '1.6', color: '#94a3b8', margin: 0 }}>
              An independent, non-partisan public intelligence repository tracking Karnataka’s 224 State Assembly MLAs and 28 Lok Sabha Members of Parliament.
            </p>
          </div>

          {/* Directory Quick Links */}
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#f8fafc', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '14px' }}>
              Public Directories
            </div>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
              <li>
                <Link href={`/${lang}/politicians`} style={{ color: '#cbd5e1', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                  <Users size={13} /> All Representatives (257)
                </Link>
              </li>
              <li>
                <Link href={`/${lang}/politicians?type=mp`} style={{ color: '#cbd5e1', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                  <Landmark size={13} /> Lok Sabha MPs (28)
                </Link>
              </li>
              <li>
                <Link href={`/${lang}/politicians?type=union_minister`} style={{ color: '#cbd5e1', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                  <ShieldCheck size={13} /> Union Cabinet Ministers
                </Link>
              </li>
              <li>
                <Link href={`/${lang}/analytics`} style={{ color: '#cbd5e1', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                  <BarChart3 size={13} /> Asset & Analytics Audit
                </Link>
              </li>
            </ul>
          </div>

          {/* Official Verification Notice */}
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#f8fafc', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '14px' }}>
              Data Sources & Standards
            </div>
            <p style={{ fontSize: '0.82rem', lineHeight: '1.6', color: '#94a3b8', margin: 0 }}>
              All financial asset declarations, educational records, and criminal disclosures are parsed directly from sworn affidavits filed with the Election Commission of India (ECI) & CEO Karnataka.
            </p>
          </div>
        </div>

        {/* Disclaimer & Copyright */}
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', fontSize: '0.78rem', color: '#64748b' }}>
          <div>
            &copy; {new Date().getFullYear()} Karnataka Legislative Tracker. Open Public Data Repository.
          </div>
          <div style={{ display: 'flex', gap: '16px' }}>
            <span>Verified ECI Affidavits</span>
            <span>•</span>
            <span>Karnataka Legislative Assembly</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
