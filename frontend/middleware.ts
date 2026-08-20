// Next.js Middleware for Locale Detection and Routing
// Handles automatic locale detection and redirection

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const locales = ['en', 'kn'] as const;
type Locale = typeof locales[number];

// Redirect paths without locale to the best matching locale
export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Check if the pathname is missing a locale
  const pathnameIsMissingLocale = locales.every(
    (locale) => !pathname.startsWith(`/${locale}/`) && pathname !== `/${locale}`
  );

  if (pathnameIsMissingLocale) {
    // Get the preferred locale from headers
    const acceptLanguage = request.headers.get('accept-language') || '';
    const preferredLocale = getPreferredLocale(acceptLanguage);

    // Redirect to the URL with the preferred locale
    const locale = preferredLocale || 'en';
    return NextResponse.redirect(
      new URL(`/${locale}${pathname}`, request.url)
    );
  }

  // Add locale to response headers for downstream use
  const response = NextResponse.next();
  
  // Set cookies for locale preference
  const currentLocale = getLocaleFromPath(pathname);
  if (currentLocale) {
    response.cookies.set('NEXT_LOCALE', currentLocale, {
      path: '/',
      maxAge: 60 * 60 * 24 * 365, // 1 year
      httpOnly: true,
    });
  }

  return response;
}

// Determine the preferred locale from Accept-Language header
function getPreferredLocale(acceptLanguage: string): Locale | null {
  if (!acceptLanguage) return null;

  // Parse Accept-Language header
  const languages = acceptLanguage
    .split(',')
    .map((lang) => {
      const [code, priority] = lang.trim().split(';q=');
      const quality = priority ? parseFloat(priority) : 1;
      return { code: code.split('-')[0], quality };
    })
    .filter((lang) => lang.quality > 0)
    .sort((a, b) => b.quality - a.quality);

  // Find matching locale
  for (const lang of languages) {
    if (locales.includes(lang.code as Locale)) {
      return lang.code as Locale;
    }
  }

  return null;
}

// Extract locale from pathname
function getLocaleFromPath(pathname: string): Locale | null {
  const segments = pathname.split('/');
  const firstSegment = segments[1];
  
  if (locales.includes(firstSegment as Locale)) {
    return firstSegment as Locale;
  }
  
  return null;
}

// Configure which paths the middleware runs on
export const config = {
  // Matcher: Ignore static files, api routes, and common asset paths
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - manifest.json (PWA manifest)
     * - robots.txt (SEO)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|manifest.json|robots.txt|sitemap.xml).*)',
  ],
};