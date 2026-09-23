import 'server-only';

export type Locale = 'en' | 'kn';

const dictionaries = {
  en: () => import('./dictionaries/en.json').then((module) => module.default),
  kn: () => import('./dictionaries/kn.json').then((module) => module.default),
};

export const getDictionary = async (locale: Locale) => {
  const loader = dictionaries[locale] ?? dictionaries.en;
  return loader();
};
