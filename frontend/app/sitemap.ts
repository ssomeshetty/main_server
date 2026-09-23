import { MetadataRoute } from 'next';
import { fetchAllPoliticianSlugs } from '../lib/api';

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://politicianstracker.in';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const locales = ['en', 'kn'];
  const routes = ['', '/politicians', '/analytics', '/cabinet'];

  // Static route URLs across locales
  const staticUrls: MetadataRoute.Sitemap = [];

  for (const lang of locales) {
    for (const route of routes) {
      staticUrls.push({
        url: `${SITE_URL}/${lang}${route}`,
        changeFrequency: route === '' ? 'daily' : 'weekly',
        priority: route === '' ? 1.0 : 0.8,
        alternates: {
          languages: {
            en: `${SITE_URL}/en${route}`,
            kn: `${SITE_URL}/kn${route}`,
          },
        },
      });
    }
  }

  // Dynamic politician detail URLs across all politicians and locales
  const politicianSlugs = await fetchAllPoliticianSlugs();
  const politicianUrls: MetadataRoute.Sitemap = [];

  for (const item of politicianSlugs) {
    const slug = item.slug;
    for (const lang of locales) {
      politicianUrls.push({
        url: `${SITE_URL}/${lang}/politicians/${slug}`,
        changeFrequency: 'weekly',
        priority: 0.9,
        alternates: {
          languages: {
            en: `${SITE_URL}/en/politicians/${slug}`,
            kn: `${SITE_URL}/kn/politicians/${slug}`,
          },
        },
      });
    }
  }

  return [...staticUrls, ...politicianUrls];
}
