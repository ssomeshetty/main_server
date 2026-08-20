import NavbarClient from './NavbarClient';
import { getDictionary, Locale } from '../lib/dictionary';

export default async function Navbar({ lang }: { lang: Locale }) {
  const dict = await getDictionary(lang);

  return (
    <NavbarClient
      lang={lang}
      dictNav={dict.navigation}
      searchPlaceholder={dict.home.searchPlaceholder || 'Search representatives by name...'}
    />
  );
}
