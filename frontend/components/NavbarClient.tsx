'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Landmark, Menu, X, Users, BarChart3, Home as HomeIcon, Search } from 'lucide-react';
import LanguageToggle from './LanguageToggle';
import SearchAutocomplete from './SearchAutocomplete';
import { Locale } from '../lib/dictionary';

interface NavbarClientProps {
  lang: Locale;
  dictNav: {
    home: string;
    politicians: string;
    analytics?: string;
  };
  searchPlaceholder: string;
}

export default function NavbarClient({ lang, dictNav, searchPlaceholder }: NavbarClientProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  const toggleMobileMenu = () => setIsMobileMenuOpen((prev) => !prev);
  const closeMobileMenu = () => setIsMobileMenuOpen(false);

  const isKn = lang === 'kn';

  // Active path helpers
  const isHome = pathname === `/${lang}`;
  const isCabinet = pathname?.includes('/cabinet');
  const isPoliticians = pathname?.includes('/politicians');
  const isAnalytics = pathname?.includes('/analytics');

  return (
    <>
      <header className="navbar">
        <div className="container navbar-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '64px', gap: '16px' }}>
          
          {/* Brand Logo & Title */}
          <Link href={`/${lang}`} className="logo" onClick={closeMobileMenu}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '34px', height: '34px', borderRadius: '8px', background: '#0f172a', color: '#ffffff', flexShrink: 0, boxShadow: '0 2px 4px rgba(15,23,42,0.15)' }}>
              <Landmark size={19} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span className="logo-title" style={{ fontWeight: 800, fontSize: '1.05rem', color: '#0f172a', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
                {isKn ? 'ಕರ್ನಾಟಕ ಶಾಸಕರ ಟ್ರ್ಯಾಕರ್' : 'Karnataka Legislative Tracker'}
              </span>
              <span className="logo-subtitle" style={{ fontSize: '0.7rem', color: '#64748b', fontWeight: 600 }}>
                {isKn ? 'ಶಾಸಕರು & ಸಂಸದರ ಅಧಿಕೃತ ಮಾಹಿತಿ' : 'Verified Public Directory'}
              </span>
            </div>
          </Link>

          {/* Desktop Search & Nav Links */}
          <div className="desktop-nav" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <SearchAutocomplete lang={lang} placeholder={searchPlaceholder} />
            
            <Link href={`/${lang}`} className="nav-link">
              {dictNav.home}
            </Link>
            
            <Link href={`/${lang}/politicians`} className="nav-link">
              {dictNav.politicians}
            </Link>

            <Link href={`/${lang}/cabinet`} className="nav-link" style={{ color: '#047857', fontWeight: 700 }}>
              {isKn ? 'ಸಚಿವ ಸಂಪುಟ' : 'Cabinet Ministries'}
            </Link>

            <Link href={`/${lang}/politicians?type=mp`} className="nav-link">
              MPs
            </Link>
            
            <Link href={`/${lang}/analytics`} className="nav-link">
              {dictNav.analytics || 'Analytics Audit'}
            </Link>
            
            <LanguageToggle currentLang={lang} />
          </div>

          {/* Mobile Header Actions */}
          <div className="mobile-actions">
            <LanguageToggle currentLang={lang} />
            <button
              onClick={toggleMobileMenu}
              aria-label="Toggle Navigation Menu"
              style={{
                background: '#f1f5f9',
                border: '1px solid #cbd5e1',
                borderRadius: '8px',
                width: '42px',
                height: '42px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#0f172a',
                cursor: 'pointer',
                flexShrink: 0,
              }}
            >
              {isMobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
        </div>

        {/* Mobile Drawer Menu */}
        {isMobileMenuOpen && (
          <div
            style={{
              background: '#ffffff',
              borderBottom: '1px solid #e2e8f0',
              boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.12)',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
            }}
          >
            <SearchAutocomplete lang={lang} placeholder={isKn ? 'ನಾಯಕರ ಹೆಸರು ಹುಡುಕಿ...' : 'Search representative by name...'} />

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <Link
                href={`/${lang}`}
                onClick={closeMobileMenu}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  color: isHome ? '#1d4ed8' : '#0f172a',
                  fontWeight: isHome ? 700 : 600,
                  textDecoration: 'none',
                  background: isHome ? '#eff6ff' : '#f8fafc',
                }}
              >
                <HomeIcon size={20} color={isHome ? '#1d4ed8' : '#64748b'} /> {dictNav.home}
              </Link>

              <Link
                href={`/${lang}/cabinet`}
                onClick={closeMobileMenu}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  color: isCabinet ? '#047857' : '#0f172a',
                  fontWeight: isCabinet ? 700 : 600,
                  textDecoration: 'none',
                  background: isCabinet ? '#ecfdf5' : '#f8fafc',
                }}
              >
                <Landmark size={20} color={isCabinet ? '#047857' : '#64748b'} /> {isKn ? 'ಸಚಿವ ಸಂಪುಟ (Cabinet Ministries)' : 'Cabinet Ministries'}
              </Link>

              <Link
                href={`/${lang}/politicians`}
                onClick={closeMobileMenu}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  color: isPoliticians && !isCabinet ? '#2563eb' : '#0f172a',
                  fontWeight: isPoliticians && !isCabinet ? 700 : 600,
                  textDecoration: 'none',
                  background: isPoliticians && !isCabinet ? '#eff6ff' : '#f8fafc',
                }}
              >
                <Users size={20} color={isPoliticians && !isCabinet ? '#2563eb' : '#64748b'} /> {isKn ? 'ಶಾಸಕರು & ಸಂಸದರ ಪಟ್ಟಿ' : 'Representatives Directory'}
              </Link>

              <Link
                href={`/${lang}/analytics`}
                onClick={closeMobileMenu}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  color: isAnalytics ? '#6d28d9' : '#0f172a',
                  fontWeight: isAnalytics ? 700 : 600,
                  textDecoration: 'none',
                  background: isAnalytics ? '#f5f3ff' : '#f8fafc',
                }}
              >
                <BarChart3 size={20} color={isAnalytics ? '#6d28d9' : '#64748b'} /> {isKn ? 'ಆಸ್ತಿ & ಕ್ರಿಮಿನಲ್ ವಿಶ್ಲೇಷಣೆ' : 'Financial & Analytics Audit'}
              </Link>
            </div>
          </div>
        )}
      </header>

      {/* App-like Mobile Bottom Navigation Dock */}
      <nav className="mobile-bottom-nav">
        <Link href={`/${lang}`} className={`mobile-bottom-item ${isHome ? 'active' : ''}`}>
          <HomeIcon size={20} />
          <span>{isKn ? 'ಮುಖಪುಟ' : 'Home'}</span>
        </Link>

        <Link href={`/${lang}/cabinet`} className={`mobile-bottom-item ${isCabinet ? 'active' : ''}`}>
          <Landmark size={20} />
          <span>{isKn ? 'ಸಂಪುಟ' : 'Cabinet'}</span>
        </Link>

        <Link href={`/${lang}/politicians`} className={`mobile-bottom-item ${isPoliticians && !isCabinet ? 'active' : ''}`}>
          <Users size={20} />
          <span>{isKn ? 'ನಾಯಕರು' : 'Directory'}</span>
        </Link>

        <Link href={`/${lang}/analytics`} className={`mobile-bottom-item ${isAnalytics ? 'active' : ''}`}>
          <BarChart3 size={20} />
          <span>{isKn ? 'ಆಸ್ತಿ ಲೆಕ್ಕ' : 'Analytics'}</span>
        </Link>
      </nav>
    </>
  );
}
