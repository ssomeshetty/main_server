'use client';

import { usePathname, useRouter } from 'next/navigation';
import { Locale } from '../lib/dictionary';

export default function LanguageToggle({ currentLang }: { currentLang: Locale }) {
  const router = useRouter();
  const pathname = usePathname();

  const toggleLang = (lang: Locale) => {
    if (lang === currentLang) return;
    const newPath = pathname.replace(`/${currentLang}`, `/${lang}`);
    router.push(newPath);
  };

  return (
    <div className="lang-switcher">
      <button 
        className={`lang-btn ${currentLang === 'en' ? 'active' : ''}`}
        onClick={() => toggleLang('en')}
      >
        EN
      </button>
      <button 
        className={`lang-btn ${currentLang === 'kn' ? 'active' : ''}`}
        onClick={() => toggleLang('kn')}
      >
        ಕನ್ನಡ
      </button>
    </div>
  );
}
